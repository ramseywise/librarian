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
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)

metadata = MetaData()

# BIGINT keys on Postgres, plain INTEGER on SQLite (only INTEGER PRIMARY KEY autoincrements there).
_ID = BigInteger().with_variant(Integer, "sqlite")

attempts = Table(
    "attempts",
    metadata,
    Column("id", _ID, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        String(64),
        ForeignKey("users.id", name="attempts_user_fk", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("kind", String(16), nullable=False),
    Column("item", Text, nullable=False),
    Column("scope", Text, nullable=False),
    Column("result", String(16), nullable=False),
    Column("payload", Text, nullable=True),
    # sha256 of user, ts, kind, item, result: the same event recorded twice is one row.
    Column("event_key", String(64), nullable=False, unique=True),
    Index("attempts_kind_item", "kind", "item"),
    Index("attempts_user_kind", "user_id", "kind"),
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
    # The last request by any credential of this user, written at most every few minutes.
    Column("last_seen_at", DateTime(timezone=True), nullable=True),
    # Set by `librarian users disable`: the user cannot sign in, and no session or key resolves.
    Column("disabled_at", DateTime(timezone=True), nullable=True),
)

# Who may sign in for the first time. Existing users and the owner need no invite.
invites = Table(
    "invites",
    metadata,
    Column("email", String(320), primary_key=True),
    Column("invited_by", String(64), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("used_at", DateTime(timezone=True), nullable=True),
)

# Email sign-in links. `id` is the sha256 of the token in the link; each is used at most once.
login_tokens = Table(
    "login_tokens",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("email", String(320), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("used_at", DateTime(timezone=True), nullable=True),
    Index("login_tokens_email", "email", "created_at"),
)

# Shared fixed-window request counters (accounts.rate_limits). One row per key; the window opens
# at `window_start` (epoch seconds) with the first hit and the row restarts once it has passed.
rate_limits = Table(
    "rate_limits",
    metadata,
    Column("key", String(255), primary_key=True),
    Column("window_start", Float, nullable=False),
    Column("hits", Integer, nullable=False),
    Index("rate_limits_window_start", "window_start"),
)

# Security-relevant events: login, logout, key create/revoke, invite, promote, admin reload.
# `target` names what was acted on (an email, a key id), never a secret.
audit = Table(
    "audit",
    metadata,
    Column("id", _ID, primary_key=True, autoincrement=True),
    Column("ts", DateTime(timezone=True), nullable=False),
    Column("user_id", String(64), nullable=True),
    Column("action", String(32), nullable=False),
    Column("target", Text, nullable=True),
    Index("audit_ts", "ts"),
)

# Browser sessions. `id` is the sha256 of the cookie value.
sessions = Table(
    "sessions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    # Last request on this session (written at most every few minutes); null = never since created_at.
    Column("last_used_at", DateTime(timezone=True), nullable=True),
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

# Lessons a user has opened or finished. `state` is "opened" or "done"; done is never undone
# by opening the lesson again, and `updated_at` is the last time either happened.
progress = Table(
    "progress",
    metadata,
    Column(
        "user_id",
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("lesson_id", Text, primary_key=True),
    Column("state", String(16), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def event_key(user_id: str, ts_iso: str, kind: str, item: str, result: str) -> str:
    """The `attempts.event_key` of one graded event."""
    import hashlib

    raw = "\x1f".join((user_id, ts_iso, kind, item, result))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# Reader feedback (librarian.feedback). `kind` is answer | page | lesson | unanswered and `target`
# names what it is about: an answer id, a wiki page id, a lesson id, or the unanswered question
# (truncated). `rating` is 1 or -1 and only on answers. `release` and `experiment` are what the
# server was serving when the row was written.
feedback = Table(
    "feedback",
    metadata,
    Column("id", String(32), primary_key=True),
    Column(
        "user_id",
        String(64),
        ForeignKey("users.id", name="feedback_user_fk", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("ts", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("kind", String(16), nullable=False),
    Column("target", String(320), nullable=False),
    Column("rating", SmallInteger, nullable=True),
    Column("body", Text, nullable=True),
    Column("release", String(64), nullable=True),
    Column("experiment", String(255), nullable=True),
    Index("feedback_kind_target", "kind", "target"),
    Index("feedback_ts", "ts"),
    Index("feedback_user", "user_id"),
)
