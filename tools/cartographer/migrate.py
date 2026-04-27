"""Migrate JSONL sessions to .claude/sessions/*.md skeleton notes.

Also provides a comparison view between JSONL-derived data and hand-written
session notes for the same date, to validate note coverage.

Usage:
    uv run cartographer --migrate       # create skeleton notes from JSONL
    uv run cartographer --compare       # diff JSONL vs session notes by date
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from tools.cartographer.enrich import _compute_cost, _get_pricing

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _checkbox(items: list[str]) -> str:
    return (
        "\n".join(f"- [ ] {item}" for item in items) if items else "- [ ] None detected"
    )


def _friction_signals(session: dict[str, Any]) -> str:
    """Build a friction signals checklist from JSONL session stats."""
    signals: list[str] = []
    errors = session.get("tool_errors", {})
    tool_counts = session.get("tool_counts", {})
    total_tools = sum(tool_counts.values()) or 1
    bash_share = tool_counts.get("Bash", 0) / total_tools

    if errors.get("edit_failed", 0) + errors.get("file_not_found", 0) > 2:
        signals.append(f"Repeated tool failures ({errors})")
    if bash_share > 0.6:
        signals.append(f"High Bash usage ({bash_share:.0%} of tool calls)")
    if session.get("user_interruptions", 0) > 3:
        signals.append(f"Frequent interruptions ({session['user_interruptions']})")
    if not signals:
        signals.append("None detected")
    return "\n".join(f"- [ ] {s}" for s in signals)


def _top_tools(session: dict[str, Any], n: int = 5) -> str:
    counts = session.get("tool_counts", {})
    top = sorted(counts.items(), key=lambda x: -x[1])[:n]
    return ", ".join(f"{k}({v})" for k, v in top)


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------


def migrate_jsonl_to_notes(
    sessions: list[dict[str, Any]],
    sessions_dir: Path,
    facets: dict[str, dict[str, Any]] | None = None,
) -> list[Path]:
    """Generate skeleton session notes from JSONL sessions.

    Skips dates already covered by an existing note.
    Quantitative fields are filled from JSONL; when facets are provided the
    session_id is used to enrich qualitative fields (goal, outcome, summary).
    """
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Index existing notes by date prefix so we don't overwrite human-written ones
    existing_dates: set[str] = {p.stem[:10] for p in sessions_dir.glob("*.md")}

    created: list[Path] = []
    for session in sorted(sessions, key=lambda s: s["start_time"]):
        date = session["start_time"][:10]
        if date in existing_dates:
            log.info("migrate.skip", date=date, reason="note already exists")
            continue

        # Derive a timestamp-based filename from the session start time
        try:
            ts = datetime.fromisoformat(session["start_time"])
            stem = ts.strftime("%Y-%m-%dT%H%M")
        except ValueError:
            stem = f"{date}T0000"

        facet = (facets or {}).get(session.get("session_id", ""))
        note_path = sessions_dir / f"{stem}.md"
        note_path.write_text(
            _render_skeleton(session, stem, facet=facet),
            encoding="utf-8",
        )
        existing_dates.add(date)
        created.append(note_path)
        log.info("migrate.created", path=str(note_path), facet_enriched=facet is not None)

    return created


def _render_skeleton(
    session: dict[str, Any], stem: str, facet: dict[str, Any] | None = None
) -> str:
    first_prompt = session.get("first_prompt", "").strip()
    langs = ", ".join(session.get("languages", {}).keys()) or "unknown"
    date = stem[:10]
    bash_ap = session.get("bash_antipatterns", 0)
    skills = session.get("skill_invocations", [])

    # Prefer facet-derived qualitative fields when available
    if facet:
        work_field = facet.get("underlying_goal") or first_prompt[:200] or "[fill in]"
        outcome = facet.get("outcome", "complete").replace("_", " ")
        brief = facet.get("brief_summary", "")
        gotchas = facet.get("friction_detail") or "[No friction recorded]"
        goal_cats = ", ".join(facet.get("goal_categories", {}).keys())
        insights = f"**Outcome**: {outcome} | **Goal**: {goal_cats}\n{brief}"
        friction = _friction_signals(session)
        source_note = "<!-- Enriched from facets + JSONL. -->"
    else:
        work_field = first_prompt[:200] if first_prompt else "[migrated from JSONL — fill in]"
        outcome = "complete"
        gotchas = "[No qualitative data available — migrated from JSONL]"
        insights = f"[Auto-generated: {session.get('user_message_count')} msgs / {session.get('duration_minutes')}min / {session.get('files_modified')} files / interruptions={session.get('user_interruptions')} / bash_antipatterns={bash_ap} / read_edit_ratio={session.get('read_edit_ratio')}]"
        friction = _friction_signals(session)
        source_note = "<!-- Migrated from JSONL. Quantitative fields auto-filled; qualitative fields need manual completion. -->"

    inp = session.get("input_tokens", 0)
    out = session.get("output_tokens", 0)
    cw = session.get("cache_write_tokens", 0)
    cr = session.get("cache_read_tokens", 0)
    model = session.get("primary_model", "claude-sonnet-4-6")
    est_cost = round(_compute_cost(inp, out, cw, cr, model), 6)

    return f"""\
---
date: {date}
time: {stem[11:] if len(stem) > 10 else "0000"}
session_id: {session.get("session_id", "~")}
duration_min: {int(session.get("duration_minutes", 0))}
project: ~
branch: ~
status: {outcome}
tests_pass: ~
files_touched: {session.get("files_modified", 0)}
compacted: false
skills_invoked: [{", ".join(skills)}]
skill_candidates: 0
friction_count: 0
input_tokens: {inp}
output_tokens: {out}
cache_write_tokens: {cw}
cache_read_tokens: {cr}
primary_model: {model}
est_cost_usd: {est_cost}
---

# Session — {stem}

{source_note}

## Position
- **Work**: {work_field}
- **Status**: {outcome}
- **Branch**: [unknown — migrated]
- **Tests**: [unknown — migrated]

## Metadata
- **Compacted**: unknown
- **Key tools**: {_top_tools(session)}
- **Files touched**: {session.get("files_modified", 0)} (languages: {langs})
- **Token hotspots**: input={session.get("input_tokens", 0):,} output={session.get("output_tokens", 0):,} bash_antipatterns={bash_ap}

## Gotchas
{gotchas}

## Friction signals
{friction}

## Attribution notes
- **Primary cause:** [unknown — migrated]
- **Solved by:** [unknown]
- **Why it worked:** [unknown]
- **Evidence:** duration={session.get("duration_minutes")}min, {session.get("user_message_count")} user msgs, errors={session.get("tool_errors")}
- **Could hooks have caught it?** unknown

## Open questions

## Skill candidates

## Session insights
{insights}

## Next session prompt
[Fill in manually]
"""


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def compare_sources(
    sessions: list[dict[str, Any]],
    notes: list[dict[str, Any]],
) -> str:
    """Produce a markdown comparison of JSONL-derived data vs session notes.

    Matches by date. Shows what each source captured and what's missing,
    so you can validate whether session notes cover the important signals.
    """
    # Index by date
    jsonl_by_date: dict[str, dict[str, Any]] = {
        s["start_time"][:10]: s for s in sessions
    }
    notes_by_date: dict[str, dict[str, Any]] = {n["session_id"][:10]: n for n in notes}

    all_dates = sorted(set(jsonl_by_date) | set(notes_by_date))

    lines: list[str] = [
        "# Source Comparison — JSONL vs Session Notes\n",
        f"Generated: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
        f"JSONL sessions: {len(sessions)} | Notes: {len(notes)} | Matched dates: {len(set(jsonl_by_date) & set(notes_by_date))}\n",
        "---\n",
    ]

    for date in all_dates:
        j = jsonl_by_date.get(date)
        n = notes_by_date.get(date)
        lines.append(f"## {date}\n")

        if j and n:
            lines.append("**Both sources present**\n")
            lines.append(_comparison_table(j, n))
        elif j and not n:
            lines.append("**JSONL only** — no session note written for this date\n")
            lines.append(_jsonl_summary(j))
        else:
            lines.append("**Session note only** — no JSONL on this machine\n")
            lines.append(_note_summary(n))  # type: ignore[arg-type]

        lines.append("")

    return "\n".join(lines)


def _comparison_table(j: dict[str, Any], n: dict[str, Any]) -> str:
    rows = [
        ("Field", "JSONL", "Session note", "Gap?"),
        ("---", "---", "---", "---"),
        (
            "Work / first prompt",
            (j.get("first_prompt") or "")[:80],
            (n.get("work") or "")[:80],
            "",
        ),
        (
            "Duration",
            f"{j.get('duration_minutes')}min",
            "—",
            "notes don't record duration",
        ),
        (
            "Tool counts",
            _top_tools(j, 3),
            n.get("key_tools", "—")[:60],
            "✓ if key tools listed" if n.get("key_tools") else "⚠ key tools missing",
        ),
        (
            "Files touched",
            str(j.get("files_modified")),
            n.get("files_touched", "—"),
            "",
        ),
        (
            "Errors",
            json.dumps(j.get("tool_errors", {})),
            "—",
            "captured in friction signals instead",
        ),
        ("Friction signals", "—", "✓" if n.get("friction_signals") else "⚠ empty", ""),
        (
            "Gotchas",
            "—",
            "✓" if n.get("gotchas") else "⚠ empty",
            "JSONL can't capture this",
        ),
        (
            "Attribution",
            "—",
            "✓" if n.get("attribution_notes") else "⚠ empty",
            "JSONL can't capture this",
        ),
        ("Skill candidates", "—", "✓" if n.get("skill_candidates") else "(none)", ""),
        (
            "Tokens",
            f"in={j.get('input_tokens', 0):,} out={j.get('output_tokens', 0):,}",
            n.get("token_hotspots", "—"),
            "",
        ),
    ]
    return "\n".join(f"| {' | '.join(str(c) for c in row)} |" for row in rows) + "\n"


def _jsonl_summary(j: dict[str, Any]) -> str:
    return (
        f"- Duration: {j.get('duration_minutes')}min\n"
        f"- Tools: {_top_tools(j, 3)}\n"
        f"- Errors: {j.get('tool_errors')}\n"
        f"- First prompt: {(j.get('first_prompt') or '')[:120]}\n"
    )


def _note_summary(n: dict[str, Any]) -> str:
    return (
        f"- Work: {(n.get('work') or '')[:120]}\n"
        f"- Status: {n.get('status')}\n"
        f"- Gotchas: {'yes' if n.get('gotchas') else 'empty'}\n"
        f"- Skill candidates: {'yes' if n.get('skill_candidates') else 'none'}\n"
    )
