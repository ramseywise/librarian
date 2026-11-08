"""Who may sign in: existing users, the owner, and emails on the invite list.

A sign-in carries an email the provider has verified. `sign_in` maps it to a user, creating a
member the first time an invited email signs in, or returns None for anyone else.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import Engine, select, update
from sqlalchemy.exc import IntegrityError

from librarian.accounts.users import (
    AccountError,
    User,
    add_user,
    ensure_owner,
    get_user,
    normalize_email,
)
from librarian.db import tables


@dataclass(frozen=True)
class Invite:
    email: str
    invited_by: str | None
    created_at: datetime
    used_at: datetime | None


def invite(engine: Engine, email: str, *, invited_by: str | None = None) -> bool:
    """Put `email` on the list. False if it is already there or already a user."""
    email = normalize_email(email)
    if get_user(engine, email) is not None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(
                tables.invites.insert().values(
                    email=email, invited_by=invited_by, created_at=datetime.now(UTC)
                )
            )
    except IntegrityError:
        return False
    return True


def is_invited(engine: Engine, email: str) -> bool:
    t = tables.invites
    with engine.connect() as conn:
        return conn.execute(select(t.c.email).where(t.c.email == email)).first() is not None


def list_invites(engine: Engine) -> list[Invite]:
    t = tables.invites
    with engine.connect() as conn:
        rows = conn.execute(select(t).order_by(t.c.created_at)).mappings().all()
    return [Invite(r["email"], r["invited_by"], r["created_at"], r["used_at"]) for r in rows]


def may_sign_in(engine: Engine, email: str, owner_email: str) -> bool:
    email = normalize_email(email)
    return (
        email == normalize_email(owner_email)
        or get_user(engine, email) is not None
        or is_invited(engine, email)
    )


def sign_in(
    engine: Engine, email: str, *, owner_email: str, name: str | None = None
) -> User | None:
    """The user for a verified `email`, created on an invite's first use; None if not allowed."""
    email = normalize_email(email)
    if email == normalize_email(owner_email):
        return ensure_owner(engine, email)
    user = get_user(engine, email)
    if user is not None:
        return user
    if not is_invited(engine, email):
        return None
    try:
        user = add_user(engine, email, name=name)
    except AccountError:  # a concurrent first sign-in made it
        user = get_user(engine, email)
    t = tables.invites
    with engine.begin() as conn:
        conn.execute(update(t).where(t.c.email == email).values(used_at=datetime.now(UTC)))
    return user
