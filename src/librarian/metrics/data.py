"""Loading answer telemetry and feedback ratings, plus the small statistics the reports share."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError

from librarian.log_config import get_logger
from librarian.pricing import TokenUsage, cost_usd
from librarian.retrieval import corpus

log = get_logger(__name__)

AGENT_LOG_NAME = "agent.jsonl"  # mirrors librarian.agent.loop (the agent layer sits above this one)
MIN_N = 30  # variants with fewer answers are shown but not compared
NO_VARIANT = "(default)"


@dataclass(frozen=True)
class Answer:
    """One logged chat answer. Fields added in 4b are None/"" on older rows."""

    ts: datetime
    answer_id: str
    release: str
    experiment: dict[str, str]
    user_id: str
    grounded: bool | None  # None when the row carries no grounding fields
    pages_read: int
    latency_ms: float | None
    cost: float | None
    error: bool = False
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def variant(self, experiment: str) -> str:
        return self.experiment.get(experiment, NO_VARIANT)


def parse_experiment(value: object) -> dict[str, str]:
    """`ranking=hybrid-union;prompt=v2` -> {"ranking": "hybrid-union", "prompt": "v2"}."""
    out: dict[str, str] = {}
    if not isinstance(value, str):
        return out
    for part in value.split(";"):
        name, sep, variant = part.strip().partition("=")
        if name and sep:
            out[name.strip()] = variant.strip()
    return out


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        ts = datetime.fromisoformat(value)
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)


def _row_cost(row: dict[str, Any]) -> float | None:
    """Cost the row logged, else computed from its token usage; None when it has neither."""
    for key in ("cost_usd", "usd"):
        v = row.get(key)
        if isinstance(v, int | float) and not isinstance(v, bool):
            return float(v)
    usage = row.get("usage")
    model = row.get("model")
    if isinstance(usage, dict) and isinstance(model, str):
        try:
            return cost_usd(
                model,
                TokenUsage(
                    input=int(usage.get("input", 0)),
                    output=int(usage.get("output", 0)),
                    cache_read=int(usage.get("cache_read", 0)),
                    cache_write=int(usage.get("cache_write", 0)),
                ),
            )
        except (KeyError, TypeError, ValueError):
            return None
    return None


def _grounded(row: dict[str, Any]) -> bool | None:
    if "ungrounded" not in row:
        return None
    return not row["ungrounded"]


def _answer(row: dict[str, Any], ts: datetime) -> Answer:
    pages = row.get("pages_read")
    latency = row.get("latency_ms")
    return Answer(
        ts=ts,
        answer_id=str(row.get("answer_id") or ""),
        release=str(row.get("release") or ""),
        experiment=parse_experiment(row.get("experiment")),
        user_id=str(row.get("user_id") or ""),
        grounded=_grounded(row),
        pages_read=len(pages) if isinstance(pages, list) else 0,
        latency_ms=float(latency) if isinstance(latency, int | float) else None,
        cost=_row_cost(row),
        error=bool(row.get("error")),
        raw=row,
    )


def load_answers(
    *,
    since: datetime | None = None,
    path: Path | None = None,
    include_eval: bool = False,
) -> list[Answer]:
    """Answers in `logs/agent.jsonl` from `since` on. Bad lines are skipped; eval traffic is not
    chat traffic and is left out unless asked for."""
    path = path or corpus.LOGS_DIR / AGENT_LOG_NAME
    if not path.exists():
        return []
    out: list[Answer] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            ts = _parse_ts(row.get("ts"))
            if ts is None or (since and ts < since):
                continue
            if not include_eval and row.get("source") == "eval":
                continue
            out.append(_answer(row, ts))
    return out


def since_from_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.combine(date.fromisoformat(value), datetime.min.time(), tzinfo=UTC)


# -- feedback ---------------------------------------------------------------------------------

# The shape of `feedback` as this module reads it. When the db package defines the table
# (`tables.feedback`), that one is used; this copy only keeps the reader working without it.
_FALLBACK = Table(
    "feedback",
    MetaData(),
    Column("id", String(32), primary_key=True),
    Column("user_id", String(64)),
    Column("ts", DateTime(timezone=True)),
    Column("kind", String(16)),
    Column("target", Text),
    Column("rating", Integer),
    Column("body", Text),
    Column("release", String(128)),
    Column("experiment", Text),
)


def feedback_table() -> Table:
    from librarian.db import tables

    return getattr(tables, "feedback", _FALLBACK)


def load_ratings(engine: Engine, since: datetime | None = None) -> dict[str, int]:
    """Latest rating (1 or -1) per answer id. Unrated answers are absent.

    An engine without a feedback table (not migrated yet) reads as no ratings.
    """
    fb = feedback_table()
    stmt = (
        select(fb.c.target, fb.c.rating, fb.c.ts)
        .where(fb.c.kind == "answer", fb.c.rating.is_not(None))
        .order_by(fb.c.ts, fb.c.id)
    )
    if since is not None:
        stmt = stmt.where(fb.c.ts >= since)
    try:
        with engine.connect() as conn:
            rows = conn.execute(stmt).all()
    except DatabaseError as exc:
        log.warning("metrics.feedback_unreadable", error=type(exc).__name__)
        return {}
    return {str(t): int(r) for t, r, _ in rows if r in (1, -1)}


# -- statistics -------------------------------------------------------------------------------


def percentile(values: Iterable[float], q: float) -> float | None:
    """Linear-interpolation percentile, q in [0, 100]; None for no values."""
    xs = sorted(values)
    if not xs:
        return None
    k = (len(xs) - 1) * q / 100
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def mean(values: Iterable[float]) -> float | None:
    xs = list(values)
    return sum(xs) / len(xs) if xs else None


def rate(hits: int, total: int) -> float | None:
    return hits / total if total else None


def group_by[T](items: Iterable[T], key: Any) -> Iterator[tuple[str, list[T]]]:  # noqa: ANN401
    groups: dict[str, list[T]] = {}
    for item in items:
        groups.setdefault(key(item), []).append(item)
    yield from sorted(groups.items())
