"""Write, list, delete and prune feedback rows."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, and_, select
from sqlalchemy import delete as sql_delete

from librarian.db import tables
from librarian.log_config import get_logger

log = get_logger(__name__)

KINDS = ("answer", "page", "lesson", "unanswered")
MAX_BODY = 2000
MAX_TARGET = 300
# One row per user and target for these kinds: rating an answer again replaces the first rating,
# and asking the same unanswered question twice is still one person's signal.
_REPLACING = ("answer", "unanswered")


class FeedbackError(ValueError):
    """The request is not a valid feedback row."""


@dataclass(frozen=True)
class Feedback:
    id: str
    ts: datetime
    kind: str
    target: str
    rating: int | None
    body: str | None
    release: str | None
    experiment: str | None


def _row(r: object) -> Feedback:
    m = getattr(r, "_mapping")  # noqa: B009  (sqlalchemy Row, kept untyped for the dialects)
    return Feedback(
        id=m["id"],
        ts=m["ts"],
        kind=m["kind"],
        target=m["target"],
        rating=m["rating"],
        body=m["body"],
        release=m["release"],
        experiment=m["experiment"],
    )


def record(
    engine: Engine,
    *,
    user_id: str,
    kind: str,
    target: str,
    rating: int | None = None,
    body: str | None = None,
    release: str | None = None,
    experiment: str | None = None,
) -> str:
    """Store one signal and return its id. Raises `FeedbackError` when it is not valid.

    `rating` (1 or -1) belongs to answers only. `body` is trimmed (empty becomes None) and capped
    at `MAX_BODY`. The target of an `unanswered` row is cut to `MAX_TARGET` characters; any other
    kind refuses a longer one. For `answer` and `unanswered` the user's earlier row for the same
    target is replaced, in the same transaction.
    """
    if kind not in KINDS:
        raise FeedbackError(f"kind must be one of {', '.join(KINDS)}")
    target = target.strip()
    if kind == "unanswered":
        target = target[:MAX_TARGET].strip()
    if not target or len(target) > MAX_TARGET:
        raise FeedbackError(f"target must be 1 to {MAX_TARGET} characters")
    if kind == "answer":
        if rating not in (1, -1):
            raise FeedbackError("an answer needs rating 1 or -1")
    elif rating is not None:
        raise FeedbackError("rating is only for answers")
    text = (body or "").strip() or None
    if text is not None and len(text) > MAX_BODY:
        raise FeedbackError(f"body is at most {MAX_BODY} characters")
    t = tables.feedback
    row_id = uuid.uuid4().hex
    with engine.begin() as conn:
        if kind in _REPLACING:
            conn.execute(
                sql_delete(t).where(
                    and_(t.c.user_id == user_id, t.c.kind == kind, t.c.target == target)
                )
            )
        conn.execute(
            t.insert().values(
                id=row_id,
                user_id=user_id,
                ts=datetime.now(UTC),
                kind=kind,
                target=target,
                rating=rating,
                body=text,
                release=release or None,
                experiment=experiment or None,
            )
        )
    return row_id


def mine(engine: Engine, user_id: str, limit: int = 200) -> list[Feedback]:
    """The user's own rows, newest first (at most 200)."""
    t = tables.feedback
    stmt = (
        select(t)
        .where(t.c.user_id == user_id)
        .order_by(t.c.ts.desc(), t.c.id)
        .limit(max(1, min(limit, 200)))
    )
    with engine.connect() as conn:
        return [_row(r) for r in conn.execute(stmt)]


def delete(engine: Engine, user_id: str, feedback_id: str) -> bool:
    """Delete one of the user's own rows. False when there is no such row of theirs."""
    t = tables.feedback
    with engine.begin() as conn:
        result = conn.execute(
            sql_delete(t).where(and_(t.c.id == feedback_id, t.c.user_id == user_id))
        )
    return result.rowcount > 0


def prune(engine: Engine, days: int, *, now: datetime | None = None) -> int:
    """Delete rows older than `days` days; returns how many."""
    cutoff = (now or datetime.now(UTC)) - timedelta(days=days)
    with engine.begin() as conn:
        result = conn.execute(sql_delete(tables.feedback).where(tables.feedback.c.ts < cutoff))
    log.info("feedback.pruned", rows=result.rowcount, days=days)
    return result.rowcount


def since(engine: Engine, start: datetime) -> list[Feedback]:
    """Every row from `start` on, oldest first. For the export: carries no user id."""
    t = tables.feedback
    with engine.connect() as conn:
        return [
            _row(r) for r in conn.execute(select(t).where(t.c.ts >= start).order_by(t.c.ts, t.c.id))
        ]
