"""Evidence for staff-review F2: multi-word queries must recall stem/term matches.

Before the fix, search_wiki's candidate SQL was a whole-phrase LIKE — the literal
query string had to appear verbatim, so "compaction strategies" could not find a
page containing "strategies for compacting context". BM25 (DuckDB fts, Porter
stemming) cures this on the primary path; a tokenized per-term OR LIKE cures it
on the fallback path. These tests fail against the pre-fix server.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
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


def test_bm25_path_answers_without_degrading(wiki: Path) -> None:
    """A query DuckDB rejects falls back to LIKE, so recall tests alone can't see it."""
    rows, degraded = server._search_rows("compaction strategies", domain="", limit=5, tool="test")
    assert rows
    assert rows[0][0].endswith("context-compaction.md")
    assert not degraded


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
    rows, _ = server._search_rows("compacting context documents")
    scores = [r[6] for r in rows]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(s, float) for s in scores)


BLOCK_LIST_TAGS_PAGE = """---
title: Hybrid Search
tags:
  - rag
  - pattern
summary: Tags in YAML block-list form
updated: 2026-08-04
---

# Hybrid Search

BM25 fused with dense retrieval.
"""


def test_block_list_tags_parse() -> None:
    """LIB-110 R4: the hand-rolled parser indexed block-list-tagged pages with zero tags."""
    meta = server._parse_frontmatter(BLOCK_LIST_TAGS_PAGE)
    assert meta.get("tags") == ["rag", "pattern"]


def test_block_list_tagged_tombstone_stays_out_of_index(wiki: Path) -> None:
    """A tombstone whose tags use block-list form must still be excluded from search."""
    (wiki / "rag" / "old-retrieval-page.md").write_text(
        "---\n"
        "title: Old Retrieval Page\n"
        "tags:\n"
        "  - rag\n"
        "  - tombstone\n"
        "summary: Retired — superseded by Chunking.\n"
        "updated: 2026-08-04\n"
        "---\n\n"
        "# Old Retrieval Page\n\n"
        "Retired. Zombie retrieval verbiage that would otherwise rank.\n"
    )
    result = server.search_wiki("zombie retrieval verbiage")
    assert "Old Retrieval Page" not in result


def _page(wiki: Path, stem: str, title: str, body: str, extra: str = "") -> None:
    (wiki / "rag" / f"{stem}.md").write_text(
        f"---\ntitle: {title}\ntags: [rag, concept]\nsummary: {title}.\n{extra}"
        f"updated: 2026-11-05\n---\n\n# {title}\n\n{body}\n"
    )


def test_fallback_ranks_by_terms_matched_not_title_word(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Common query words match everywhere; they must not crowd out the page matching them all."""
    for i in range(20):
        _page(wiki, f"filler-{i}", f"What Filler {i}", "what")
    _page(wiki, "target", "Consensus Notes", "What zebra quorum means.")
    monkeypatch.setattr(server, "_ensure_fts", lambda con: False)
    rows, _ = server._search_rows("What zebra quorum?", limit=1, tool="test")
    assert rows[0][0].endswith("target.md")


@pytest.mark.parametrize("has_fts", [True, False], ids=["bm25", "fallback"])
def test_frontmatter_alias_is_searchable(
    wiki: Path, monkeypatch: pytest.MonkeyPatch, has_fts: bool
) -> None:
    """Indexed content is the whole file, frontmatter included, so aliases match without a column."""
    _page(wiki, "aliased", "Formal Name", "Body text.", extra="aliases: [zanzibarism]\n")
    if not has_fts:
        monkeypatch.setattr(server, "_ensure_fts", lambda con: False)
    rows, _ = server._search_rows("zanzibarism", limit=3, tool="test")
    assert rows[0][0].endswith("aliased.md")


class _FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool = True) -> np.ndarray:
        return np.array([[1.0, 0.0]])


def _row(path: str, score: float | None, backlinks: int, vec: list[float] | None) -> tuple:
    blob = server._vec_to_blob(vec) if vec else None
    return (path, path, "", "", "", backlinks, blob, score)


@pytest.fixture()
def embedded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(server, "_get_emb_model", lambda: _FakeModel())


@pytest.mark.usefixtures("embedded")
def test_a_heavily_linked_page_gets_no_lift_from_its_links() -> None:
    rows = [_row("hub", 1.0, 100, [0.5, 0.5]), _row("specific", 0.95, 0, [1.0, 0.0])]
    assert [r[0] for r in server._rerank("q", rows, 2)] == ["specific", "hub"]


@pytest.mark.usefixtures("embedded")
def test_similarity_can_overturn_a_small_text_lead() -> None:
    rows = [_row("keyword", 1.0, 0, [0.0, 1.0]), _row("meaning", 0.9, 0, [1.0, 0.0])]
    assert [r[0] for r in server._rerank("q", rows, 2)] == ["meaning", "keyword"]


@pytest.mark.usefixtures("embedded")
def test_a_large_text_lead_survives_a_small_similarity_gap() -> None:
    rows = [_row("strong", 1.0, 0, [0.6, 0.8]), _row("weak", 0.2, 0, [0.7, 0.71])]
    assert [r[0] for r in server._rerank("q", rows, 2)] == ["strong", "weak"]


@pytest.mark.usefixtures("embedded")
def test_a_page_with_no_embedding_still_ranks_on_text() -> None:
    rows = [_row("no-vector", 1.0, 0, None), _row("weak", 0.1, 0, [0.5, 0.5])]
    assert [r[0] for r in server._rerank("q", rows, 2)] == ["no-vector", "weak"]


def test_without_embeddings_the_candidate_order_stands(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    rows = [_row("first", None, 0, None), _row("second", None, 50, None)]
    assert [r[0] for r in server._rerank("q", rows, 2)] == ["first", "second"]
