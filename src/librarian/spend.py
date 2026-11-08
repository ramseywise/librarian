"""Chat spend, summed from the `chat_usage` table: per user, global, and per model.

One reader for `GET /api/admin/spend` and the Prometheus spend gauges (`librarian.api.prom`), so
the two cannot disagree. The figures are the estimate the spend cap uses (`librarian.pricing`),
not a bill.

`chat_usage` is one row per user and UTC day. It has no model column (adding one would change the
unique key, which the expand-only rule forbids within a release), so the per-model split comes
from `logs/agent.jsonl`, which logs the model and cost of every answer. It covers the answers
that file still holds, and says so in its `source` field.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.engine import Engine

from librarian.config import Settings
from librarian.db import tables

WINDOW_DAYS = 30


@dataclass(frozen=True)
class Totals:
    today_usd: float
    last_30d_usd: float


def _today() -> date:
    return datetime.now(UTC).date()


def totals(engine: Engine, today: date | None = None) -> Totals:
    """Everyone's spend today and over the last 30 UTC days (today included)."""
    today = today or _today()
    t = tables.chat_usage
    since = today - timedelta(days=WINDOW_DAYS - 1)
    with engine.connect() as conn:
        day = conn.execute(select(func.sum(t.c.usd)).where(t.c.day == today)).scalar()
        month = conn.execute(select(func.sum(t.c.usd)).where(t.c.day >= since)).scalar()
    return Totals(float(day or 0.0), float(month or 0.0))


def by_user(engine: Engine, today: date | None = None) -> list[dict[str, Any]]:
    """Per user, dearest first over 30 days: id, display name (never the email), spend."""
    today = today or _today()
    since = today - timedelta(days=WINDOW_DAYS - 1)
    c, u = tables.chat_usage, tables.users
    today_usd = func.sum(func.coalesce(c.c.usd, 0.0)).filter(c.c.day == today)
    stmt = (
        select(
            c.c.user_key,
            u.c.name,
            today_usd.label("today"),
            func.sum(c.c.usd).label("month"),
            func.sum(c.c.requests).label("requests"),
        )
        .select_from(c.outerjoin(u, u.c.id == c.c.user_key))
        .where(c.c.day >= since)
        .group_by(c.c.user_key, u.c.name)
        .order_by(func.sum(c.c.usd).desc())
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).all()
    return [
        {
            "user_id": r.user_key or None,
            "name": r.name,
            "today_usd": round(float(r.today or 0.0), 4),
            "last_30d_usd": round(float(r.month or 0.0), 4),
            "requests_30d": int(r.requests or 0),
        }
        for r in rows
    ]


def by_model(days: int = WINDOW_DAYS) -> dict[str, Any]:
    """Answers and logged cost per model from the agent log, for the last `days` days."""
    from librarian.metrics.data import load_answers  # the log reader; no I/O at import

    since = datetime.now(UTC) - timedelta(days=days)
    models: dict[str, dict[str, Any]] = {}
    for a in load_answers(since=since):
        name = str(a.raw.get("model") or "unknown")
        m = models.setdefault(name, {"answers": 0, "usd": 0.0, "answers_without_cost": 0})
        m["answers"] += 1
        if a.cost is None:
            m["answers_without_cost"] += 1
        else:
            m["usd"] += a.cost
    for m in models.values():
        m["usd"] = round(m["usd"], 4)
    return {"source": "logs/agent.jsonl", "days": days, "models": models}


def report(engine: Engine, settings: Settings, today: date | None = None) -> dict[str, Any]:
    """The admin view: global spend against the cap, per user, per model. No email addresses."""
    tot = totals(engine, today)
    cap = settings.chat_daily_budget_usd
    return {
        "currency": "USD",
        "estimate": True,
        "global": {
            "today_usd": round(tot.today_usd, 4),
            "last_30d_usd": round(tot.last_30d_usd, 4),
            "daily_cap_usd": cap or None,
            "today_fraction_of_cap": round(tot.today_usd / cap, 4) if cap > 0 else None,
            "user_daily_cap_usd": settings.chat_user_daily_budget_usd or None,
        },
        "configured_model": settings.anthropic_model,
        "users": by_user(engine, today),
        "models": by_model(),
    }
