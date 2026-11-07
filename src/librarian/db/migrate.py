"""Run the Alembic migrations that ship inside this package."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
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
