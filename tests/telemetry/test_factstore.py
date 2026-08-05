from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer.factstore import (
    ERA_JSONL,
    ERA_NOTE,
    ERROR_CATEGORY_CODE,
    ERROR_CATEGORY_ENV,
    ERROR_CATEGORY_TOOL,
    ERROR_CATEGORY_UNKNOWN,
    REGIME_UNCLASSIFIED,
    SchemaError,
    _classify_intent,
    _classify_meta,
    append_verdicts,
    classify_error_kind,
    from_findings_jsonl,
    from_jsonl,
    from_notes,
    read_all,
    read_findings,
    read_verdicts,
    regime_for,
    upsert,
    upsert_findings,
    validate_row,
)


def _row(session_id: str = "s1", **overrides: object) -> dict[str, Any]:
    row = {
        "session_id": session_id,
        "date": "2026-07-16",
        "project": "/Users/x/repo",
        "era": ERA_JSONL,
        "regime": "telemetry-v1",
        "source_path": "/tmp/x",
        "input_tokens": 100,
        "output_tokens": 200,
        "cache_read_tokens": 300,
        "cache_write_tokens": 40,
        "cost_units": 1234.5,
        "compacted": False,
        "is_meta": False,
    }
    row.update(overrides)
    return row


# --- Step 1: schema + writer ------------------------------------------------


def test_upsert_is_idempotent_on_session_id(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    rows = [_row(f"s{i}") for i in range(10)]

    upsert(rows, store)
    upsert(rows, store)

    assert len(read_all(store)) == 10


def test_upsert_replaces_rather_than_duplicates(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([_row("s1", cost_units=1.0)], store)
    upsert([_row("s1", cost_units=99.0)], store)

    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0]["cost_units"] == 99.0


@pytest.mark.parametrize("column", ["session_id", "date", "era", "regime", "cost_units"])
def test_schema_rejects_null_cross_era_column(column: str) -> None:
    with pytest.raises(SchemaError, match=column):
        validate_row(_row(**{column: None}))


def test_nullable_columns_default_to_none() -> None:
    validated = validate_row(_row())
    assert validated["max_context"] is None
    assert validated["primary_model"] is None


def test_booleans_round_trip(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([_row("s1", compacted=True, is_meta=True)], store)

    stored = read_all(store)[0]
    assert stored["compacted"] is True
    assert stored["is_meta"] is True


# --- regime lookup (Q0) -----------------------------------------------------


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        ("2026-04-10", "migrated-jsonl"),
        ("2026-04-21", "migrated-jsonl"),
        ("2026-04-26", "note-hook"),
        ("2026-06-04", "note-hook"),
        ("2026-07-15", "telemetry-v1"),
        ("2026-07-17", "session-hygiene-v1"),
        ("2026-07-19", "session-hygiene-v1"),
    ],
)
def test_regime_lookup(date: str, expected: str) -> None:
    assert regime_for(date) == expected


def test_april_logging_switch_is_its_own_regime() -> None:
    """The 04-22 boundary is empirical: daily compaction is exactly 0% through
    04-21 (migrated notes never recorded it) and exactly 100% from 04-26 (the hook
    only fired on compaction). One regime spanning both would render that logger
    swap as a 0->100% workflow trend."""
    assert regime_for("2026-04-21") != regime_for("2026-04-26")


def test_unmapped_date_is_unclassified_not_dropped() -> None:
    assert regime_for("2025-01-01") == REGIME_UNCLASSIFIED


# --- Step 2: JSONL adapter --------------------------------------------------


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records))


def _jsonl_session(cwd: str = "/Users/x/repo", compact: bool = False) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = [
        {
            "type": "user",
            "timestamp": "2026-07-16T10:00:00Z",
            "cwd": cwd,
            "message": {"content": "hello"},
        },
        {
            "type": "assistant",
            "timestamp": "2026-07-16T10:01:00Z",
            "message": {
                "model": "claude-opus-4-8",
                "content": [{"type": "text", "text": "ok"}],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_input_tokens": 900,
                    "cache_creation_input_tokens": 10,
                },
            },
        },
    ]
    if compact:
        records.append({"type": "system", "subtype": "compact_boundary"})
    return records


def test_jsonl_adapter_produces_valid_rows(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    _write_jsonl(projects / "abc.jsonl", _jsonl_session())

    rows = from_jsonl(projects)

    assert len(rows) == 1
    row = rows[0]
    assert row["era"] == ERA_JSONL
    assert row["date"] == "2026-07-16"
    assert row["input_tokens"] == 100
    assert row["cache_read_tokens"] == 900
    assert row["primary_model"] == "claude-opus-4-8"
    # Every cross-era column is fillable from JSONL.
    validate_row(row)


def test_jsonl_adapter_sets_compacted_from_compact_count(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    _write_jsonl(projects / "a.jsonl", _jsonl_session(compact=True))
    _write_jsonl(projects / "b.jsonl", _jsonl_session(compact=False))

    by_id = {r["session_id"]: r for r in from_jsonl(projects)}

    assert by_id["a"]["compacted"] is True
    assert by_id["b"]["compacted"] is False


def test_jsonl_adapter_populates_max_context(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    _write_jsonl(projects / "abc.jsonl", _jsonl_session())

    # input + cache_read + cache_write
    assert from_jsonl(projects)[0]["max_context"] == 1010


# --- Step 3: note-prose adapter ---------------------------------------------

_HOOK_NOTE = """---
tags: [context-management, research]
branch: null
compacted: true
date: 2026-05-20
duration_min: 120
files_touched: 3
project: null
status: complete
---

# Session — 2026-05-20T1200

## Metadata

- **Token hotspots**: input=2406 output=217596 cache_read=16641587 cache_write=876804
"""

_HOOK_NOTE_DEGRADED = """---
tags: [context-management]
compacted: false
date: 2026-04-11
files_touched: 0
project: null
---

# Session — 2026-04-11T1218

## Metadata

- **Token hotspots**: input=2,249 output=87,040 bash_antipatterns=41
"""

_MIGRATED_NOTE = """---
tags: [context-management, refactor]
cache_read_tokens: 33656975
date: 2026-04-11
est_cost_usd: 11.855491
input_tokens: 278
output_tokens: 117171
primary_model: claude-opus-4-1
project: -Users-ramsey-wise-Workspace
session_id: 394ba556-c64e-4f80-b60a-80878d32413e
total_tokens: 310269
---

# Claude Code Session — 2026-04-11
"""


def _write_notes(tmp_path: Path, **notes: str) -> Path:
    notes_dir = tmp_path / "sessions"
    notes_dir.mkdir()
    for name, content in notes.items():
        (notes_dir / f"{name}.md").write_text(content)
    return notes_dir


def test_note_adapter_parses_hotspot_prose(tmp_path: Path) -> None:
    notes_dir = _write_notes(tmp_path, **{"2026-05-20T1200": _HOOK_NOTE})

    row = from_notes(notes_dir)[0]

    assert row["era"] == ERA_NOTE
    assert row["input_tokens"] == 2406
    assert row["output_tokens"] == 217596
    assert row["cache_read_tokens"] == 16641587
    assert row["cache_write_tokens"] == 876804
    assert row["compacted"] is True
    validate_row(row)


def test_note_adapter_handles_degraded_hotspot_without_cache_fields(tmp_path: Path) -> None:
    """17 notes carry `bash_antipatterns=` instead of cache fields — parse, don't skip."""
    notes_dir = _write_notes(tmp_path, **{"2026-04-11T1218": _HOOK_NOTE_DEGRADED})

    row = from_notes(notes_dir)[0]

    assert row["input_tokens"] == 2249  # comma separator stripped
    assert row["output_tokens"] == 87040
    assert row["cache_read_tokens"] == 0
    assert row["cache_write_tokens"] == 0


def test_note_adapter_prefers_frontmatter_for_migrated_notes(tmp_path: Path) -> None:
    """Path A: `claude-` notes carry counts + model in YAML, the only pre-July model rows."""
    notes_dir = _write_notes(tmp_path, **{"claude-2026-04-11-refactor-394ba556": _MIGRATED_NOTE})

    row = from_notes(notes_dir)[0]

    assert row["input_tokens"] == 278
    assert row["output_tokens"] == 117171
    assert row["cache_read_tokens"] == 33656975
    assert row["primary_model"] == "claude-opus-4-1"
    assert row["session_id"] == "394ba556-c64e-4f80-b60a-80878d32413e"


def test_note_adapter_never_populates_max_context(tmp_path: Path) -> None:
    """max_context is unknowable pre-July; total_tokens must never be mapped onto it."""
    notes_dir = _write_notes(
        tmp_path,
        **{
            "2026-05-20T1200": _HOOK_NOTE,
            "claude-2026-04-11-refactor-394ba556": _MIGRATED_NOTE,
        },
    )

    assert all(r["max_context"] is None for r in from_notes(notes_dir))


def test_note_adapter_cost_units_match_july_weighting(tmp_path: Path) -> None:
    notes_dir = _write_notes(tmp_path, **{"2026-05-20T1200": _HOOK_NOTE})

    # input*1 + cache_write*1.25 + cache_read*0.1 + output*5
    expected = 2406 * 1.0 + 876804 * 1.25 + 16641587 * 0.1 + 217596 * 5.0
    assert from_notes(notes_dir)[0]["cost_units"] == pytest.approx(expected, rel=1e-6)


def test_note_adapter_skips_notes_without_token_data(tmp_path: Path) -> None:
    notes_dir = _write_notes(tmp_path, **{"puffin-chat-2026-07-16-22-00": "no frontmatter here"})

    assert from_notes(notes_dir) == []


def test_note_adapter_skips_totals_without_input_output_split(tmp_path: Path) -> None:
    """76 `claude-` notes carry total_tokens but no split; inventing one would
    corrupt cost_units, which weights output at 5x input."""
    note = (
        "---\n"
        "date: 2026-04-22\n"
        "cache_read_tokens: 757634\n"
        "total_tokens: 9477\n"
        "project: -Users-x-Workspace\n"
        "---\n\n# Session\n"
    )
    notes_dir = _write_notes(tmp_path, **{"claude-2026-04-22-insights-198e7d2c": note})

    assert from_notes(notes_dir) == []


def test_compacted_unknown_is_not_treated_as_compacted(tmp_path: Path) -> None:
    """`- **Compacted**: unknown` must read as False — matching the label rather
    than the value inflates the compaction rate by 17 notes."""
    note = (
        "---\ndate: 2026-04-11\nproject: null\n---\n\n"
        "## Metadata\n\n"
        "- **Compacted**: unknown\n"
        "- **Token hotspots**: input=100 output=200 cache_read=300 cache_write=40\n"
    )
    notes_dir = _write_notes(tmp_path, **{"2026-04-11T1218": note})

    assert from_notes(notes_dir)[0]["compacted"] is False


def test_compacted_yes_prose_is_honoured(tmp_path: Path) -> None:
    note = (
        "---\ndate: 2026-04-11\nproject: null\n---\n\n"
        "## Metadata\n\n"
        "- **Compacted**: yes (manual)\n"
        "- **Token hotspots**: input=100 output=200 cache_read=300 cache_write=40\n"
    )
    notes_dir = _write_notes(tmp_path, **{"2026-04-11T1218": note})

    assert from_notes(notes_dir)[0]["compacted"] is True


# --- Step 4: meta classifier ------------------------------------------------


def test_config_only_edits_classify_as_meta() -> None:
    row = {
        "project": "/Users/wiseer/workspace",
        "files_modified": 2,
        "edited_paths": [
            "/Users/wiseer/.claude/skills/wake/SKILL.md",
            "/Users/wiseer/workspace/librarian/.claude/settings.json",
        ],
    }
    assert _classify_meta(row) is True


def test_product_edits_are_not_meta() -> None:
    row = {
        "project": "/Users/wiseer/workspace/librarian",
        "files_modified": 2,
        "edited_paths": ["/Users/wiseer/workspace/librarian/tools/cartographer/parser.py"],
    }
    assert _classify_meta(row) is False


def test_product_work_launched_from_workspace_root_is_not_meta() -> None:
    """The regression that failed hand-validation: `cwd` is the launch directory,
    so a template plan executed from ~/workspace must not be labelled meta."""
    row = {
        "project": "/Users/wiseer/workspace",
        "files_modified": 20,
        "edited_paths": [
            "/Users/wiseer/workspace/ai-project-template/template/backend/main.py",
            "/Users/wiseer/workspace/ai-project-template/README.md",
        ],
    }
    assert _classify_meta(row) is False


def test_mixed_edits_are_not_meta() -> None:
    """Any product file touched means the session did product work."""
    row = {
        "project": "/Users/wiseer/workspace",
        "files_modified": 2,
        "edited_paths": [
            "/Users/wiseer/.claude/settings.json",
            "/Users/wiseer/workspace/librarian/tools/cartographer/factstore.py",
        ],
    }
    assert _classify_meta(row) is False


def test_zero_edits_classifies_as_meta() -> None:
    """A session that changed nothing did no product work."""
    row = {"project": "/Users/wiseer/workspace/librarian", "files_modified": 0, "edited_paths": []}
    assert _classify_meta(row) is True


# --- Session intent classification -------------------------------------------


def test_classify_intent_execution_by_skill() -> None:
    """Skill invocation alone → execution, regardless of edit count."""
    session = {
        "skill_invocations": ["workflow-execute"],
        "tool_counts": {"Edit": 0},
        "user_message_count": 10,
    }
    assert _classify_intent(session) == "execution"


def test_classify_intent_execution_by_edits() -> None:
    """Edits from tool_counts (not files_modified) + turns>=3 → execution."""
    session = {
        "skill_invocations": [],
        "tool_counts": {"Edit": 3, "Bash": 5},
        "user_message_count": 5,
    }
    assert _classify_intent(session) == "execution"


def test_classify_intent_brief_execution() -> None:
    """Real file work in 1-2 turns → brief-execution (focused delegate session)."""
    session = {
        "skill_invocations": [],
        "tool_counts": {"Edit": 5, "Write": 1},
        "user_message_count": 1,
    }
    assert _classify_intent(session) == "brief-execution"


def test_classify_intent_scoping() -> None:
    session = {
        "skill_invocations": [],
        "tool_counts": {},
        "user_message_count": 4,
        "read_edit_ratio": 10.0,
    }
    assert _classify_intent(session) == "scoping"


def test_classify_intent_scoping_no_ratio() -> None:
    """read_edit_ratio=None (all reads) is scoping."""
    session = {
        "skill_invocations": [],
        "tool_counts": {},
        "user_message_count": 3,
        "read_edit_ratio": None,
    }
    assert _classify_intent(session) == "scoping"


def test_classify_intent_unknown() -> None:
    """1 turn, 1 edit — too ambiguous for any named category."""
    session = {"skill_invocations": [], "tool_counts": {"Edit": 1}, "user_message_count": 1}
    assert _classify_intent(session) == "unknown"


# --- New column storage -------------------------------------------------------


def test_friction_label_count_stored(tmp_path: Path) -> None:
    from tests.shared.test_cartographer_parser import _assistant, _user, _write_jsonl

    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [
            _user("2026-07-20T10:00:00Z", text="FRICTION: hook blocked edit"),
            _assistant("2026-07-20T10:00:05Z"),
        ],
    )
    rows = from_jsonl(tmp_path)
    assert len(rows) == 1
    assert rows[0]["friction_label_count"] == 1


def test_agent_spawns_stored_as_json(tmp_path: Path) -> None:
    from tests.shared.test_cartographer_parser import (
        _assistant_with_tools,
        _user,
        _write_jsonl,
    )

    tools = [
        {
            "type": "tool_use",
            "name": "Agent",
            "input": {
                "subagent_type": "Explore",
                "description": "Find files",
            },
        }
    ]
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z"), _assistant_with_tools("2026-07-20T10:00:05Z", tools)],
    )
    rows = from_jsonl(tmp_path)
    assert len(rows) == 1
    spawns = json.loads(rows[0]["agent_spawns"])
    assert len(spawns) == 1
    assert spawns[0]["type"] == "Explore"


# --- GUA-43: surface column --------------------------------------------------


def _jsonl_session_with_entrypoint(
    cwd: str = "/Users/x/repo", entrypoint: str = "claude-vscode"
) -> list[dict]:
    """Minimal JSONL records with an entrypoint field."""
    return [
        {
            "type": "user",
            "timestamp": "2026-07-16T10:00:00Z",
            "cwd": cwd,
            "entrypoint": entrypoint,
            "message": {"content": "hello"},
        },
        {
            "type": "assistant",
            "timestamp": "2026-07-16T10:01:00Z",
            "message": {
                "model": "claude-opus-4-8",
                "content": [{"type": "text", "text": "ok"}],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            },
        },
    ]


def test_surface_column_round_trips_jsonl_era(tmp_path: Path) -> None:
    """JSONL-era rows carry the surface value extracted from entrypoint."""
    projects = tmp_path / "projects"
    projects.mkdir()
    _write_jsonl(projects / "abc.jsonl", _jsonl_session_with_entrypoint(entrypoint="claude-vscode"))
    store = tmp_path / "facts.db"
    rows = from_jsonl(projects)
    upsert(rows, store)
    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0]["surface"] == "claude-vscode"


def test_surface_column_none_for_notes_era(tmp_path: Path) -> None:
    """Notes-era rows carry surface=None (no entrypoint telemetry pre-July).

    validate_row() defaults absent nullable columns to None, so a row upserted
    without a surface key must read back as None -- same apparatus that backfills
    every prior NULLABLE_COLUMNS addition.
    """
    store = tmp_path / "facts.db"
    # A minimal notes-era row: no surface key at all
    row = _row("n1", date="2026-06-01", regime="note-hook", era=ERA_NOTE)
    upsert([row], store)
    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0].get("surface") is None


# --- Step 1: turns_since_last_compact + compact_trigger columns --------------


def _jsonl_session_with_compact(trigger: str = "manual") -> list[dict[str, Any]]:
    """Session JSONL with a compact_boundary carrying the given trigger."""
    return [
        {
            "type": "user",
            "timestamp": "2026-07-16T10:00:00Z",
            "cwd": "/Users/x/repo",
            "message": {"content": "hello"},
        },
        {
            "type": "assistant",
            "timestamp": "2026-07-16T10:01:00Z",
            "message": {
                "model": "claude-opus-4-8",
                "content": [{"type": "text", "text": "ok"}],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            },
        },
        {
            "type": "system",
            "subtype": "compact_boundary",
            "timestamp": "2026-07-16T10:02:00Z",
            "compactMetadata": {"trigger": trigger, "preTokens": 90000, "postTokens": 5000},
        },
        {
            "type": "user",
            "timestamp": "2026-07-16T10:03:00Z",
            "message": {"content": "post-compact turn"},
        },
    ]


def test_compact_trigger_column_round_trips_jsonl_era(tmp_path: Path) -> None:
    """compact_trigger from compactMetadata.trigger is stored and read back."""
    projects = tmp_path / "projects"
    projects.mkdir()
    _write_jsonl(projects / "cs.jsonl", _jsonl_session_with_compact(trigger="manual"))
    store = tmp_path / "facts.db"
    rows = from_jsonl(projects)
    upsert(rows, store)
    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0]["compact_trigger"] == "manual"
    assert stored[0]["turns_since_last_compact"] == 1


def test_compact_columns_none_when_no_compact(tmp_path: Path) -> None:
    """Sessions without a compact_boundary return None for both new columns."""
    store = tmp_path / "facts.db"
    row = _row("nc1")
    upsert([row], store)
    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0].get("compact_trigger") is None
    assert stored[0].get("turns_since_last_compact") is None


# --- LIB-57: failure attribution + bash antipatterns -------------------------


@pytest.mark.parametrize(
    ("error_kind", "expected"),
    [
        ("user_rejected", ERROR_CATEGORY_TOOL),
        ("permission_denied", ERROR_CATEGORY_ENV),
        ("command_failed", ERROR_CATEGORY_CODE),
        ("file_not_found", ERROR_CATEGORY_CODE),
        ("file_too_large", ERROR_CATEGORY_ENV),
        ("edit_failed", ERROR_CATEGORY_CODE),
        ("other", ERROR_CATEGORY_UNKNOWN),
    ],
)
def test_classify_error_kind_matches_skill_lookup_table(error_kind: str, expected: str) -> None:
    """Ported 1:1 from the step-9 lookup table in workflow-insights/SKILL.md."""
    assert classify_error_kind(error_kind) == expected


def test_classify_error_kind_unknown_kind_falls_to_unknown() -> None:
    """A kind absent from the lookup table must never be force-fit into
    code/env/tool -- a high unknown rate is the signal the table needs expansion."""
    assert classify_error_kind("some_new_kind_the_parser_never_emitted") == ERROR_CATEGORY_UNKNOWN


def test_jsonl_adapter_attributes_errors_by_category(tmp_path: Path) -> None:
    """Classification happens at parse time in _to_fact_from_jsonl: the parser
    discards raw error text after reducing it to the error_kind count dict, so
    this is the only point attribution can be applied."""
    from tests.shared.test_cartographer_parser import _assistant, _user, _write_jsonl

    records = [
        _user("2026-07-20T10:00:00Z"),
        _assistant("2026-07-20T10:00:05Z"),
        _user(
            "2026-07-20T10:01:00Z",
            text=[
                {
                    "type": "tool_result",
                    "tool_use_id": "1",
                    "is_error": True,
                    "content": "no such file or directory",
                },
                {
                    "type": "tool_result",
                    "tool_use_id": "2",
                    "is_error": True,
                    "content": "permission denied",
                },
                {
                    "type": "tool_result",
                    "tool_use_id": "3",
                    "is_error": True,
                    "content": "rejected by hook",
                },
                {
                    "type": "tool_result",
                    "tool_use_id": "4",
                    "is_error": True,
                    "content": "something unrecognisable happened",
                },
            ],
        ),
    ]
    _write_jsonl(tmp_path / "proj" / "sess-1.jsonl", records)

    rows = from_jsonl(tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["errors_code"] == 1  # file_not_found
    assert row["errors_env"] == 1  # permission_denied
    assert row["errors_tool"] == 1  # user_rejected
    assert row["errors_unknown"] == 1  # other
    validate_row(row)


def test_jsonl_adapter_stores_bash_antipatterns_from_parser(tmp_path: Path) -> None:
    """bash_antipatterns is written from the value the parser already computes --
    no re-derivation in factstore."""
    from tests.shared.test_cartographer_parser import _assistant_with_tools, _user, _write_jsonl

    tools = [
        {"type": "tool_use", "name": "Bash", "input": {"command": "cat foo.txt"}},
        {"type": "tool_use", "name": "Bash", "input": {"command": "grep bar foo.txt"}},
        {"type": "tool_use", "name": "Bash", "input": {"command": "python script.py"}},
    ]
    _write_jsonl(
        tmp_path / "proj" / "sess-1.jsonl",
        [_user("2026-07-20T10:00:00Z"), _assistant_with_tools("2026-07-20T10:00:05Z", tools)],
    )

    rows = from_jsonl(tmp_path)

    assert len(rows) == 1
    assert rows[0]["bash_antipatterns"] == 2  # cat + grep; python script.py is not flagged


def test_error_attribution_columns_none_for_notes_era(tmp_path: Path) -> None:
    """Notes-era rows carry no tool_errors data, so the new columns default to
    None via the same NULLABLE_COLUMNS mechanism as every other backfilled column."""
    store = tmp_path / "facts.db"
    row = _row("n1", date="2026-06-01", regime="note-hook", era=ERA_NOTE)
    upsert([row], store)
    stored = read_all(store)
    assert len(stored) == 1
    assert stored[0].get("errors_code") is None
    assert stored[0].get("errors_env") is None
    assert stored[0].get("errors_tool") is None
    assert stored[0].get("errors_unknown") is None
    assert stored[0].get("bash_antipatterns") is None


# --- experiment_verdicts (LIB-58) -------------------------------------------


def _verdict_row(**overrides: str) -> dict[str, str]:
    row = {
        "experiment": "bash-antipattern-nudge",
        "date": "2026-07-20",
        "metric": "absence:bash-antipatterns",
        "verdict": "confirmed",
        "evidence": "bash-antipatterns=0 across scored sessions",
    }
    row.update(overrides)
    return row


def test_append_verdicts_round_trips_through_read_verdicts(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    written = append_verdicts([_verdict_row()], store, run_at="2026-07-20T00:00:00Z")

    assert written == 1
    rows = read_verdicts(store)
    assert len(rows) == 1
    assert rows[0]["experiment"] == "bash-antipattern-nudge"
    assert rows[0]["verdict"] == "confirmed"
    assert rows[0]["run_at"] == "2026-07-20T00:00:00Z"


def test_append_verdicts_accumulates_across_runs_same_experiment(tmp_path: Path) -> None:
    """The table is append-only: two runs for the same experiment/date produce
    two rows (a trajectory), not an overwrite -- unlike `upsert` on `sessions`."""
    store = tmp_path / "facts.db"
    append_verdicts([_verdict_row(verdict="inconclusive")], store, run_at="2026-07-18T00:00:00Z")
    append_verdicts([_verdict_row(verdict="trending")], store, run_at="2026-07-19T00:00:00Z")
    append_verdicts([_verdict_row(verdict="confirmed")], store, run_at="2026-07-20T00:00:00Z")

    rows = read_verdicts(store)
    assert len(rows) == 3
    verdict_sequence = [r["verdict"] for r in rows]
    assert verdict_sequence == ["inconclusive", "trending", "confirmed"]


def test_append_verdicts_same_run_at_replaces_not_duplicates(tmp_path: Path) -> None:
    """Re-running the same insights run (identical run_at) is idempotent, since
    (experiment, date, run_at) is the primary key -- guards against double-invocation
    within a single --facts run rather than accumulating duplicate trajectory steps."""
    store = tmp_path / "facts.db"
    append_verdicts([_verdict_row(verdict="trending")], store, run_at="2026-07-20T00:00:00Z")
    append_verdicts([_verdict_row(verdict="confirmed")], store, run_at="2026-07-20T00:00:00Z")

    rows = read_verdicts(store)
    assert len(rows) == 1
    assert rows[0]["verdict"] == "confirmed"


def test_append_verdicts_empty_rows_is_noop(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    written = append_verdicts([], store, run_at="2026-07-20T00:00:00Z")
    assert written == 0
    assert not store.exists()


def test_append_verdicts_missing_field_raises_schema_error(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    bad_row = _verdict_row()
    del bad_row["evidence"]
    with pytest.raises(SchemaError):
        append_verdicts([bad_row], store, run_at="2026-07-20T00:00:00Z")


def test_read_verdicts_missing_store_returns_empty_list(tmp_path: Path) -> None:
    assert read_verdicts(tmp_path / "does-not-exist.db") == []


def test_append_verdicts_multiple_experiments_distinct_rows(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    rows = [
        _verdict_row(experiment="exp-a", date="2026-07-18"),
        _verdict_row(experiment="exp-b", date="2026-07-19", verdict="failed"),
    ]
    written = append_verdicts(rows, store, run_at="2026-07-20T00:00:00Z")

    assert written == 2
    stored = read_verdicts(store)
    experiments = {r["experiment"] for r in stored}
    assert experiments == {"exp-a", "exp-b"}


# ---------------------------------------------------------------------------
# LIB-50: findings table
# ---------------------------------------------------------------------------

# The 7 production rows from guacamayo/.claude/docs/review-findings.jsonl,
# verbatim. AK-006 and WH-001/WH-002 have no `symbols` key in production.
_FINDINGS_JSONL = """\
{"id": "SY-001", "source": "sanyi", "date": "2026-07-29", "repo": "librarian", "issue": "GUA-45", "file": "tools/cartographer/factstore.py", "lines": "114", "symbols": ["SUBAGENT_ATTRIBUTION_SINCE"], "category": "config", "merge_impact": "important", "evidence_state": "supported", "title": "SUBAGENT_ATTRIBUTION_SINCE hardcoded date not externalized", "review_type": "workflow-review"}
{"id": "AK-001", "source": "akira-scan", "date": "2026-07-29", "repo": "atlas", "issue": "ATL-37", "file": "src/graph.py", "lines": "155", "symbols": ["knowledge_tool_node"], "category": "resource-leak", "merge_impact": "important", "evidence_state": "verified", "title": "knowledge_tool_node leaks AtlasGraph on exception path", "review_type": "workflow-review"}
{"id": "AK-003", "source": "akira-scan", "date": "2026-07-29", "repo": "atlas", "issue": "ATL-37", "file": "core/preprocessing/crypto/indicators.py", "lines": "92", "symbols": ["compute_volume_sma"], "category": "api-contract", "merge_impact": "important", "evidence_state": "verified", "title": "volume_ratio now nullable \\u2014 contract change undocumented", "review_type": "workflow-review"}
{"id": "AK-006", "source": "akira-scan", "date": "2026-07-29", "repo": "atlas", "issue": "ATL-37", "file": "tests/api/test_main.py", "lines": "22-24", "category": "test-quality", "merge_impact": "suggestion", "evidence_state": "verified", "title": "exception-path test asserts close() only, not HTTP 500 surfaced", "review_type": "workflow-review"}
{"id": "AK-007", "source": "sanyi", "date": "2026-07-29", "repo": "atlas", "issue": "ATL-37", "file": "src/config.py", "lines": "7", "symbols": ["ATLAS_LLM_MODEL"], "category": "sanyi", "merge_impact": "nit", "evidence_state": "verified", "title": "hardcoded model fallback string remains (SANYI BN-1)", "review_type": "workflow-review"}
{"id": "WH-001", "source": "workflow-review", "date": "2026-07-29", "repo": "guacamayo", "issue": "fleet", "file": "n/a", "category": "workspace-hygiene", "merge_impact": "nit", "evidence_state": "verified", "title": "9 empty worktree-agent-* branches in guacamayo", "review_type": "workflow-review"}
{"id": "WH-002", "source": "workflow-review", "date": "2026-07-29", "repo": "librarian", "issue": "GUA-43", "file": "n/a", "category": "workspace-hygiene", "merge_impact": "important", "evidence_state": "verified", "title": "GUA-43 commit 39bca10 + /tmp/librarian-gua43 worktree redundant with staged state", "review_type": "workflow-review"}
"""


def test_findings_round_trip_all_seven_rows(tmp_path: Path) -> None:
    """Gate 1: upsert all 7 production findings, read back, assert field-level equality."""
    jsonl_path = tmp_path / "review-findings.jsonl"
    jsonl_path.write_text(_FINDINGS_JSONL, encoding="utf-8")
    store = tmp_path / "facts.db"

    rows = from_findings_jsonl(jsonl_path)
    assert len(rows) == 7

    written = upsert_findings(rows, store)
    assert written == 7

    stored = read_findings(store)
    assert len(stored) == 7

    # Index by id for field-level comparison
    by_id = {r["id"]: r for r in stored}

    # SY-001 — has symbols, has session_id=None (pre-GUA-63)
    sy001 = by_id["SY-001"]
    assert sy001["source"] == "sanyi"
    assert sy001["date"] == "2026-07-29"
    assert sy001["session_id"] is None  # Gate 3: nullable confirmed
    assert sy001["repo"] == "librarian"
    assert sy001["issue"] == "GUA-45"
    assert sy001["file"] == "tools/cartographer/factstore.py"
    assert sy001["lines"] == "114"
    assert json.loads(sy001["symbols"]) == ["SUBAGENT_ATTRIBUTION_SINCE"]
    assert sy001["title"] == "SUBAGENT_ATTRIBUTION_SINCE hardcoded date not externalized"
    assert sy001["category"] == "config"
    assert sy001["merge_impact"] == "important"
    assert sy001["evidence_state"] == "supported"
    assert sy001["review_type"] == "workflow-review"

    # AK-006 — no `symbols` key in JSONL → stored as "[]"
    ak006 = by_id["AK-006"]
    assert ak006["lines"] == "22-24"
    assert json.loads(ak006["symbols"]) == []

    # WH-001 — no `symbols`, no `session_id`
    wh001 = by_id["WH-001"]
    assert wh001["session_id"] is None
    assert wh001["repo"] == "guacamayo"
    assert wh001["issue"] == "fleet"

    # WH-002
    wh002 = by_id["WH-002"]
    assert wh002["merge_impact"] == "important"
    assert wh002["file"] == "n/a"


def test_findings_upsert_is_idempotent_on_id(tmp_path: Path) -> None:
    """Re-running over same JSONL replaces rows, not appends."""
    jsonl_path = tmp_path / "review-findings.jsonl"
    jsonl_path.write_text(_FINDINGS_JSONL, encoding="utf-8")
    store = tmp_path / "facts.db"

    rows = from_findings_jsonl(jsonl_path)
    upsert_findings(rows, store)
    upsert_findings(rows, store)

    assert len(read_findings(store)) == 7


def test_findings_session_id_nullable(tmp_path: Path) -> None:
    """Gate 3: all 7 pre-GUA-63 rows load with session_id=None."""
    jsonl_path = tmp_path / "review-findings.jsonl"
    jsonl_path.write_text(_FINDINGS_JSONL, encoding="utf-8")
    store = tmp_path / "facts.db"

    upsert_findings(from_findings_jsonl(jsonl_path), store)
    stored = read_findings(store)

    assert all(r["session_id"] is None for r in stored)


def test_findings_session_id_stored_when_present(tmp_path: Path) -> None:
    """A finding with a session_id round-trips correctly."""
    line = json.dumps(
        {
            "id": "AK-999",
            "source": "akira-scan",
            "date": "2026-08-01",
            "session_id": "abc123",
            "repo": "librarian",
            "issue": "LIB-50",
            "file": "tools/x.py",
            "lines": "1",
            "symbols": [],
            "title": "test finding",
            "category": "test",
            "merge_impact": "nit",
            "evidence_state": "verified",
            "review_type": "workflow-review",
        }
    )
    jsonl_path = tmp_path / "review-findings.jsonl"
    jsonl_path.write_text(line + "\n", encoding="utf-8")
    store = tmp_path / "facts.db"

    upsert_findings(from_findings_jsonl(jsonl_path), store)
    stored = read_findings(store)

    assert len(stored) == 1
    assert stored[0]["session_id"] == "abc123"


def test_findings_malformed_line_skipped(tmp_path: Path) -> None:
    """A malformed JSON line is skipped; surrounding rows are still loaded."""
    content = (
        '{"id": "AK-001", "source": "akira-scan", "date": "2026-07-29", "repo": "atlas", '
        '"issue": "ATL-37", "file": "f.py", "lines": "1", "title": "t", "category": "c", '
        '"merge_impact": "nit", "evidence_state": "verified", "review_type": "workflow-review"}\n'
        "not valid json\n"
        '{"id": "AK-002", "source": "akira-scan", "date": "2026-07-29", "repo": "atlas", '
        '"issue": "ATL-37", "file": "g.py", "lines": "2", "title": "t2", "category": "c", '
        '"merge_impact": "nit", "evidence_state": "verified", "review_type": "workflow-review"}\n'
    )
    jsonl_path = tmp_path / "review-findings.jsonl"
    jsonl_path.write_text(content, encoding="utf-8")

    rows = from_findings_jsonl(jsonl_path)
    assert len(rows) == 2
    assert rows[0]["id"] == "AK-001"
    assert rows[1]["id"] == "AK-002"


def test_findings_missing_jsonl_returns_empty(tmp_path: Path) -> None:
    rows = from_findings_jsonl(tmp_path / "does-not-exist.jsonl")
    assert rows == []


def test_read_findings_missing_store_returns_empty(tmp_path: Path) -> None:
    assert read_findings(tmp_path / "does-not-exist.db") == []
