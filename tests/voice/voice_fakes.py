"""A scripted stand-in for the Anthropic client, and a small catalog of invented lessons."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from librarian.courses.loader import Catalog, LessonRec


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def grade_call(score: object = 0.8, tool_id: str = "g1") -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=tool_id, name="record_grade", input={"score": score})


def tool_call(name: str, args: object, tool_id: str = "t1") -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=args)


@dataclass
class Reply:
    """One model round. `chunks` stream as text deltas, `blocks` are the extra final content."""

    chunks: list[str] = field(default_factory=list)
    blocks: list[SimpleNamespace] = field(default_factory=list)
    stop_reason: str = "end_turn"
    error: Exception | None = None
    hang_after_chunks: bool = False
    tokens: int = 10


class FakeStream:
    def __init__(self, reply: Reply, client: FakeClient) -> None:
        self._reply = reply
        self._client = client

    async def __aenter__(self) -> FakeStream:
        self._client.opened += 1
        return self

    async def __aexit__(self, *_exc: object) -> None:
        self._client.closed += 1

    def __aiter__(self) -> AsyncIterator[SimpleNamespace]:
        return self._events()

    async def _events(self) -> AsyncIterator[SimpleNamespace]:
        for chunk in self._reply.chunks:
            yield SimpleNamespace(
                type="content_block_delta", delta=SimpleNamespace(type="text_delta", text=chunk)
            )
        if self._reply.error is not None:
            raise self._reply.error
        if self._reply.hang_after_chunks:
            self._client.hanging.set()
            await asyncio.Event().wait()

    async def get_final_message(self) -> SimpleNamespace:
        reply = self._reply
        content = [text_block("".join(reply.chunks)), *reply.blocks]
        return SimpleNamespace(
            stop_reason=reply.stop_reason,
            content=content,
            usage=SimpleNamespace(input_tokens=reply.tokens, output_tokens=0),
        )


class FakeClient:
    """Replays `replies` in order and records each request. Runs out loudly."""

    def __init__(self, *replies: Reply) -> None:
        self._replies = list(replies)
        self.requests: list[dict[str, Any]] = []
        self.opened = 0
        self.closed = 0
        self.hanging = asyncio.Event()
        self.messages = SimpleNamespace(stream=self._stream)

    def _stream(self, **kwargs: object) -> FakeStream:
        # The list is the one the conversation goes on appending to, so copy it as it stands.
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})  # type: ignore[call-overload]
        return FakeStream(self._replies.pop(0), self)


def lesson(lesson_id: str, *, kind: str = "reading", body: str = "Some prose.") -> LessonRec:
    return LessonRec(
        id=lesson_id,
        course=lesson_id.split("/")[0],
        module="m",
        title=lesson_id.rsplit("/", 1)[-1],
        summary="",
        order=1,
        section="",
        kind=kind,
        source="",
        body=body,
    )


DRILL_BODY = """---
title: Invented Drill
---

## Prompt

Count how many lanterns are lit in a row of lanterns.

## Hints

Walk the row once from the left.

## Solution

<details><summary>Solution</summary>

Keep a running tally of lit lanterns and return the tally at the very end.

</details>
"""
REFERENCE_QUOTE = "Keep a running tally of lit lanterns and return the tally"
UNRECOGNISED_DRILL_BODY = "## Prompt\n\nCount the lanterns.\n\n## Afterwards\n\nThe tally.\n"

DECK_CARDS = [
    {"id": "c1", "front": "What lights a lantern?", "back": "A small flame on the wick."},
    {"id": "c2", "front": "What puts one out?", "back": "A puff of air.", "lesson": "maths/m/a"},
]


def make_catalog() -> Catalog:
    lessons = [
        lesson("maths/m/a"),
        lesson("maths/m/drill", kind="drill", body=DRILL_BODY),
        lesson("maths/m/odd-drill", kind="drill", body=UNRECOGNISED_DRILL_BODY),
        lesson("interviewing/m/tell-me", body="# Tell me\n\nTalk about a lantern you built.\n"),
        lesson("interviewing/m/drill", kind="drill", body=DRILL_BODY),
    ]
    decks = {
        "maths/m": {"id": "maths/m", "title": "Lanterns", "course": "maths", "cards": DECK_CARDS},
        "maths/empty": {"id": "maths/empty", "title": "Empty", "course": "maths", "cards": []},
        "interviewing/m": {
            "id": "interviewing/m",
            "title": "Interview cards",
            "course": "interviewing",
            "cards": DECK_CARDS,
        },
        "maths/borrowed": {
            "id": "maths/borrowed",
            "title": "Borrowed",
            "course": "maths",
            "cards": [{"front": "Q?", "back": "A.", "lesson": "interviewing/m/tell-me"}],
        },
    }
    return Catalog(
        courses=[],
        lessons={rec.id: rec for rec in lessons},
        wiki={},
        by_concept={},
        decks=decks,
    )
