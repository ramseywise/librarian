from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest

from tools.codemap import symbol_embeddings


@pytest.fixture()
def con(tmp_path: Path) -> Iterator[duckdb.DuckDBPyConnection]:
    connection = duckdb.connect(str(tmp_path / "embed_test.duckdb"))
    connection.execute(
        """
        CREATE TABLE symbols (
            symbol_id TEXT PRIMARY KEY, file_id TEXT, repo_id TEXT,
            name TEXT, kind TEXT, signature TEXT, docstring TEXT
        )
        """
    )
    connection.execute(
        "INSERT INTO symbols VALUES "
        "('f1:0', 'f1', 'repo', 'foo', 'function', 'def foo()', 'does foo')"
    )
    yield connection
    connection.close()


@pytest.mark.unit
def test_sync_embeddings_is_noop_when_dependency_absent(con: duckdb.DuckDBPyConnection) -> None:
    """This dev environment has [codemap] installed without [api], so
    sentence-transformers is genuinely absent here — this exercises the real
    graceful-absence path, not a mock."""
    if symbol_embeddings.HAS_EMBEDDINGS:
        pytest.skip("sentence-transformers is installed in this environment")
    assert symbol_embeddings.sync_embeddings(con) == 0


@pytest.mark.unit
def test_semantic_search_returns_empty_when_dependency_absent(
    con: duckdb.DuckDBPyConnection,
) -> None:
    if symbol_embeddings.HAS_EMBEDDINGS:
        pytest.skip("sentence-transformers is installed in this environment")
    assert symbol_embeddings.semantic_search(con, "foo") == []


@pytest.mark.unit
def test_ensure_table_is_idempotent(con: duckdb.DuckDBPyConnection) -> None:
    symbol_embeddings.ensure_table(con)
    symbol_embeddings.ensure_table(con)  # must not raise
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    assert "symbol_embeddings" in tables
