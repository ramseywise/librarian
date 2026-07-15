from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from tools.codemap import db as codemap_db


def _build_v1_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Recreates the exact v1 edges table shape (no src_symbol_id/dst_symbol_id)
    to prove init_schema migrates a pre-existing v1 database correctly."""
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, val TEXT)")
    con.execute(
        """
        CREATE TABLE edges (
            src_file_id   TEXT NOT NULL,
            dst_file_id   TEXT,
            dst_symbol    TEXT,
            edge_type     TEXT NOT NULL,
            weight        INTEGER DEFAULT 1
        )
        """
    )
    con.execute("INSERT INTO meta VALUES ('schema_version', '1')")


@pytest.fixture()
def v1_db_path(tmp_path: Path) -> Path:
    return tmp_path / "v1_test.duckdb"


@pytest.mark.unit
def test_init_schema_migrates_v1_db_to_v2(v1_db_path: Path) -> None:
    con = duckdb.connect(str(v1_db_path))
    _build_v1_schema(con)

    codemap_db.init_schema(con)

    version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
    assert version[0] == "2"

    columns = {row[1] for row in con.execute("PRAGMA table_info(edges)").fetchall()}
    assert "src_symbol_id" in columns
    assert "dst_symbol_id" in columns

    con.close()


@pytest.mark.unit
def test_init_schema_is_idempotent_on_already_migrated_db(v1_db_path: Path) -> None:
    con = duckdb.connect(str(v1_db_path))
    _build_v1_schema(con)
    codemap_db.init_schema(con)
    # second call must not raise (columns already exist)
    codemap_db.init_schema(con)

    version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
    assert version[0] == "2"

    con.close()


@pytest.mark.unit
def test_init_schema_on_fresh_db_gets_final_shape_directly(v1_db_path: Path) -> None:
    con = duckdb.connect(str(v1_db_path))
    codemap_db.init_schema(con)

    version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
    assert version[0] == codemap_db.SCHEMA_VERSION

    columns = {row[1] for row in con.execute("PRAGMA table_info(edges)").fetchall()}
    assert "src_symbol_id" in columns
    assert "dst_symbol_id" in columns

    con.close()
