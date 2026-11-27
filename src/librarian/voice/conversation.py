"""One voice conversation: what is said, when the model is called, and what gets graded.

No Pipecat here. The pipeline feeds in transcribed turns and consumes `Event`s, so all the rules
can be tested with a fake model client and no audio. `respond` can be cancelled at any point: that
is a barge-in, and the stream closes as the `async with` unwinds, which stops the billed call.

Replies are spoken a sentence at a time, and the model's reply is the only thing that needs it.
The opening line and each flashcard front come from the plan, so nothing is billed until the
learner has spoken and nothing the model holds can be read out before an attempt.

A guard sits between the model and the voice, as a prompt alone is no promise:
- Explaining an approach: a sentence sharing a run of words with the drill's reference is dropped.
- Flashcards: a sentence sharing a run with the back is held until the reply ends, and spoken only
  if the reply graded an attempt. A nudge or a chat about the card stays unsaid.
This catches quoted text. A paraphrase gets through, and only the prompt forbids that.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import aclosing
from dataclasses import dataclass
from typing import Any, Literal

import anthropic

from librarian.log_config import get_logger

from .config import VoiceConfig
from .drill_prompt import clean_inline, to_speech
from .grades import build_event, parse_grade
from .limits import EndReason, SessionLimits
from .policy import Card, SessionPlan
from .prompts import system_prompt
from .tools import RECORD_GRADE, run_read_only, tools_for

log = get_logger(__name__)

UngradedReason = Literal[
    "no_grade", "malformed", "refusal", "cut_off", "llm_error", "write_failed", "interrupted"
]
FinishReason = EndReason | Literal["deck_end"]

MAX_TOOL_ROUNDS = 2
LEAK_RUN_TOKENS = 6
FILLER = "One moment."
NOTED = "Noted."
LEAK_REPLACEMENT = "I'll leave that part for you to work out."
TRY_FIRST = "Have a go at it first."
REFUSED = "I can't help with that one."
UNREACHABLE = "I couldn't reach the model, so this one isn't graded."
CUT_OFF = "That ran long, so this one isn't graded."
DECK_DONE = "That was the last card."

_SENTENCE_END_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+")
_TOKEN_RE = re.compile(r"\w+")


@dataclass(frozen=True)
class Say:
    text: str


@dataclass(frozen=True)
class Graded:
    score: float


@dataclass(frozen=True)
class Ungraded:
    reason: UngradedReason


@dataclass(frozen=True)
class Finished:
    reason: FinishReason


Event = Say | Graded | Ungraded | Finished
GradeWriter = Callable[[Any], Awaitable[bool]]


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.casefold())


class LeakGuard:
    """Whether a sentence quotes a run of words from a reference. Short references, such as a
    one-word flashcard back, use their whole length as the run."""

    def __init__(self, reference: str, run: int = LEAK_RUN_TOKENS) -> None:
        tokens = _tokens(reference)
        self._run = min(run, len(tokens))
        self._runs = (
            {tuple(tokens[i : i + self._run]) for i in range(len(tokens) - self._run + 1)}
            if self._run
            else set()
        )

    def leaks(self, sentence: str) -> bool:
        if not self._run:
            return False
        tokens = _tokens(sentence)
        return any(
            tuple(tokens[i : i + self._run]) in self._runs
            for i in range(len(tokens) - self._run + 1)
        )


class Conversation:
    def __init__(
        self,
        plan: SessionPlan,
        client: anthropic.AsyncAnthropic,
        cfg: VoiceConfig,
        limits: SessionLimits,
        write_grade: GradeWriter,
    ) -> None:
        self._plan = plan
        self._client = client
        self._cfg = cfg
        self._limits = limits
        self._write_grade = write_grade
        self._system = system_prompt(plan)
        self._tools = tools_for(plan.mode)
        self._messages: list[dict[str, Any]] = []
        self._pending_results: list[dict[str, Any]] = []
        self._card_index = 0
        self._guard = LeakGuard(plan.reference) if plan.mode == "approach" else None

    @property
    def _card(self) -> Card | None:
        cards = self._plan.cards
        return cards[self._card_index] if self._card_index < len(cards) else None

    def opening(self) -> str:
        """Said before any model call, so a silent session costs nothing."""
        if self._plan.mode == "flashcard":
            front = to_speech(self._plan.cards[0].front)
            return f"First card. {front}"
        if self._plan.mode == "approach":
            return f"Explain your approach. {self._plan.prompt}"
        return (
            f"Interview practice on {clean_inline(self._plan.title)}. "
            "Say ready when you want the first question."
        )

    def _user_message(self, text: str) -> dict[str, Any]:
        spoken = f"<spoken>{text}</spoken>"
        card = self._card
        if self._plan.mode == "flashcard" and card is not None:
            spoken = (
                f"<card>\n<front>{card.front}</front>\n<back>{card.back}</back>\n</card>\n{spoken}"
            )
        content = [*self._pending_results, {"type": "text", "text": spoken}]
        self._pending_results = []
        return {"role": "user", "content": content}

    async def _stream_round(self) -> AsyncGenerator[str | Any, None]:
        """Yields each spoken sentence as it completes, then the final message."""
        kwargs: dict[str, Any] = {
            "model": self._cfg.model,
            "max_tokens": self._cfg.max_tokens,
            "system": self._system,
            "tools": self._tools,
            "messages": self._messages,
        }
        if self._cfg.effort:
            kwargs["output_config"] = {"effort": self._cfg.effort}
        buffer = ""
        async with self._client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    buffer += event.delta.text
                    while (m := _SENTENCE_END_RE.search(buffer)) is not None:
                        yield buffer[: m.end()].strip()
                        buffer = buffer[m.end() :]
            final = await stream.get_final_message()
        if buffer.strip():
            yield buffer.strip()
        yield final

    async def _run_tools(self, uses: list[Any]) -> tuple[list[dict[str, Any]], float | None, bool]:
        """Results for every call, the grade if a valid one came, and whether one was malformed.
        A barge-in during a tool still owes the model a result for each call, or the next request
        would be rejected."""
        results: list[dict[str, Any]] = []
        score: float | None = None
        malformed = False
        try:
            for block in uses:
                if block.name == RECORD_GRADE:
                    parsed = parse_grade(block.input)
                    if parsed is None or score is not None:
                        malformed = malformed or parsed is None
                        results.append(_result(block.id, "Not recorded.", is_error=True))
                    else:
                        score = parsed
                        results.append(_result(block.id, "Recorded."))
                else:
                    outcome = await run_read_only(
                        block.name, block.input, self._plan.mode, self._plan.user_id
                    )
                    results.append(_result(block.id, outcome.text, is_error=outcome.is_error))
        except asyncio.CancelledError:
            done = {r["tool_use_id"] for r in results}
            self._pending_results = results + [
                _result(b.id, "Interrupted.", is_error=True) for b in uses if b.id not in done
            ]
            raise
        return results, score, malformed

    async def respond(self, text: str) -> AsyncGenerator[Event, None]:
        """One user turn, to the end of the reply. Cancel it to interrupt."""
        if (over := self._limits.over_budget()) is not None:
            yield Finished(over)
            return
        self._limits.add_turn()
        self._messages.append(self._user_message(text))
        card = self._card
        back_guard = (
            LeakGuard(card.back) if self._plan.mode == "flashcard" and card is not None else None
        )
        spoke = False
        filler_said = False
        replaced = False
        held: list[str] = []
        score: float | None = None
        malformed = False
        ungraded: UngradedReason | None = None

        for round_no in range(MAX_TOOL_ROUNDS + 1):
            try:
                final = None
                async with asyncio.timeout(self._cfg.llm_timeout_s):
                    # aclosing: a cancel while the caller holds a sentence must still end the
                    # stream, or the billed call runs on until something collects the generator.
                    async with aclosing(self._stream_round()) as items:
                        async for item in items:
                            if not isinstance(item, str):
                                final = item
                                continue
                            sentence = clean_inline(item)
                            if not sentence:
                                continue
                            if held or (back_guard is not None and back_guard.leaks(sentence)):
                                held.append(sentence)
                            elif self._guard is not None and self._guard.leaks(sentence):
                                if not replaced:
                                    replaced = True
                                    spoke = True
                                    yield Say(LEAK_REPLACEMENT)
                            else:
                                spoke = True
                                yield Say(sentence)
            except (anthropic.APIError, TimeoutError) as e:
                log.warning("voice.llm.failed", error=type(e).__name__, mode=self._plan.mode)
                yield Say(UNREACHABLE)
                yield Ungraded("llm_error")
                return
            if final is None:
                yield Ungraded("llm_error")
                return
            usage = getattr(final, "usage", None)
            self._limits.add_tokens(
                getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)
            )
            if final.stop_reason == "refusal":
                yield Say(REFUSED)
                ungraded = "refusal"
                break
            if final.stop_reason == "max_tokens":
                # An unfinished tool call can't be replayed, so nothing is recorded or run.
                yield Say(CUT_OFF)
                ungraded = "cut_off"
                break
            self._messages.append({"role": "assistant", "content": final.content})
            uses = [b for b in final.content if b.type == "tool_use"]
            if not uses:
                break
            read_only = [b for b in uses if b.name != RECORD_GRADE]
            if read_only and not filler_said and not spoke and round_no < MAX_TOOL_ROUNDS:
                filler_said = True
                spoke = True
                yield Say(FILLER)  # The tool runs while this plays, so the audio doesn't stall.
            results, round_score, round_malformed = await self._run_tools(uses)
            if score is None:
                score = round_score
            malformed = malformed or round_malformed
            if not read_only or round_no == MAX_TOOL_ROUNDS:
                # Nothing more is needed from the model this turn. The results go first in the
                # next user message, which saves a second billed call.
                self._pending_results = results
                break
            self._messages.append({"role": "user", "content": results})

        async for event in self._close_turn(score, malformed, ungraded, spoke, held, card):
            yield event

    async def _close_turn(
        self,
        score: float | None,
        malformed: bool,
        ungraded: UngradedReason | None,
        spoke: bool,
        held: list[str],
        card: Card | None,
    ) -> AsyncGenerator[Event, None]:
        graded = False
        if ungraded is None and score is not None:
            written = await self._write_grade(build_event(self._plan, score, card))
            graded = written
            if not written:
                ungraded = "write_failed"
        if graded:
            for sentence in held:
                spoke = True
                yield Say(sentence)
            yield Graded(score)  # type: ignore[arg-type]
        else:
            if held:
                spoke = True
                yield Say(TRY_FIRST)
            yield Ungraded(ungraded or ("malformed" if malformed else "no_grade"))
        if graded and not spoke:
            yield Say(NOTED)
        if graded and self._plan.mode == "flashcard":
            self._card_index += 1
            if self._card is None:
                yield Say(DECK_DONE)
                yield Finished("deck_end")
                return
            yield Say(f"Next card. {to_speech(self._card.front)}")
        if (over := self._limits.over_budget()) is not None:
            yield Finished(over)


def _result(tool_use_id: str, content: str, *, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        result["is_error"] = True
    return result
