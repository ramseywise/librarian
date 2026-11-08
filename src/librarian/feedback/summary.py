"""The admin summary: the top ten of each signal, with no emails and no user ids."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, case, func, select

from librarian.db import tables
from librarian.log_config import get_logger

log = get_logger(__name__)

TOP = 10
NOTES = 3
MIN_ATTEMPTS = 5  # a lesson needs this many graded attempts before its miss rate counts
_MISSES = ("missed", "wrong")


def _notes(engine: Engine, kind: str, target: str) -> list[str]:
    """The newest `NOTES` free-text bodies for a target."""
    t = tables.feedback
    stmt = (
        select(t.c.body)
        .where(t.c.kind == kind, t.c.target == target, t.c.body.is_not(None))
        .order_by(t.c.ts.desc(), t.c.id)
        .limit(NOTES)
    )
    with engine.connect() as conn:
        return [b for (b,) in conn.execute(stmt)]


def _top_feedback(engine: Engine, kind: str, *, rating: int | None = None) -> list[dict[str, Any]]:
    t = tables.feedback
    where = [t.c.kind == kind]
    if rating is not None:
        where.append(t.c.rating == rating)
    stmt = (
        select(t.c.target, func.count().label("n"), func.max(t.c.ts).label("last"))
        .where(*where)
        .group_by(t.c.target)
        .order_by(func.count().desc(), func.max(t.c.ts).desc(), t.c.target)
        .limit(TOP)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).all()
    return [
        {"target": target, "count": n, "notes": _notes(engine, kind, target)}
        for target, n, _ in rows
    ]


def lesson_miss_rates(engine: Engine) -> list[dict[str, Any]]:
    """Flashcard and quiz misses over attempts per deck, quiz or lesson id, across all users.

    The id is the attempt's `scope` (a lesson id, or the module id a module-level deck or quiz is
    studied under). Fewer than `MIN_ATTEMPTS` attempts is too few to rate.
    """
    t = tables.attempts
    misses = func.sum(case((t.c.result.in_(_MISSES), 1), else_=0))
    stmt = (
        select(t.c.scope, func.count().label("n"), misses.label("missed"))
        .where(t.c.kind.in_(("flashcard", "mcq")))
        .group_by(t.c.scope)
        .having(func.count() >= MIN_ATTEMPTS)
    )
    with engine.connect() as conn:
        rows = [(s, n, int(m or 0)) for s, n, m in conn.execute(stmt)]
    rows.sort(key=lambda r: (-r[2] / r[1], -r[1], r[0]))
    return [
        {"target": s, "count": n, "misses": m, "miss_rate": round(m / n, 3), "notes": []}
        for s, n, m in rows[:TOP]
    ]


def page_reads(agent_log: Path) -> list[dict[str, Any]]:
    """Per page, from the chat rows of `agent.jsonl`: answers that read it, cited it, cited it unread.

    `read` counts answers in which the agent called `read_page` on it. Search hits that were not
    then read are not logged, so they cannot be counted here. Ranked by `read`.
    """
    read: Counter[str] = Counter()
    cited: Counter[str] = Counter()
    ungrounded: Counter[str] = Counter()
    try:
        lines = agent_log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict) or row.get("source") != "chat":
            continue
        read.update(set(_ids(row.get("pages_read"))))
        cited.update(set(_ids(row.get("cited"))))
        ungrounded.update(set(_ids(row.get("ungrounded"))))
    pages = set(read) | set(cited)
    ranked = sorted(pages, key=lambda p: (-read[p], -cited[p], p))[:TOP]
    return [
        {
            "target": p,
            "count": read[p],
            "read": read[p],
            "cited": cited[p],
            "ungrounded": ungrounded[p],
            "notes": [],
        }
        for p in ranked
    ]


def _ids(value: object) -> list[str]:
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def summary(engine: Engine, agent_log: Path) -> dict[str, list[dict[str, Any]]]:
    """Top ten of each signal. Every item is `{target, count, ..., notes}`; `notes` is at most
    three bodies, newest first."""
    return {
        "answers_down": _top_feedback(engine, "answer", rating=-1),
        "pages_reported": _top_feedback(engine, "page"),
        "lessons_reported": _top_feedback(engine, "lesson"),
        "unanswered": _top_feedback(engine, "unanswered"),
        "lesson_miss_rates": lesson_miss_rates(engine),
        "page_reads": page_reads(agent_log),
    }
