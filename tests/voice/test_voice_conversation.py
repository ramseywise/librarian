"""What gets said, billed and graded, with a scripted model client and no audio."""

from __future__ import annotations

import asyncio
from contextlib import aclosing
from typing import Any

import anthropic
import httpx
import pytest
from voice_fakes import REFERENCE_QUOTE, FakeClient, Reply, grade_call, tool_call

from librarian.courses.learning import EventIn
from librarian.voice import conversation as conv
from librarian.voice.config import VoiceConfig
from librarian.voice.conversation import (
    Conversation,
    Event,
    Finished,
    Graded,
    Say,
    Ungraded,
)
from librarian.voice.limits import SessionLimits
from librarian.voice.policy import Card, SessionPlan
from librarian.voice.tools import ToolOutcome

BACK = "A small flame sitting on the wick of the lantern"
CARDS = (
    Card("What lights a lantern?", BACK, "maths/m/a"),
    Card("What puts one out?", "A puff of air from somewhere nearby"),
)
FLASHCARD = SessionPlan(mode="flashcard", title="Lanterns", local_only=False, deck="d", cards=CARDS)
APPROACH = SessionPlan(
    mode="approach",
    title="Lanterns",
    local_only=False,
    lesson="maths/m/drill",
    prompt="Count the lit lanterns.",
    reference=f"{REFERENCE_QUOTE} at the very end.",
)
INTERVIEW = SessionPlan(
    mode="interview",
    title="Lantern `design`",
    local_only=True,
    lesson="interviewing/m/t",
    material="Talk about a lantern you built.",
)
CFG = VoiceConfig(model="test-model", max_tokens=321, effort="low")


class Rig:
    def __init__(
        self, plan: SessionPlan, *replies: Reply, written: bool = True, **limits: float
    ) -> None:
        self.client = FakeClient(*replies)
        self.events: list[Any] = []
        self.written = written
        settings = {
            "started": 0.0,
            "idle_timeout_s": 60.0,
            "max_duration_s": 600.0,
            "max_turns": 10,
            "max_tokens": 1000,
        }
        self.limits = SessionLimits(**{**settings, **limits})
        self.conv = Conversation(plan, self.client, CFG, self.limits, self._write)  # type: ignore[arg-type]

    async def _write(self, event: EventIn) -> bool:
        self.events.append(event)
        return self.written

    async def turn(self, text: str = "an answer") -> list[Event]:
        return [event async for event in self.conv.respond(text)]


def said(events: list[Event]) -> str:
    return " ".join(e.text for e in events if isinstance(e, Say))


def last_user_text(request: dict[str, Any]) -> str:
    return request["messages"][-1]["content"][-1]["text"]


# ── Before an attempt, nothing is billed or spoiled ──────────────────────────


def test_the_opening_comes_from_the_plan_with_no_model_call() -> None:
    rig = Rig(FLASHCARD)
    assert rig.conv.opening() == "First card. What lights a lantern?"
    assert rig.client.requests == []
    assert BACK not in rig.conv.opening()
    assert REFERENCE_QUOTE not in Rig(APPROACH).conv.opening()
    assert "Count the lit lanterns" in Rig(APPROACH).conv.opening()
    assert "`" not in Rig(INTERVIEW).conv.opening()


async def test_each_request_carries_only_the_current_cards_back() -> None:
    rig = Rig(
        FLASHCARD,
        Reply(chunks=["Right. "], blocks=[grade_call(1.0)], stop_reason="tool_use"),
        Reply(chunks=["Almost. "], blocks=[grade_call(0.5)], stop_reason="tool_use"),
    )
    assert BACK not in rig.conv._system
    await rig.turn()
    first = rig.client.requests[0]
    assert BACK in last_user_text(first)
    assert CARDS[1].back not in str(first["messages"])
    await rig.turn()
    second = last_user_text(rig.client.requests[1])
    assert CARDS[1].back in second
    assert BACK not in second


async def test_a_reply_quoting_the_back_before_an_attempt_is_replaced() -> None:
    rig = Rig(FLASHCARD, Reply(chunks=[f"It is {BACK}. ", "Does that help?"]))
    events = await rig.turn("give me a hint")
    assert BACK not in said(events)
    assert conv.TRY_FIRST in said(events)
    assert Ungraded("no_grade") in events
    assert rig.events == []


async def test_after_a_graded_attempt_the_back_is_spoken_and_the_next_card_follows() -> None:
    rig = Rig(
        FLASHCARD,
        Reply(
            chunks=[f"Not quite, it is {BACK}. "], blocks=[grade_call(0.0)], stop_reason="tool_use"
        ),
    )
    events = await rig.turn("no idea")
    assert BACK in said(events)
    assert said(events).endswith("Next card. What puts one out?")
    assert Graded(0.0) in events


async def test_the_guard_splits_at_sentences_even_across_stream_chunks() -> None:
    half = len(BACK) // 2
    rig = Rig(FLASHCARD, Reply(chunks=["Well. It is ", BACK[:half], BACK[half:], ". Think."]))
    events = await rig.turn()
    assert events[0] == Say("Well.")
    assert BACK not in said(events)


async def test_approach_never_speaks_a_quote_of_the_reference() -> None:
    rig = Rig(
        APPROACH,
        Reply(chunks=[f"Try this: {REFERENCE_QUOTE}. ", "Then again, what do you think?"]),
    )
    events = await rig.turn("just tell me")
    text = said(events)
    assert "running tally" not in text
    assert conv.LEAK_REPLACEMENT in text


def test_the_guard_handles_case_punctuation_and_short_references() -> None:
    guard = conv.LeakGuard("Keep a running tally of lit lanterns", run=6)
    assert guard.leaks("KEEP a running, tally of lit!")
    assert not guard.leaks("Keep a running count of the lit lanterns")
    assert conv.LeakGuard("Paris").leaks("I think it is paris.")
    assert not conv.LeakGuard("").leaks("anything at all here")


async def test_approach_holds_the_reference_in_the_system_prompt_with_a_prohibition() -> None:
    rig = Rig(APPROACH, Reply(chunks=["Go on."]))
    await rig.turn()
    system = rig.client.requests[0]["system"]
    assert REFERENCE_QUOTE in system
    assert "Never state, read out" in system


# ── Grades: only a valid tool call counts ────────────────────────────────────


@pytest.mark.parametrize(
    "bad_input",
    [
        {"score": 1.5},
        {"score": "0.5"},
        {"score": True},
        {"score": None},
        {"score": float("nan")},
        {},
        {"score": 0.5, "x": 1},
    ],
)
async def test_a_malformed_grade_emits_nothing_and_is_never_a_zero(bad_input: dict) -> None:
    block = tool_call("record_grade", bad_input)
    rig = Rig(APPROACH, Reply(chunks=["Fine. "], blocks=[block], stop_reason="tool_use"))
    events = await rig.turn()
    assert rig.events == []
    assert Ungraded("malformed") in events
    assert not any(isinstance(e, Graded) for e in events)


async def test_no_grade_call_is_visible_as_ungraded() -> None:
    rig = Rig(APPROACH, Reply(chunks=["Say more about that."]))
    events = await rig.turn()
    assert rig.events == []
    assert events[-1] == Ungraded("no_grade")


async def test_a_real_zero_is_recorded_as_a_zero() -> None:
    rig = Rig(APPROACH, Reply(chunks=["No. "], blocks=[grade_call(0)], stop_reason="tool_use"))
    events = await rig.turn()
    assert Graded(0.0) in events
    assert rig.events[0].score == 0.0
    assert rig.events[0].model_dump(exclude_none=True) == {
        "kind": "voice_grade",
        "lesson": "maths/m/drill",
        "score": 0.0,
        "mode": "approach",
    }


async def test_a_card_grade_links_the_card_lesson_and_the_deck() -> None:
    rig = Rig(FLASHCARD, Reply(chunks=["Yes. "], blocks=[grade_call(1)], stop_reason="tool_use"))
    await rig.turn()
    assert (rig.events[0].lesson, rig.events[0].deck) == ("maths/m/a", "d")


async def test_a_failed_write_says_ungraded_and_keeps_the_card() -> None:
    rig = Rig(
        FLASHCARD,
        Reply(chunks=["Yes. "], blocks=[grade_call(1)], stop_reason="tool_use"),
        written=False,
    )
    events = await rig.turn()
    assert Ungraded("write_failed") in events
    assert not any(isinstance(e, Graded) for e in events)
    assert "Next card" not in said(events)


async def test_grading_makes_no_second_billed_call_and_the_result_leads_the_next_message() -> None:
    rig = Rig(
        APPROACH,
        Reply(chunks=["Good. "], blocks=[grade_call(1, tool_id="g9")], stop_reason="tool_use"),
        Reply(chunks=["Next."]),
    )
    await rig.turn()
    assert len(rig.client.requests) == 1
    await rig.turn()
    content = rig.client.requests[1]["messages"][-1]["content"]
    assert content[0]["type"] == "tool_result"
    assert content[0]["tool_use_id"] == "g9"
    assert content[-1]["type"] == "text"


async def test_two_grades_in_one_reply_record_the_first_and_refuse_the_second() -> None:
    blocks = [grade_call(0.9, "a"), grade_call(0.1, "b")]
    rig = Rig(APPROACH, Reply(chunks=["Yes. "], blocks=blocks, stop_reason="tool_use"))
    await rig.turn()
    assert [e.score for e in rig.events] == [0.9]


@pytest.mark.parametrize(
    "stop_reason, reason, line",
    [("refusal", "refusal", conv.REFUSED), ("max_tokens", "cut_off", conv.CUT_OFF)],
)
async def test_a_stopped_reply_records_nothing_even_with_a_grade_in_it(
    stop_reason: str, reason: str, line: str
) -> None:
    rig = Rig(APPROACH, Reply(chunks=["Well. "], blocks=[grade_call(1)], stop_reason=stop_reason))
    events = await rig.turn()
    assert rig.events == []
    assert line in said(events)
    assert events[-1] == Ungraded(reason)  # type: ignore[arg-type]


def _api_error() -> anthropic.APIError:
    request = httpx.Request("POST", "http://api.test")
    return anthropic.APIConnectionError(request=request)


@pytest.mark.parametrize("error", [_api_error(), TimeoutError()])
async def test_a_model_failure_says_so_and_is_ungraded(error: Exception) -> None:
    rig = Rig(APPROACH, Reply(chunks=["Well. "], error=error))
    events = await rig.turn()
    assert conv.UNREACHABLE in said(events)
    assert events[-1] == Ungraded("llm_error")
    assert rig.client.closed == 1


async def test_a_call_that_never_finishes_times_out_and_closes_its_stream() -> None:
    rig = Rig(APPROACH, Reply(hang_after_chunks=True))
    rig.conv._cfg = VoiceConfig(llm_timeout_s=0.02)
    events = await rig.turn()
    assert events[-1] == Ungraded("llm_error")
    assert rig.client.closed == 1


# ── Requests and limits ──────────────────────────────────────────────────────


async def test_requests_are_bounded_and_use_the_setting() -> None:
    rig = Rig(APPROACH, Reply(chunks=["Go on."]))
    await rig.turn()
    request = rig.client.requests[0]
    assert request["model"] == "test-model"
    assert request["max_tokens"] == 321
    assert request["output_config"] == {"effort": "low"}
    assert "thinking" not in request
    assert "<spoken>an answer</spoken>" in last_user_text(request)


async def test_the_turn_cap_ends_the_session_before_another_billed_call() -> None:
    rig = Rig(APPROACH, Reply(chunks=["One."]), max_turns=1)
    events = await rig.turn()
    assert events[-1] == Finished("turn_cap")
    assert await rig.turn() == [Finished("turn_cap")]
    assert len(rig.client.requests) == 1


async def test_the_token_cap_ends_the_session() -> None:
    rig = Rig(APPROACH, Reply(chunks=["One."], tokens=50), max_tokens=50)
    assert (await rig.turn())[-1] == Finished("token_cap")
    assert await rig.turn() == [Finished("token_cap")]


async def test_the_deck_ends_after_its_last_card() -> None:
    plan = SessionPlan(mode="flashcard", title="t", local_only=False, deck="d", cards=CARDS[:1])
    rig = Rig(plan, Reply(chunks=["Yes. "], blocks=[grade_call(1)], stop_reason="tool_use"))
    events = await rig.turn()
    assert conv.DECK_DONE in said(events)
    assert events[-1] == Finished("deck_end")


# ── Tools ────────────────────────────────────────────────────────────────────


async def test_a_read_only_tool_gets_a_filler_first_and_its_result_goes_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []

    async def fake(_name: str, _args: object, _mode: str, _user: str | None = None) -> ToolOutcome:
        order.append("tool")
        return ToolOutcome("weak on lanterns")

    monkeypatch.setattr(conv, "run_read_only", fake)
    rig = Rig(
        INTERVIEW,
        Reply(blocks=[tool_call("concept_status", {"concept": "x"})], stop_reason="tool_use"),
        Reply(chunks=["You are weak on lanterns."]),
    )
    events = []
    async for event in rig.conv.respond("how am I doing"):
        order.append("event")
        events.append(event)
    assert events[0] == Say(conv.FILLER)
    assert order[:2] == ["event", "tool"]  # The filler is out before the tool holds anything up.
    second = rig.client.requests[1]["messages"][-1]
    assert second["content"][0]["content"] == "weak on lanterns"


async def test_no_filler_once_the_reply_has_already_started(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake(_name: str, _args: object, _mode: str, _user: str | None = None) -> ToolOutcome:
        return ToolOutcome("ok")

    monkeypatch.setattr(conv, "run_read_only", fake)
    rig = Rig(
        INTERVIEW,
        Reply(
            chunks=["Let me check. "],
            blocks=[tool_call("concept_status", {})],
            stop_reason="tool_use",
        ),
        Reply(chunks=["Done."]),
    )
    assert conv.FILLER not in said(await rig.turn())


async def test_tool_rounds_are_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake(_name: str, _args: object, _mode: str, _user: str | None = None) -> ToolOutcome:
        return ToolOutcome("ok")

    monkeypatch.setattr(conv, "run_read_only", fake)
    looping = Reply(blocks=[tool_call("concept_status", {})], stop_reason="tool_use")
    rig = Rig(INTERVIEW, *[looping] * (conv.MAX_TOOL_ROUNDS + 5))
    await rig.turn()
    assert len(rig.client.requests) == conv.MAX_TOOL_ROUNDS + 1


async def test_an_unknown_tool_runs_nothing_and_writes_nothing() -> None:
    rig = Rig(
        APPROACH,
        Reply(blocks=[tool_call("delete_everything", {})], stop_reason="tool_use"),
        Reply(chunks=["Sorry."]),
    )
    await rig.turn()
    result = rig.client.requests[1]["messages"][-1]["content"][0]
    assert result["is_error"] is True
    assert rig.events == []


# ── Barge-in ─────────────────────────────────────────────────────────────────


async def _consume(rig: Rig, seen: list[Event]) -> None:
    async for event in rig.conv.respond("an answer"):
        seen.append(event)


async def test_cancelling_mid_stream_closes_the_billed_call() -> None:
    rig = Rig(APPROACH, Reply(chunks=["First sentence. "], hang_after_chunks=True))
    seen: list[Event] = []
    task = asyncio.create_task(_consume(rig, seen))
    await asyncio.wait_for(rig.client.hanging.wait(), 1)
    assert rig.client.closed == 0
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert rig.client.closed == 1
    assert rig.events == []


async def test_cancelling_while_the_consumer_holds_a_sentence_also_closes_it() -> None:
    """The stream sits suspended at a yield here, and nothing else would come back for it."""
    rig = Rig(
        APPROACH, Reply(chunks=["First sentence. ", "Second sentence. "], hang_after_chunks=True)
    )
    held = asyncio.Event()

    async def slow_consumer() -> None:
        async with aclosing(rig.conv.respond("an answer")) as events:  # As `_run_turn` holds it.
            async for _event in events:
                held.set()
                await asyncio.Event().wait()

    task = asyncio.create_task(slow_consumer())
    await asyncio.wait_for(held.wait(), 1)
    assert rig.client.opened == 1
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert rig.client.closed == 1


async def test_cancelling_during_a_tool_still_pays_the_tool_results_next_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started = asyncio.Event()

    async def hang(_name: str, _args: object, _mode: str, _user: str | None = None) -> ToolOutcome:
        started.set()
        await asyncio.Event().wait()
        raise AssertionError

    monkeypatch.setattr(conv, "run_read_only", hang)
    use = tool_call("concept_status", {}, tool_id="t7")
    rig = Rig(INTERVIEW, Reply(blocks=[use], stop_reason="tool_use"), Reply(chunks=["Okay."]))
    task = asyncio.create_task(_consume(rig, []))
    await asyncio.wait_for(started.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await rig.turn("never mind")
    content = rig.client.requests[1]["messages"][-1]["content"]
    assert content[0]["tool_use_id"] == "t7"
    assert content[0]["is_error"] is True
