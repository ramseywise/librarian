"""Codemap DuckDB schema — symbols, files, import edges for indexed repos.

Mirrors the meta/schema_version/built_at convention used by
app/mcp_server/server.py's .wiki_index.duckdb.
"""

from __future__ import annotations

import contextlib
import time
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / ".code_index.duckdb"
SCHEMA_VERSION = "2"

_SCHEMA_STATEMENTS = [
    "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, val TEXT)",
    """
    CREATE TABLE IF NOT EXISTS repos (
        repo_id         TEXT PRIMARY KEY,
        root_path       TEXT NOT NULL,
        language        TEXT,
        last_indexed_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS files (
        file_id       TEXT PRIMARY KEY,
        repo_id       TEXT NOT NULL,
        rel_path      TEXT NOT NULL,
        language      TEXT,
        content_hash  TEXT NOT NULL,
        loc           INTEGER,
        indexed_at    TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS files_repo ON files (repo_id)",
    """
    CREATE TABLE IF NOT EXISTS symbols (
        symbol_id     TEXT PRIMARY KEY,
        file_id       TEXT NOT NULL,
        repo_id       TEXT NOT NULL,
        name          TEXT NOT NULL,
        kind          TEXT NOT NULL,
        signature     TEXT,
        docstring     TEXT,
        parent_scope  TEXT,
        start_line    INTEGER NOT NULL,
        end_line      INTEGER NOT NULL,
        start_byte    INTEGER NOT NULL,
        end_byte      INTEGER NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS symbols_name ON symbols (name)",
    "CREATE INDEX IF NOT EXISTS symbols_file ON symbols (file_id)",
    "CREATE INDEX IF NOT EXISTS symbols_repo ON symbols (repo_id)",
    """
    CREATE TABLE IF NOT EXISTS edges (
        src_file_id   TEXT NOT NULL,
        dst_file_id   TEXT,
        dst_symbol    TEXT,
        edge_type     TEXT NOT NULL,
        weight        INTEGER DEFAULT 1,
        src_symbol_id TEXT,
        dst_symbol_id TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS edges_src ON edges (src_file_id)",
    "CREATE INDEX IF NOT EXISTS edges_dst ON edges (dst_file_id)",
]

# Additive schema migrations, keyed by the version they upgrade FROM.
# Applied in a loop by init_schema until no further migration is pending.
_MIGRATIONS: dict[str, list[str]] = {
    "1": [
        "ALTER TABLE edges ADD COLUMN src_symbol_id TEXT",
        "ALTER TABLE edges ADD COLUMN dst_symbol_id TEXT",
    ],
}


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Create all codemap tables/indexes if absent, and migrate schema_version."""
    for stmt in _SCHEMA_STATEMENTS:
        con.execute(stmt)

    row = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
    if not row:
        con.execute("INSERT INTO meta VALUES ('schema_version', ?)", [SCHEMA_VERSION])
        return

    current = row[0]
    while current in _MIGRATIONS:
        for stmt in _MIGRATIONS[current]:
            # column/table already present on an idempotent re-run — ignore
            with contextlib.suppress(duckdb.CatalogException):
                con.execute(stmt)
        current = str(int(current) + 1)
        con.execute("UPDATE meta SET val = ? WHERE key = 'schema_version'", [current])


def touch_built_at(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("INSERT OR REPLACE INTO meta VALUES ('built_at', ?)", [str(time.time())])


def get_con(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Open the codemap DB, creating the schema if this is a fresh file.

    read_only=True is for query-only consumers (the FastAPI service) — it
    assumes the schema already exists and will not attempt to create it.
    """
    con = duckdb.connect(str(DB_PATH), read_only=read_only)
    if not read_only:
        init_schema(con)
    return con
