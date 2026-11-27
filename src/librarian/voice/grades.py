"""Contract 6: turn the model's `record_grade` call into a `voice_grade` event.

A score must be a real number from 0 to 1 in a call holding nothing else. Anything missing or
malformed is no grade at all, never a zero: a bad tool call says nothing about the learner.
"""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from librarian import accounts
from librarian.config import get_settings
from librarian.courses import learning
from librarian.db import get_engine
from librarian.log_config import get_logger

from .policy import Card, SessionPlan


def parse_grade(raw: object) -> float | None:
    if not isinstance(raw, dict) or set(raw) != {"score"}:
        return None
    score = raw["score"]
    if isinstance(score, bool) or not isinstance(score, int | float):
        return None
    if not math.isfinite(score) or not 0 <= score <= 1:
        return None
    return float(score)


def build_event(plan: SessionPlan, score: float, card: Card | None) -> learning.EventIn:
    """A card's grade links to the card's lesson when it has one. A lesson-less deck's stays in
    the log and counts for nothing. Holds a number and ids, and no words."""
    lesson = card.lesson if card is not None else plan.lesson
    return learning.EventIn(
        kind="voice_grade", lesson=lesson, deck=plan.deck, score=score, mode=plan.mode
    )


log = get_logger(__name__)


def _learner(user_id: str | None) -> str:
    """The user a grade belongs to: the caller, else the owner (this process serves the owner)."""
    return user_id or accounts.ensure_owner(get_engine(), get_settings().owner_email).id


def grade_writer(user_id: str | None) -> Callable[[learning.EventIn], Awaitable[bool]]:
    """A writer that records each grade for `user_id` (None: the owner, as in open mode)."""

    async def emit_grade(event: learning.EventIn) -> bool:
        """Off the event loop: the catalog can block on its first build and the store locks."""
        try:
            await asyncio.to_thread(learning.record_event, _learner(user_id), event)
        except (OSError, ValidationError, learning.LearningError, SQLAlchemyError) as exc:
            log.warning("voice.grade.write_failed", error=type(exc).__name__)
            return False
        return True

    return emit_grade
