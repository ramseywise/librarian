"""POST /api/chat/stream: the chat agent's events as server-sent events.

POST /api/chat/citations/check: whether the pages an earlier answer cited have changed since.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Literal, Self

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.exc import SQLAlchemyError

from librarian import experiments, feedback
from librarian.agent import run_agent_stream
from librarian.api import prom
from librarian.api.routers.release import served_release
from librarian.api.security import SignedIn, chat_limiter
from librarian.config import get_release, get_settings
from librarian.courses import catalog as courses
from librarian.db import get_engine
from librarian.log_config import get_logger
from librarian.observability import set_variant
from librarian.pricing import TokenUsage
from librarian.retrieval import citations

log = get_logger(__name__)

router = APIRouter()

# Per-message bound at the boundary; the agent applies the tighter count/total-chars
# trim (agent.MAX_HISTORY_TURNS / MAX_HISTORY_CHARS). This cap only rejects payloads
# no real chat produces. The list cap is loose for the same reason — the client may
# send its whole transcript and let the agent keep the tail.
_MAX_MESSAGE_CHARS = 32_000
_MAX_HISTORY_ITEMS = 200
# Citations checked per request: far more than one answer cites.
_MAX_CITATIONS = 50


class ChatTurn(BaseModel):
    """One prior text-only turn. Tool blocks never cross the wire."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)


class LabContext(BaseModel):
    """The lab open beside the chat: the editor's files and the last run. The server builds the
    agent's brief from it (the diff against the lab's own files, its notes), never the client."""

    id: str = Field(min_length=1, max_length=400)
    files: dict[str, str] = Field(default_factory=dict, max_length=30)
    output: str = Field(default="", max_length=_MAX_MESSAGE_CHARS)
    exit: int | None = None


class StudyContext(BaseModel):
    """What the user is studying beside the chat, by catalog id only: a flashcard (`deck`, `card`),
    a quiz question (`quiz`, `question`) or a lesson. The server builds the brief from the catalog.
    `revealed` says the user has answered the question, so its answer may go in the brief."""

    deck: str | None = Field(default=None, max_length=400)
    card: str | None = Field(default=None, max_length=400)
    quiz: str | None = Field(default=None, max_length=400)
    question: str | None = Field(default=None, max_length=400)
    lesson: str | None = Field(default=None, max_length=400)
    revealed: bool = False


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default_factory=list, max_length=_MAX_HISTORY_ITEMS)
    lab: LabContext | None = None
    study: StudyContext | None = None

    @model_validator(mode="after")
    def _alternating(self) -> Self:
        # The new query is appended as the next user turn, so history must alternate
        # user/assistant and end on assistant. Reject rather than repair: a malformed
        # transcript means a client bug, and silently merging turns would hide it.
        for i, turn in enumerate(self.history):
            expected = "user" if i % 2 == 0 else "assistant"
            if turn.role != expected:
                raise ValueError(f"history[{i}] must have role {expected!r}")
        if self.history and self.history[-1].role != "assistant":
            raise ValueError("history must end with an assistant turn")
        return self


@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, user: SignedIn, request: Request) -> StreamingResponse:
    request_started = time.perf_counter()
    settings = get_settings()
    if not settings.chat_enabled:
        raise HTTPException(status_code=404, detail="chat is disabled")
    # 429 before any model call
    chat_limiter.admit(settings, user_id=user.id, user_cap=not user.is_admin)
    history = [t.model_dump() for t in req.history]
    brief = None
    if req.lab is not None:
        if any(len(text) > 200_000 for text in req.lab.files.values()):
            raise HTTPException(status_code=413, detail="lab file too large")
        brief = await asyncio.to_thread(
            courses.lab_brief, req.lab.id, req.lab.files, req.lab.output, req.lab.exit
        )
        if brief is None:
            raise HTTPException(status_code=404, detail="lab not found")
    study = None
    if req.study is not None:
        s = req.study
        study = await asyncio.to_thread(
            courses.study_brief,
            deck=s.deck,
            card=s.card,
            quiz_id=s.quiz,
            question=s.question,
            lesson=s.lesson,
            revealed=s.revealed,
        )
        # Unknown and private look the same: private course text never reaches the chat model.
        if study is None:
            raise HTTPException(status_code=404, detail="study item not found")

    def on_usage(usage: TokenUsage) -> None:
        chat_limiter.record_usage(settings, usage, user.id)

    variant = experiments.resolve(
        settings,
        user.id,
        is_admin=user.is_admin,
        override=request.headers.get(experiments.VARIANT_HEADER),
    )

    def note_unanswered() -> None:
        """A per-user `unanswered` row for a question that got no cited page. Never raises."""
        try:
            feedback.record(
                get_engine(),
                user_id=user.id,
                kind="unanswered",
                target=req.query,
                release=served_release() or get_release(),
                experiment=variant,
            )
        except (SQLAlchemyError, feedback.FeedbackError) as e:
            log.warning("feedback.unanswered_failed", error=str(e))

    async def generate() -> AsyncIterator[str]:
        # The variant applies to this request only: the hybrid candidate path reads it through
        # observability.experiment(), and worker threads inherit it.
        set_variant(variant)
        stream = run_agent_stream(
            req.query,
            history,
            on_usage=on_usage,
            user_id=None if settings.open_mode else user.id,
            variant=variant,
            release=served_release() or get_release(),
            brief=brief,
            study=study,
        )
        first_token = True
        async for event in stream:
            if first_token and event["type"] == "token":
                first_token = False
                prom.observe_first_token(request_started)
            if event["type"] == "grounding" and not event["cited"]:
                await asyncio.to_thread(note_unanswered)
            yield f"data: {json.dumps(event)}\n\n"
        if first_token:
            prom.note_no_token()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class CitedPage(BaseModel):
    """One citation as the `grounding` event gave it: the page id and its content hash then."""

    id: str = Field(max_length=200, pattern=f"^{citations.PAGE_ID_PATTERN}$")
    hash: str = Field(min_length=1, max_length=64)


class CitationCheckRequest(BaseModel):
    citations: list[CitedPage] = Field(max_length=_MAX_CITATIONS)


@router.post("/api/chat/citations/check")
async def check_citations(req: CitationCheckRequest, user: SignedIn) -> dict[str, list[dict]]:
    """Per citation: `current`, `changed` (with `now` when the page was renamed) or `missing`.

    A private page is `missing`, like one that never existed.
    """
    if not get_settings().chat_enabled:
        raise HTTPException(status_code=404, detail="chat is disabled")

    def run() -> list[dict]:
        return [dict(citations.check(c.id, c.hash)) for c in req.citations]

    return {"citations": await asyncio.to_thread(run)}
