"""Leitner scheduling replayed from the flashcard self-grade log (librarian/courses/leitner.py)."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from librarian.courses.leitner import BOX_DAYS, CardState, card_key, load_states, replay, status_of

DECK = "programming/drills"
FRONT = "What is a closure?"
KEY = card_key(DECK, FRONT)


def _rec(day: date, result: str, **extra: object) -> dict[str, object]:
    # Noon in the server's own zone, so the local review date is the day given.
    ts = datetime(day.year, day.month, day.day, 12).astimezone()
    return {"ts": ts.isoformat(), "deck": DECK, "front": FRONT, "result": result} | extra


def _walk(*steps: tuple[int, str]) -> CardState:
    """Replay (days after start, grade) steps for one card."""
    start = date(2026, 1, 1)
    states = replay([_rec(start + timedelta(days=d), grade) for d, grade in steps])
    return states[KEY]


def test_box_intervals_are_the_fixed_ones() -> None:
    assert BOX_DAYS == (1, 2, 4, 8, 16)


def test_knew_climbs_one_box_at_a_time_and_tops_out_at_five() -> None:
    start = date(2026, 1, 1)
    steps = [(0, "knew")]
    assert _walk(*steps) == CardState(2, start + timedelta(days=2))
    day = 2
    for box, interval in [(3, 4), (4, 8), (5, 16), (5, 16)]:
        steps.append((day, "knew"))
        assert _walk(*steps) == CardState(box, start + timedelta(days=day + interval))
        day += interval


def test_a_miss_returns_the_card_to_box_one_from_any_box() -> None:
    state = _walk((0, "knew"), (2, "knew"), (6, "knew"), (14, "missed"))
    assert state == CardState(1, date(2026, 1, 1) + timedelta(days=15))


def test_a_miss_on_a_new_card_is_box_one_due_tomorrow() -> None:
    assert _walk((0, "missed")) == CardState(1, date(2026, 1, 2))


def test_knew_before_the_due_date_changes_nothing() -> None:
    assert _walk((0, "knew"), (0, "knew"), (1, "knew")) == CardState(2, date(2026, 1, 3))


def test_a_miss_before_the_due_date_still_counts() -> None:
    assert _walk((0, "knew"), (0, "missed")) == CardState(1, date(2026, 1, 2))


def test_late_review_schedules_from_the_review_not_the_old_due_date() -> None:
    assert _walk((0, "knew"), (30, "knew")) == CardState(3, date(2026, 1, 31) + timedelta(days=4))


def test_records_replay_in_time_order_not_file_order() -> None:
    first, second = _rec(date(2026, 1, 1), "knew"), _rec(date(2026, 1, 3), "missed")
    assert replay([second, first])[KEY] == CardState(1, date(2026, 1, 4))


def test_old_records_without_a_card_field_match_new_ones() -> None:
    old = _rec(date(2026, 1, 1), "knew")
    new = _rec(date(2026, 1, 3), "knew", card=KEY)
    assert replay([old, new])[KEY].box == 3


def test_lesson_deck_and_module_deck_share_a_card() -> None:
    assert card_key(f"{DECK}/some-lesson", FRONT) == card_key(DECK, FRONT)
    assert card_key("programming/other", FRONT) != KEY
    assert card_key(DECK, "Another front") != KEY


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "text",
        [],
        {},
        {"ts": "not a date", "deck": DECK, "front": FRONT, "result": "knew"},
        {"ts": 12, "deck": DECK, "front": FRONT, "result": "knew"},
        {"ts": "2026-01-01T12:00:00+00:00", "deck": DECK, "front": FRONT, "result": "maybe"},
        {"ts": "2026-01-01T12:00:00+00:00", "result": "knew"},
        {"ts": "2026-01-01T12:00:00+00:00", "deck": 1, "front": FRONT, "result": "knew"},
    ],
)
def test_unreadable_records_are_skipped(bad: object) -> None:
    assert replay([bad]) == {}
    assert replay([bad, _rec(date(2026, 1, 1), "knew")])[KEY].box == 2


def test_naive_timestamp_is_read_as_utc() -> None:
    rec = {"ts": "2026-01-15T12:00:00", "deck": DECK, "front": FRONT, "result": "knew"}
    assert replay([rec])[KEY].box == 2


def test_load_states_missing_empty_and_corrupt_logs(tmp_path: Path) -> None:
    log_path = tmp_path / "flashcards.jsonl"
    assert load_states(log_path) == {}
    log_path.write_text("")
    assert load_states(log_path) == {}
    log_path.write_text("{broken\n\n" + json.dumps(_rec(date(2026, 1, 1), "knew")) + "\n")
    assert load_states(log_path)[KEY].box == 2
    log_path.write_bytes(b"\xff\xfe\xff")
    assert load_states(log_path) == {}


def test_status_of_is_new_due_or_later() -> None:
    today = date(2026, 1, 10)
    assert status_of(None, today) == "new"
    assert status_of(CardState(1, today), today) == "due"
    assert status_of(CardState(1, today - timedelta(days=3)), today) == "due"
    assert status_of(CardState(1, today + timedelta(days=1)), today) == "later"


def test_a_timestamp_at_the_end_of_the_calendar_is_skipped() -> None:
    rec = {"ts": "9999-12-31T23:59:59+00:00", "result": "knew", "card": "a"}
    assert replay([rec]) == {}
