"""Evidence for Buyi "data/wiki/private/ never leaves the machine", clause (b) — agent side.

tests/app/test_private_exclusion.py covers the MCP server. The chat agent in
app/backend/agent.py used to reach the same pages through its own rglob walk; since
the S7 collapse it delegates to server._search_rows/_read_page_text, so these tests
now prove the delegation preserves the exclusion end-to-end from the agent's entry
points (the SSE chat panel's tool handlers).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.backend import agent
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
    """A wiki with one public and one private page, both reachable on disk."""
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

    # The agent delegates to the server core, so the seam is the server's anchors.
    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    return wiki_dir


def test_search_wiki_never_returns_private_content(wiki: Path) -> None:
    result = agent._search_wiki("ACME_SECRET_MARKER client billing")
    assert "client billing detail" not in result
    assert "acme-engagement" not in result


def test_search_wiki_still_returns_public_pages(wiki: Path) -> None:
    result = agent._search_wiki("chunking")
    assert "Chunking" in result


def test_search_wiki_excerpt_skips_frontmatter(wiki: Path) -> None:
    """Excerpts show page body, not the YAML block the index stores with it."""
    result = agent._search_wiki("chunking")
    assert "Public chunking notes." in result
    assert "updated: 2026-07-20" not in result


def test_read_page_refuses_private_by_id(wiki: Path) -> None:
    result = agent._read_page("acme-engagement")
    assert "ACME_SECRET_MARKER" not in result
    assert "not found" in result.lower()


def test_read_page_refuses_private_by_title(wiki: Path) -> None:
    """The title fallback must not become the way around the ID check."""
    result = agent._read_page("Acme Engagement")
    assert "ACME_SECRET_MARKER" not in result


def test_read_page_still_serves_public_pages(wiki: Path) -> None:
    result = agent._read_page("chunking")
    assert "Public chunking notes." in result


def test_server_anchor_is_absolute() -> None:
    """The shared filter must not depend on the process cwd.

    Before S5 the server anchored on a relative Path("data/wiki"), so under
    `make api` (cwd=app/) PRIVATE_DIR resolved to a nonexistent app/data/wiki/private
    — a filter that read as correct and excluded nothing. The agent now binds to the
    server's anchors, so absoluteness is the invariant that keeps clause (b) intact
    regardless of where uvicorn starts.
    """
    assert server.WIKI_DIR.is_absolute()
    assert server.PRIVATE_DIR.is_absolute()
    assert server.PRIVATE_DIR == server.WIKI_DIR / "private"
