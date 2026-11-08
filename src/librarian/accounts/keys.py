"""API keys: `lk_<id>_<secret>`, shown once, stored as a sha256 of the whole key.

The secret is 256 random bits, so a fast hash is enough: there is nothing to brute-force.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, select, update

from librarian.accounts.users import ALL_SCOPES, AccountError, User, get_user, user_from_row
from librarian.db import tables

PREFIX = "lk_"
# last_used_at is written at most this often per key, so a busy key does not write on every request.
LAST_USED_RESOLUTION = timedelta(minutes=5)


@dataclass(frozen=True)
class KeyInfo:
    id: str
    email: str
    name: str | None
    scopes: frozenset[str]
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def parse_scopes(scopes: str) -> frozenset[str]:
    parsed = frozenset(scopes.replace(",", " ").split())
    if not parsed or not parsed <= ALL_SCOPES:
        raise AccountError(f"scopes must be from {sorted(ALL_SCOPES)}, not {scopes!r}")
    return parsed | {"read"}  # write implies read


def create_key(
    engine: Engine, email: str, *, scopes: str = "read write", name: str | None = None
) -> tuple[KeyInfo, str]:
    """A new key for the user with `email`. Returns the key's record and the key itself."""
    user = get_user(engine, email)
    if user is None:
        raise AccountError(f"no user with email {email!r}")
    granted = parse_scopes(scopes)
    key_id = secrets.token_hex(6)
    key = f"{PREFIX}{key_id}_{secrets.token_urlsafe(32)}"
    now = datetime.now(UTC)
    with engine.begin() as conn:
        conn.execute(
            tables.api_keys.insert().values(
                id=key_id,
                user_id=user.id,
                hash=hash_key(key),
                name=name,
                scopes=" ".join(sorted(granted)),
                created_at=now,
            )
        )
    return KeyInfo(key_id, user.email, name, granted, now, None, None), key


def resolve_key(engine: Engine, key: str) -> User | None:
    """The user a live key belongs to, with the key's scopes; None if unknown or revoked."""
    k, u = tables.api_keys, tables.users
    stmt = (
        select(u, k.c.id.label("key_id"), k.c.scopes, k.c.last_used_at, k.c.revoked_at)
        .join(u, u.c.id == k.c.user_id)
        .where(k.c.hash == hash_key(key))
    )
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    if row is None or row["revoked_at"] is not None:
        return None
    now = datetime.now(UTC)
    last = row["last_used_at"]
    if last is not None and last.tzinfo is None:  # SQLite returns naive datetimes
        last = last.replace(tzinfo=UTC)
    if last is None or now - last >= LAST_USED_RESOLUTION:
        with engine.begin() as conn:
            conn.execute(update(k).where(k.c.id == row["key_id"]).values(last_used_at=now))
    return user_from_row(row, frozenset(row["scopes"].split()))


def list_keys(engine: Engine, email: str | None = None) -> list[KeyInfo]:
    k, u = tables.api_keys, tables.users
    stmt = select(k, u.c.email).join(u, u.c.id == k.c.user_id).order_by(k.c.created_at)
    if email is not None:
        stmt = stmt.where(u.c.email == email.strip().lower())
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [
        KeyInfo(
            r["id"],
            r["email"],
            r["name"],
            frozenset(r["scopes"].split()),
            r["created_at"],
            r["last_used_at"],
            r["revoked_at"],
        )
        for r in rows
    ]


def revoke_key(engine: Engine, key_id: str) -> bool:
    """Revoke a key by its id (`lk_<id>_...`). False if no live key has that id."""
    key_id = key_id.removeprefix(PREFIX).split("_", 1)[0]
    k = tables.api_keys
    with engine.begin() as conn:
        done = conn.execute(
            update(k)
            .where(k.c.id == key_id, k.c.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
    return done.rowcount == 1


def is_api_key(token: str) -> bool:
    return token.startswith(PREFIX)
