"""Stale citations: an answer keeps each cited page's id and content hash, and
POST /api/chat/citations/check says whether the page has changed, moved or gone since.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from librarian.agent import loop as agent
from librarian.api import main as main_module
from librarian.retrieval import citations, corpus, embeddings

PAGE = """---
title: {title}
tags: [rag, concept]
summary: How to {title}
updated: 2026-07-20
---

# {title}

{body}
"""


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "private").mkdir(parents=True)
    (wiki_dir / "rag" / "chunking.md").write_text(
        PAGE.format(title="Chunking", body="Chunk by headings.")
    )
    (wiki_dir / "rag" / "reranking.md").write_text(
        PAGE.format(title="Reranking", body="Cross-encoders.")
    )
    (wiki_dir / "private" / "client-notes.md").write_text(
        PAGE.format(title="Client Notes", body="Internal.")
    )
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


async def _answer(fake_anthropic: type, text: str, *read: str) -> dict[str, Any]:
    """Run one scripted answer that reads `read` and says `text`; returns its grounding event."""
    client = fake_anthropic(
        [
            *(fake_anthropic.tool_turn(("read_page", {"page_id": p})) for p in read),
            fake_anthropic.text_turn(text),
        ]
    )
    events = [e async for e in _stream(client)]
    (grounding,) = [e for e in events if e["type"] == "grounding"]
    return grounding


def _stream(client: object) -> AsyncIterator[dict[str, Any]]:
    return agent.run_agent_stream("how to chunk", client=client)


def _check(sources: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    resp = TestClient(main_module.app).post(
        "/api/chat/citations/check", json={"citations": sources}
    )
    assert resp.status_code == 200, resp.text
    return {c["id"]: c for c in resp.json()["citations"]}


@pytest.mark.unit
async def test_grounding_and_telemetry_carry_cited_page_hashes(
    wiki: Path, fake_anthropic: type
) -> None:
    grounding = await _answer(
        fake_anthropic, "Split [page:chunking], see [page:made-up] too.", "chunking"
    )
    # A citation with no page behind it has nothing to go stale, so it gets no hash.
    assert grounding["sources"] == [{"id": "chunking", "hash": citations.fingerprint("chunking")}]
    assert len(grounding["sources"][0]["hash"]) == citations.HASH_CHARS

    line = json.loads((corpus.LOGS_DIR / agent.AGENT_LOG_NAME).read_text().splitlines()[0])
    assert line["sources"] == grounding["sources"]


@pytest.mark.unit
async def test_edit_after_the_answer_marks_the_citation_changed(
    wiki: Path, fake_anthropic: type
) -> None:
    grounding = await _answer(
        fake_anthropic,
        "Split [page:chunking] then rerank [page:reranking].",
        "chunking",
        "reranking",
    )
    sources = grounding["sources"]
    assert {s["status"] for s in _check(sources).values()} == {"current"}

    page = wiki / "rag" / "chunking.md"
    page.write_text(page.read_text().replace("by headings", "by sentences"))

    after = _check(sources)
    assert after["chunking"] == {"id": "chunking", "status": "changed"}
    assert after["reranking"] == {"id": "reranking", "status": "current"}


@pytest.mark.unit
async def test_deleted_page_is_missing(wiki: Path, fake_anthropic: type) -> None:
    grounding = await _answer(fake_anthropic, "Split [page:chunking].", "chunking")
    (wiki / "rag" / "chunking.md").unlink()
    assert _check(grounding["sources"])["chunking"] == {"id": "chunking", "status": "missing"}


@pytest.mark.unit
async def test_renamed_page_resolves_through_its_alias(wiki: Path, fake_anthropic: type) -> None:
    grounding = await _answer(fake_anthropic, "Split [page:chunking].", "chunking")
    old = wiki / "rag" / "chunking.md"
    renamed = old.read_text().replace(
        "title: Chunking\n", "title: Splitting\naliases: [Chunking]\n"
    )
    (wiki / "rag" / "splitting.md").write_text(renamed)
    old.unlink()

    assert _check(grounding["sources"])["chunking"] == {
        "id": "chunking",
        "status": "changed",
        "now": "splitting",
    }


@pytest.mark.unit
def test_private_page_looks_missing(wiki: Path) -> None:
    assert citations.fingerprint("client-notes") is None
    assert citations.sources(["client-notes"]) == []
    # Even with the right hash, the check must not confirm the page exists.
    private = wiki / "private" / "client-notes.md"
    digest = citations._digest(private)
    assert _check([{"id": "client-notes", "hash": digest}])["client-notes"]["status"] == "missing"

    # An alias on a private page does not resolve either.
    private.write_text(private.read_text().replace("title:", "aliases: [Old Name]\ntitle:"))
    assert citations.check("old-name", digest) == {"id": "old-name", "status": "missing"}


@pytest.mark.unit
@pytest.mark.parametrize(
    "body",
    [
        {"citations": [{"id": "../etc/passwd", "hash": "x"}]},
        {"citations": [{"id": "a*", "hash": "x"}]},
        {"citations": [{"id": "chunking", "hash": ""}]},
        {"citations": [{"id": "p", "hash": "x"}] * 51},
    ],
    ids=["traversal", "glob", "empty-hash", "too-many"],
)
def test_check_rejects_malformed_citations(wiki: Path, body: dict[str, Any]) -> None:
    assert (
        TestClient(main_module.app).post("/api/chat/citations/check", json=body).status_code == 422
    )
