from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tools.codemap import db as codemap_db
from tools.codemap import manifest as codemap_manifest
from tools.codemap.indexer import RepoConfig, _resolve_call_edges, _resolve_import_edges, index_repo

FIXTURE_SRC = '''\
def hello(name: str) -> str:
    """Say hello."""
    return f"hello {name}"


class Greeter:
    def greet(self):
        return hello("world")
'''


@pytest.fixture()
def temp_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    repo_dir = tmp_path / "fixture_repo"
    repo_dir.mkdir()
    (repo_dir / "greet.py").write_text(FIXTURE_SRC)

    db_path = tmp_path / "test_code_index.duckdb"
    monkeypatch.setattr(codemap_db, "DB_PATH", db_path)

    manifest_path = tmp_path / "test_manifest.jsonl"
    monkeypatch.setattr(codemap_manifest, "MANIFEST_PATH", manifest_path)

    yield repo_dir

    if db_path.exists():
        db_path.unlink()
    if manifest_path.exists():
        manifest_path.unlink()


@pytest.mark.unit
def test_index_repo_populates_tables(temp_repo: Path) -> None:
    con = codemap_db.get_con(read_only=False)
    repo = RepoConfig(repo_id="fixture", root_path=temp_repo)
    counts = index_repo(con, repo)

    assert counts["parsed"] == 1
    assert counts["errors"] == 0

    files = con.execute("SELECT rel_path FROM files WHERE repo_id = 'fixture'").fetchall()
    assert files == [("greet.py",)]

    symbols = con.execute(
        "SELECT name, kind FROM symbols WHERE repo_id = 'fixture' ORDER BY name"
    ).fetchall()
    assert ("Greeter", "class") in symbols
    assert ("greet", "method") in symbols
    assert ("hello", "function") in symbols

    con.close()


@pytest.mark.unit
def test_reindex_unchanged_file_is_skipped(temp_repo: Path) -> None:
    con = codemap_db.get_con(read_only=False)
    repo = RepoConfig(repo_id="fixture", root_path=temp_repo)

    first = index_repo(con, repo)
    assert first["parsed"] == 1

    second = index_repo(con, repo)
    assert second["parsed"] == 0
    assert second["skipped"] == 1

    con.close()


@pytest.mark.unit
def test_changing_one_file_reparses_only_that_file(temp_repo: Path) -> None:
    (temp_repo / "other.py").write_text("def other():\n    return 1\n")

    con = codemap_db.get_con(read_only=False)
    repo = RepoConfig(repo_id="fixture", root_path=temp_repo)
    index_repo(con, repo)

    (temp_repo / "greet.py").write_text(FIXTURE_SRC + "\n\ndef added():\n    return 2\n")

    counts = index_repo(con, repo)
    assert counts["parsed"] == 1
    assert counts["skipped"] == 1

    names = {
        row[0]
        for row in con.execute(
            "SELECT name FROM symbols WHERE repo_id = 'fixture'"
        ).fetchall()
    }
    assert "added" in names
    assert "other" in names

    con.close()


@pytest.mark.unit
def test_call_edges_resolve_to_correct_callee(temp_repo: Path) -> None:
    con = codemap_db.get_con(read_only=False)
    repo = RepoConfig(repo_id="fixture", root_path=temp_repo)
    index_repo(con, repo)
    _resolve_import_edges(con)
    _resolve_call_edges(con)

    rows = con.execute(
        "SELECT dst_symbol, dst_symbol_id FROM edges "
        "WHERE edge_type = 'call' AND dst_symbol = 'hello'"
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][1] is not None
    assert rows[0][1].endswith(":greet.py:0")  # hello() starts at byte 0

    con.close()


@pytest.mark.unit
def test_ambiguous_call_name_fans_out_to_one_edge_per_match(temp_repo: Path) -> None:
    (temp_repo / "greet.py").write_text(
        "class A:\n"
        "    def run(self):\n"
        "        return 1\n\n"
        "class B:\n"
        "    def run(self):\n"
        "        return 2\n\n"
        "def caller():\n"
        "    run()\n"
    )

    con = codemap_db.get_con(read_only=False)
    repo = RepoConfig(repo_id="fixture", root_path=temp_repo)
    index_repo(con, repo)
    _resolve_call_edges(con)

    rows = con.execute(
        "SELECT dst_symbol_id FROM edges WHERE edge_type = 'call' AND dst_symbol = 'run'"
    ).fetchall()
    assert len(rows) == 2
    assert len({r[0] for r in rows}) == 2  # each edge points at a distinct A.run/B.run symbol_id

    con.close()
