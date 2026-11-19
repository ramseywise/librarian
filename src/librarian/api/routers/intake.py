"""The intake and the tiers it leaves, for the signed-in caller only.

GET  /api/intake              where the caller's intake stands, and the block waiting for answers
POST /api/intake/profile      open a sitting with a profile (409 once it has answers, or too soon)
POST /api/intake/answers      answer the waiting block; returns the next state
GET  /api/placement           the caller's tier per subject, and the last sitting's questions
PUT  /api/placement/{subject} choose a tier for one subject

Nothing sent before a sitting is complete carries a key or an explanation.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from librarian.accounts import User
from librarian.agent.loop import _get_client
from librarian.agent.support import _usage_of
from librarian.api.security import SignedIn, chat_limiter
from librarian.config import Settings, get_settings
from librarian.courses import intake
from librarian.log_config import get_logger

log = get_logger(__name__)

router = APIRouter()

INTERPRET_MAX_TOKENS = 300


class Profile(BaseModel):
    role: str
    goal: str
    subjects: list[str] = Field(min_length=1, max_length=20)
    experience: dict[str, str]
    untested: list[str] = Field(default_factory=list, max_length=20)
    hoursPerWeek: int | None = None  # noqa: N815 - the JSON field name
    experienceText: str = Field(default="", max_length=intake.MAX_FREE_TEXT)  # noqa: N815
    interestsText: str = Field(default="", max_length=intake.MAX_FREE_TEXT)  # noqa: N815


class Answer(BaseModel):
    key: str = Field(min_length=1, max_length=160)
    choice: str | None = None  # None is "I don't know"
    ms: int | None = Field(default=None, ge=0, le=3_600_000)


class Answers(BaseModel):
    answers: list[Answer] = Field(min_length=1, max_length=40)


class Tier(BaseModel):
    tier: str


async def _interpret(profile: dict[str, Any], settings: Settings, user: User) -> dict[str, Any]:
    """Map the two free-text answers to modules with one model call (BILLABLE). Any reason it
    cannot be done (no text, chat off, budget spent, no key, a failed or unreadable reply) gives
    the uninterpreted fallback: the intake never waits on the model. The text is never logged."""
    if not (profile["experienceText"] or profile["interestsText"]) or not settings.chat_enabled:
        return intake.NO_INTERESTS
    modules = await asyncio.to_thread(intake.interest_modules, settings)
    if not modules:
        return intake.NO_INTERESTS
    try:
        chat_limiter.admit(settings, user_id=user.id, user_cap=not user.is_admin)
        resp = await asyncio.wait_for(
            _get_client().messages.create(
                model=settings.chat_model,
                max_tokens=INTERPRET_MAX_TOKENS,
                system=intake.INTERESTS_SYSTEM,
                messages=[{"role": "user", "content": intake.interests_prompt(profile, modules)}],
            ),
            timeout=settings.intake_interpret_timeout_s,
        )
    except HTTPException as e:
        log.info("intake.interpret_skipped", status=e.status_code)
        return intake.NO_INTERESTS
    except Exception as e:
        log.warning("intake.interpret_failed", error=type(e).__name__)
        return intake.NO_INTERESTS
    chat_limiter.record_usage(settings, _usage_of(resp), user.id)
    text = "".join(b.text for b in resp.content if b.type == "text")
    return intake.parse_interests(text, modules) or intake.NO_INTERESTS


@router.get("/api/intake")
def get_intake(user: SignedIn) -> dict[str, Any]:
    return intake.state(user.id)


@router.post("/api/intake/profile")
async def post_profile(body: Profile, user: SignedIn) -> dict[str, Any]:
    settings = get_settings()
    raw = body.model_dump()
    try:
        # Checked before the model call, so a refused profile costs nothing.
        profile = await asyncio.to_thread(intake.check_profile, raw, settings)
        await asyncio.to_thread(intake.check_can_start, user.id)
        interests = await _interpret(profile, settings, user)
        await asyncio.to_thread(intake.start, user.id, raw, interests)
    except intake.IntakeConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except intake.IntakeError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return await asyncio.to_thread(intake.state, user.id)


@router.post("/api/intake/answers")
def post_answers(body: Answers, user: SignedIn) -> dict[str, Any]:
    try:
        intake.answer(user.id, [a.model_dump() for a in body.answers])
    except intake.IntakeConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except intake.IntakeError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return intake.state(user.id)


@router.get("/api/placement")
def get_placement(user: SignedIn) -> dict[str, Any]:
    return {"placements": intake.placements(user.id), "review": intake.review(user.id)}


@router.put("/api/placement/{subject}")
def put_placement(subject: str, body: Tier, user: SignedIn) -> dict[str, Any]:
    try:
        intake.set_tier(user.id, subject, body.tier)
    except LookupError as e:
        raise HTTPException(status_code=404, detail="No such subject.") from e
    except intake.IntakeError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return {"placements": intake.placements(user.id)}
