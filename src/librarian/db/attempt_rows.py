"""Row-level access to `attempts`, shared by the courses repository and the SQLite import."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Connection, Engine

from librarian.db import tables
from librarian.db.engine import get_engine, upsert
from librarian.log_config import get_logger

log = get_logger(__name__)


def parse_ts(raw: object) -> datetime | None:
    """An ISO timestamp as an aware UTC datetime (naive input is read as UTC); None when unreadable."""
    if isinstance(raw, datetime):
        ts = raw
    else:
        try:
            ts = datetime.fromisoformat(str(raw))
        except ValueError:
            return None
    try:
        return (ts if ts.tzinfo else ts.replace(tzinfo=UTC)).astimezone(UTC)
    except (OverflowError, OSError):
        return None


def add_attempt(
    conn: Connection,
    engine: Engine,
    *,
    user_id: str,
    ts: datetime,
    kind: str,
    item: str,
    scope: str,
    result: str,
    payload: str | None,
) -> int:
    """Insert one event; the same event twice adds nothing. Returns rows added (0 or 1)."""
    stmt = (
        upsert(engine, tables.attempts)
        .values(
            user_id=user_id,
            ts=ts,
            kind=kind,
            item=item,
            scope=scope,
            result=result,
            payload=payload,
            event_key=tables.event_key(user_id, ts.isoformat(), kind, item, result),
        )
        .on_conflict_do_nothing(index_elements=["event_key"])
    )
    return conn.execute(stmt).rowcount


def import_sqlite_attempts(
    path: Path, *, user_id: str, engine: Engine | None = None
) -> tuple[int, int, int]:
    """Copy the rows of an old `attempts.sqlite3` into `user_id`'s history once. Returns (read, added, skipped).

    Idempotent: a row already present is not added again. The file is opened read-only and
    left alone. A row with an unreadable timestamp is skipped.
    """
    engine = engine or get_engine()
    uri = f"file:{path}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as old:
        rows = old.execute(
            "SELECT ts, kind, item, scope, result, payload FROM attempts ORDER BY id"
        ).fetchall()
    added = skipped = 0
    with engine.begin() as conn:
        for raw_ts, kind, item, scope, result, payload in rows:
            ts = parse_ts(raw_ts)
            if ts is None:
                skipped += 1
                continue
            added += add_attempt(
                conn,
                engine,
                user_id=user_id,
                ts=ts,
                kind=kind,
                item=item,
                scope=scope,
                result=result,
                payload=payload,
            )
    log.info("db.attempts_imported", read=len(rows), added=added, skipped=skipped)
    return len(rows), added, skipped
