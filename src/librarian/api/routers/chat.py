"""POST /api/chat/stream: the chat agent's events as server-sent events."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Literal, Self

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.exc import SQLAlchemyError

from librarian import experiments, feedback
from librarian.agent import run_agent_stream
from librarian.api.routers.release import served_release
from librarian.api.security import SignedIn, chat_limiter
from librarian.config import get_release, get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger
from librarian.observability import set_variant
from librarian.pricing import TokenUsage

log = get_logger(__name__)

router = APIRouter()

# Per-message bound at the boundary; the agent applies the tighter count/total-chars
# trim (agent.MAX_HISTORY_TURNS / MAX_HISTORY_CHARS). This cap only rejects payloads
# no real chat produces. The list cap is loose for the same reason — the client may
# send its whole transcript and let the agent keep the tail.
_MAX_MESSAGE_CHARS = 32_000
_MAX_HISTORY_ITEMS = 200


class ChatTurn(BaseModel):
    """One prior text-only turn. Tool blocks never cross the wire."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=_MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default_factory=list, max_length=_MAX_HISTORY_ITEMS)

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
    settings = get_settings()
    if not settings.chat_enabled:
        raise HTTPException(status_code=404, detail="chat is disabled")
    # 429 before any model call
    chat_limiter.admit(settings, user_id=user.id, user_cap=not user.is_admin)
    history = [t.model_dump() for t in req.history]

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
        )
        async for event in stream:
            if event["type"] == "grounding" and not event["cited"]:
                await asyncio.to_thread(note_unanswered)
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
