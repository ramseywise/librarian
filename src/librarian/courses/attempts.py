"""The attempts store: one table for every graded study event.

A flashcard self-grade, a multiple-choice answer and a drill run are all rows of `attempts`:
(whose, when, kind, item id, module or lesson id, result, optional JSON payload). Every read and
write names the user: one user's history is never another's. The Leitner schedule
(`leitner.py`), the study home (`study.py`) and the coursework signals read it; nothing keeps a
second copy. This module is a thin repository over the `attempts` table of `librarian.db`
(Postgres via `DATABASE_URL`, else a SQLite file in the state dir). It is personal study history,
so it never lives in `data/`: this repo is public.

An earlier version kept `var/attempts.sqlite3` (copy it in once with `librarian db
import-attempts`) and, before that, appended flashcard grades to `logs/flashcards.jsonl`. The
first connection imports that jsonl into the owner's history (`LIBRARIAN_OWNER_EMAIL`). The
import is idempotent (a unique key on the event, so re-reading the same file adds nothing) and
leaves the file where it is.

Writes never raise: a store that cannot be written must not interrupt studying, so `record`
reports False and the route says `logged: false`.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, Engine, Row, select
from sqlalchemy.exc import SQLAlchemyError

from librarian import accounts
from librarian.config import get_settings
from librarian.db import get_engine, tables, upsert
from librarian.db.attempt_rows import add_attempt, parse_ts
from librarian.log_config import get_logger

log = get_logger(__name__)

# Module-level so a test can point it at a temp dir, as the catalog's paths are.
LEGACY_FLASHCARD_LOG = get_settings().flashcard_log

KINDS = ("flashcard", "mcq", "drill")
# What each kind may record. `knew`/`correct`/`pass` are the good outcomes.
RESULTS: dict[str, tuple[str, ...]] = {
    "flashcard": ("knew", "missed"),
    "mcq": ("correct", "wrong"),
    "drill": ("pass", "fail", "revealed"),
}
GOOD = {"knew", "correct", "pass"}


@dataclass(frozen=True)
class Attempt:
    ts: datetime
    kind: str
    item: str
    scope: str  # the deck, quiz or lesson id it was studied under
    result: str
    payload: dict[str, Any]

    @property
    def good(self) -> bool:
        return self.result in GOOD

    @property
    def module(self) -> str:
        """`<course>/<module>` of the scope, the id the decks and quizzes use."""
        return "/".join(self.scope.split("/")[:2])


def record(
    user_id: str,
    kind: str,
    item: str,
    scope: str,
    result: str,
    *,
    payload: dict[str, Any] | None = None,
    ts: str | None = None,
) -> bool:
    """Store one graded event. False when the store cannot be written; ValueError on a bad kind/result."""
    if result not in RESULTS.get(kind, ()):
        raise ValueError(f"{result!r} is not a result of kind {kind!r}")
    when = parse_ts(ts) if ts else datetime.now(UTC)
    if when is None:
        raise ValueError(f"unreadable timestamp {ts!r}")
    try:
        engine = get_engine()
        _import_legacy(engine)
        with engine.begin() as conn:
            add_attempt(
                conn,
                engine,
                user_id=user_id,
                ts=when,
                kind=kind,
                item=item,
                scope=scope,
                result=result,
                payload=json.dumps(payload, ensure_ascii=False) if payload else None,
            )
    except (SQLAlchemyError, OSError) as e:
        log.warning("attempts.write_failed", error=str(e))
        return False
    return True


def _parse(row: Row[Any, Any, Any, Any, Any, Any]) -> Attempt:
    try:
        body = json.loads(row.payload) if row.payload else {}
    except json.JSONDecodeError:
        body = {}
    ts = row.ts if row.ts.tzinfo else row.ts.replace(tzinfo=UTC)  # SQLite returns naive UTC
    return Attempt(
        ts, row.kind, row.item, row.scope, row.result, body if isinstance(body, dict) else {}
    )


def attempts(user_id: str, kinds: Iterable[str] | None = None) -> list[Attempt]:
    """`user_id`'s attempts of `kinds` (default all), oldest first. [] when nothing is stored yet."""
    wanted = tuple(kinds) if kinds is not None else KINDS
    t = tables.attempts
    stmt = (
        select(t.c.ts, t.c.kind, t.c.item, t.c.scope, t.c.result, t.c.payload)
        .where(t.c.user_id == user_id, t.c.kind.in_(wanted))
        .order_by(t.c.ts, t.c.id)
    )
    try:
        engine = get_engine()
        _import_legacy(engine)
        with engine.connect() as conn:
            rows = conn.execute(stmt).all()
    except (SQLAlchemyError, OSError) as e:
        log.warning("attempts.read_failed", error=str(e))
        return []
    return [_parse(row) for row in rows]


def flashcard_rows(user_id: str) -> list[dict[str, Any]]:
    """A user's flashcard grades in the shape the old jsonl had (deck, front, result, source), for the signals report."""
    return [
        {
            "ts": a.ts.isoformat(),
            "deck": a.scope,
            "card": a.item,
            "result": a.result,
            "front": a.payload.get("front", ""),
            "source": a.payload.get("source", ""),
            "lesson": a.payload.get("lesson"),
        }
        for a in attempts(user_id, ["flashcard"])
    ]


# ── one-time import of logs/flashcards.jsonl ────────────────────────────────


def _legacy_key(rec: dict[str, Any]) -> str | None:
    from librarian.courses import leitner  # deferred: leitner imports this module

    key = rec.get("card")
    if isinstance(key, str) and key:
        return key
    deck, front = rec.get("deck"), rec.get("front")
    if isinstance(deck, str) and isinstance(front, str):
        return leitner.card_key(deck, front)
    return None


def import_flashcard_log(conn: Connection, engine: Engine, path: Path, user_id: str) -> int:
    """Add the grades in a flashcards.jsonl to `user_id`'s history. Unreadable lines are skipped. Returns rows added."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as e:
        log.warning("attempts.legacy_unreadable", error=str(e))
        return 0
    added = 0
    for line in lines:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        key, ts, result = _legacy_key(rec), parse_ts(rec.get("ts")), rec.get("result")
        deck = rec.get("deck")
        if not key or ts is None or result not in RESULTS["flashcard"]:
            continue
        payload = {k: rec[k] for k in ("front", "source", "lesson") if rec.get(k)}
        added += add_attempt(
            conn,
            engine,
            user_id=user_id,
            ts=ts,
            kind="flashcard",
            item=key,
            scope=deck if isinstance(deck, str) else "",
            result=result,
            payload=json.dumps(payload, ensure_ascii=False) if payload else None,
        )
    return added


def _import_legacy(engine: Engine) -> None:
    """Import the old log into the owner's history when it has changed since the last import.

    Size and mtime are the marker. The owner's row is resolved before the import's transaction
    opens, since creating it is a write of its own.
    """
    try:
        stat = LEGACY_FLASHCARD_LOG.stat()
    except OSError:
        return
    marker = hashlib.sha256(
        f"{LEGACY_FLASHCARD_LOG}:{stat.st_size}:{stat.st_mtime_ns}".encode()
    ).hexdigest()
    m = tables.meta
    with engine.connect() as conn:
        if conn.execute(select(m.c.value).where(m.c.key == "flashcard_log")).scalar() == marker:
            return
    owner = accounts.ensure_owner(engine, get_settings().owner_email)
    with engine.begin() as conn:
        added = import_flashcard_log(conn, engine, LEGACY_FLASHCARD_LOG, owner.id)
        conn.execute(
            upsert(engine, m)
            .values(key="flashcard_log", value=marker)
            .on_conflict_do_update(index_elements=["key"], set_={"value": marker})
        )
    if added:
        log.info("attempts.legacy_imported", rows=added)
