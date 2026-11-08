"""Email sign-in links: a random token, stored as its sha256, single use, 15 minutes.

Used up by one conditional UPDATE, so two clicks racing on two workers sign in at most once.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, func, select, update

from librarian.accounts.users import normalize_email
from librarian.db import tables

TTL = timedelta(minutes=15)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue(engine: Engine, email: str, *, ttl: timedelta = TTL) -> str:
    """A new sign-in token for `email`; the caller puts it in the link it sends."""
    token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    with engine.begin() as conn:
        conn.execute(
            tables.login_tokens.insert().values(
                id=_hash(token), email=normalize_email(email), created_at=now, expires_at=now + ttl
            )
        )
    return token


def consume(engine: Engine, token: str) -> str | None:
    """The email a live, unused token was issued for, marking it used; None otherwise."""
    t = tables.login_tokens
    now = datetime.now(UTC)
    with engine.begin() as conn:
        done = conn.execute(
            update(t)
            .where(t.c.id == _hash(token), t.c.used_at.is_(None), t.c.expires_at > now)
            .values(used_at=now)
        )
        if done.rowcount != 1:
            return None
        return conn.execute(select(t.c.email).where(t.c.id == _hash(token))).scalar_one()


def issued_since(engine: Engine, email: str, since: datetime) -> int:
    """How many tokens `email` was sent since `since`, for the per-address send limit."""
    t = tables.login_tokens
    stmt = select(func.count()).where(t.c.email == normalize_email(email), t.c.created_at >= since)
    with engine.connect() as conn:
        return int(conn.execute(stmt).scalar() or 0)
