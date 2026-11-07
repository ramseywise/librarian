"""The engine: built from `DATABASE_URL`, one per URL per process, created on first use."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from sqlalchemy import Engine, Table, create_engine, event
from sqlalchemy.dialects.postgresql import Insert as PgInsert
from sqlalchemy.dialects.sqlite import Insert as SqliteInsert
from sqlalchemy.engine import make_url
from sqlalchemy.pool import ConnectionPoolEntry

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

_engines: dict[str, Engine] = {}
_lock = threading.Lock()


def database_url() -> str:
    """The configured URL with a psycopg 3 driver; SQLite in the state dir when unset."""
    return normalize_url(get_settings().database_url_or_default)


def normalize_url(url: str) -> str:
    """`postgres://` and `postgresql://` URLs name the psycopg 3 driver; anything else is as given."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def _sqlite_file(url: str) -> Path | None:
    parsed = make_url(url)
    if parsed.get_backend_name() != "sqlite" or parsed.database in (None, "", ":memory:"):
        return None
    return Path(str(parsed.database))


def _build(url: str) -> Engine:
    path = _sqlite_file(url)
    if path is None:
        return create_engine(url, pool_pre_ping=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, connect_args={"timeout": 5})

    @event.listens_for(engine, "connect")
    def _wal(dbapi_conn: sqlite3.Connection, _record: ConnectionPoolEntry) -> None:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.close()

    return engine


def get_engine(url: str | None = None) -> Engine:
    """The engine for `url` (default: the configured one). A SQLite database is migrated on first use.

    Postgres is not: run `librarian db upgrade` first (the container entrypoint does).
    """
    url = url or database_url()
    with _lock:
        engine = _engines.get(url)
        if engine is None:
            engine = _engines[url] = _build(url)
            if _sqlite_file(url) is not None:
                from librarian.db.migrate import upgrade

                upgrade(engine)
    return engine


def reset_engines() -> None:
    """Dispose every cached engine (tests, and a changed `DATABASE_URL`)."""
    with _lock:
        for engine in _engines.values():
            engine.dispose()
        _engines.clear()


def upsert(engine: Engine, table: Table) -> PgInsert | SqliteInsert:
    """An INSERT with `on_conflict_do_update` / `_do_nothing`, from the engine's own dialect."""
    if engine.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        return pg_insert(table)
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    return sqlite_insert(table)
