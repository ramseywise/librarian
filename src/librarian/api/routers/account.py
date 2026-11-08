"""GET /api/me (who the caller is, their course progress and what chat they have left) and the admin routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from librarian import accounts
from librarian.accounts import User
from librarian.api.security import Admin, SignedIn, chat_limiter
from librarian.config import get_settings
from librarian.courses import progress
from librarian.db import get_engine

router = APIRouter()


def _user_json(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "timezone": user.timezone,
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


@router.get("/api/admin/users")
def admin_users(_: Admin) -> list[dict[str, Any]]:
    return [_user_json(u) for u in accounts.list_users(get_engine())]
