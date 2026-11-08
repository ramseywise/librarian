"""Per-user lesson progress: which lessons a user has opened and which they have finished.

One row per (user, lesson) in the `progress` table, `state` "opened" or "done". Opening a finished
lesson again moves its `updated_at` but leaves it done, so "continue where you left off" is the
most recently touched lesson and module progress counts only what was finished. Unknown lesson ids
are refused by the caller (`known`), so the table only holds lessons the catalog serves.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import case, select
from sqlalchemy.exc import SQLAlchemyError

from librarian.accounts import User
from librarian.courses import catalog
from librarian.db import get_engine, tables, upsert
from librarian.log_config import get_logger

log = get_logger(__name__)

State = Literal["opened", "done"]
STATES: tuple[State, ...] = ("opened", "done")


def known(lesson_id: str) -> bool:
    return lesson_id in catalog.catalog().lessons


def mark(user_id: str, lesson_id: str, state: State) -> bool:
    """Record that `user_id` opened or finished `lesson_id`. False when the store cannot be written."""
    if state not in STATES:
        raise ValueError(f"{state!r} is not a progress state")
    t = tables.progress
    now = datetime.now(UTC)
    try:
        engine = get_engine()
        stmt = upsert(engine, t).values(
            user_id=user_id, lesson_id=lesson_id, state=state, updated_at=now
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "lesson_id"],
            set_={
                "state": case((t.c.state == "done", "done"), else_=stmt.excluded.state),
                "updated_at": now,
            },
        )
        with engine.begin() as conn:
            conn.execute(stmt)
    except (SQLAlchemyError, OSError) as e:
        log.warning("progress.write_failed", error=str(e))
        return False
    return True


def lessons(user_id: str) -> dict[str, tuple[str, datetime]]:
    """lesson id -> (state, updated_at) for `user_id`. {} when nothing is stored or readable."""
    t = tables.progress
    stmt = select(t.c.lesson_id, t.c.state, t.c.updated_at).where(t.c.user_id == user_id)
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(stmt).all()
    except (SQLAlchemyError, OSError) as e:
        log.warning("progress.read_failed", error=str(e))
        return {}
    return {
        r.lesson_id: (
            r.state,
            r.updated_at if r.updated_at.tzinfo else r.updated_at.replace(tzinfo=UTC),
        )
        for r in rows
    }


def summary(user: User) -> dict[str, Any]:
    """`user`'s progress: each lesson's state, done/total per module, and the last lesson touched.

    Only lessons the catalog serves are counted; a row for a lesson since removed is ignored.
    """
    cat = catalog.catalog()
    rows = {i: v for i, v in lessons(user.id).items() if i in cat.lessons}
    totals: dict[str, dict[str, int]] = {}
    for r in cat.lessons.values():
        counts = totals.setdefault(f"{r.course}/{r.module}", {"done": 0, "total": 0})
        counts["total"] += 1
        if rows.get(r.id, ("",))[0] == "done":
            counts["done"] += 1
    last = max(rows.items(), key=lambda kv: kv[1][1], default=None)
    return {
        "lessons": {i: {"state": s, "updatedAt": ts.isoformat()} for i, (s, ts) in rows.items()},
        "modules": [{"module": m, **c} for m, c in totals.items() if c["done"]],
        "done": sum(1 for s, _ in rows.values() if s == "done"),
        "last": (
            catalog.outline(cat.lessons[last[0]])
            | {"course": cat.lessons[last[0]].course, "state": last[1][0]}
            if last
            else None
        ),
    }
