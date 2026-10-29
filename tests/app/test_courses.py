"""The /api/courses router: catalog shape, lesson ↔ wiki concept links, search, files.

Runs against a tmp courses tree and tmp wiki (module constants monkeypatched, the
signature-keyed catalog cache cleared) on a bare FastAPI app carrying only the
courses router, so main.py's lifespan (embedder, index build) never runs.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backend import courses

WIKI_PAGE = """---
title: {title}
tags: [{tags}]
summary: {title} summary.
updated: 2026-10-28
---

# {title}
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    wiki = tmp_path / "wiki"
    _write(
        wiki / "context" / "context-engineering.md",
        WIKI_PAGE.format(title="Context Engineering", tags="context, concept"),
    )
    _write(
        wiki / "rag" / "hybrid-search.md",
        WIKI_PAGE.format(title="Hybrid Search", tags="rag, concept"),
    )
    _write(
        wiki / "private" / "client-secret.md",
        WIKI_PAGE.format(title="Client Secret Project", tags="projects, project"),
    )
    _write(
        wiki / "rag" / "old-page.md",
        WIKI_PAGE.format(title="Old Retired Page", tags="rag, tombstone"),
    )

    root = tmp_path / "courses"
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\nsummary: S.\norder: 2\n---\n")
    _write(root / "basics" / "_course.md", "---\ntitle: Basics\norder: 1\n---\n")
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\norder: 1\n---\n")
    _write(
        root / "gen-ai" / "01-rag" / "intro.md",
        "---\ntitle: Intro\norder: 1\n---\n\n# Intro\n\nWe combine keywords and vectors with hybrid "
        "search. See [[Context Engineering]] and [[Client Secret Project]].\n\n"
        "```python\n# hybrid search inside code is not a mention\n```\n",
    )
    _write(
        root / "gen-ai" / "01-rag" / "deep" / "rerank.md",
        "---\ntitle: Reranking\norder: 2\nsection: Deep\nwiki: [old-page, client-secret]\n---\n\nRerankers sort candidates.\n",
    )
    _write(root / "gen-ai" / "02-agents" / "_module.md", "---\ntitle: Agents\norder: 2\n---\n")
    _write(root / "gen-ai" / "02-agents" / "loop.md", "---\ntitle: The Loop\n---\n\nAgents loop.\n")
    _write(root / "gen-ai" / "01-rag" / "assets" / "fig.png", "png")
    _write(root / "gen-ai" / "01-rag" / "assets" / "notes.txt", "not an image")
    _write(root / "basics" / "01-python" / "vars.md", "---\ntitle: Variables\n---\n\nx = 1\n")
    _write(tmp_path / "secret.png", "outside")

    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", wiki)
    monkeypatch.setattr(courses, "DRILL_LOG", tmp_path / "no-drill-log.md")  # never the real one
    courses._load.cache_clear()
    app = FastAPI()
    app.include_router(courses.router)
    with TestClient(app) as c:
        yield c
    courses._load.cache_clear()


def test_catalog_orders_courses_modules_and_lessons(client: TestClient) -> None:
    data = client.get("/api/courses").json()
    assert [c["id"] for c in data] == ["basics", "gen-ai"]
    gen = data[1]
    assert gen["lessonCount"] == 3
    assert [m["title"] for m in gen["modules"]] == ["RAG", "Agents"]
    assert [lesson["id"] for lesson in gen["modules"][0]["lessons"]] == [
        "gen-ai/01-rag/intro",
        "gen-ai/01-rag/deep/rerank",
    ]
    assert gen["modules"][0]["lessons"][1]["section"] == "Deep"


def test_lesson_links_concepts_and_excludes_private_and_tombstones(client: TestClient) -> None:
    lesson = client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()
    ids = {c["id"] for c in lesson["concepts"]}
    # Explicit [[link]] plus a verbatim title mention in prose.
    assert ids == {"context-engineering", "hybrid-search"}
    assert "[Context Engineering](#wiki:context-engineering)" in lesson["body"]
    # Unresolvable (private) wikilink degrades to plain text, never a link.
    assert "#wiki:client-secret" not in lesson["body"]
    assert "Client Secret Project" in lesson["body"]

    rerank = client.get("/api/courses/lessons/gen-ai/01-rag/deep/rerank").json()
    assert rerank["concepts"] == []  # wiki: frontmatter naming private/tombstoned pages


def test_prev_next_crosses_modules_but_not_courses(client: TestClient) -> None:
    rerank = client.get("/api/courses/lessons/gen-ai/01-rag/deep/rerank").json()
    assert rerank["prev"]["id"] == "gen-ai/01-rag/intro"
    assert rerank["next"]["id"] == "gen-ai/02-agents/loop"
    intro = client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()
    assert intro["prev"] is None


def test_unknown_lesson_404(client: TestClient) -> None:
    assert client.get("/api/courses/lessons/gen-ai/nope").status_code == 404


def test_search_ranks_title_hits_and_strips_markdown(client: TestClient) -> None:
    hits = client.get("/api/courses/search", params={"q": "rerank"}).json()
    assert hits[0]["id"] == "gen-ai/01-rag/deep/rerank"
    hits = client.get("/api/courses/search", params={"q": "hybrid"}).json()
    assert hits and "#" not in hits[0]["snippet"] and "[[" not in hits[0]["snippet"]
    assert client.get("/api/courses/search", params={"q": "x"}).json() == []


def test_concept_endpoint_returns_covering_lessons(client: TestClient) -> None:
    hits = client.get("/api/courses/concept/hybrid-search").json()
    assert [h["id"] for h in hits] == ["gen-ai/01-rag/intro"]
    assert hits[0]["course"] == "gen-ai"


def test_files_serves_images_only_inside_root(client: TestClient) -> None:
    assert client.get("/api/courses/files/gen-ai/01-rag/assets/fig.png").status_code == 200
    assert client.get("/api/courses/files/gen-ai/01-rag/assets/notes.txt").status_code == 400
    assert client.get("/api/courses/files/gen-ai/01-rag/intro.md").status_code == 400
    assert client.get("/api/courses/files/gen-ai/missing.png").status_code == 404
    # Encoded traversal survives URL normalisation and must hit the guard.
    assert client.get("/api/courses/files/gen-ai/%2E%2E/%2E%2E/secret.png").status_code in (
        400,
        404,
    )


def test_catalog_cache_refreshes_on_new_file(client: TestClient) -> None:
    before = client.get("/api/courses").json()[0]["lessonCount"]
    _write(
        courses.COURSES_DIR / "basics" / "01-python" / "loops.md", "---\ntitle: Loops\n---\n\nfor\n"
    )
    assert client.get("/api/courses").json()[0]["lessonCount"] == before + 1


def test_practice_lists_drills_with_filters_and_concepts(client: TestClient) -> None:
    _write(
        courses.COURSES_DIR / "basics" / "02-sql" / "top-orders.md",
        "---\ntitle: Top orders\nkind: drill\ntrack: sql\ntopic: window-functions\n"
        "difficulty: medium\ntimebox_min: 20\nwiki: [hybrid-search, client-secret, window-functions]\n"
        "---\n\nRank.\n",
    )
    _write(
        courses.COURSES_DIR / "basics" / "02-sql" / "group-by.md",
        "---\ntitle: Group by\nkind: drill\ntrack: typescript\ndifficulty: easy\n---\n\nGroup.\n",
    )
    drills = client.get("/api/courses/practice").json()
    assert [d["title"] for d in drills] == ["Group by", "Top orders"]
    top = client.get("/api/courses/practice", params={"track": "sql"}).json()
    assert len(top) == 1
    assert top[0]["drill"] == {
        "track": "sql",
        "topic": "window-functions",
        "difficulty": "medium",
        "timebox_min": 20,
        "tags": ["window-functions"],  # no wiki page yet; the private page is not echoed
    }
    assert [c["id"] for c in top[0]["concepts"]] == ["hybrid-search"]  # private page dropped
    assert client.get("/api/courses/practice", params={"difficulty": "hard"}).json() == []
    assert (
        client.get("/api/courses/practice", params={"concept": "hybrid-search"}).json()[0]["title"]
        == "Top orders"
    )
    assert (
        len(client.get("/api/courses/practice", params={"concept": "window-functions"}).json()) == 1
    )
    # Ordinary lessons carry no drill block.
    assert "drill" not in client.get("/api/courses/lessons/basics/01-python/vars").json()


def test_practice_attaches_attempts_from_drill_log_without_notes(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(
        courses.COURSES_DIR / "basics" / "02-sql" / "top-orders.md",
        "---\ntitle: Top orders\nkind: drill\ntrack: sql\n---\n\nRank.\n",
    )
    log = tmp_path / "drill-log.md"
    log.write_text(
        "# Log\n\n| Date | QID | Score | Note |\n|---|---|---|---|\n"
        "| 2026-10-01 | top-orders | C✓ P✗ | private reflection |\n"
        "| 2026-10-20 | top-orders | C✓ P✓ | private reflection |\n"
        "| 2026-10-05 | top-orders | C✗ P✗ | private reflection |\n"
    )
    monkeypatch.setattr(courses, "DRILL_LOG", log)
    [drill] = client.get("/api/courses/practice").json()
    assert drill["attempts"] == {"count": 3, "last": "2026-10-20", "score": "C✓ P✓"}
    assert "private reflection" not in str(drill)

    monkeypatch.setattr(courses, "DRILL_LOG", tmp_path / "missing.md")
    assert "attempts" not in client.get("/api/courses/practice").json()[0]
