"""Leitner scheduling replayed from graded attempts (librarian/courses/leitner.py)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from librarian import accounts
from librarian.accounts import User
from librarian.config import get_settings
from librarian.courses import attempts, leitner
from librarian.courses.leitner import BOX_DAYS, CardState, card_key, status_of
from librarian.db import get_engine

DECK = "programming/drills"
FRONT = "What is a closure?"
KEY = card_key(DECK, FRONT)


def _me() -> User:
    return accounts.ensure_owner(get_engine(), get_settings().owner_email)  # timezone UTC


def load_states() -> dict[str, CardState]:
    return leitner.load_states(_me())


def _record(kind: str, key: str, scope: str, result: str, ts: str) -> None:
    attempts.record(_me().id, kind, key, scope, result, ts=ts)


def _grade(day: date, result: str, key: str = KEY) -> None:
    # Noon UTC, the owner's zone, so the review date is the day given.
    ts = datetime(day.year, day.month, day.day, 12, tzinfo=UTC)
    _record("flashcard", key, DECK, result, ts.isoformat())


def _walk(*steps: tuple[int, str]) -> CardState:
    """Replay (days after start, grade) steps for one card."""
    start = date(2026, 1, 1)
    for d, grade in steps:
        _grade(start + timedelta(days=d), grade)
    return load_states()[KEY]


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


def test_attempts_replay_in_time_order_not_insertion_order() -> None:
    _grade(date(2026, 1, 3), "missed")
    _grade(date(2026, 1, 1), "knew")
    assert load_states()[KEY] == CardState(1, date(2026, 1, 4))


def test_lesson_deck_and_module_deck_share_a_card() -> None:
    assert card_key(f"{DECK}/some-lesson", FRONT) == card_key(DECK, FRONT)
    assert card_key("programming/other", FRONT) != KEY
    assert card_key(DECK, "Another front") != KEY


def test_naive_timestamp_is_read_as_utc() -> None:
    _record("flashcard", KEY, DECK, "knew", "2026-01-15T12:00:00")
    assert load_states()[KEY].box == 2


def test_load_states_reads_the_attempts_store() -> None:
    assert load_states() == {}
    when = datetime(2026, 1, 1, 12, tzinfo=UTC).isoformat()
    _record("flashcard", KEY, DECK, "knew", when)
    assert load_states()[KEY].box == 2
    # A wrong multiple-choice answer is a miss, in the same queue.
    _record("mcq", "programming/drills:q:abc", DECK, "correct", when)
    _record("mcq", "programming/drills:q:abc", DECK, "wrong", when)
    assert load_states()["programming/drills:q:abc"].box == 1
    # Drill runs are not scheduled.
    _record("drill", "programming/drills/x", "programming/drills/x", "fail", when)
    assert set(load_states()) == {KEY, "programming/drills:q:abc"}


def test_status_of_is_new_due_or_later() -> None:
    today = date(2026, 1, 10)
    assert status_of(None, today) == "new"
    assert status_of(CardState(1, today), today) == "due"
    assert status_of(CardState(1, today - timedelta(days=3)), today) == "due"
    assert status_of(CardState(1, today + timedelta(days=1)), today) == "later"


def test_a_timestamp_at_the_end_of_the_calendar_is_skipped() -> None:
    _record("flashcard", "a", DECK, "knew", "9999-12-31T23:59:59+00:00")
    assert load_states() == {}


def test_private_prefix_does_not_change_the_key() -> None:
    assert card_key(f"private/{DECK}/lesson", FRONT) == KEY


def test_days_are_the_users_calendar_days() -> None:
    # 23:30 UTC on Jan 1 is already Jan 2 in Tokyo: the card is due two days after *that*.
    rows = [
        attempts.Attempt(
            datetime(2026, 1, 1, 23, 30, tzinfo=UTC), "flashcard", KEY, DECK, "knew", {}
        )
    ]
    assert leitner.states_from(rows, "UTC")[KEY].due_on == date(2026, 1, 3)
    assert leitner.states_from(rows, "Asia/Tokyo")[KEY].due_on == date(2026, 1, 4)
    assert leitner.states_from(rows, "America/Los_Angeles")[KEY].due_on == date(2026, 1, 3)


def test_today_is_the_users_today_and_an_unknown_zone_is_utc() -> None:
    tokyo = User("u", "t@example.com", "member", timezone="Asia/Tokyo")
    assert leitner.today(tokyo) == datetime.now(leitner.zone("Asia/Tokyo")).date()
    assert leitner.zone("Not/AZone") == leitner.zone("UTC")
