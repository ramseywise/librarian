"""Retrieval telemetry + tombstone index exclusion (knowledge-compaction plan Steps 1–3)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Never

import duckdb
import pytest

from app.mcp_server import server

if TYPE_CHECKING:
    from pathlib import Path


def test_log_retrieval_appends_valid_json_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")

    server._log_retrieval("search_wiki", query="crag", domain="rag", n_results=3)

    lines = (tmp_path / "logs" / "retrieval.jsonl").read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["tool"] == "search_wiki"
    assert entry["query"] == "crag"
    assert entry["n_results"] == 3
    assert "ts" in entry


class _ExplodingPath:
    def mkdir(self, *a: object, **k: object) -> Never:
        raise OSError("read-only filesystem")


def test_log_retrieval_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "LOGS_DIR", _ExplodingPath())
    # Must not propagate — telemetry can never break retrieval
    server._log_retrieval("read_page", path="data/wiki/x.md", found=True)


@pytest.fixture()
def tmp_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "alive.md").write_text(
        "---\ntitle: Alive Page\ntags: [rag, concept]\nsummary: A live page\n"
        "updated: 2026-07-17\n---\n\n# Alive Page\n\nContent. [[Retired Page]]\n"
    )
    (wiki / "retired.md").write_text(
        "---\ntitle: Retired Page\ntags: [rag, tombstone]\nsummary: Retired\n"
        "updated: 2026-07-17\n---\n\n# Retired Page\n\nSee [[Alive Page]] — supersedes\n"
    )
    monkeypatch.setattr(server, "WIKI_DIR", wiki)
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    return wiki


def test_build_index_skips_tombstones(tmp_wiki: Path, tmp_path: Path) -> None:
    con = duckdb.connect(str(tmp_path / "idx.duckdb"))
    server.build_index(con)
    paths = [r[0] for r in con.execute("SELECT path FROM pages").fetchall()]
    con.close()

    assert any("alive.md" in p for p in paths)
    assert not any("retired.md" in p for p in paths)


def test_tombstone_still_readable(tmp_wiki: Path) -> None:
    content = server.read_page.fn if hasattr(server.read_page, "fn") else server.read_page
    result = content(str(tmp_wiki / "retired.md"))
    assert "supersedes" in result
