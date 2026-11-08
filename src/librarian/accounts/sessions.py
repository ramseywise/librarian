"""Browser sessions: a random cookie value, stored as its sha256, valid for `days`.

Like API keys, the value is 256 random bits, so a fast hash is enough. Expired rows are removed
when a new session is made.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, delete, select

from librarian.accounts.users import User, user_from_row
from librarian.db import tables


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
        conn.execute(delete(s).where(s.c.expires_at < now))
        conn.execute(
            s.insert().values(
                id=_hash(token),
                user_id=user_id,
                created_at=now,
                expires_at=now + timedelta(days=days),
            )
        )
    return token


def resolve_session(engine: Engine, token: str) -> User | None:
    """The user a live session belongs to; None if unknown or expired."""
    s, u = tables.sessions, tables.users
    stmt = select(u, s.c.expires_at.label("session_expires")).join(u, u.c.id == s.c.user_id)
    with engine.connect() as conn:
        row = conn.execute(stmt.where(s.c.id == _hash(token))).mappings().first()
    if row is None or _aware(row["session_expires"]) <= datetime.now(UTC):
        return None
    return user_from_row(row)


def revoke_session(engine: Engine, token: str) -> None:
    s = tables.sessions
    with engine.begin() as conn:
        conn.execute(delete(s).where(s.c.id == _hash(token)))


def revoke_user_sessions(engine: Engine, user_id: str) -> int:
    """Sign a user out everywhere. Returns how many sessions ended."""
    s = tables.sessions
    with engine.begin() as conn:
        return conn.execute(delete(s).where(s.c.user_id == user_id)).rowcount
