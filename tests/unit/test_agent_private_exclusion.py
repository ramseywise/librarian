"""Evidence for Buyi "wiki/private/ never leaves the machine", clause (b) — agent side.

tests/unit/test_private_exclusion.py covers the MCP server. The chat agent in
app/backend/agent.py reaches the same pages through its own rglob walk, so it needs
its own evidence: before the cure, _search_wiki and _read_page walked WIKI_DIR with
no private filter at all and served wiki/private/ content into the SSE chat panel.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.backend import agent

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
    """A wiki with one public and one private page, both reachable by the walk."""
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

    monkeypatch.setattr(agent, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(agent, "PRIVATE_DIR", wiki_dir / "private")
    return wiki_dir


def test_search_wiki_never_returns_private_content(wiki: Path) -> None:
    result = agent._search_wiki("ACME_SECRET_MARKER client billing")
    assert "client billing detail" not in result
    assert "acme-engagement" not in result


def test_search_wiki_still_returns_public_pages(wiki: Path) -> None:
    result = agent._search_wiki("chunking")
    assert "Chunking" in result


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


def test_private_filter_is_independent_of_server_cwd(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The agent's filter must not depend on the MCP server's relative PRIVATE_DIR.

    server.PRIVATE_DIR is Path("wiki")/"private" — relative, so under `make api`
    (cwd=app/) it resolves to a nonexistent app/wiki/private. Binding the agent to
    that would yield a filter that excludes nothing while still reading as correct.
    """
    from app.mcp_server import server

    monkeypatch.setattr(server, "PRIVATE_DIR", Path("nonexistent") / "private")

    assert agent._is_private(wiki / "private" / "acme-engagement.md")
    result = agent._read_page("acme-engagement")
    assert "ACME_SECRET_MARKER" not in result
