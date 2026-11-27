"""Grades, limits, latency, logging policy, tools and prompts: the small parts, without Pipecat."""

from __future__ import annotations

import logging
import math
import os
import re

import pytest

from librarian.agent.tools import LEARNING_TOOLS
from librarian.courses import learning
from librarian.voice import grades, log_policy
from librarian.voice.latency import LatencyTracker
from librarian.voice.limits import END_MESSAGES, SessionLimits
from librarian.voice.policy import Card, SessionPlan
from librarian.voice.prompts import system_prompt
from librarian.voice.tools import READ_ONLY_TOOLS, RECORD_GRADE, run_read_only, tools_for

# ── Grades ───────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw, score",
    [
        ({"score": 0}, 0.0),
        ({"score": 0.0}, 0.0),
        ({"score": 1}, 1.0),
        ({"score": 0.25}, 0.25),
        ({"score": 1.0001}, None),
        ({"score": -0.0001}, None),
        ({"score": "0.5"}, None),
        ({"score": None}, None),
        ({"score": True}, None),
        ({"score": math.nan}, None),
        ({"score": math.inf}, None),
        ({"score": 0.5, "comment": "words"}, None),
        ({}, None),
        (None, None),
        ([0.5], None),
        ("0.5", None),
    ],
)
def test_parse_grade(raw: object, score: float | None) -> None:
    assert grades.parse_grade(raw) == score


PLANS = {
    "lesson": SessionPlan(mode="approach", title="t", local_only=False, lesson="a/b/c"),
    "deck": SessionPlan(mode="flashcard", title="t", local_only=False, deck="a/b"),
}


def test_event_for_a_lesson_holds_ids_and_a_number() -> None:
    event = grades.build_event(PLANS["lesson"], 0.5, None)
    assert event.model_dump(exclude_none=True) == {
        "kind": "voice_grade",
        "lesson": "a/b/c",
        "score": 0.5,
        "mode": "approach",
    }


def test_event_for_a_card_links_to_its_lesson_when_it_has_one() -> None:
    linked = grades.build_event(PLANS["deck"], 0.5, Card("f", "b", lesson="a/b/c"))
    assert (linked.lesson, linked.deck) == ("a/b/c", "a/b")
    bare = grades.build_event(PLANS["deck"], 0.5, Card("f", "b"))
    assert (bare.lesson, bare.deck) == (None, "a/b")


async def test_a_failed_write_reports_false_rather_than_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(_user: str, _event: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(learning, "record_event", fail)
    monkeypatch.setattr(grades, "_learner", lambda _user_id: "learner")
    write = grades.grade_writer(None)
    assert await write(grades.build_event(PLANS["lesson"], 0.5, None)) is False


async def test_a_grade_is_written_for_the_user_it_was_opened_for(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[tuple[str, str]] = []

    def record(user: str, event: learning.EventIn) -> dict[str, object]:
        seen.append((user, event.kind))
        return {"logged": True, "concepts": []}

    monkeypatch.setattr(learning, "record_event", record)
    write = grades.grade_writer("user-7")
    assert await write(grades.build_event(PLANS["lesson"], 0.5, None)) is True
    assert seen == [("user-7", "voice_grade")]


# ── Limits ───────────────────────────────────────────────────────────────────


def _limits(**kw: float) -> SessionLimits:
    settings = {
        "started": 100.0,
        "idle_timeout_s": 10.0,
        "max_duration_s": 60.0,
        "max_turns": 2,
        "max_tokens": 100,
    }
    return SessionLimits(**{**settings, **kw})  # type: ignore[arg-type]


def test_idle_counts_from_the_last_activity() -> None:
    limits = _limits()
    assert limits.expired(109.0) is None
    assert limits.expired(110.0) == "idle"
    limits.touch(109.0)
    assert limits.expired(118.0) is None
    assert limits.expired(119.0) == "idle"


def test_activity_cannot_outlast_the_hard_maximum() -> None:
    limits = _limits()
    limits.touch(159.0)
    assert limits.expired(160.0) == "max_duration"


def test_turn_and_token_caps() -> None:
    limits = _limits()
    limits.add_turn()
    assert limits.over_budget() is None
    limits.add_turn()
    assert limits.over_budget() == "turn_cap"
    tokens = _limits()
    tokens.add_tokens(99)
    assert tokens.over_budget() is None
    tokens.add_tokens(1)
    assert tokens.over_budget() == "token_cap"
    assert limits.expired(101.0) == "turn_cap"


def test_every_end_reason_has_a_message() -> None:
    assert set(END_MESSAGES) == {"idle", "max_duration", "turn_cap", "token_cap"}


# ── Latency ──────────────────────────────────────────────────────────────────


def _full_turn(tracker: LatencyTracker, start: float = 10.0) -> dict | None:
    tracker.user_stopped(start)
    tracker.transcript(start + 0.1)
    tracker.turn_closed(start + 0.2)
    tracker.llm_request(start + 0.2)
    tracker.llm_first(start + 0.7)
    tracker.tts_first(start + 1.0)
    return tracker.bot_started(start + 1.01)


def test_a_turn_breaks_down_into_its_stages_counting_the_vad_wait() -> None:
    report = _full_turn(LatencyTracker(vad_stop_ms=200.0))
    assert report == {
        "turn": 1,
        "vad_stop_ms": 200.0,
        "stt_ms": 100.0,
        "turn_ms": 200.0,
        "llm_first_ms": 500.0,
        "tts_first_ms": 300.0,
        "output_ms": 10.0,
        "gap_ms": 1210.0,
    }


def test_the_report_holds_numbers_only() -> None:
    report = _full_turn(LatencyTracker())
    assert report is not None
    assert all(isinstance(v, int | float) for v in report.values())


def test_an_opening_line_has_no_stop_to_measure_from() -> None:
    assert LatencyTracker().bot_started(1.0) is None


def test_speech_resuming_voids_the_stop_before_it() -> None:
    tracker = LatencyTracker()
    tracker.user_stopped(1.0)
    tracker.user_started()
    report = _full_turn(tracker, start=5.0)
    assert report is not None
    assert report["gap_ms"] == 1010.0


def test_the_first_mark_of_each_kind_wins_and_turns_number_up() -> None:
    tracker = LatencyTracker()
    tracker.user_stopped(1.0)
    tracker.user_stopped(1.5)
    tracker.tts_first(2.0)
    tracker.tts_first(3.0)
    report = tracker.bot_started(4.0)
    assert report is not None
    assert report["gap_ms"] == 3000.0
    assert report["stt_ms"] is None
    assert _full_turn(tracker)["turn"] == 2  # type: ignore[index]


# ── Logging policy ───────────────────────────────────────────────────────────


def test_settings_that_would_write_content_elsewhere_are_forced_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PIPECAT_SMART_TURN_LOG_DATA", "1")
    monkeypatch.setenv("ANTHROPIC_LOG", "debug")
    monkeypatch.setenv("HF_HUB_DISABLE_TELEMETRY", "0")
    levels = {n: logging.getLogger(n).level for n in log_policy.CHATTY_STDLIB_LOGGERS}
    try:
        log_policy.pin_logging(sink=lambda _message: None)
        assert "PIPECAT_SMART_TURN_LOG_DATA" not in os.environ
        assert "ANTHROPIC_LOG" not in os.environ
        assert os.environ["HF_HUB_DISABLE_TELEMETRY"] == "1"
        assert logging.getLogger("anthropic").level == logging.ERROR
        assert logging.getLogger("httpx").level == logging.ERROR
    finally:
        for name, level in levels.items():
            logging.getLogger(name).setLevel(level)


# ── Tools ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("mode", ["flashcard", "approach", "interview"])
def test_the_grade_is_the_only_write_and_no_tool_returns_a_lesson_body(mode: str) -> None:
    names = {tool["name"] for tool in tools_for(mode)}  # type: ignore[arg-type]
    assert RECORD_GRADE in names
    assert names - {RECORD_GRADE} == set(READ_ONLY_TOOLS[mode])  # type: ignore[index]
    assert not names & {"read_lesson", "search_lessons"}
    assert all(tool["eager_input_streaming"] for tool in tools_for(mode))  # type: ignore[arg-type]


def test_read_only_tools_are_in_the_registry() -> None:
    for names in READ_ONLY_TOOLS.values():
        assert set(names) <= LEARNING_TOOLS


@pytest.mark.parametrize(
    "name, args",
    [
        ("read_lesson", {"id": "a"}),
        ("search_lessons", {"query": "a"}),
        (RECORD_GRADE, {"score": 1}),
        ("learning_next", {}),  # real, but not offered to flashcards
        ("concept_status", "not a dict"),
    ],
)
async def test_a_tool_not_offered_is_refused_whatever_the_model_asks(
    name: str, args: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*_a: object, **_k: object) -> None:
        raise AssertionError("must not be called")

    monkeypatch.setattr("librarian.voice.tools.registry_tools", explode)
    outcome = await run_read_only(name, args, "flashcard")
    assert outcome.is_error


# ── Prompts ──────────────────────────────────────────────────────────────────

CARD_PLAN = SessionPlan(
    mode="flashcard",
    title="Cards",
    local_only=False,
    deck="a/b",
    cards=(Card("Front text here", "Back text here"),),
)
APPROACH_PLAN = SessionPlan(
    mode="approach",
    title="Drill",
    local_only=False,
    lesson="a/b/c",
    prompt="Count the lanterns.",
    reference="Keep a tally.",
)
INTERVIEW_PLAN = SessionPlan(
    mode="interview",
    title="Topic",
    local_only=True,
    lesson="interviewing/a/b",
    material="Talk about a lantern.",
)
ALL_PROMPTS = [system_prompt(p) for p in (CARD_PLAN, APPROACH_PLAN, INTERVIEW_PLAN)]


@pytest.mark.parametrize("which", range(len(ALL_PROMPTS)))
def test_every_prompt_writes_for_the_ear_and_never_grades_delivery(which: int) -> None:
    prompt = ALL_PROMPTS[which]
    assert "No markdown" in prompt
    assert "Never bring up how something was said" in prompt
    assert "record_grade" in prompt


def test_flashcard_prompt_forbids_the_back_and_does_not_hold_it() -> None:
    assert "Do not say it" in ALL_PROMPTS[0]
    assert "Back text here" not in ALL_PROMPTS[0]


def test_approach_prompt_holds_the_reference_and_forbids_stating_it() -> None:
    assert "Keep a tally." in ALL_PROMPTS[1]
    assert "Never state, read out, summarise or walk through the reference" in ALL_PROMPTS[1]


@pytest.mark.parametrize("which", range(len(ALL_PROMPTS)))
@pytest.mark.parametrize(
    "term",
    ["salary", "compensation", "employer", "resume", "voice-notes", "/users/", "her", "she"],
)
def test_prompts_hold_nothing_personal(which: int, term: str) -> None:
    assert not re.search(rf"\b{re.escape(term)}\b", ALL_PROMPTS[which].lower())
