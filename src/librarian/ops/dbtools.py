"""The database side of backup and restore: dump, count rows, read the Alembic revision.

SQLite goes through `sqlite3.Connection.backup` (a consistent copy while the API writes);
Postgres through `pg_dump -Fc` and `pg_restore`. Counts and the revision are read from the same
snapshot as the dump, so a write during the backup cannot make the restore check fail.
Engines here are plain `create_engine`s: `librarian.db.get_engine` migrates a SQLite file on
first use, and a check must not change what it checks.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, create_engine
from sqlalchemy.engine import URL, make_url

import librarian.db.migrate as migrate
from librarian.db.engine import normalize_url
from librarian.ops import proc
from librarian.ops.proc import OpsError

VERSION_TABLE = "alembic_version"


@dataclass(frozen=True)
class Snapshot:
    dialect: str
    counts: dict[str, int]
    revision: str | None


def parse(url: str) -> URL:
    return make_url(normalize_url(url))


def sqlite_path(url: str) -> Path | None:
    parsed = parse(url)
    if parsed.get_backend_name() != "sqlite" or parsed.database in (None, "", ":memory:"):
        return None
    return Path(str(parsed.database))


def code_head() -> str:
    """The newest Alembic revision this code ships."""
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(migrate.__file__).parent / "migrations"))
    head = ScriptDirectory.from_config(cfg).get_current_head()
    if head is None:
        raise OpsError("the migrations have no head")
    return head


def known_revision(revision: str) -> bool:
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(migrate.__file__).parent / "migrations"))
    try:
        return ScriptDirectory.from_config(cfg).get_revision(revision) is not None
    except Exception:  # alembic raises CommandError for an unknown id; any failure means unknown
        return False


def _read(conn: Connection) -> tuple[dict[str, int], str | None]:
    from sqlalchemy import inspect

    prep = conn.dialect.identifier_preparer
    names = sorted(inspect(conn).get_table_names())
    counts = {
        n: int(conn.exec_driver_sql(f"SELECT count(*) FROM {prep.quote(n)}").scalar() or 0)
        for n in names
        if n != VERSION_TABLE
    }
    revision = None
    if VERSION_TABLE in names:
        revision = conn.exec_driver_sql(f"SELECT version_num FROM {VERSION_TABLE}").scalar()
    return counts, revision


def read_state(url: str) -> Snapshot:
    """Row counts and Alembic revision of an existing database."""
    path = sqlite_path(url)
    if path is not None and not path.is_file():
        return Snapshot("sqlite", {}, None)
    engine = create_engine(normalize_url(url))
    try:
        with engine.connect() as conn:
            counts, revision = _read(conn)
            return Snapshot(engine.dialect.name, counts, revision)
    finally:
        engine.dispose()


def is_empty(url: str) -> bool:
    """No rows in any table (a missing or freshly created database counts as empty)."""
    return not any(read_state(url).counts.values())


# ── dump ─────────────────────────────────────────────────────────────────────


def dump_sqlite(path: Path, out: Path) -> Snapshot:
    if not path.is_file():
        raise OpsError(f"SQLite database not found: {path}")
    with (
        closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as src,
        closing(sqlite3.connect(out)) as dst,
    ):
        src.backup(dst)
    return read_state(f"sqlite:///{out}")


def pg_args(url: str) -> tuple[list[str], dict[str, str]]:
    """libpq connection flags and env: the password goes in PGPASSWORD, never on the command line."""
    u = parse(url)
    args = ["--host", u.host or "localhost", "--port", str(u.port or 5432)]
    if u.username:
        args += ["--username", u.username]
    env = {"PGPASSWORD": u.password} if u.password else {}
    return args, env


class _PgSnapshot(Protocol):
    id: str

    def read(self) -> tuple[dict[str, int], str | None]: ...


class _LivePgSnapshot:
    def __init__(self, conn: Connection, snapshot_id: str) -> None:
        self.id = snapshot_id
        self._conn = conn

    def read(self) -> tuple[dict[str, int], str | None]:
        return _read(self._conn)


@contextmanager
def _pg_snapshot(url: str) -> Iterator[_PgSnapshot]:
    """An exported snapshot held open, so pg_dump and the counts see the same data."""
    engine = create_engine(normalize_url(url))
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            snap_id = str(conn.exec_driver_sql("SELECT pg_export_snapshot()").scalar())
            try:
                yield _LivePgSnapshot(conn, snap_id)
            finally:
                conn.rollback()
    finally:
        engine.dispose()


def dump_postgres(url: str, out: Path) -> Snapshot:
    args, env = pg_args(url)
    dbname = parse(url).database or "postgres"
    proc.require("pg_dump")
    with _pg_snapshot(url) as snap:
        proc.run(
            [
                "pg_dump",
                "-Fc",
                *args,
                "--dbname",
                dbname,
                "--snapshot",
                snap.id,
                "--file",
                str(out),
            ],
            env=env,
        )
        counts, revision = snap.read()
    return Snapshot("postgresql", counts, revision)


def dump_database(url: str, out: Path) -> Snapshot:
    path = sqlite_path(url)
    if path is not None:
        return dump_sqlite(path, out)
    if parse(url).get_backend_name() == "postgresql":
        return dump_postgres(url, out)
    raise OpsError(f"unsupported database for backup: {parse(url).get_backend_name()}")
