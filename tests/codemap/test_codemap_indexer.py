from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from librarian.tools.codemap import db as codemap_db
from librarian.tools.codemap.indexer import (
    RepoConfig,
    _resolve_call_edges,
    _resolve_import_edges,
    index_repo,
)

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

    yield repo_dir

    if db_path.exists():
        db_path.unlink()


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
        for row in con.execute("SELECT name FROM symbols WHERE repo_id = 'fixture'").fetchall()
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


def _index(repo_dir: Path) -> dict:
    con = codemap_db.get_con(read_only=False)
    try:
        counts = index_repo(con, RepoConfig(repo_id="fixture", root_path=repo_dir))
        _resolve_import_edges(con)
        _resolve_call_edges(con)
    finally:
        con.close()
    return counts


def _call_targets(callee: str) -> list[tuple[str, str]]:
    con = codemap_db.get_con(read_only=False)
    try:
        return con.execute(
            "SELECT e.dst_symbol_id, s.file_id FROM edges e "
            "LEFT JOIN symbols s ON s.symbol_id = e.dst_symbol_id "
            "WHERE e.edge_type = 'call' AND e.dst_symbol = ?",
            [callee],
        ).fetchall()
    finally:
        con.close()


@pytest.mark.unit
def test_editing_callee_file_keeps_cross_file_callers_resolved(temp_repo: Path) -> None:
    (temp_repo / "lib.py").write_text("def helper():\n    return 1\n")
    (temp_repo / "app.py").write_text("def main():\n    return helper()\n")
    _index(temp_repo)
    assert _call_targets("helper") == [("fixture:lib.py:0", "fixture:lib.py")]

    # shift helper's start_byte so its symbol id changes
    (temp_repo / "lib.py").write_text("# moved\n\ndef helper():\n    return 2\n")
    counts = _index(temp_repo)
    assert counts["parsed"] == 1

    targets = _call_targets("helper")
    assert len(targets) == 1
    assert targets[0][0] != "fixture:lib.py:0"
    assert targets[0][1] == "fixture:lib.py"  # id still joins to a live symbol


@pytest.mark.unit
def test_editing_callee_does_not_duplicate_fanned_out_edges(temp_repo: Path) -> None:
    (temp_repo / "a.py").write_text("def run():\n    return 1\n")
    (temp_repo / "b.py").write_text("def run():\n    return 2\n")
    (temp_repo / "app.py").write_text("def main():\n    run()\n")
    _index(temp_repo)
    assert len(_call_targets("run")) == 2

    (temp_repo / "a.py").write_text("# x\ndef run():\n    return 3\n")
    _index(temp_repo)
    targets = _call_targets("run")
    assert len(targets) == 2
    assert all(file_id is not None for _, file_id in targets)


@pytest.mark.unit
def test_deleting_file_leaves_no_dangling_edges(temp_repo: Path) -> None:
    (temp_repo / "lib.py").write_text("def helper():\n    return 1\n")
    (temp_repo / "app.py").write_text("import lib\n\ndef main():\n    return helper()\n")
    _index(temp_repo)

    (temp_repo / "lib.py").unlink()
    counts = _index(temp_repo)
    assert counts["removed"] == 1

    con = codemap_db.get_con(read_only=False)
    try:
        dangling = con.execute(
            "SELECT count(*) FROM edges WHERE "
            "(dst_symbol_id IS NOT NULL AND dst_symbol_id NOT IN (SELECT symbol_id FROM symbols)) "
            "OR (dst_file_id IS NOT NULL AND dst_file_id NOT IN (SELECT file_id FROM files)) "
            "OR src_file_id NOT IN (SELECT file_id FROM files)"
        ).fetchone()
    finally:
        con.close()
    assert dangling == (0,)


@pytest.mark.unit
def test_deleting_db_reindexes_everything(temp_repo: Path) -> None:
    _index(temp_repo)
    codemap_db.DB_PATH.unlink()

    counts = _index(temp_repo)
    assert counts["parsed"] == 1
    assert counts["skipped"] == 0


@pytest.mark.unit
def test_repo_under_excluded_dir_name_still_indexes(tmp_path: Path) -> None:
    from librarian.tools.codemap.indexer import _iter_source_files

    root = tmp_path / "build" / "proj"
    root.mkdir(parents=True)
    (root / "a.py").write_text("def a():\n    pass\n")
    assert [p.name for p in _iter_source_files(root)] == ["a.py"]


@pytest.mark.unit
def test_excluded_dirs_are_not_descended(tmp_path: Path) -> None:
    from librarian.tools.codemap.indexer import _iter_source_files

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("x = 1\n")
    (tmp_path / "node_modules" / "pkg").mkdir(parents=True)
    (tmp_path / "node_modules" / "pkg" / "bad.py").write_text("x = 1\n")
    (tmp_path / "src" / "build").mkdir()
    (tmp_path / "src" / "build" / "bad2.py").write_text("x = 1\n")
    assert [p.name for p in _iter_source_files(tmp_path)] == ["ok.py"]


@pytest.mark.unit
def test_api_returns_503_when_index_is_locked_in_process(
    temp_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from fastapi import HTTPException

    from librarian.tools.codemap import api

    monkeypatch.setattr(api, "_OPEN_BACKOFF_S", 0)
    writer = codemap_db.get_con(read_only=False)
    try:
        with pytest.raises(HTTPException) as exc:
            api._con()
    finally:
        writer.close()
    assert exc.value.status_code == 503


@pytest.mark.unit
def test_api_returns_503_when_another_process_holds_the_lock(
    temp_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess
    import sys

    from fastapi import HTTPException

    from librarian.tools.codemap import api

    codemap_db.get_con(read_only=False).close()  # create the file and schema
    monkeypatch.setattr(api, "_OPEN_BACKOFF_S", 0)
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import duckdb, sys; c = duckdb.connect(sys.argv[1]); print('ready', flush=True); "
            "sys.stdin.read()",
            str(codemap_db.DB_PATH),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "ready"
        with pytest.raises(HTTPException) as exc:
            api._con()
        assert exc.value.status_code == 503
    finally:
        holder.communicate("", timeout=10)

    api._con().close()  # lock released: opens normally


@pytest.mark.unit
def test_api_returns_503_when_index_missing(temp_repo: Path) -> None:
    from fastapi import HTTPException

    from librarian.tools.codemap import api

    with pytest.raises(HTTPException) as exc:
        api._con()
    assert exc.value.status_code == 503
