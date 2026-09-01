"""Tests for one-hop typed-relationship expansion (spike)."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest

from app.mcp_server import server
from app.mcp_server.graph_expansion import (
    EXPANSION_RELATIONSHIPS,
    build_typed_edges,
    expand_one_hop,
)

PAGES = [
    (
        "foundations/transformer.md",
        "Transformer Architecture",
        "# Transformer Architecture\n\nAttention blocks.\n",
    ),
    (
        "infra/inference-economics.md",
        "LLM Inference Economics",
        "# LLM Inference Economics\n\nPrefill versus decode.\n\n"
        "## See Also\n"
        "- [[Transformer Architecture]] — prerequisite-for\n"
        "- [[Prefix Caching]] — instance-of\n",
    ),
    (
        "context/prefix-caching.md",
        "Prefix Caching",
        "# Prefix Caching\n\nReuse the KV prefix.\n\n"
        "## See Also\n"
        "- [[LLM Inference Economics]] — extends\n",
    ),
    (
        "rag/unrelated.md",
        "Chunking Strategy",
        "# Chunking Strategy\n\nSplit documents.\n\nNo typed links here.\n",
    ),
]


def test_build_typed_edges_extracts_only_annotated_links() -> None:
    edges = build_typed_edges(PAGES)
    rels = {(s.split("/")[-1], t.split("/")[-1], r) for s, t, r in edges}
    assert ("inference-economics.md", "transformer.md", "prerequisite-for") in rels
    assert ("inference-economics.md", "prefix-caching.md", "instance-of") in rels
    assert ("prefix-caching.md", "inference-economics.md", "extends") in rels
    # The page with no typed annotations contributes nothing.
    assert not any(s.endswith("unrelated.md") for s, _, _ in edges)


def test_build_typed_edges_drops_unresolvable_links() -> None:
    pages = [
        ("a.md", "Page A", "## See Also\n- [[Nonexistent Page]] — extends\n"),
    ]
    assert build_typed_edges(pages) == []


def test_expansion_follows_prerequisite_forward() -> None:
    """A seed's declared prerequisite is surfaced as a foundation."""
    edges = build_typed_edges(PAGES)
    out = expand_one_hop(["infra/inference-economics.md"], edges)
    hits = {path: rel for path, rel, _ in out}
    assert hits["foundations/transformer.md"] == "prerequisite-for"


def test_expansion_labels_reverse_traversal_as_inverse() -> None:
    """Walking `prerequisite-for` backwards must not claim the dependent is a foundation.

    `inference-economics` declares `[[Transformer Architecture]] — prerequisite-for`,
    meaning the transformer page is the foundation. Seeding on the transformer page
    should surface inference-economics as something that *builds on* it — not as a
    prerequisite, which would invert the hierarchy.
    """
    edges = build_typed_edges(PAGES)
    out = expand_one_hop(["foundations/transformer.md"], edges)
    hits = {path: rel for path, rel, _ in out}
    assert hits["infra/inference-economics.md"] == "builds-on"


def test_expansion_excludes_untyped_and_non_expansion_relationships() -> None:
    """`instance-of` is a real edge but not one we traverse."""
    edges = build_typed_edges(PAGES)
    # Precondition: the fixture must contain an edge type we do NOT traverse,
    # otherwise the exclusion assertions below pass vacuously.
    assert any(r not in EXPANSION_RELATIONSHIPS for _, _, r in edges)
    out = expand_one_hop(["infra/inference-economics.md"], edges)
    # prefix-caching is reachable from the seed only via `instance-of` (forward)
    # and `extends` (backward) — the latter is in scope, so it appears, but as
    # the inverse label rather than `instance-of`.
    hits = {path: rel for path, rel, _ in out}
    assert hits.get("context/prefix-caching.md") == "extended-by"
    assert "rag/unrelated.md" not in hits


def test_expansion_never_returns_the_seeds_themselves() -> None:
    edges = build_typed_edges(PAGES)
    seeds = ["infra/inference-economics.md", "context/prefix-caching.md"]
    out = expand_one_hop(seeds, edges)
    assert not any(path in seeds for path, _, _ in out)


def test_expansion_respects_the_cap() -> None:
    edges = build_typed_edges(PAGES)
    out = expand_one_hop(["infra/inference-economics.md"], edges, max_expansions=1)
    assert len(out) == 1


def test_empty_seeds_expand_to_nothing() -> None:
    assert expand_one_hop([], build_typed_edges(PAGES)) == []


# ---------------------------------------------------------------------------
# Materialized edges table (LIB-114 Step 1)
# ---------------------------------------------------------------------------

FIXTURE_PAGE = """---
title: {title}
tags: [rag, concept]
summary: {summary}
updated: 2026-08-05
---

# {title}

{body}
"""


@pytest.fixture()
def typed_wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A wiki whose pages carry canonical, non-canonical, and no annotations."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)

    (wiki_dir / "rag" / "chunking.md").write_text(
        FIXTURE_PAGE.format(
            title="Chunking",
            summary="How to chunk",
            body="Chunking notes. ZQUERYMARKER\n\n## See Also\n- [[Reranking]] — prerequisite-for\n",
        )
    )
    (wiki_dir / "rag" / "reranking.md").write_text(
        FIXTURE_PAGE.format(
            title="Reranking",
            summary="Second-stage ranking",
            body="Reranking notes.\n\n## See Also\n- [[Chunking]] — complements\n",
        )
    )

    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    return wiki_dir


def test_build_index_materializes_typed_edges(typed_wiki: Path) -> None:
    con = duckdb.connect(":memory:")
    server.build_index(con)
    edges = con.execute("SELECT source_path, target_path, relationship FROM edges").fetchall()
    con.close()

    assert len(edges) == 1  # the canonical annotation only; `complements` is dropped
    source, target, rel = edges[0]
    assert source.endswith("rag/chunking.md")
    assert target.endswith("rag/reranking.md")
    assert rel == "prerequisite-for"


def test_expansion_section_reads_edges_table(typed_wiki: Path) -> None:
    """Same output as the old per-call full scan, now served from the table."""
    section = server._expansion_section([str(typed_wiki / "rag" / "chunking.md")])
    assert "one typed hop away" in section
    assert "Reranking" in section
    assert "prerequisite-for" in section


# ---------------------------------------------------------------------------
# Row-merging expansion path (LIB-114 Step 2)
# ---------------------------------------------------------------------------


def test_search_rows_expand_merges_neighbour_with_decay(typed_wiki: Path) -> None:
    """The one-hop neighbour joins the rows at DECAY × its best seed's score."""
    rows, _ = server._search_rows("ZQUERYMARKER", expand=True)
    by_name = {Path(r[0]).name: r for r in rows}
    assert set(by_name) == {"chunking.md", "reranking.md"}

    seed_score = by_name["chunking.md"][6]
    assert by_name["reranking.md"][6] == pytest.approx(server.EXPANSION_DECAY * seed_score)
    # An expanded page never outranks the direct hit that reached it.
    assert Path(rows[0][0]).name == "chunking.md"


def test_search_rows_without_expand_is_unchanged(typed_wiki: Path) -> None:
    """expand=False (the production default) returns only direct hits."""
    rows, _ = server._search_rows("ZQUERYMARKER")
    assert [Path(r[0]).name for r in rows] == ["chunking.md"]


def test_expand_telemetry_logs_fired_edges(typed_wiki: Path) -> None:
    """Fired edges land in retrieval telemetry as (seed, neighbour, rel) triples."""
    server._search_rows("ZQUERYMARKER", expand=True)
    entry = json.loads(server.RETRIEVAL_LOG.read_text().strip().splitlines()[-1])
    edges = [tuple(e) for e in entry["expansion_edges"]]
    assert len(edges) == 1
    seed, neighbour, rel = edges[0]
    assert seed.endswith("rag/chunking.md")
    assert neighbour.endswith("rag/reranking.md")
    assert rel == "prerequisite-for"


def test_expand_false_logs_no_expansion_edges(typed_wiki: Path) -> None:
    server._search_rows("ZQUERYMARKER")
    entry = json.loads(server.RETRIEVAL_LOG.read_text().strip().splitlines()[-1])
    assert "expansion_edges" not in entry
