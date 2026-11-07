"""The attempts store: one SQLite table for every graded study event.

A flashcard self-grade, a multiple-choice answer and a drill run are all rows of `attempts`:
(when, kind, item id, module or lesson id, result, optional JSON payload). The Leitner schedule
(`leitner.py`), the study home (`study.py`) and the coursework signals read it; nothing keeps a
second copy. It is personal study history, so it lives in the state dir (`var/attempts.sqlite3`,
gitignored) and never in `data/`: this repo is public.

An earlier version appended flashcard grades to `logs/flashcards.jsonl`. The first connection
imports that file once. The import is idempotent (a unique key on the event, so re-reading the
same file adds nothing) and leaves the file where it is.

Writes never raise: a store that cannot be written must not interrupt studying, so `record`
reports False and the route says `logged: false`.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

_settings = get_settings()
# Module-level so a test can point them at a temp dir, as the catalog's paths are.
DB_PATH = _settings.attempts_db
LEGACY_FLASHCARD_LOG = _settings.flashcard_log

KINDS = ("flashcard", "mcq", "drill")
# What each kind may record. `knew`/`correct`/`pass` are the good outcomes.
RESULTS: dict[str, tuple[str, ...]] = {
    "flashcard": ("knew", "missed"),
    "mcq": ("correct", "wrong"),
    "drill": ("pass", "fail", "revealed"),
}
GOOD = {"knew", "correct", "pass"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      TEXT NOT NULL,
    kind    TEXT NOT NULL,
    item    TEXT NOT NULL,
    scope   TEXT NOT NULL,
    result  TEXT NOT NULL,
    payload TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS attempts_event ON attempts (ts, kind, item, result);
CREATE INDEX IF NOT EXISTS attempts_item ON attempts (kind, item);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


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


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH, timeout=5)) as conn:
        conn.executescript(_SCHEMA)
        yield conn


def _now() -> str:
    return datetime.now(UTC).isoformat()


def record(
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
    try:
        with _connect() as conn:
            _import_legacy(conn)
            conn.execute(
                "INSERT OR IGNORE INTO attempts (ts, kind, item, scope, result, payload) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    ts or _now(),
                    kind,
                    item,
                    scope,
                    result,
                    json.dumps(payload, ensure_ascii=False) if payload else None,
                ),
            )
            conn.commit()
    except (sqlite3.Error, OSError) as e:
        log.warning("attempts.write_failed", error=str(e))
        return False
    return True


def _parse(row: tuple[Any, ...]) -> Attempt | None:
    ts_raw, kind, item, scope, result, payload = row
    try:
        ts = datetime.fromisoformat(ts_raw)
    except (TypeError, ValueError):
        return None
    try:
        body = json.loads(payload) if payload else {}
    except json.JSONDecodeError:
        body = {}
    return Attempt(
        ts if ts.tzinfo else ts.replace(tzinfo=UTC),
        kind,
        item,
        scope,
        result,
        body if isinstance(body, dict) else {},
    )


def attempts(kinds: Iterable[str] | None = None) -> list[Attempt]:
    """Every stored attempt of `kinds` (default all), oldest first. [] when nothing is stored yet."""
    if not DB_PATH.exists() and not LEGACY_FLASHCARD_LOG.exists():
        return []
    wanted = tuple(kinds) if kinds is not None else KINDS
    marks = ",".join("?" * len(wanted))
    try:
        with _connect() as conn:
            _import_legacy(conn)
            rows = conn.execute(
                f"SELECT ts, kind, item, scope, result, payload FROM attempts "
                f"WHERE kind IN ({marks}) ORDER BY ts, id",
                wanted,
            ).fetchall()
    except (sqlite3.Error, OSError) as e:
        log.warning("attempts.read_failed", error=str(e))
        return []
    return [a for row in rows if (a := _parse(row))]


def flashcard_rows() -> list[dict[str, Any]]:
    """Flashcard grades in the shape the old jsonl had (deck, front, result, source), for the signals report."""
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
        for a in attempts(["flashcard"])
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


def import_flashcard_log(conn: sqlite3.Connection, path: Path) -> int:
    """Add the grades in a flashcards.jsonl. Unreadable lines are skipped. Returns rows added."""
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
        key, ts, result = _legacy_key(rec), rec.get("ts"), rec.get("result")
        deck = rec.get("deck")
        if not key or not isinstance(ts, str) or result not in RESULTS["flashcard"]:
            continue
        payload = {k: rec[k] for k in ("front", "source", "lesson") if rec.get(k)}
        cur = conn.execute(
            "INSERT OR IGNORE INTO attempts (ts, kind, item, scope, result, payload) "
            "VALUES (?, 'flashcard', ?, ?, ?, ?)",
            (
                ts,
                key,
                deck if isinstance(deck, str) else "",
                result,
                json.dumps(payload, ensure_ascii=False) if payload else None,
            ),
        )
        added += cur.rowcount
    return added


def _import_legacy(conn: sqlite3.Connection) -> None:
    """Import the old log when it has changed since the last import (size and mtime are the marker)."""
    try:
        stat = LEGACY_FLASHCARD_LOG.stat()
    except OSError:
        return
    marker = hashlib.sha256(
        f"{LEGACY_FLASHCARD_LOG}:{stat.st_size}:{stat.st_mtime_ns}".encode()
    ).hexdigest()
    seen = conn.execute("SELECT value FROM meta WHERE key = 'flashcard_log'").fetchone()
    if seen and seen[0] == marker:
        return
    added = import_flashcard_log(conn, LEGACY_FLASHCARD_LOG)
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('flashcard_log', ?)", (marker,))
    conn.commit()
    if added:
        log.info("attempts.legacy_imported", rows=added)
