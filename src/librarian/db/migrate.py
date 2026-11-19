"""Run the Alembic migrations that ship inside this package."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, Engine, text

from librarian.log_config import get_logger

log = get_logger(__name__)

_HERE = Path(__file__).parent
_LOCK_ID = 7_261_001  # Postgres advisory lock: replicas starting together upgrade one at a time


def _config(connection: Connection) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(_HERE / "migrations"))
    cfg.attributes["connection"] = connection
    return cfg


def upgrade(engine: Engine, revision: str = "head") -> None:
    """Bring the database to `revision`. A second run changes nothing."""
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": _LOCK_ID})
        command.upgrade(_config(conn), revision)
    log.info("db.upgraded", revision=revision, dialect=engine.dialect.name)


class MigrationStateError(Exception):
    """The database holds a revision this code does not know (it is ahead of, or from, another build)."""


def pending(engine: Engine) -> list[str]:
    """Revisions this code ships that the database has not applied, oldest first. Read-only.

    A database that was never migrated has them all pending. Raises `MigrationStateError` when the
    database is at a revision not among this code's: that is not pending work, and an upgrade over
    it would not be safe either.
    """
    cfg = Config()
    cfg.set_main_option("script_location", str(_HERE / "migrations"))
    script = ScriptDirectory.from_config(cfg)
    with engine.connect() as conn:
        current = MigrationContext.configure(conn).get_current_heads()
    known = {r.revision for r in script.walk_revisions()}
    unknown = [r for r in current if r not in known]
    if unknown:
        raise MigrationStateError(f"database is at unknown revision(s): {', '.join(unknown)}")
    applied = {r.revision for c in current for r in script.iterate_revisions(c, "base")}
    ordered = [r.revision for r in script.walk_revisions()][::-1]  # base first
    return [rev for rev in ordered if rev not in applied]
