"""The audit log: one row per security-relevant event. Never raises: a failed write is logged."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import Engine, select
from sqlalchemy.exc import SQLAlchemyError

from librarian.db import tables
from librarian.log_config import get_logger

log = get_logger(__name__)

# The actions written. `target` is an email, a key id or a release, never a secret.
ACTIONS = frozenset(
    {
        "login",
        "login_refused",
        "logout",
        "key_create",
        "key_revoke",
        "invite",
        "promote",
        "admin_reload",
    }
)


@dataclass(frozen=True)
class Event:
    ts: datetime
    user_id: str | None
    email: str | None
    action: str
    target: str | None


def record(
    engine: Engine, action: str, *, user_id: str | None = None, target: str | None = None
) -> None:
    if action not in ACTIONS:
        raise ValueError(f"unknown audit action {action!r}")
    try:
        with engine.begin() as conn:
            conn.execute(
                tables.audit.insert().values(
                    ts=datetime.now(UTC), user_id=user_id, action=action, target=target
                )
            )
    except SQLAlchemyError as e:
        log.error("audit.write_failed", action=action, error=str(e))


def recent(engine: Engine, limit: int = 100) -> list[Event]:
    """The latest events, newest first, with the acting user's email where there is one."""
    a, u = tables.audit, tables.users
    stmt = (
        select(a.c.ts, a.c.user_id, u.c.email, a.c.action, a.c.target)
        .outerjoin(u, u.c.id == a.c.user_id)
        .order_by(a.c.ts.desc(), a.c.id.desc())
        .limit(limit)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).all()
    return [Event(r.ts, r.user_id, r.email, r.action, r.target) for r in rows]
