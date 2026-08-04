"""Evidence for Buyi "data/wiki/private/ never leaves the machine", clause (b).

Cures the BY-4 debt record: build_index indexed data/wiki/private/ and every read
tool served it. These tests fail against the pre-cure server.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from app.mcp_server import server

PAGE = """---
title: {title}
tags: [rag, concept]
summary: {summary}
updated: 2026-07-20
---

# {title}

{body}
"""


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A wiki with one public and one private page, both indexed-eligible."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir(parents=True)

    (wiki_dir / "rag" / "chunking.md").write_text(
        PAGE.format(title="Chunking", summary="How to chunk", body="Public chunking notes.")
    )
    (wiki_dir / "private" / "acme-engagement.md").write_text(
        PAGE.format(
            title="Acme Engagement",
            summary="Client roadmap",
            body="ACME_SECRET_MARKER client billing detail.",
        )
    )

    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    return wiki_dir


def test_build_index_excludes_private_pages(wiki: Path) -> None:
    con = duckdb.connect(":memory:")
    server.build_index(con)

    paths = [r[0] for r in con.execute("SELECT path FROM pages").fetchall()]
    con.close()

    # tmp_path itself resolves under /private/var on macOS — compare wiki-relative
    rel = [str(Path(p).relative_to(wiki)) for p in paths]
    assert rel == ["rag/chunking.md"], f"only the public page may be indexed, got {rel}"


def test_search_wiki_never_returns_private_content(wiki: Path) -> None:
    # The query is echoed back in the no-results message, so assert on the page
    # body and path instead of on the marker alone.
    result = server.search_wiki("ACME_SECRET_MARKER")
    assert "client billing detail" not in result
    assert "acme-engagement" not in result


def test_read_page_refuses_private_path(wiki: Path) -> None:
    result = server.read_page(str(wiki / "private" / "acme-engagement.md"))
    assert "ACME_SECRET_MARKER" not in result
    assert "not found" in result.lower()


def test_read_page_refuses_private_by_title(wiki: Path) -> None:
    result = server.read_page("Acme Engagement")
    assert "ACME_SECRET_MARKER" not in result


def test_read_page_refuses_private_via_traversal(wiki: Path) -> None:
    """A ../ path that lands inside private/ is still private."""
    result = server.read_page(str(wiki / "rag" / ".." / "private" / "acme-engagement.md"))
    assert "ACME_SECRET_MARKER" not in result


def test_read_page_still_serves_public_pages(wiki: Path) -> None:
    result = server.read_page("rag/chunking.md")
    assert "Public chunking notes." in result


@pytest.mark.parametrize(
    "attack_path",
    [
        "/etc/passwd",
        ".env",
        "../../.env",
        "data/wiki/../../.env",
    ],
)
def test_read_page_refuses_paths_outside_wiki(wiki: Path, attack_path: str) -> None:
    """Existing files outside WIKI_DIR are indistinguishable from missing pages."""
    result = server.read_page(attack_path)
    assert "not found" in result.lower()
    assert "root:" not in result  # /etc/passwd content
    assert "API_KEY" not in result  # .env content


def test_read_page_refuses_absolute_path_outside_wiki(wiki: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    outside.write_text("OUTSIDE_WIKI_MARKER")
    result = server.read_page(str(outside))
    assert "OUTSIDE_WIKI_MARKER" not in result
    assert "not found" in result.lower()


def test_list_pages_omits_private(wiki: Path) -> None:
    result = server.list_pages()
    assert "acme-engagement" not in result
    assert "Chunking" in result


def test_list_domain_rejects_private_as_domain(wiki: Path) -> None:
    result = server.list_domain("private")
    assert "acme-engagement" not in result
    assert "Unknown domain" in result


def test_get_domain_briefing_rejects_private_as_domain(wiki: Path) -> None:
    result = server.get_domain_briefing("private")
    assert "ACME_SECRET_MARKER" not in result
    assert "Unknown domain" in result
