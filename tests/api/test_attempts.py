"""The attempts store (librarian/courses/attempts.py): one table for every graded study event."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from librarian.courses import attempts

TS = "2026-01-01T12:00:00+00:00"


def test_nothing_stored_reads_as_empty() -> None:
    assert attempts.attempts() == []
    assert attempts.flashcard_rows() == []


def test_record_and_read_back_in_time_order() -> None:
    assert attempts.record("mcq", "m:q:a", "c/m", "wrong", ts="2026-01-02T00:00:00+00:00")
    assert attempts.record("flashcard", "m:abc", "c/m", "knew", payload={"front": "F"}, ts=TS)
    rows = attempts.attempts()
    assert [(a.kind, a.result, a.module, a.good) for a in rows] == [
        ("flashcard", "knew", "c/m", True),
        ("mcq", "wrong", "c/m", False),
    ]
    assert rows[0].payload == {"front": "F"}
    assert [a.kind for a in attempts.attempts(["mcq"])] == ["mcq"]


def test_module_is_the_first_two_segments_of_the_scope() -> None:
    attempts.record("drill", "a/b/c", "a/b/c", "pass", ts=TS)
    assert attempts.attempts()[0].module == "a/b"


@pytest.mark.parametrize(
    ("kind", "result"), [("flashcard", "correct"), ("mcq", "knew"), ("x", "pass")]
)
def test_a_result_the_kind_does_not_allow_is_refused(kind: str, result: str) -> None:
    with pytest.raises(ValueError, match="not a result"):
        attempts.record(kind, "i", "s", result)
    assert attempts.attempts() == []


def test_the_same_event_twice_is_stored_once() -> None:
    attempts.record("flashcard", "k", "c/m", "knew", ts=TS)
    attempts.record("flashcard", "k", "c/m", "knew", ts=TS)
    assert len(attempts.attempts()) == 1


def test_a_store_that_cannot_be_written_reports_false(tmp_path: Path) -> None:
    (tmp_path / "state").write_text("a file where the state dir should be")
    assert attempts.record("flashcard", "k", "c/m", "knew") is False


def _legacy(*lines: str) -> None:
    attempts.LEGACY_FLASHCARD_LOG.parent.mkdir(parents=True, exist_ok=True)
    attempts.LEGACY_FLASHCARD_LOG.write_text("\n".join(lines) + "\n")


def test_legacy_log_is_imported_once_and_left_in_place() -> None:
    good = {"ts": TS, "deck": "c/m", "front": "Why?", "result": "missed", "source": "s"}
    keyed = {"ts": "2026-01-03T00:00:00+00:00", "deck": "c/m", "card": "c/m:xyz", "result": "knew"}
    _legacy(
        json.dumps(good), "{broken", json.dumps(keyed), json.dumps({"ts": TS, "result": "maybe"})
    )
    first = attempts.attempts()
    assert [(a.item.split(":")[0], a.result) for a in first] == [("c/m", "missed"), ("c/m", "knew")]
    assert first[0].payload == {"front": "Why?", "source": "s"}
    assert attempts.LEGACY_FLASHCARD_LOG.exists()
    # Reading again, or a write, adds nothing.
    attempts.record("flashcard", "other", "c/m", "knew", ts="2026-02-01T00:00:00+00:00")
    assert len(attempts.attempts()) == 3
    assert len(attempts.attempts()) == 3


def test_a_log_that_grew_imports_only_the_new_lines() -> None:
    row = {"ts": TS, "deck": "c/m", "front": "A", "result": "knew"}
    _legacy(json.dumps(row))
    assert len(attempts.attempts()) == 1
    _legacy(json.dumps(row), json.dumps(row | {"ts": "2026-01-05T00:00:00+00:00", "front": "B"}))
    assert len(attempts.attempts()) == 2


def test_flashcard_rows_keep_the_old_shape() -> None:
    attempts.record(
        "flashcard",
        "k",
        "c/m",
        "missed",
        payload={"front": "Q?", "source": "s", "lesson": "c/m/l"},
        ts=TS,
    )
    (row,) = attempts.flashcard_rows()
    assert row["deck"] == "c/m" and row["front"] == "Q?" and row["result"] == "missed"
    assert row["source"] == "s" and row["lesson"] == "c/m/l"
