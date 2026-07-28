"""Append-only fact table: one immutable row per Claude Code session.

Two adapters feed it — `from_jsonl()` for the July-forward telemetry era and
`from_notes()` for the Apr-Jun session-note archive — so trend charts are
recomputed from stored history rather than re-derived from an ever-shrinking
JSONL scan (local retention is ~5 days).

Costs are recorded as `cost_units` (input-price-relative, per `parser._usage_cost`),
never USD: the weights are model-blind, so a `_usd` suffix would be a lie.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

import structlog

from tools.cartographer.parser import (
    _COST_CACHE_READ,
    _COST_CACHE_WRITE,
    _COST_INPUT,
    _COST_OUTPUT,
    WORKSPACE_ROOT,
    _extract_field,
    _parse_frontmatter,
    _split_sections,
    iter_sessions,
    iter_subagent_sessions,
    parse_session,
)

log = structlog.get_logger(__name__)

# Cross-era columns: both adapters must fill these, and a row is rejected without
# them. Era-specific columns live in NULLABLE_COLUMNS and stay None outside their era.
FACT_COLUMNS: dict[str, type] = {
    "session_id": str,
    "date": str,
    "project": str,
    "era": str,
    "regime": str,
    "source_path": str,
    "input_tokens": int,
    "output_tokens": int,
    "cache_read_tokens": int,
    "cache_write_tokens": int,
    "cost_units": float,
    "compacted": bool,
    "is_meta": bool,
}

NULLABLE_COLUMNS: dict[str, type] = {
    "max_context": int,
    "primary_model": str,
    "duration_min": float,
    "files_modified": int,
    "skill_costs": str,  # JSON object
    "models": str,  # JSON object
    "tool_counts": str,  # JSON object
    # Friction (2026-07-20). Parsed since the JSONL era but never stored, so a
    # re-parse backfills these to 2026-07-15 -- no new regime, the measurement
    # apparatus is unchanged and only the stored projection widened.
    "tool_errors": str,  # JSON object: error-kind -> count
    "tool_error_count": int,  # total is_error tool results
    "user_interruptions": int,
    "hook_blocks": int,
    # Subagent attribution (2026-07-20). Subagent transcripts were always parsed
    # (parser.iter_subagent_sessions) but never stored, so a re-parse backfills
    # this -- no new regime, same apparatus, only the stored projection widened.
    # JSON object: {"by_agent": {name -> {cost, output_tokens, n}},
    #               "by_model": {model -> {cost, output_tokens, n}}}.
    # `by_agent` keys are subagent-type names, plus UNATTRIBUTED_AGENT for
    # transcripts predating SUBAGENT_ATTRIBUTION_CLI. NULL on parent rows.
    "subagent_costs": str,
    # Session shape (2026-07-20). Human turns per session -- the denominator for
    # "am I running one long session or ten cold starts". Backfills to the July
    # boundary from retained transcripts; same apparatus, no new regime.
    "human_turns": int,
    # Repo attribution (2026-07-20). JSON {repo: record_count} from every `cwd` in
    # the transcript, not just the launch dir -- see parser._session_repos. The
    # `project` column holds the launch dir, which is the bare workspace root for
    # 86% of July sessions and names no repo; this column resolves a repo for 87%
    # of transcripts. Backfills from retained JSONL, same apparatus, no new regime.
    # {} means the session never left the root (genuinely repo-less, not missing).
    "session_repos": str,
    # Usage observability (2026-07-24). Three new signals extracted from parent
    # sessions: friction labels (user-reported), session intent (heuristic),
    # and agent spawns (from Agent tool_use blocks). Backfills to July boundary.
    "friction_label_count": int,
    "session_intent": str,  # "scoping" | "execution" | "brief-execution" | "meta" | "unknown"
    "agent_spawns": str,  # JSON list of {type, description, model}
}

# `attributionAgent` (the subagent-type name) is emitted only by CLI 2.1.201+.
# Transcripts from older builds carry no name, so their spend is real but
# unattributable -- bucketed under UNATTRIBUTED_AGENT rather than dropped, so the
# panel's per-agent shares never silently understate total subagent cost.
SUBAGENT_ATTRIBUTION_CLI = "2.1.201"
UNATTRIBUTED_AGENT = "unattributed"

ALL_COLUMNS = {**FACT_COLUMNS, **NULLABLE_COLUMNS}

ERA_NOTE = "note"
ERA_JSONL = "jsonl"

# Instrumentation regimes (Q0): the setup in force is the independent variable,
# not noise to normalise away. Hand-authored — Ramsey owns this table, code only
# joins on it. Dates are inclusive start, exclusive end; None = open-ended.
#
# The 2026-04-22 boundary is empirical, not a guess (verified 2026-07-19): daily
# compaction is exactly 0% every day through 04-21 and exactly 100% every day
# from 04-26, with a gap between. That is two logging mechanisms, not a change in
# how Ramsey worked —
#   migrated-jsonl: 45 of 56 rows are `claude-*` notes migrated from JSONL, which
#                   never recorded compaction at all -> structural 0%.
#   note-hook:      all 238 rows are hook-written notes, and the hook only fired
#                   ON compaction -> structural 100%.
# Merging them under one regime would have produced a 0->100% "trend" that is
# purely an artifact of the logger changing.
REGIMES: list[tuple[str, str | None, str]] = [
    ("2026-04-10", "2026-04-22", "migrated-jsonl"),
    ("2026-04-22", "2026-07-15", "note-hook"),
    ("2026-07-15", "2026-07-17", "telemetry-v1"),
    ("2026-07-17", None, "session-hygiene-v1"),
]

REGIME_UNCLASSIFIED = "unclassified"


def regime_for(date: str) -> str:
    """Look up the instrumentation regime covering `date` (YYYY-MM-DD).

    Unmapped dates return "unclassified" and are still rendered — never dropped.
    """
    for start, end, name in REGIMES:
        if date >= start and (end is None or date < end):
            return name
    return REGIME_UNCLASSIFIED


# ---------------------------------------------------------------------------
# Meta-session classification (Q4)
# ---------------------------------------------------------------------------

# Config/tooling targets: a file under one of these is meta-work, not product work.
_META_FILE_PATTERN = re.compile(r"(/\.claude/|/\.vscode/|/dotfiles/|/\.github/)", re.IGNORECASE)


_EDIT_TOOL_NAMES = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def _classify_intent(session: dict[str, Any]) -> str:
    """Heuristic session intent: what the session was *doing*.

    Returns "execution", "brief-execution", "scoping", or "unknown". "meta"
    is handled by _classify_meta and takes precedence in from_jsonl.

    NOTE: session["files_modified"] is always 0 due to a known parser gap
    (parse_session reads record["fileId"] from file-history-snapshot records
    but current transcripts nest paths under snapshot.trackedFileBackups).
    We derive the edit count directly from tool_counts instead, matching what
    _edit_counts() does for the factstore row.
    """
    skills = session.get("skill_invocations") or []
    human_turns = session.get("user_message_count", 0) or 0
    read_edit_ratio = session.get("read_edit_ratio")

    # Derive actual edit count from tool_counts — session["files_modified"] is
    # always 0 for JSONL-era sessions (parser reads a stale field).
    tool_counts: dict[str, int] = session.get("tool_counts") or {}
    edit_count = sum(tool_counts.get(name, 0) for name in _EDIT_TOOL_NAMES)

    # Execution: any skill invoked, or substantive edits with enough turns for
    # back-and-forth direction.
    if skills or (edit_count >= 1 and human_turns >= 3):
        return "execution"

    # Brief-execution: low turn count but real file work happened. These are
    # focused delegate sessions (e.g. "fix this one thing") — execution-shaped
    # output, not a conversation.
    if edit_count >= 2 and human_turns < 3:
        return "brief-execution"

    # Scoping: reading/discussing with minimal writes — planning or review.
    if (
        human_turns >= 2
        and not skills
        and edit_count <= 1
        and (read_edit_ratio is None or read_edit_ratio > 3)
    ):
        return "scoping"

    return "unknown"


def _classify_meta(row: dict[str, Any]) -> bool:
    """Research Disconfirming section 1: meta-sessions depress median size
    independently of any hygiene rule. Separate series, never pooled.

    Classified on **what the session edited**, not where it was launched: `cwd` is
    the launch directory, and Ramsey drives many repos from `~/workspace`, so a
    path-based rule labels genuine product work (executing an `ai-project-template`
    plan from the workspace root) as meta. A 15-session hand-check put that version
    at ~8/15 against the plan's 13/15 gate.

    A session is meta when it changed nothing, or when every file it changed was
    config/tooling (`.claude/`, `.vscode/`, dotfiles).
    """
    edited: list[str] = row.get("edited_paths") or []
    if not edited:
        # No edits at all — nothing product-shaped happened.
        return row.get("files_modified", 0) == 0
    return all(_META_FILE_PATTERN.search(p) for p in edited)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class SchemaError(ValueError):
    """A fact row is missing a cross-era column or has a wrong-typed value."""


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return a normalised row, or raise SchemaError.

    Cross-era columns must be present and non-null; nullable columns default to
    None. Unknown keys are dropped so adapters can pass through richer dicts.
    """
    out: dict[str, Any] = {}
    for col, typ in FACT_COLUMNS.items():
        if col not in row or row[col] is None:
            raise SchemaError(f"missing cross-era column: {col}")
        value = row[col]
        if typ is bool:
            value = bool(value)
        elif typ is float:
            value = float(value)
        elif typ is int:
            value = int(value)
        elif not isinstance(value, str):
            value = str(value)
        out[col] = value
    for col, typ in NULLABLE_COLUMNS.items():
        value = row.get(col)
        if value is None:
            out[col] = None
        elif typ is float:
            out[col] = float(value)
        elif typ is int:
            out[col] = int(value)
        else:
            out[col] = value if isinstance(value, str) else json.dumps(value)
    return out


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

_SQL_TYPES = {str: "TEXT", int: "INTEGER", float: "REAL", bool: "INTEGER"}


def _connect(store: Path) -> sqlite3.Connection:
    store.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(store)
    cols = ", ".join(f"{name} {_SQL_TYPES[typ]}" for name, typ in ALL_COLUMNS.items())
    conn.execute(f"CREATE TABLE IF NOT EXISTS sessions ({cols}, PRIMARY KEY (session_id))")
    _add_missing_columns(conn)
    return conn


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    """Widen an existing table when ALL_COLUMNS grows.

    CREATE TABLE IF NOT EXISTS is a no-op on an existing store, so a new column
    would silently never appear. Added columns are NULL for every prior row --
    re-running the adapter over retained JSONL is what fills them.
    """
    existing = {row[1] for row in conn.execute("PRAGMA table_info(sessions)")}
    for name, typ in ALL_COLUMNS.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE sessions ADD COLUMN {name} {_SQL_TYPES[typ]}")
            log.info("factstore.column_added", column=name)
    conn.commit()


def upsert(rows: list[dict[str, Any]], store: Path) -> int:
    """Idempotent on session_id. Returns rows written.

    Re-running an adapter over the same corpus replaces rows in place rather than
    appending duplicates, so `--facts` is safe to schedule.
    """
    validated = [validate_row(r) for r in rows]
    if not validated:
        return 0
    names = list(ALL_COLUMNS)
    placeholders = ", ".join("?" for _ in names)
    sql = f"INSERT OR REPLACE INTO sessions ({', '.join(names)}) VALUES ({placeholders})"
    conn = _connect(store)
    try:
        conn.executemany(sql, [tuple(r[n] for n in names) for r in validated])
        conn.commit()
    finally:
        conn.close()
    log.info("factstore.upsert", rows=len(validated), store=str(store))
    return len(validated)


def read_all(store: Path) -> list[dict[str, Any]]:
    """Read every fact row back as a list of dicts."""
    if not store.exists():
        return []
    conn = _connect(store)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM sessions ORDER BY date, session_id").fetchall()
    finally:
        conn.close()
    out: list[dict[str, Any]] = []
    for row in rows:
        rec = dict(row)
        for col in ("compacted", "is_meta"):
            rec[col] = bool(rec[col])
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Adapter: JSONL (July-forward)
# ---------------------------------------------------------------------------


def _edit_counts(session: dict[str, Any]) -> int:
    """Files-modified proxy from Edit/Write/MultiEdit tool calls.

    `parse_session`'s own `files_modified` reads `record["fileId"]` on
    file-history-snapshot records, but the current transcript format nests paths
    under `snapshot.trackedFileBackups`, so it returns 0 for every session. The
    parser is out of scope for this plan (consume, don't refactor), so the
    classifier derives the signal here instead of trusting that field.
    """
    counts = session.get("tool_counts", {}) or {}
    return sum(counts.get(name, 0) for name in ("Edit", "Write", "MultiEdit", "NotebookEdit"))


def _to_fact_from_jsonl(session: dict[str, Any], source_path: str) -> dict[str, Any]:
    date = str(session.get("start_time", ""))[:10]
    errors: dict[str, int] = session.get("tool_errors", {}) or {}
    row: dict[str, Any] = {
        "session_id": session["session_id"],
        "date": date,
        "project": session.get("project_path") or "",
        "era": ERA_JSONL,
        "regime": regime_for(date),
        "source_path": source_path,
        "input_tokens": session.get("input_tokens", 0),
        "output_tokens": session.get("output_tokens", 0),
        "cache_read_tokens": session.get("cache_read_tokens", 0),
        "cache_write_tokens": session.get("cache_write_tokens", 0),
        "cost_units": session.get("cost_units", 0.0),
        "compacted": session.get("compact_count", 0) > 0,
        "max_context": session.get("max_context"),
        "primary_model": session.get("primary_model"),
        "duration_min": session.get("duration_minutes"),
        "files_modified": _edit_counts(session),
        "skill_costs": json.dumps(session.get("skill_costs", {})),
        "models": json.dumps(session.get("models", {})),
        "tool_counts": json.dumps(session.get("tool_counts", {})),
        "tool_errors": json.dumps(errors),
        "tool_error_count": sum(errors.values()),
        "user_interruptions": session.get("user_interruptions"),
        "human_turns": session.get("user_message_count"),
        "hook_blocks": errors.get("user_rejected", 0),
        "session_repos": json.dumps(session.get("session_repos", {})),
    }
    row["is_meta"] = _classify_meta({**row, "edited_paths": session.get("edited_paths", [])})
    return row


_EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def _scan_session_files(projects_dir: Path) -> dict[str, dict[str, Any]]:
    """Per session, recover the working directory and the files it actually edited.

    Two gaps in `parse_session` make this necessary, and the plan puts that module
    out of scope (consume, don't refactor):
      - `project_path` reads `records[0]["cwd"]`, but the opening record usually
        omits `cwd`, so it comes back empty for most sessions.
      - `files_modified` counts `record["fileId"]` on file-history-snapshot records,
        but current transcripts nest paths under `snapshot.trackedFileBackups`, so
        it is 0 for every session.
    """
    found: dict[str, dict[str, Any]] = {}
    for jsonl in projects_dir.rglob("*.jsonl"):
        if "/subagents/" in str(jsonl):
            continue
        cwd = ""
        repos: dict[str, int] = {}
        edited: list[str] = []
        for line in jsonl.read_text(errors="replace").splitlines():
            if '"cwd"' not in line and '"tool_use"' not in line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("cwd"):
                if not cwd:
                    cwd = str(record["cwd"])
                repo_prefix = WORKSPACE_ROOT + "/"
                value = str(record["cwd"])
                if value.startswith(repo_prefix):
                    name = value[len(repo_prefix) :].split("/", 1)[0]
                    if name:
                        repos[name] = repos.get(name, 0) + 1
            for block in record.get("message", {}).get("content", []) or []:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") in _EDIT_TOOLS
                ):
                    path = block.get("input", {}).get("file_path", "")
                    if path:
                        edited.append(str(path))
        found[jsonl.stem] = {"cwd": cwd, "repos": repos, "edited_paths": edited}
    return found


def _subagent_costs_by_parent(projects_dir: Path) -> dict[str, dict[str, Any]]:
    """Roll subagent transcripts up onto the parent session that spawned them.

    Subagent spend belongs to the parent's session row: a subagent has no user
    turns of its own, so storing it as a standalone session would inflate session
    counts and halve per-session medians. Each parent gets one nested breakdown,
    by subagent-type name and by model.

    For pre-2.1.201 transcripts lacking ``attribution_agent``, a best-effort
    enrichment matches unattributed children to the parent's ``agent_spawns``
    by spawn order when the counts match exactly.
    """
    children_by_parent: dict[str, list[dict[str, Any]]] = {}
    for sub in iter_subagent_sessions(projects_dir):
        parent = sub.get("parent_session_id")
        if not parent:
            continue
        children_by_parent.setdefault(parent, []).append(sub)

    parent_spawns: dict[str, list[dict[str, str | None]]] = {}
    for parent_id, children in children_by_parent.items():
        has_unattributed = any(not c.get("attribution_agent") for c in children)
        if not has_unattributed:
            continue
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            parent_jsonl = project_dir / f"{parent_id}.jsonl"
            if parent_jsonl.exists():
                parent_session = parse_session(parent_jsonl)
                if parent_session:
                    parent_spawns[parent_id] = parent_session.get("agent_spawns", [])
                break

    for parent_id, children in children_by_parent.items():
        spawns = parent_spawns.get(parent_id, [])
        unattributed = [c for c in children if not c.get("attribution_agent")]
        if spawns and len(unattributed) == len(spawns):
            unattributed.sort(key=lambda c: c.get("start_time", ""))
            for child, spawn in zip(unattributed, spawns, strict=False):
                child["attribution_agent"] = spawn.get("type") or "general-purpose"

    by_parent: dict[str, dict[str, dict[str, Any]]] = {}
    for parent_id, children in children_by_parent.items():
        buckets = by_parent.setdefault(parent_id, {"by_agent": {}, "by_model": {}})
        for sub in children:
            agent = sub.get("attribution_agent") or UNATTRIBUTED_AGENT
            entry = buckets["by_agent"].setdefault(agent, {"cost": 0.0, "output_tokens": 0, "n": 0})
            entry["cost"] += sub.get("cost_units", 0.0)
            entry["output_tokens"] += sub.get("output_tokens", 0)
            entry["n"] += 1

            for model, cost in (sub.get("model_costs") or {}).items():
                slot = buckets["by_model"].setdefault(
                    model, {"cost": 0.0, "output_tokens": 0, "n": 0}
                )
                slot["cost"] += cost
                slot["output_tokens"] += (sub.get("model_output_tokens") or {}).get(model, 0)
                slot["n"] += 1

    for buckets in by_parent.values():
        for group in buckets.values():
            for slot in group.values():
                slot["cost"] = round(slot["cost"], 1)
    return by_parent


def from_jsonl(projects_dir: Path) -> list[dict[str, Any]]:
    """Map parsed JSONL sessions onto fact rows (era="jsonl")."""
    scanned = _scan_session_files(projects_dir)
    sub_costs = _subagent_costs_by_parent(projects_dir)
    rows: list[dict[str, Any]] = []
    for session in iter_sessions(projects_dir):
        extra = scanned.get(session["session_id"], {})
        if not session.get("project_path"):
            session["project_path"] = extra.get("cwd", "")
        if not session.get("session_repos"):
            session["session_repos"] = extra.get("repos", {})
        session["edited_paths"] = extra.get("edited_paths", [])
        row = _to_fact_from_jsonl(session, str(projects_dir))
        costs = sub_costs.get(session["session_id"])
        row["subagent_costs"] = json.dumps(costs) if costs else None
        flc = session.get("friction_label_count", 0)
        row["friction_label_count"] = flc if flc else None
        intent = _classify_intent(session)
        row["session_intent"] = "meta" if row["is_meta"] else intent
        spawns = session.get("agent_spawns")
        row["agent_spawns"] = json.dumps(spawns) if spawns else None
        rows.append(row)
    log.info(
        "factstore.from_jsonl",
        rows=len(rows),
        with_subagents=sum(1 for r in rows if r["subagent_costs"]),
        projects_dir=str(projects_dir),
    )
    return rows


# ---------------------------------------------------------------------------
# Adapter: session notes (Apr-Jun)
# ---------------------------------------------------------------------------

# Hook-written notes carry a prose hotspot line. Two variants exist:
#   full     — input= output= cache_read= cache_write=   (235 notes)
#   degraded — input= output= bash_antipatterns=          (17 notes, no cache data)
# Counts may include comma thousands separators.
_NUM = r"([\d,]+)"
HOTSPOT = re.compile(rf"input={_NUM}\s+output={_NUM}(?:\s+cache_read={_NUM}\s+cache_write={_NUM})?")

# NOTE: `total_tokens` frontmatter is NEVER mapped to max_context — it is not a
# context measurement. In `claude-` migrated notes it does not even equal
# input+output (13 of 45 disagree, verified 2026-07-19), so it is left unread.


def _int(raw: str | None) -> int:
    return int(raw.replace(",", "")) if raw else 0


def _cost_units(inp: int, out: int, cache_read: int, cache_write: int) -> float:
    """Same weighting July uses, so costs are methodologically identical across eras."""
    return round(
        inp * _COST_INPUT
        + cache_write * _COST_CACHE_WRITE
        + cache_read * _COST_CACHE_READ
        + out * _COST_OUTPUT,
        1,
    )


def _fm_int(fm: dict[str, Any], key: str) -> int:
    value = fm.get(key)
    return int(value) if isinstance(value, int) else 0


def _note_to_fact(path: Path) -> dict[str, Any] | None:
    """Parse one session note into a fact row via whichever path it supports.

    Path A — frontmatter-first: `claude-*.md` JSONL-migrated notes carry token
    counts, cost and model in YAML. These are the only pre-July rows with model
    attribution.
    Path B — hotspot-prose: hook-written `YYYY-MM-DDTHHMM.md` notes carry the
    counts in a body line instead.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = _parse_frontmatter(text)
    date = str(fm.get("date") or path.stem[:10])
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        return None

    primary_model = None
    if fm.get("input_tokens") is not None or fm.get("output_tokens") is not None:
        # Path A — frontmatter carries the counts directly.
        inp = _fm_int(fm, "input_tokens")
        out = _fm_int(fm, "output_tokens")
        cache_read = _fm_int(fm, "cache_read_tokens")
        cache_write = _fm_int(fm, "cache_write_tokens")
        model = fm.get("primary_model") or fm.get("model")
        primary_model = str(model) if model else None
    else:
        # Path B — regex the prose hotspot line.
        match = HOTSPOT.search(body)
        if not match:
            return None
        inp = _int(match.group(1))
        out = _int(match.group(2))
        cache_read = _int(match.group(3))
        cache_write = _int(match.group(4))

    # Frontmatter `compacted:` is authoritative. The prose line is a fallback for
    # notes predating that field — and it must read the VALUE, not the label:
    # "- **Compacted**: unknown" is not evidence of a compaction.
    compacted = fm.get("compacted")
    if compacted is None:
        prose = _extract_field(_split_sections(body).get("Metadata", ""), "Compacted")
        compacted = prose.lower().startswith("yes")
    compacted = bool(compacted)
    files_touched = fm.get("files_touched")
    duration = fm.get("duration_min")

    row: dict[str, Any] = {
        "session_id": fm.get("session_id") or path.stem,
        "date": date,
        "project": str(fm.get("project") or ""),
        "era": ERA_NOTE,
        "regime": regime_for(date),
        "source_path": str(path),
        "input_tokens": inp,
        "output_tokens": out,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "cost_units": _cost_units(inp, out, cache_read, cache_write),
        "compacted": compacted,
        # max_context is unknowable for this era and must stay null.
        "max_context": None,
        "primary_model": primary_model,
        "duration_min": float(duration) if isinstance(duration, int | float) else None,
        "files_modified": files_touched if isinstance(files_touched, int) else None,
    }
    row["is_meta"] = _classify_meta(row)
    return row


def from_notes(notes_dir: Path) -> list[dict[str, Any]]:
    """Map session notes onto fact rows (era="note").

    Notes carrying neither an input/output pair nor a hotspot line are skipped, not
    zero-filled. 76 `claude-*` notes have `total_tokens` + `cache_read_tokens` but no
    input/output split; since cost weights output at 5x input, splitting that total
    would fabricate the cost. The skipped count is logged so the gap stays visible.
    """
    rows: list[dict[str, Any]] = []
    skipped = 0
    for path in sorted(notes_dir.glob("*.md")):
        row = _note_to_fact(path)
        if row is None:
            skipped += 1
            continue
        rows.append(row)
    log.info("factstore.from_notes", rows=len(rows), skipped=skipped, notes_dir=str(notes_dir))
    return rows
