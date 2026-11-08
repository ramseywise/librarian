"""Browser sessions: a random cookie value, stored as its sha256.

Like API keys, the value is 256 random bits, so a fast hash is enough. A session ends at its
absolute expiry (`days` from creation, never extended) or after `idle_days` without a request,
whichever comes first. Dead rows are removed when a new session is made. A user who is disabled
has no live session. A role change or a disable ends every session of that user
(`revoke_user_sessions`, called by `set_role` and `disable_user`).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import ColumnElement, Engine, delete, func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError

from librarian.accounts.users import User, user_from_row
from librarian.config import get_settings
from librarian.db import tables
from librarian.log_config import get_logger

log = get_logger(__name__)

# sessions.last_used_at is written at most this often, so a busy session does not write per request.
USED_RESOLUTION = timedelta(minutes=5)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _aware(ts: datetime) -> datetime:
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)  # SQLite returns naive UTC


def create_session(engine: Engine, user_id: str, *, days: int = 30) -> str:
    """A new session for `user_id`; returns the cookie value (shown nowhere else)."""
    token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    s = tables.sessions
    with engine.begin() as conn:
        conn.execute(delete(s).where(_dead(now, get_settings().session_idle_days)))
        conn.execute(
            s.insert().values(
                id=_hash(token),
                user_id=user_id,
                created_at=now,
                expires_at=now + timedelta(days=days),
                last_used_at=now,
            )
        )
    return token


def _dead(now: datetime, idle_days: int) -> ColumnElement[bool]:
    """SQL: the session has passed its absolute expiry or has been idle too long."""
    s = tables.sessions
    dead = s.c.expires_at < now
    if idle_days > 0:
        last = func.coalesce(s.c.last_used_at, s.c.created_at)
        dead = or_(dead, last < now - timedelta(days=idle_days))
    return dead


def resolve_session(engine: Engine, token: str, *, idle_days: int | None = None) -> User | None:
    """The user a live session belongs to.

    None if the session is unknown, past its absolute expiry, idle for more than `idle_days`
    (default `Settings.session_idle_days`; 0 turns the idle timeout off), or its user is disabled.
    """
    idle = get_settings().session_idle_days if idle_days is None else idle_days
    s, u = tables.sessions, tables.users
    stmt = select(
        u,
        s.c.expires_at.label("session_expires"),
        s.c.created_at.label("session_created"),
        s.c.last_used_at.label("used"),
    ).join(u, u.c.id == s.c.user_id)
    with engine.connect() as conn:
        row = conn.execute(stmt.where(s.c.id == _hash(token))).mappings().first()
    if row is None or row["disabled_at"] is not None:
        return None
    now = datetime.now(UTC)
    if _aware(row["session_expires"]) <= now:
        return None
    used = _aware(row["used"] or row["session_created"])
    if idle > 0 and now - used >= timedelta(days=idle):
        return None
    if now - used >= USED_RESOLUTION:
        _touch(engine, token, now)
    return user_from_row(row)


def _touch(engine: Engine, token: str, now: datetime) -> None:
    """Record use. A failed write is logged and never signs the user out."""
    s = tables.sessions
    try:
        with engine.begin() as conn:
            conn.execute(update(s).where(s.c.id == _hash(token)).values(last_used_at=now))
    except SQLAlchemyError as e:
        log.warning("session.touch_failed", error=str(e))


def revoke_session(engine: Engine, token: str) -> None:
    s = tables.sessions
    with engine.begin() as conn:
        conn.execute(delete(s).where(s.c.id == _hash(token)))


def revoke_user_sessions(engine: Engine, user_id: str) -> int:
    """Sign a user out everywhere. Returns how many sessions ended."""
    s = tables.sessions
    with engine.begin() as conn:
        return conn.execute(delete(s).where(s.c.user_id == user_id)).rowcount
