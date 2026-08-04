"""Evidence for staff-review F2: multi-word queries must recall stem/term matches.

Before the fix, search_wiki's candidate SQL was a whole-phrase LIKE — the literal
query string had to appear verbatim, so "compaction strategies" could not find a
page containing "strategies for compacting context". BM25 (DuckDB fts, Porter
stemming) cures this on the primary path; a tokenized per-term OR LIKE cures it
on the fallback path. These tests fail against the pre-fix server.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.mcp_server import server

PAGE = """---
title: {title}
tags: [{tags}]
summary: {summary}
updated: 2026-08-04
---

# {title}

{body}
"""


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A wiki where the target page never contains the query phrase verbatim."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "context").mkdir(parents=True)
    (wiki_dir / "rag").mkdir(parents=True)

    (wiki_dir / "context" / "context-compaction.md").write_text(
        PAGE.format(
            title="Context Compaction",
            tags="context, pattern",
            summary="Keeping the window lean",
            body="Strategies for compacting context: summarize, prune, checkpoint.",
        )
    )
    (wiki_dir / "rag" / "chunking.md").write_text(
        PAGE.format(
            title="Chunking",
            tags="rag, concept",
            summary="Splitting documents",
            body="Fixed-size and semantic chunking of documents.",
        )
    )

    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    return wiki_dir


def test_multiword_query_recalls_stemmed_page(wiki: Path) -> None:
    """The phrase "compaction strategies" never appears verbatim — stems must match."""
    result = server.search_wiki("compaction strategies")
    assert "Context Compaction" in result, (
        "a multi-word query must reach a page containing its terms in any "
        "order/inflection; whole-phrase LIKE returns nothing here"
    )


def test_fallback_tokenized_like_recalls_per_term(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With fts unavailable, per-term OR LIKE still finds the page."""
    monkeypatch.setattr(server, "_ensure_fts", lambda con: False)
    result = server.search_wiki("compaction strategies")
    assert "Context Compaction" in result


def test_irrelevant_pages_stay_out(wiki: Path) -> None:
    result = server.search_wiki("compaction strategies")
    assert "Chunking" not in result


def test_search_rows_scores_are_descending(wiki: Path) -> None:
    rows = server._search_rows("compacting context documents")
    scores = [r[6] for r in rows]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(s, float) for s in scores)
