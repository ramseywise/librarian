"""Claude Code session JSONL parser — extracts session stats and generates reports.

Reads ~/.claude/projects/**/*.jsonl, computes per-session and aggregate metrics,
optionally calls the Anthropic API to generate an HTML insights report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# Relative cost weights: multiples of the input-token price (Anthropic cache pricing).
# "cost units" throughout = token counts weighted by these, so percentages reflect
# spend, not raw message counts. Output priced at ~5x input across Claude models.
_COST_INPUT = 1.0
_COST_CACHE_WRITE = 1.25
_COST_CACHE_READ = 0.1
_COST_OUTPUT = 5.0

# Effective request context = input + cache_read + cache_creation tokens
_CONTEXT_BUCKETS = ("<50k", "50-100k", "100-150k", ">150k")


def _context_bucket(context_tokens: int) -> str:
    if context_tokens < 50_000:
        return "<50k"
    if context_tokens < 100_000:
        return "50-100k"
    if context_tokens < 150_000:
        return "100-150k"
    return ">150k"


def _usage_cost(usage: dict[str, Any]) -> float:
    """Cost of one request in input-price-relative units."""
    return (
        usage.get("input_tokens", 0) * _COST_INPUT
        + usage.get("cache_creation_input_tokens", 0) * _COST_CACHE_WRITE
        + usage.get("cache_read_input_tokens", 0) * _COST_CACHE_READ
        + usage.get("output_tokens", 0) * _COST_OUTPUT
    )


# ---------------------------------------------------------------------------
# JSONL parsing
# ---------------------------------------------------------------------------


def iter_sessions(projects_dir: Path) -> list[dict[str, Any]]:
    """Return one dict of stats per .jsonl session file."""
    sessions: list[dict[str, Any]] = []
    for jsonl in sorted(projects_dir.rglob("*.jsonl")):
        if "/subagents/" in str(jsonl):
            continue
        session = parse_session(jsonl)
        if session:
            sessions.append(session)
    return sessions


def iter_subagent_sessions(projects_dir: Path) -> list[dict[str, Any]]:
    """Parse subagent transcripts, each attributed to its parent session.

    Layout: <projects>/<project>/<session-id>/subagents/agent-*.jsonl
    """
    subs: list[dict[str, Any]] = []
    for jsonl in sorted(projects_dir.rglob("*/subagents/*.jsonl")):
        session = parse_session(jsonl)
        if session:
            session["is_subagent"] = True
            session["parent_session_id"] = jsonl.parent.parent.name
            subs.append(session)
    return subs


def _text(content: object) -> str:
    """Extract plain text from a message content field."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    return ""


def _parse_timestamp(record: dict[str, Any]) -> datetime | None:
    """Extract a datetime from a record's timestamp field."""
    raw = record.get("timestamp", "")
    if raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None


def _is_human_turn(record: dict[str, Any]) -> bool:
    """True when a user-role record is a real human turn, not a tool result.

    Tool results are delivered as user-role messages, so any timing or counting
    over raw type=="user" records is dominated by machine traffic.
    """
    content = record.get("message", {}).get("content", [])
    if isinstance(content, str):
        return bool(content.strip())
    if not isinstance(content, list):
        return False
    return not any(
        isinstance(block, dict) and block.get("type") == "tool_result" for block in content
    )


WORKSPACE_ROOT = "/Users/wiseer/workspace"


def _session_repos(records: list[dict[str, Any]]) -> dict[str, int]:
    """Repos this session actually worked in, by record count under each.

    `records[0]["cwd"]` is the *launch* directory, which is the workspace root for
    86% of July sessions (measured 2026-07-20) -- Ramsey drives many repos from
    the root, so the launch dir names no repo at all. But `cwd` is emitted on
    every record and follows the session into subdirectories, so scanning all of
    them resolves a repo for 87% of transcripts instead of 14%.

    Returns {repo_name: record_count}, empty when a session never left the root.
    Callers decide how to attribute a multi-repo session -- this deliberately
    returns the whole distribution rather than picking a winner, because 22% of
    sessions touch more than one repo and the median dominant share is only 57%.
    """
    counts: dict[str, int] = {}
    prefix = WORKSPACE_ROOT + "/"
    for record in records:
        cwd = record.get("cwd")
        if not isinstance(cwd, str) or not cwd.startswith(prefix):
            continue
        repo = cwd[len(prefix) :].split("/", 1)[0]
        if repo:
            counts[repo] = counts.get(repo, 0) + 1
    return counts


def _human_turn_times(user_msgs: list[dict[str, Any]]) -> list[datetime]:
    """Timestamps of genuine human turns, in record order."""
    return [t for r in user_msgs if _is_human_turn(r) and (t := _parse_timestamp(r)) is not None]


# Language map for file extension detection
_LANG_MAP: dict[str, str] = {
    "py": "Python",
    "ts": "TypeScript",
    "tsx": "TypeScript",
    "js": "JavaScript",
    "jsx": "JavaScript",
    "md": "Markdown",
    "json": "JSON",
    "yaml": "YAML",
    "yml": "YAML",
    "sh": "Shell",
    "bash": "Shell",
    "ipynb": "Notebook",
    "sql": "SQL",
    "toml": "TOML",
    "html": "HTML",
    "css": "CSS",
}


def parse_session(path: Path) -> dict[str, Any] | None:
    """Parse a single JSONL session file into a stats dict."""
    lines = path.read_text(errors="replace").splitlines()
    records: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    user_msgs = [r for r in records if r.get("type") == "user"]
    asst_msgs = [r for r in records if r.get("type") == "assistant"]

    if not user_msgs:
        return None

    # Subagent type name, e.g. "Explore" / "akira-scan". Emitted per-record by CLI
    # 2.1.201+; transcripts written by older builds carry no attribution at all and
    # leave this None (see SUBAGENT_ATTRIBUTION_CLI in factstore).
    attribution_agent = next(
        (str(a) for r in records if (a := r.get("attributionAgent"))),
        None,
    )

    # Surface the session ran on (e.g. "claude-vscode"). Constant per session/CLI
    # launch. None on transcripts predating this field — see factstore.NULLABLE_COLUMNS.
    entrypoint = next(
        (str(e) for r in records if (e := r.get("entrypoint"))),
        None,
    )

    # Timestamps
    user_times = [t for r in user_msgs if (t := _parse_timestamp(r)) is not None]
    if not user_times:
        return None

    start = min(user_times)
    end = max(user_times)
    duration_minutes = (end - start).total_seconds() / 60

    # First real user prompt (skip ide_opened_file injections)
    first_prompt = ""
    for record in user_msgs:
        txt = _text(record.get("message", {}).get("content", ""))
        txt = re.sub(r"<[^>]+>.*?</[^>]+>", "", txt, flags=re.DOTALL).strip()
        if txt:
            first_prompt = txt[:200]
            break

    # Tool counts from assistant messages
    tool_counts: dict[str, int] = defaultdict(int)
    for record in asst_msgs:
        for block in record.get("message", {}).get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tool_counts[block.get("name", "unknown")] += 1

    # Agent spawn metadata from parent sessions
    agent_spawns: list[dict[str, str | None]] = []
    for record in asst_msgs:
        for block in record.get("message", {}).get("content", []):
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Agent"
            ):
                inp = block.get("input", {})
                agent_spawns.append(
                    {
                        "type": inp.get("subagent_type", "general-purpose"),
                        "description": inp.get("description"),
                        "model": inp.get("model"),
                    }
                )

    # Tool result errors from user messages
    tool_errors: dict[str, int] = defaultdict(int)
    for record in user_msgs:
        for block in record.get("message", {}).get("content", []):
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_result"
                and block.get("is_error")
            ):
                content_text = _text(block.get("content", "")).lower()
                if "no such file" in content_text or "not found" in content_text:
                    tool_errors["file_not_found"] += 1
                elif "permission" in content_text:
                    tool_errors["permission_denied"] += 1
                elif "rejected" in content_text:
                    tool_errors["user_rejected"] += 1
                elif "failed" in content_text or "exit code" in content_text:
                    tool_errors["command_failed"] += 1
                elif "too large" in content_text or "too long" in content_text:
                    tool_errors["file_too_large"] += 1
                elif "edit" in content_text:
                    tool_errors["edit_failed"] += 1
                else:
                    tool_errors["other"] += 1

    # Token usage + model tracking + per-request cost/context
    input_tokens = 0
    output_tokens = 0
    cache_write_tokens = 0
    cache_read_tokens = 0
    cost_units = 0.0
    max_context = 0
    context_bucket_cost: dict[str, float] = dict.fromkeys(_CONTEXT_BUCKETS, 0.0)
    cost_events: list[tuple[str, float]] = []
    model_counts: dict[str, int] = defaultdict(int)
    model_costs: dict[str, float] = defaultdict(float)
    model_tokens: dict[str, int] = defaultdict(int)
    for record in asst_msgs:
        msg = record.get("message", {})
        usage = msg.get("usage", {})
        input_tokens += usage.get("input_tokens", 0)
        output_tokens += usage.get("output_tokens", 0)
        cache_write_tokens += usage.get("cache_creation_input_tokens", 0)
        cache_read_tokens += usage.get("cache_read_input_tokens", 0)
        cost = _usage_cost(usage)
        cost_units += cost
        context = (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
        )
        if context:
            max_context = max(max_context, context)
            context_bucket_cost[_context_bucket(context)] += cost
        event_ts = _parse_timestamp(record)
        if event_ts is not None and cost:
            cost_events.append((event_ts.isoformat(), cost))
        model_id = msg.get("model", "")
        if model_id:
            model_counts[model_id] += 1
            model_costs[model_id] += cost
            model_tokens[model_id] += usage.get("output_tokens", 0)
    primary_model = max(model_counts, key=lambda k: model_counts[k]) if model_counts else "unknown"

    # Compaction events (system compact_boundary records; older format flags the
    # summary message instead — take the max to avoid double-counting pairs)
    compact_count = max(
        sum(
            1
            for r in records
            if r.get("type") == "system" and r.get("subtype") == "compact_boundary"
        ),
        sum(1 for r in records if r.get("isCompactSummary")),
    )

    # Files modified via file-history-snapshots
    files_modified: set[str] = set()
    for record in records:
        if record.get("type") == "file-history-snapshot":
            file_id = record.get("fileId", "")
            if file_id:
                files_modified.add(file_id)

    # Languages from file extensions in tool_use Read/Write/Edit
    langs: dict[str, int] = defaultdict(int)
    for record in asst_msgs:
        for block in record.get("message", {}).get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                inp = block.get("input", {})
                fpath = inp.get("file_path", inp.get("path", ""))
                if fpath:
                    ext = Path(fpath).suffix.lstrip(".").lower()
                    lang = _LANG_MAP.get(ext)
                    if lang:
                        langs[lang] += 1

    # User response times (gap between consecutive *human* turns).
    #
    # `user_msgs` is every type=="user" record, but ~90% of those are synthetic:
    # a tool_result is delivered as a user-role message. Timing those measured
    # tool latency, not the human, and inflated the interruption count roughly
    # 10x (verified 2026-07-20 over 6 transcripts). Human turns only.
    response_times: list[float] = []
    sorted_user_times = sorted(_human_turn_times(user_msgs))
    for i in range(1, len(sorted_user_times)):
        delta = (sorted_user_times[i] - sorted_user_times[i - 1]).total_seconds()
        if 1 < delta < 7200:  # ignore tiny/huge gaps
            response_times.append(delta)

    # Message hours (UTC)
    message_hours = [t.hour for t in user_times]

    # User interruptions: a human turn arriving <5s after the previous one, i.e.
    # too fast to be a considered reply. Still a heuristic, but calibrated --
    # over human-only turns the gap median is ~226s and only 3.8% fall under 5s
    # (measured 2026-07-20, n=157), so the threshold isolates a real tail rather
    # than splitting the bulk of the distribution.
    interruptions = sum(1 for t in response_times if t < 5)

    # --- Context engineering signals ---

    # Bash antipatterns: shell used where a dedicated tool exists
    _SHELL_ANTIPATTERNS = re.compile(
        r"\bcat\s+\S|\bhead\s|\btail\s|\bsed\s|\bawk\s"
        r"|\bgrep\s|\brg\s|\bfind\s+\.|\bls\s|\bwc\s"
    )
    bash_antipatterns = 0
    for record in asst_msgs:
        for block in record.get("message", {}).get("content", []):
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Bash"
            ):
                cmd = block.get("input", {}).get("command", "")
                if _SHELL_ANTIPATTERNS.search(cmd):
                    bash_antipatterns += 1

    # Skill invocations: /skill-name patterns in user messages
    skill_invocations: list[str] = []
    for record in user_msgs:
        txt = _text(record.get("message", {}).get("content", ""))
        txt = re.sub(r"<[^>]+>.*?</[^>]+>", "", txt, flags=re.DOTALL)
        skill_invocations.extend(re.findall(r"(?:^|\s)/([a-z][a-z0-9-]+)", txt))

    # Skill tool calls: the regex above only sees typed /slash text, so skills
    # invoked through the Skill tool (including auto-triggered ones) are missed.
    for record in asst_msgs:
        for block in record.get("message", {}).get("content", []):
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Skill"
            ):
                name = block.get("input", {}).get("skill")
                if name:
                    skill_invocations.append(name)

    # Friction labels from user messages
    friction_labels: list[str] = []
    for record in user_msgs:
        txt = _text(record.get("message", {}).get("content", ""))
        for match in re.findall(r"FRICTION:\s*(.+?)(?:\n|$)", txt):
            friction_labels.append(match.strip()[:200])

    # Output tokens per assistant message (verbosity signal)
    output_tokens_per_msg = round(output_tokens / len(asst_msgs), 1) if asst_msgs else 0.0

    # Skill/command cost attribution: assistant cost between a slash invocation
    # and the next real user prompt is attributed to that skill. The invocation
    # record is followed by a user message carrying the expanded skill prompt —
    # consume it as part of the same turn rather than resetting.
    skill_costs: dict[str, float] = defaultdict(float)
    current_skill: str | None = None
    expansion_pending = False
    for record in records:
        rtype = record.get("type")
        if rtype == "user":
            txt = _text(record.get("message", {}).get("content", ""))
            if not txt.strip():
                continue  # tool results — same turn continues
            cmd = re.search(r"<command-name>/([\w-]+)</command-name>", txt)
            if cmd:
                current_skill = cmd.group(1)
                expansion_pending = True
                continue
            stripped = re.sub(r"<[^>]+>.*?</[^>]+>", "", txt, flags=re.DOTALL).strip()
            if not stripped:
                continue
            if expansion_pending:
                expansion_pending = False
                continue
            slash = re.match(r"/([a-z][a-z0-9_-]+)", stripped)
            current_skill = slash.group(1) if slash else None
        elif rtype == "assistant" and current_skill:
            skill_costs[current_skill] += _usage_cost(record.get("message", {}).get("usage", {}))

    # Read/Edit ratio: should be > 1 (understand before changing)
    edit_calls = (
        tool_counts.get("Edit", 0) + tool_counts.get("Write", 0) + tool_counts.get("MultiEdit", 0)
    )
    read_edit_ratio = round(tool_counts.get("Read", 0) / edit_calls, 2) if edit_calls > 0 else None

    # Hook blocks: user_rejected errors on Bash (hook-triggered rejections)
    hook_blocks = tool_errors.get("user_rejected", 0)

    # Long session without TodoWrite (planning discipline)
    has_todo_write = tool_counts.get("TodoWrite", 0) > 0

    return {
        "session_id": path.stem,
        "project_path": str(records[0].get("cwd", "")) if records else "",
        # Repo attribution from every cwd, not just the launch dir -- see
        # _session_repos. JSON {repo: record_count}; {} when the session never
        # left the workspace root.
        "session_repos": _session_repos(records),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_minutes": round(duration_minutes, 1),
        # Human turns only. `user_msgs` is ~92% tool_result records (measured
        # 2026-07-20, n=3869 over 60 transcripts), so len(user_msgs) reported
        # roughly 12x the real prompt count and made msgs_per_day meaningless.
        "user_message_count": sum(1 for r in user_msgs if _is_human_turn(r)),
        "assistant_message_count": len(asst_msgs),
        "tool_counts": dict(tool_counts),
        "tool_errors": dict(tool_errors),
        "languages": dict(langs),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read_tokens,
        "cache_write_tokens": cache_write_tokens,
        "cost_units": round(cost_units, 1),
        "max_context": max_context,
        "context_bucket_cost": {k: round(v, 1) for k, v in context_bucket_cost.items()},
        "cost_events": cost_events,
        "compact_count": compact_count,
        "skill_costs": {k: round(v, 1) for k, v in skill_costs.items()},
        "is_subagent": False,
        "parent_session_id": None,
        "attribution_agent": attribution_agent,
        "models": dict(model_counts),
        "model_costs": {k: round(v, 1) for k, v in model_costs.items()},
        "model_output_tokens": dict(model_tokens),
        "primary_model": primary_model,
        "files_modified": len(files_modified),
        "first_prompt": first_prompt,
        "user_response_times": response_times,
        "user_interruptions": interruptions,
        "message_hours": message_hours,
        "uses_task_agent": tool_counts.get("Task", 0) > 0,
        # CE / PE signals
        "bash_antipatterns": bash_antipatterns,
        "skill_invocations": skill_invocations,
        "output_tokens_per_msg": output_tokens_per_msg,
        "read_edit_ratio": read_edit_ratio,
        "hook_blocks": hook_blocks,
        "has_todo_write": has_todo_write,
        "agent_spawns": agent_spawns,
        "friction_labels": friction_labels,
        "friction_label_count": len(friction_labels),
        "entrypoint": entrypoint,
    }


# ---------------------------------------------------------------------------
# Aggregate stats
# ---------------------------------------------------------------------------


def _aggregate_economics(
    sessions: list[dict[str, Any]],
    subagent_sessions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cost-weighted usage signals: context buckets, cache economics, subagent
    share, parallelism, and skill share — all as % of total cost units."""
    everything = [*sessions, *subagent_sessions]
    total_cost = sum(s.get("cost_units", 0.0) for s in everything)

    # Context-size distribution, cost-weighted
    bucket_cost: dict[str, float] = dict.fromkeys(_CONTEXT_BUCKETS, 0.0)
    for s in everything:
        for bucket, cost in s.get("context_bucket_cost", {}).items():
            bucket_cost[bucket] = bucket_cost.get(bucket, 0.0) + cost
    context_usage_pct = {
        k: round(v / total_cost * 100) if total_cost else 0 for k, v in bucket_cost.items()
    }

    # Cache economics: hit rate + savings vs. running the same tokens uncached
    total_input = sum(s.get("input_tokens", 0) for s in everything)
    total_cache_read = sum(s.get("cache_read_tokens", 0) for s in everything)
    total_cache_write = sum(s.get("cache_write_tokens", 0) for s in everything)
    total_output = sum(s.get("output_tokens", 0) for s in everything)
    all_input = total_input + total_cache_read + total_cache_write
    cost_uncached = all_input * _COST_INPUT + total_output * _COST_OUTPUT
    cache = {
        "hit_rate_pct": round(total_cache_read / all_input * 100) if all_input else 0,
        "savings_vs_uncached_pct": round((cost_uncached - total_cost) / cost_uncached * 100)
        if cost_uncached
        else 0,
    }

    # Subagent share + subagent-heavy sessions (>25% of session cost in subagents)
    sub_cost_by_parent: dict[str, float] = defaultdict(float)
    for sub in subagent_sessions:
        sub_cost_by_parent[sub.get("parent_session_id") or ""] += sub.get("cost_units", 0.0)
    subagent_cost = sum(sub_cost_by_parent.values())
    heavy_sessions = 0
    heavy_cost = 0.0
    for s in sessions:
        sub = sub_cost_by_parent.get(s["session_id"], 0.0)
        whole = s.get("cost_units", 0.0) + sub
        if whole and sub / whole > 0.25:
            heavy_sessions += 1
            heavy_cost += whole
    subagents = {
        "transcripts": len(subagent_sessions),
        "share_of_usage_pct": round(subagent_cost / total_cost * 100) if total_cost else 0,
        "heavy_sessions": heavy_sessions,
        "pct_usage_in_heavy_sessions": round(heavy_cost / total_cost * 100) if total_cost else 0,
    }

    # Parallelism, cost-weighted: concurrency = main sessions active at each request.
    # Intervals extend past end_time (last user msg) to the last billed request.
    starts: list[datetime] = []
    ends: list[datetime] = []
    for s in sessions:
        end = datetime.fromisoformat(s["end_time"])
        event_times = [datetime.fromisoformat(ts) for ts, _ in s.get("cost_events", [])]
        if event_times:
            end = max(end, max(event_times))
        starts.append(datetime.fromisoformat(s["start_time"]))
        ends.append(end)
    starts.sort()
    ends.sort()
    parallel_cost = {"1": 0.0, "2-3": 0.0, "4+": 0.0}
    for s in everything:
        for ts_iso, cost in s.get("cost_events", []):
            ts = datetime.fromisoformat(ts_iso)
            concurrent = max(bisect_right(starts, ts) - bisect_left(ends, ts), 1)
            if concurrent == 1:
                parallel_cost["1"] += cost
            elif concurrent <= 3:
                parallel_cost["2-3"] += cost
            else:
                parallel_cost["4+"] += cost
    parallelism_usage_pct = {
        k: round(v / total_cost * 100) if total_cost else 0 for k, v in parallel_cost.items()
    }

    # Skill/command share of usage (turn-attributed, main sessions carry these)
    skill_cost_totals: dict[str, float] = defaultdict(float)
    for s in everything:
        for skill, cost in s.get("skill_costs", {}).items():
            skill_cost_totals[skill] += cost
    skill_usage_pct = {
        k: round(v / total_cost * 100, 1) if total_cost else 0
        for k, v in sorted(skill_cost_totals.items(), key=lambda x: -x[1])[:8]
    }

    compacts_total = sum(s.get("compact_count", 0) for s in sessions)
    sessions_with_compacts = sum(1 for s in sessions if s.get("compact_count", 0) > 0)

    return {
        "usage_cost_units": round(total_cost),
        "context_usage_pct": context_usage_pct,
        "pct_usage_over_150k_context": context_usage_pct.get(">150k", 0),
        "cache": cache,
        "subagents": subagents,
        "parallelism_usage_pct": parallelism_usage_pct,
        "skill_usage_pct": skill_usage_pct,
        "compacts": {
            "total": compacts_total,
            "sessions_with_compacts": sessions_with_compacts,
        },
    }


def aggregate(
    sessions: list[dict[str, Any]],
    subagent_sessions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute aggregate statistics across all sessions.

    subagent_sessions (from iter_subagent_sessions) contribute to the
    cost-weighted economics signals only, attributed to their parent sessions.
    """
    if not sessions:
        return {}
    subagent_sessions = subagent_sessions or []

    all_tools: dict[str, int] = defaultdict(int)
    all_langs: dict[str, int] = defaultdict(int)
    all_errors: dict[str, int] = defaultdict(int)
    all_hours: list[int] = []
    all_response_times: list[float] = []
    total_user_msgs = 0
    total_files = 0
    total_interruptions = 0
    dates: list[str] = []
    # CE / PE accumulators
    total_bash_antipatterns = 0
    all_skill_invocations: list[str] = []
    output_tpm_list: list[float] = []
    read_edit_ratios: list[float] = []
    total_hook_blocks = 0
    total_cache_read = 0
    long_sessions_no_todo = 0

    all_models: dict[str, int] = defaultdict(int)
    total_cache_write = 0

    for session in sessions:
        for model_id, count in session.get("models", {}).items():
            all_models[model_id] += count
        total_cache_write += session.get("cache_write_tokens", 0)
        for key, val in session["tool_counts"].items():
            all_tools[key] += val
        for key, val in session["languages"].items():
            all_langs[key] += val
        for key, val in session["tool_errors"].items():
            all_errors[key] += val
        all_hours.extend(session["message_hours"])
        all_response_times.extend(session["user_response_times"])
        total_user_msgs += session["user_message_count"]
        total_files += session["files_modified"]
        total_interruptions += session["user_interruptions"]
        dates.append(session["start_time"][:10])
        # CE / PE
        total_bash_antipatterns += session.get("bash_antipatterns", 0)
        all_skill_invocations.extend(session.get("skill_invocations", []))
        if session.get("output_tokens_per_msg"):
            output_tpm_list.append(session["output_tokens_per_msg"])
        if session.get("read_edit_ratio") is not None:
            read_edit_ratios.append(session["read_edit_ratio"])
        total_hook_blocks += session.get("hook_blocks", 0)
        total_cache_read += session.get("cache_read_tokens", 0)
        if session["duration_minutes"] > 30 and not session.get("has_todo_write"):
            long_sessions_no_todo += 1

    dates.sort()

    # Detect parallel sessions (overlap heuristic)
    sorted_sessions = sorted(sessions, key=lambda x: x["start_time"])
    overlap_events = 0
    sessions_involved: set[str] = set()
    for i, sess_a in enumerate(sorted_sessions):
        for sess_b in sorted_sessions[i + 1 :]:
            if sess_b["start_time"] > sess_a["end_time"]:
                break
            overlap_events += 1
            sessions_involved.add(sess_a["session_id"])
            sessions_involved.add(sess_b["session_id"])

    overlap_messages = sum(
        s["user_message_count"] for s in sessions if s["session_id"] in sessions_involved
    )
    overlap_pct = round(overlap_messages / total_user_msgs * 100) if total_user_msgs else 0

    # Time-of-day buckets
    hour_counts: dict[int, int] = defaultdict(int)
    for hour in all_hours:
        hour_counts[hour] += 1

    median_rt = (
        sorted(all_response_times)[len(all_response_times) // 2] if all_response_times else 0
    )
    avg_rt = sum(all_response_times) / len(all_response_times) if all_response_times else 0

    # Response time distribution
    rt_buckets: dict[str, int] = {
        "2-10s": 0,
        "10-30s": 0,
        "30s-1m": 0,
        "1-2m": 0,
        "2-5m": 0,
        "5-15m": 0,
        ">15m": 0,
    }
    for time_val in all_response_times:
        if time_val < 10:
            rt_buckets["2-10s"] += 1
        elif time_val < 30:
            rt_buckets["10-30s"] += 1
        elif time_val < 60:
            rt_buckets["30s-1m"] += 1
        elif time_val < 120:
            rt_buckets["1-2m"] += 1
        elif time_val < 300:
            rt_buckets["2-5m"] += 1
        elif time_val < 900:
            rt_buckets["5-15m"] += 1
        else:
            rt_buckets[">15m"] += 1

    days_active = len(set(dates))
    # Human prompts per active day. Counts genuine human turns only (see
    # `user_message_count`) -- before 2026-07-20 this counted tool_result records
    # too and ran ~12x higher, so figures quoted from older reports are not
    # comparable to these.
    msgs_per_day = round(total_user_msgs / days_active, 1) if days_active else 0

    economics = _aggregate_economics(sessions, subagent_sessions)

    return {
        **economics,
        "session_count": len(sessions),
        "total_user_messages": total_user_msgs,
        "days_active": days_active,
        "msgs_per_day": msgs_per_day,
        "date_range": f"{dates[0]} to {dates[-1]}" if dates else "",
        "top_tools": dict(sorted(all_tools.items(), key=lambda x: -x[1])[:8]),
        "languages": dict(sorted(all_langs.items(), key=lambda x: -x[1])[:6]),
        "tool_errors": dict(sorted(all_errors.items(), key=lambda x: -x[1])[:6]),
        "hour_counts": dict(hour_counts),
        "response_time_distribution": rt_buckets,
        "median_response_time": round(median_rt, 1),
        "avg_response_time": round(avg_rt, 1),
        "total_files_touched": total_files,
        "total_interruptions": total_interruptions,
        "parallel_sessions": {
            "overlap_events": overlap_events,
            "sessions_involved": len(sessions_involved),
            "pct_messages": overlap_pct,
        },
        "uses_task_agent": sum(1 for s in sessions if s["uses_task_agent"]),
        # --- Context engineering signals ---
        "bash_antipatterns_total": total_bash_antipatterns,
        "bash_antipatterns_per_session": round(total_bash_antipatterns / len(sessions), 2),
        "skill_invocations": dict(
            sorted(
                defaultdict(
                    int,
                    {s: all_skill_invocations.count(s) for s in set(all_skill_invocations)},
                ).items(),
                key=lambda x: -x[1],
            )
        ),
        "hook_blocks_total": total_hook_blocks,
        "cache_read_tokens_total": total_cache_read,
        "cache_write_tokens_total": total_cache_write,
        "model_distribution": dict(sorted(all_models.items(), key=lambda x: -x[1])),
        "long_sessions_without_todo": long_sessions_no_todo,
        # --- Prompt engineering signals ---
        "output_tokens_per_msg": {
            "median": round(sorted(output_tpm_list)[len(output_tpm_list) // 2], 1)
            if output_tpm_list
            else 0,
            "p75": round(sorted(output_tpm_list)[int(len(output_tpm_list) * 0.75)], 1)
            if output_tpm_list
            else 0,
            "p90": round(sorted(output_tpm_list)[int(len(output_tpm_list) * 0.90)], 1)
            if output_tpm_list
            else 0,
        },
        "read_edit_ratio": {
            "avg": round(sum(read_edit_ratios) / len(read_edit_ratios), 2)
            if read_edit_ratios
            else None,
            "sessions_below_1": sum(1 for r in read_edit_ratios if r < 1.0),
        },
    }


# ---------------------------------------------------------------------------
# Session notes parsing (cord / no-JSONL environments)
# ---------------------------------------------------------------------------


def _split_sections(text: str) -> dict[str, str]:
    """Split markdown into a dict of {section_title: body} by ## headers."""
    sections: dict[str, str] = {}
    current_key: str | None = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(lines).strip()
            current_key = line[3:].strip()
            lines = []
        else:
            lines.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(lines).strip()
    return sections


def _extract_field(text: str, field: str) -> str:
    """Extract value from '- **Field**: value' markdown format."""
    for line in text.splitlines():
        if f"**{field}**:" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return ""


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML front-matter from markdown body.

    Returns (frontmatter_dict, body_text). If no front-matter, returns ({}, text).
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    fm: dict[str, Any] = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            # Parse simple lists: [a, b, c]
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                fm[key] = [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
            elif val in ("true", "false"):
                fm[key] = val == "true"
            elif val.lstrip("-").isdigit():
                fm[key] = int(val)
            elif val == "~" or val == "":
                fm[key] = None
            else:
                fm[key] = val
    return fm, body


def _parse_one_session_note(path: Path) -> dict[str, Any] | None:
    """Parse a single .claude/sessions/*.md file into a structured dict.

    Prefers YAML front-matter for machine-readable fields; falls back to
    markdown section parsing for notes written before front-matter was added.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = _parse_frontmatter(text)
    sections = _split_sections(body)

    position = sections.get("Position", "")
    meta = sections.get("Metadata", "")

    # Prefer front-matter values; fall back to parsed markdown
    work = fm.get("work") or _extract_field(position, "Work")
    if not work:
        return None

    return {
        "session_id": path.stem,
        # Front-matter fields (machine-readable, time-series trackable)
        "date": fm.get("date") or path.stem[:10],
        "duration_min": fm.get("duration_min"),
        "project": fm.get("project"),
        "status": fm.get("status") or _extract_field(position, "Status"),
        "tests_pass": fm.get("tests_pass"),
        "files_touched_count": fm.get("files_touched"),
        "compacted_fm": fm.get("compacted"),
        "skills_invoked": fm.get("skills_invoked") or [],
        "skill_candidates_count": fm.get("skill_candidates") or 0,
        "friction_count": fm.get("friction_count") or 0,
        # Markdown section fields (qualitative context)
        "work": work,
        "branch": fm.get("branch") or _extract_field(position, "Branch"),
        "tests": _extract_field(position, "Tests"),
        "key_tools": _extract_field(meta, "Key tools"),
        "files_touched": _extract_field(meta, "Files touched"),
        "token_hotspots": _extract_field(meta, "Token hotspots"),
        "compacted": _extract_field(meta, "Compacted"),
        "gotchas": sections.get("Gotchas", "").strip(),
        "friction_signals": sections.get("Friction signals", "").strip(),
        "attribution_notes": sections.get("Attribution notes", "").strip(),
        "skill_candidates": sections.get("Skill candidates", "").strip(),
        "session_insights": sections.get("Session insights", "").strip(),
        "open_questions": sections.get("Open questions", "").strip(),
    }


def parse_session_notes(sessions_dir: Path, max_notes: int = 20) -> list[dict[str, Any]]:
    """Parse up to max_notes recent session note files from sessions_dir."""
    if not sessions_dir.exists():
        return []
    notes: list[dict[str, Any]] = []
    for path in sorted(sessions_dir.glob("*.md"), reverse=True)[:max_notes]:
        note = _parse_one_session_note(path)
        if note:
            notes.append(note)
    return notes


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are analyzing a developer's Claude Code usage data across two evaluation dimensions:

**Context Engineering (CE)**: Are the right augmentation tools being used efficiently?
  - bash_antipatterns: Bash used where Read/Grep/Glob exists (wastes context, slower)
  - skill_invocations: Which /skills are being triggered vs. ignored
  - hook_blocks: Hooks firing correctly (high = good discipline; zero = hooks may be misconfigured)
  - read_edit_ratio: Should be >1 — understand before changing; <1 means editing blind
  - long_sessions_without_todo: Long sessions with no planning structure
  - cache_read_tokens: Prompt cache hits (higher = better context reuse)

**Prompt Engineering (PE)**: Are responses appropriately sized and well-directed?
  - output_tokens_per_msg p75/p90: High values indicate verbose responses that could be trimmed
  - user_interruptions: Frequent interruptions mean intent wasn't clear upfront
  - tool_errors (file_not_found, edit_failed): Prompts producing wrong file paths

**Token Economics (TE)**: Where is spend actually going? (all % are cost-weighted:
input=1x, cache write=1.25x, cache read=0.1x, output=5x the input price)
  - context_usage_pct / pct_usage_over_150k_context: Share of spend at large request
    context — high >150k share means sessions run too long before /compact or /clear
  - cache.hit_rate_pct + cache.savings_vs_uncached_pct: Prompt-cache efficiency
  - subagents.share_of_usage_pct + pct_usage_in_heavy_sessions: Subagent cost; each
    subagent re-sends its own context — flag if heavy sessions dominate spend
  - parallelism_usage_pct: Spend while 2-3 or 4+ sessions ran concurrently
  - skill_usage_pct: Which /skills consume the most budget
  - compacts: How often sessions compact (0 with high >150k share = compact too late)

Generate a rich, insightful HTML report. Return ONLY valid HTML starting with <!DOCTYPE html>.

The report must include these sections with these exact id attributes:
- #section-work     : What You Work On (project areas with session counts)
- #section-usage    : How You Use Claude Code (narrative + key CE/PE insight)
- #section-wins     : Impressive Things You Did (3 big wins)
- #section-economics: Token Economics (context-size spend distribution, cache savings, subagent share, parallelism)
- #section-ce       : Context Engineering Health (bash antipatterns, skill usage, hook discipline, read/edit ratio)
- #section-pe       : Prompt Engineering Health (verbosity, interruptions, path errors, cache efficiency)
- #section-features : Existing CC Features to Try (3 features with copyable prompts)
- #section-patterns : New Ways to Use Claude Code (3 usage patterns)
- #section-horizon  : On the Horizon (2-3 ambitious future workflows)

Style requirements (inline CSS, no external deps except Google Fonts):
- Clean, modern design using Inter font
- Stat cards at the top: session count, CE health score, PE health score, cache hit rate
- CE health score: 0-100 based on bash_antipatterns_per_session (<0.5=good), read_edit_ratio (>1=good), skill invocations present, hook_blocks present
- PE health score: 0-100 based on output_tokens_per_msg p75 (<800=good), interruptions_per_session (<2=good), error rate
- Bar charts built from divs (no canvas/svg needed)
- Color-coded sections (green for wins, orange for CE, blue for PE, purple for horizon)
- "At a Glance" summary box at top with 4 bullets linking to sections
- A fun/memorable quote at the bottom from the sessions
- All charts use relative widths (100% = max value)
- Copyable code blocks with copy buttons using clipboard API

Make the analysis specific — use actual numbers, first prompts, and patterns. No generic advice.
"""


def _key_from_env_file() -> str:
    """Fallback key lookup for shells without ANTHROPIC_API_KEY exported."""
    for env_path in (Path.home() / ".claude" / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    return ""


def call_claude(api_key: str, prompt: str, model: str = "claude-sonnet-4-6") -> str:
    """Call the Anthropic API to generate an HTML report."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system="You are an expert data analyst generating HTML reports.",
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text if message.content else ""


def build_prompt(
    sessions: list[dict[str, Any]],
    agg: dict[str, Any],
    session_notes: list[dict[str, Any]] | None = None,
) -> str:
    """Build the prompt for the HTML report generation.

    sessions / agg come from JSONL parsing (local mode).
    session_notes come from .claude/sessions/*.md (cord mode or enrichment).
    Either or both may be present.
    """
    parts: list[str] = [
        "Analyze this Claude Code usage data and generate the HTML report described in the system prompt.\n"
    ]

    if agg:
        parts.append(f"## Aggregate Statistics\n{json.dumps(agg, indent=2)}\n")

    if sessions:
        sample_prompts = [s["first_prompt"] for s in sessions if s["first_prompt"]][:30]
        session_summaries: list[dict[str, Any]] = []
        for session in sessions:
            top_tools = sorted(session["tool_counts"].items(), key=lambda x: -x[1])[:3]
            session_summaries.append(
                {
                    "id": session["session_id"][:8],
                    "date": session["start_time"][:10],
                    "duration_min": session["duration_minutes"],
                    "user_msgs": session["user_message_count"],
                    "first_prompt": session["first_prompt"][:120],
                    "top_tools": dict(top_tools),
                    "langs": list(session["languages"].keys()),
                    "errors": session["tool_errors"],
                    "interruptions": session["user_interruptions"],
                    "files": session["files_modified"],
                    # CE signals
                    "bash_antipatterns": session.get("bash_antipatterns", 0),
                    "skill_invocations": session.get("skill_invocations", []),
                    "read_edit_ratio": session.get("read_edit_ratio"),
                    "hook_blocks": session.get("hook_blocks", 0),
                    "has_todo_write": session.get("has_todo_write", False),
                    # PE signals
                    "output_tokens_per_msg": session.get("output_tokens_per_msg", 0),
                    "cache_read_tokens": session.get("cache_read_tokens", 0),
                    # TE signals
                    "cost_units": session.get("cost_units", 0),
                    "max_context": session.get("max_context", 0),
                    "compact_count": session.get("compact_count", 0),
                }
            )
        parts.append(
            f"## Session Summaries (JSONL — {len(session_summaries)} sessions)\n"
            f"{json.dumps(session_summaries, indent=2)}\n"
        )
        parts.append(f"## Sample First Prompts\n{json.dumps(sample_prompts, indent=2)}\n")

    if session_notes:
        note_summaries = [
            {
                "id": n["session_id"],
                "work": n["work"],
                "status": n["status"],
                "branch": n["branch"],
                "tests": n["tests"],
                "key_tools": n["key_tools"],
                "files_touched": n["files_touched"],
                "token_hotspots": n["token_hotspots"],
                "gotchas": n["gotchas"][:300] if n["gotchas"] else "",
                "friction_signals": n["friction_signals"][:300] if n["friction_signals"] else "",
                "attribution_notes": n["attribution_notes"][:400] if n["attribution_notes"] else "",
                "skill_candidates": n["skill_candidates"][:300] if n["skill_candidates"] else "",
                "session_insights": n["session_insights"][:300] if n["session_insights"] else "",
            }
            for n in session_notes
        ]
        source_label = "primary source" if not sessions else "qualitative enrichment"
        parts.append(
            f"## Session Notes ({source_label} — {len(note_summaries)} notes)\n"
            f"{json.dumps(note_summaries, indent=2)}\n"
        )

    parts.append(
        "Generate the complete HTML report now. Remember: return ONLY the HTML, starting with <!DOCTYPE html>."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Hook telemetry
# ---------------------------------------------------------------------------


def parse_hook_log(
    log_path: Path,
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Parse ~/.claude/.hook-log.jsonl and aggregate per-hook stats.

    Returns {hook_name: {blocks: int, advisories: int, repos: list[str]}}.
    Filters by date range when start/end are provided.
    """
    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"blocks": 0, "advisories": 0, "repos": set()}
    )
    if not log_path.exists():
        return {}
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_raw = event.get("ts", "")
        if ts_raw:
            try:
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                if start and ts < start:
                    continue
                if end and ts > end:
                    continue
            except ValueError:
                pass
        hook = event.get("hook", "unknown")
        if event.get("exit_code") == 2:
            stats[hook]["blocks"] += 1
        else:
            stats[hook]["advisories"] += 1
        stats[hook]["repos"].add(event.get("repo", "unknown"))
    # Convert sets to sorted lists for JSON serialisation
    return {k: {**v, "repos": sorted(v["repos"])} for k, v in stats.items()}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse args, extract session stats, optionally generate HTML report.

    Data source routing:
    - JSONL only (local):  quantitative stats from ~/.claude/projects/
    - Notes only (cord):   qualitative data from .claude/sessions/*.md
    - Both (local+notes):  JSONL stats enriched with session note context
    """
    parser = argparse.ArgumentParser(description="Generate Claude Code Insights report")
    parser.add_argument("--key", help="Anthropic API key (or set ANTHROPIC_API_KEY)")
    parser.add_argument("--output", default=".claude/docs/insights/report.html")
    parser.add_argument("--projects-dir", default="~/.claude/projects")
    parser.add_argument(
        "--sessions-dir",
        default="~/.claude/sessions",
        help="Session notes dir (used on cord or to enrich JSONL report)",
    )
    parser.add_argument("--model", default=None, help="Model ID (default: from settings)")
    parser.add_argument("--dry-run", action="store_true", help="Extract stats only, skip API call")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY", "") or _key_from_env_file()
    if not api_key and not args.dry_run:
        log.error(
            "parser.no_api_key",
            msg="Set ANTHROPIC_API_KEY, pass --key, or put it in ~/.claude/.env; "
            "use --dry-run for keyless mechanical stats",
        )
        sys.exit(1)

    projects_dir = Path(args.projects_dir).expanduser()
    sessions_dir = Path(args.sessions_dir).expanduser()
    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- JSONL source ---
    log.info("parser.scanning", path=str(projects_dir))
    sessions = iter_sessions(projects_dir)
    subagent_sessions = iter_subagent_sessions(projects_dir)
    log.info("parser.found_sessions", count=len(sessions), subagents=len(subagent_sessions))

    # --- Session notes source ---
    session_notes = parse_session_notes(sessions_dir)
    log.info("parser.found_session_notes", count=len(session_notes))

    if not sessions and not session_notes:
        log.error("parser.no_data", msg="No JSONL sessions or session notes found")
        sys.exit(1)

    agg: dict[str, Any] = {}
    if sessions:
        agg = aggregate(sessions, subagent_sessions)
        log.info(
            "parser.aggregated",
            date_range=agg.get("date_range", ""),
            messages=agg.get("total_user_messages", 0),
            mode="jsonl+notes" if session_notes else "jsonl",
        )
    else:
        log.info(
            "parser.cord_mode",
            notes=len(session_notes),
            msg="No JSONL found — using session notes as primary source",
        )

    # --- Hook telemetry ---
    hook_log_path = Path.home() / ".claude" / ".hook-log.jsonl"
    hook_telemetry = parse_hook_log(hook_log_path)
    if hook_telemetry:
        log.info("parser.hook_telemetry_loaded", hooks=len(hook_telemetry))

    if args.dry_run:
        out: dict[str, Any] = {}
        if agg:
            out["aggregate"] = agg
        if session_notes:
            out["session_notes_count"] = len(session_notes)
            out["session_note_ids"] = [n["session_id"] for n in session_notes]
        out["hook_telemetry"] = hook_telemetry
        sys.stdout.write(json.dumps(out, indent=2))
        sys.stdout.write("\n")
        return

    model = args.model or "claude-sonnet-4-6"
    log.info("parser.calling_api", model=model)
    prompt = build_prompt(sessions, agg, session_notes=session_notes or None)

    try:
        html = call_claude(api_key, prompt, model=model)
    except Exception as exc:
        log.error("parser.api_error", error=str(exc))
        sys.exit(1)

    # Ensure it starts with <!DOCTYPE
    if "<!DOCTYPE" not in html[:100]:
        match = re.search(r"<!DOCTYPE.*", html, re.DOTALL | re.IGNORECASE)
        if match:
            html = match.group(0)
        else:
            log.warning("parser.html_not_detected", msg="Response doesn't look like HTML")

    output_path.write_text(html)
    log.info("parser.report_written", path=str(output_path))


if __name__ == "__main__":
    main()
