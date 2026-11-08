"""Users: one row per verified email. The owner is the admin the bootstrap token and open mode act as."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import Engine, select, update
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError

from librarian.db import tables

Role = Literal["admin", "member"]
ROLES: tuple[Role, ...] = ("admin", "member")
ALL_SCOPES = frozenset({"read", "write"})
# users.last_seen_at is written at most this often, so a busy user does not write on every request.
SEEN_RESOLUTION = timedelta(minutes=5)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+$")


class AccountError(ValueError):
    """A bad email, role, timezone or scope, or a user or key that does not exist."""


@dataclass(frozen=True)
class User:
    id: str
    email: str
    role: Role
    timezone: str = "UTC"
    name: str | None = None
    # What this request may do: a read-only key gives {"read"}; every other credential both.
    scopes: frozenset[str] = field(default=ALL_SCOPES)
    last_seen_at: datetime | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise AccountError(f"not an email address: {email!r}")
    return email


def _check_timezone(tz: str) -> str:
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as e:
        raise AccountError(f"unknown timezone: {tz!r}") from e
    return tz


def user_from_row(row: RowMapping, scopes: frozenset[str] = ALL_SCOPES) -> User:
    seen = row.get("last_seen_at")
    return User(
        id=row["id"],
        email=row["email"],
        role=row["role"],
        timezone=row["timezone"],
        name=row["name"],
        scopes=scopes,
        last_seen_at=seen.replace(tzinfo=UTC) if seen and seen.tzinfo is None else seen,
    )


def get_user(engine: Engine, email: str) -> User | None:
    t = tables.users
    with engine.connect() as conn:
        row = conn.execute(select(t).where(t.c.email == normalize_email(email))).mappings().first()
    return user_from_row(row) if row else None


def get_user_by_id(engine: Engine, user_id: str) -> User | None:
    t = tables.users
    with engine.connect() as conn:
        row = conn.execute(select(t).where(t.c.id == user_id)).mappings().first()
    return user_from_row(row) if row else None


def list_users(engine: Engine) -> list[User]:
    t = tables.users
    with engine.connect() as conn:
        rows = conn.execute(select(t).order_by(t.c.created_at, t.c.email)).mappings().all()
    return [user_from_row(r) for r in rows]


def add_user(
    engine: Engine,
    email: str,
    *,
    name: str | None = None,
    role: Role = "member",
    timezone: str = "UTC",
) -> User:
    """Create a user; AccountError if the email is taken."""
    if role not in ROLES:
        raise AccountError(f"role must be one of {', '.join(ROLES)}, not {role!r}")
    values = {
        "id": uuid.uuid4().hex,
        "email": normalize_email(email),
        "name": name,
        "role": role,
        "timezone": _check_timezone(timezone),
        "created_at": datetime.now(UTC),
    }
    try:
        with engine.begin() as conn:
            conn.execute(tables.users.insert().values(**values))
    except IntegrityError as e:
        raise AccountError(f"a user with email {values['email']} exists") from e
    return user_from_row(values)  # type: ignore[arg-type]


def ensure_owner(engine: Engine, email: str) -> User:
    """The owner's row, created as admin on first use and kept admin."""
    owner = get_user(engine, email)
    if owner is None:
        try:
            return add_user(engine, email, role="admin")
        except AccountError:  # another worker created it first
            owner = get_user(engine, email)
            assert owner is not None
    if owner.role != "admin":
        t = tables.users
        with engine.begin() as conn:
            conn.execute(update(t).where(t.c.id == owner.id).values(role="admin"))
        owner = replace(owner, role="admin")
    return owner


def set_role(engine: Engine, email: str, role: Role) -> User:
    """Make an existing user an admin or a member; AccountError if there is no such user."""
    if role not in ROLES:
        raise AccountError(f"role must be one of {', '.join(ROLES)}, not {role!r}")
    user = get_user(engine, email)
    if user is None:
        raise AccountError(f"no user with email {email!r}")
    t = tables.users
    with engine.begin() as conn:
        conn.execute(update(t).where(t.c.id == user.id).values(role=role))
    return replace(user, role=role)


def touch_seen(engine: Engine, user: User) -> None:
    """Record that `user` made a request now, unless that was recorded in the last few minutes."""
    now = datetime.now(UTC)
    if user.last_seen_at is not None and now - user.last_seen_at < SEEN_RESOLUTION:
        return
    t = tables.users
    with engine.begin() as conn:
        conn.execute(update(t).where(t.c.id == user.id).values(last_seen_at=now))
