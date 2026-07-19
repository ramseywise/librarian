from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer.factstore import (
    ERA_JSONL,
    ERA_NOTE,
    REGIME_UNCLASSIFIED,
    SchemaError,
    _classify_meta,
    from_jsonl,
    from_notes,
    read_all,
    regime_for,
    upsert,
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
