"""User state in a SQL database: one SQLAlchemy Core engine, Alembic migrations, the tables.

`DATABASE_URL` picks Postgres; unset, a SQLite file in the state dir keeps `make api` and the
tests working with nothing installed. Code here is portable Core: the only dialect-specific
statement is the insert with `ON CONFLICT` (`engine.upsert`). This package imports no other
`librarian` layer.
"""

from librarian.db.engine import get_engine, reset_engines, upsert

__all__ = ["get_engine", "reset_engines", "upsert"]
