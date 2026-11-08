"""The caller's account and the admin routes.

GET    /api/me                     who the caller is, their course progress, chat left today
GET    /api/me/keys                their API keys (no secrets)
POST   /api/me/keys                a new key, shown once (for `librarian mcp` remote mode)
DELETE /api/me/keys/{key_id}       revoke one of their keys
GET    /api/admin/users            every user: role, last seen, chat spend today
POST   /api/admin/users/{email}/role
GET    /api/admin/invites          the invite list
POST   /api/admin/invites          invite an email
GET    /api/admin/audit            the latest audit events
GET    /api/legal/third-party      the course tree's THIRD_PARTY.md (public, for the privacy page)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from librarian import accounts
from librarian.accounts import User, audit
from librarian.api.security import Admin, SignedIn, chat_limiter
from librarian.config import get_settings
from librarian.courses import progress
from librarian.db import get_engine

router = APIRouter()


def _iso(ts: datetime | None) -> str | None:
    return ts.isoformat() if ts else None


def _user_json(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "timezone": user.timezone,
    }


def _key_json(k: accounts.KeyInfo) -> dict[str, Any]:
    return {
        "id": k.id,
        "name": k.name,
        "scopes": sorted(k.scopes),
        "created_at": _iso(k.created_at),
        "last_used_at": _iso(k.last_used_at),
        "revoked_at": _iso(k.revoked_at),
    }


@router.get("/api/me")
def me(user: SignedIn) -> dict[str, Any]:
    settings = get_settings()
    done = progress.summary(user)
    return {
        **_user_json(user),
        "scopes": sorted(user.scopes),
        "progress": {"done": done["done"], "modules": done["modules"], "last": done["last"]},
        "chat": {
            "spent_today_usd": round(chat_limiter.spent_usd(user.id), 4),
            # Admins have only the global cap.
            "daily_budget_usd": None if user.is_admin else settings.chat_user_daily_budget_usd,
        },
    }


@router.get("/api/me/keys")
def my_keys(user: SignedIn) -> list[dict[str, Any]]:
    return [_key_json(k) for k in accounts.list_keys(get_engine(), user.email)]


class NewKey(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    scopes: Literal["read", "read write"] = "read"


@router.post("/api/me/keys", status_code=201)
def create_my_key(body: NewKey, user: SignedIn) -> dict[str, Any]:
    """A new key for the caller. The key is in this response only."""
    engine = get_engine()
    info, key = accounts.create_key(engine, user.email, scopes=body.scopes, name=body.name)
    audit(engine, "key_create", user_id=user.id, target=info.id)
    return {**_key_json(info), "key": key}


@router.delete("/api/me/keys/{key_id}", status_code=204)
def revoke_my_key(key_id: str, user: SignedIn) -> None:
    engine = get_engine()
    mine = {k.id for k in accounts.list_keys(engine, user.email) if k.revoked_at is None}
    if key_id not in mine or not accounts.revoke_key(engine, key_id):
        raise HTTPException(status_code=404, detail="No live key with that id.")
    audit(engine, "key_revoke", user_id=user.id, target=key_id)


@router.get("/api/admin/users")
def admin_users(_: Admin) -> list[dict[str, Any]]:
    return [
        {
            **_user_json(u),
            "last_seen_at": _iso(u.last_seen_at),
            "chat_spent_today_usd": round(chat_limiter.spent_usd(u.id), 4),
        }
        for u in accounts.list_users(get_engine())
    ]


class RoleChange(BaseModel):
    role: Literal["admin", "member"]


@router.post("/api/admin/users/{email}/role")
def admin_set_role(email: str, body: RoleChange, admin: Admin) -> dict[str, Any]:
    engine = get_engine()
    if accounts.normalize_email(email) == accounts.normalize_email(get_settings().owner_email):
        raise HTTPException(status_code=409, detail="The owner is always an admin.")
    try:
        user = accounts.set_role(engine, email, body.role)
    except accounts.AccountError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    audit(engine, "promote", user_id=admin.id, target=f"{user.email}:{body.role}")
    return _user_json(user)


@router.get("/api/admin/invites")
def admin_invites(_: Admin) -> list[dict[str, Any]]:
    return [
        {"email": i.email, "created_at": _iso(i.created_at), "used_at": _iso(i.used_at)}
        for i in accounts.list_invites(get_engine())
    ]


class NewInvite(BaseModel):
    email: str = Field(max_length=320)


@router.post("/api/admin/invites", status_code=201)
def admin_invite(body: NewInvite, admin: Admin) -> dict[str, Any]:
    engine = get_engine()
    try:
        added = accounts.invite(engine, body.email, invited_by=admin.id)
    except accounts.AccountError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    email = accounts.normalize_email(body.email)
    if added:
        audit(engine, "invite", user_id=admin.id, target=email)
    return {"email": email, "added": added}


@router.get("/api/admin/audit")
def admin_audit(_: Admin, limit: int = 100) -> list[dict[str, Any]]:
    events = accounts.audit_events(get_engine(), max(1, min(limit, 500)))
    return [
        {"ts": _iso(e.ts), "email": e.email, "action": e.action, "target": e.target} for e in events
    ]


@router.get("/api/legal/third-party", response_class=PlainTextResponse)
def third_party() -> PlainTextResponse:
    """What the course tree copied from others and under which licence. Public, like the terms."""
    path = get_settings().courses_dir / "THIRD_PARTY.md"
    try:
        return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="text/markdown")
    except OSError as e:
        raise HTTPException(status_code=404, detail="No third-party notice here.") from e
