"""Concept mastery maths (pure) and the plain-text forms of the learning payloads."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from librarian.courses import learning, learning_text
from librarian.courses.learning import EventIn, Evidence, score_concept

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)


def _ev(value: float, *, days: float = 0, link: str = "explicit", kind: str = "drill") -> Evidence:
    return Evidence(kind=kind, ts=NOW - timedelta(days=days), value=value, link=link)  # type: ignore[arg-type]


def test_no_evidence_scores_nothing() -> None:
    assert score_concept([], NOW) is None


def test_strength_is_the_weighted_mean_over_the_prior() -> None:
    s = score_concept([_ev(1.0), _ev(1.0)], NOW)
    assert s is not None
    assert s.strength == pytest.approx(2 / 3)  # 2 / (2 + PRIOR)
    assert s.recency == pytest.approx(1.0)
    assert not s.due and s.direct


def test_recency_halves_every_fourteen_days() -> None:
    s = score_concept([_ev(1.0, days=14)], NOW)
    assert s is not None
    assert s.recency == pytest.approx(0.5)


def test_a_weak_failure_run_goes_due() -> None:
    s = score_concept([_ev(0.0), _ev(0.0)], NOW)
    assert s is not None and s.due


def test_weak_only_evidence_is_capped_and_never_due() -> None:
    s = score_concept([_ev(1.0, link="semantic"), _ev(0.0, days=60, link="semantic")], NOW)
    assert s is not None
    assert not s.direct and not s.due
    assert s.strength <= learning.WEAK_ONLY_CAP


def test_direct_evidence_ignores_weak_evidence() -> None:
    s = score_concept([_ev(0.0), _ev(1.0, link="semantic")], NOW)
    assert s is not None
    assert s.strength == pytest.approx(0.0)
    assert s.counts["drills"] == 1


def test_only_the_last_twenty_events_count() -> None:
    old = [_ev(0.0, days=100 + i) for i in range(30)]
    new = [_ev(1.0, days=i / 100) for i in range(20)]
    s = score_concept(old + new, NOW)
    assert s is not None
    assert s.strength == pytest.approx(20 / 21)


def test_event_validation() -> None:
    EventIn(kind="lesson_done", lesson="a/b/c")
    for bad in (
        {"kind": "lesson_done"},
        {"kind": "drill_attempt", "score": 0.5},
        {"kind": "card_grade", "score": 0.5},
        {"kind": "drill_attempt", "lesson": "a/b", "score": 1.5},
        {"kind": "voice_grade", "lesson": "a/b", "score": 0.5},
        {"kind": "drill_attempt", "lesson": "a/b", "score": 0.5, "mode": "approach"},
        {"kind": "drill_attempt", "lesson": "a/b", "score": 0.5, "note": "my answer"},
        {"kind": "drill_attempt", "lesson": "../x y", "score": 0.5},
    ):
        with pytest.raises(ValidationError):
            EventIn(**bad)  # type: ignore[arg-type]


def test_naive_timestamps_become_utc() -> None:
    e = EventIn(kind="lesson_done", lesson="a/b", ts=datetime(2026, 1, 1))
    assert e.ts is not None and e.ts.tzinfo is UTC


def test_clamp_limit() -> None:
    assert learning_text.clamp_limit("junk") == learning_text.NEXT_DEFAULT_LIMIT
    assert learning_text.clamp_limit(0) == 1
    assert learning_text.clamp_limit(99) == learning_text.NEXT_MAX_LIMIT


def test_empty_forms_say_what_the_absence_means() -> None:
    assert learning_text.format_next([]) == learning_text.NOTHING_DUE
    assert "No wiki page" in learning_text.format_no_page("x")
    detail = {"id": "p", "title": "P", "summary": "s", "mastery": None, "catalogReady": False}
    text = learning_text.format_concept(detail)
    assert learning_text.NO_EVIDENCE_NOTE in text
    assert learning_text.CATALOG_UNAVAILABLE in text
