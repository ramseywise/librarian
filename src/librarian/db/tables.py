"""The tables, for queries. Migrations are written by hand and do not import this module."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)

metadata = MetaData()

# BIGINT keys on Postgres, plain INTEGER on SQLite (only INTEGER PRIMARY KEY autoincrements there).
_ID = BigInteger().with_variant(Integer, "sqlite")

attempts = Table(
    "attempts",
    metadata,
    Column("id", _ID, primary_key=True, autoincrement=True),
    Column("user_id", String(64), nullable=True),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("kind", String(16), nullable=False),
    Column("item", Text, nullable=False),
    Column("scope", Text, nullable=False),
    Column("result", String(16), nullable=False),
    Column("payload", Text, nullable=True),
    # sha256 of user, ts, kind, item, result: a unique key that still works while user_id is NULL.
    Column("event_key", String(64), nullable=False, unique=True),
    Index("attempts_kind_item", "kind", "item"),
)

meta = Table(
    "meta",
    metadata,
    Column("key", String(128), primary_key=True),
    Column("value", Text, nullable=False),
)

chat_usage = Table(
    "chat_usage",
    metadata,
    Column("id", _ID, primary_key=True, autoincrement=True),
    Column("user_id", String(64), nullable=True),
    # '' while user_id is NULL, so (user_key, day) is unique on both dialects.
    Column("user_key", String(64), nullable=False),
    Column("day", Date, nullable=False),
    Column("requests", Integer, nullable=False, server_default="0"),
    Column("input_tokens", BigInteger, nullable=False, server_default="0"),
    Column("output_tokens", BigInteger, nullable=False, server_default="0"),
    Column("usd", Float, nullable=False, server_default="0"),
    UniqueConstraint("user_key", "day", name="chat_usage_user_day"),
)

# Accounts. `email` is stored lowercased; `role` is "admin" or "member".
users = Table(
    "users",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("email", String(320), nullable=False, unique=True),
    Column("name", Text, nullable=True),
    Column("role", String(16), nullable=False, server_default="member"),
    Column("timezone", String(64), nullable=False, server_default="UTC"),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# Browser sessions (login, phase 3 wave B). `id` is the sha256 of the cookie value.
sessions = Table(
    "sessions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Index("sessions_user", "user_id"),
)

# `hash` is the sha256 of the whole key (`lk_<id>_<secret>`); the key itself is never stored.
# `scopes` is space-separated: "read" or "read write".
api_keys = Table(
    "api_keys",
    metadata,
    Column("id", String(32), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("hash", String(64), nullable=False, unique=True),
    Column("name", Text, nullable=True),
    Column("scopes", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("last_used_at", DateTime(timezone=True), nullable=True),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
    Index("api_keys_user", "user_id"),
)


def event_key(user_id: str | None, ts_iso: str, kind: str, item: str, result: str) -> str:
    """The `attempts.event_key` of one graded event."""
    import hashlib

    raw = "\x1f".join((user_id or "", ts_iso, kind, item, result))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
