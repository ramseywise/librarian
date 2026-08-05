"""Evidence that --domain matches on directory OR domain tag, not either/or.

Before the fix, search_wiki resolved a domain name to a directory and filtered on
path alone whenever that directory existed. A page filed in one subject directory
but carrying another domain's tag was therefore unreachable via that domain — the
tag fallback at the else-branch was only taken when the directory did not exist.

These tests fail against the pre-fix server.
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
    """A wiki where one page lives in foundations/ but is tagged `interview`."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "interview").mkdir(parents=True)
    (wiki_dir / "foundations").mkdir(parents=True)
    (wiki_dir / "private").mkdir(parents=True)

    # Lives in interview/ — reachable by path.
    (wiki_dir / "interview" / "narration-formula.md").write_text(
        PAGE.format(
            title="Trade-Off Narration Formula",
            tags="interview, pattern",
            summary="How to narrate a tradeoff",
            body="Consider solutions then narrate SPLINTERCUE tradeoffs.",
        )
    )
    # Lives in foundations/, tagged interview — only reachable by tag.
    (wiki_dir / "foundations" / "inference-economics.md").write_text(
        PAGE.format(
            title="LLM Inference Economics",
            tags="foundations, interview, concept",
            summary="Prefill versus decode",
            body="Decode is sequential which makes SPLINTERCUE output expensive.",
        )
    )
    # Lives in foundations/, NOT tagged interview — must stay out of the results.
    (wiki_dir / "foundations" / "batch-norm.md").write_text(
        PAGE.format(
            title="Batch Normalization",
            tags="foundations, concept",
            summary="Normalizing activations",
            body="Batch norm stabilizes SPLINTERCUE training.",
        )
    )

    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    return wiki_dir


def test_domain_search_returns_pages_in_the_directory(wiki: Path) -> None:
    """The path branch still works — this is the pre-existing behaviour."""
    result = server.search_wiki("SPLINTERCUE", domain="interview")
    assert "Trade-Off Narration Formula" in result


def test_domain_search_returns_tagged_pages_outside_the_directory(wiki: Path) -> None:
    """The regression this fix cures: tagged-but-relocated pages stay reachable."""
    result = server.search_wiki("SPLINTERCUE", domain="interview")
    assert "LLM Inference Economics" in result, (
        "a page tagged `interview` but filed under foundations/ must still be "
        "reachable via --domain interview; filtering on path alone drops it"
    )


def test_domain_search_still_excludes_untagged_pages(wiki: Path) -> None:
    """The union must not degrade into no filter at all."""
    result = server.search_wiki("SPLINTERCUE", domain="interview")
    assert "Batch Normalization" not in result, (
        "a foundations/ page with no `interview` tag must not leak into the domain"
    )


def test_unknown_domain_still_falls_back_to_tag_match(wiki: Path) -> None:
    """No directory named `concept` exists, so the else-branch handles it."""
    result = server.search_wiki("SPLINTERCUE", domain="concept")
    assert "LLM Inference Economics" in result
    assert "Batch Normalization" in result
