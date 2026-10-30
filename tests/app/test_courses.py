"""The /api/courses router: catalog shape, lesson ↔ wiki concept links, search, files.

Runs against a tmp courses tree and tmp wiki (module constants monkeypatched, the
signature-keyed catalog cache cleared) on a bare FastAPI app carrying only the
courses router, so main.py's lifespan (embedder, index build) never runs.

Semantic concept linking is stubbed: the fixture disables it (so the explicit and
title-mention tests see exactly the pre-embedding behaviour) and the semantic tests
inject a fake neighbour function. The real MiniLM model is never loaded here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backend import courses

_REAL_NEIGHBOURS = courses._semantic_neighbours

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
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
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


# ── Semantic concept linking (D5) ────────────────────────────────────────────


def _use_neighbours(
    monkeypatch: pytest.MonkeyPatch, by_title: dict[str, list[tuple[str, float]]]
) -> list[list[str]]:
    """Fake embedder: candidates keyed by lesson title (the text starts with it)."""
    calls: list[list[str]] = []

    def fake(texts: list[str], wiki_ids: list[str]) -> list[list[tuple[str, float]]]:
        calls.append(wiki_ids)
        return [by_title.get(t.split(".")[0], []) for t in texts]

    monkeypatch.setattr(courses, "_semantic_neighbours", fake)
    courses._load.cache_clear()
    return calls


def test_semantic_neighbours_rank_after_explicit_and_mentions(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _use_neighbours(
        monkeypatch,
        {
            "Intro": [
                ("hybrid-search", 0.9),  # already a title mention: not duplicated
                ("context-engineering", 0.8),  # already explicit
                ("client-secret", 0.99),  # private: never surfaced, whatever the score
                ("old-page", 0.95),  # tombstoned: same
            ],
            "The Loop": [("context-engineering", 0.7), ("hybrid-search", 0.54)],  # 0.54 < 0.55
        },
    )
    intro = client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()
    assert [c["id"] for c in intro["concepts"]] == ["context-engineering", "hybrid-search"]
    loop = client.get("/api/courses/lessons/gen-ai/02-agents/loop").json()
    assert [c["id"] for c in loop["concepts"]] == ["context-engineering"]
    # The by-concept index (graph → course direction) sees semantic links too.
    hits = client.get("/api/courses/concept/context-engineering").json()
    assert "gen-ai/02-agents/loop" in [h["id"] for h in hits]
    # Only visible pages are offered to the embedder in the first place.
    assert set(calls[0]) == {"context-engineering", "hybrid-search"}


def test_merge_semantic_caps_top_k_and_total() -> None:
    wiki = {f"p{i}" for i in range(30)}
    cands = [(f"p{i}", 0.9 - i * 0.001) for i in range(30)]
    assert len(courses._merge_semantic([], cands, wiki)) == courses.SEMANTIC_TOP_K
    ranked = [f"x{i}" for i in range(courses.MAX_CONCEPTS - 2)]
    merged = courses._merge_semantic(ranked, cands, wiki)
    assert merged[: len(ranked)] == ranked  # explicit/mention order preserved
    assert len(merged) == courses.MAX_CONCEPTS
    # Unsorted input is handled; below-threshold candidates never get in.
    assert courses._merge_semantic([], [("p1", 0.5), ("p2", 0.6)], wiki) == ["p2"]


def test_semantic_falls_back_without_api_extra(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CI installs no extras: numpy / shared.embeddings are not importable. The real
    neighbour function must return None and the catalog keep explicit + mention links."""
    for mod in ("numpy", "shared.embeddings", "sentence_transformers"):
        monkeypatch.setitem(sys.modules, mod, None)  # None in sys.modules → ImportError
    assert _REAL_NEIGHBOURS(["some lesson"], ["hybrid-search"]) is None

    monkeypatch.setattr(courses, "_semantic_neighbours", _REAL_NEIGHBOURS)
    courses._load.cache_clear()
    intro = client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()
    assert {c["id"] for c in intro["concepts"]} == {"context-engineering", "hybrid-search"}


def test_semantic_failure_degrades_instead_of_failing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("numpy")  # needs the api extra to reach the embedding stack
    import shared.embeddings

    def boom() -> None:
        raise OSError("cache locked")

    monkeypatch.setattr(shared.embeddings, "compute_embeddings", boom)
    assert _REAL_NEIGHBOURS(["some lesson"], ["hybrid-search"]) is None


def test_warm_catalog_builds_and_never_raises(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    courses._load.cache_clear()
    courses.warm_catalog()
    assert courses._load.cache_info().currsize == 1  # the first request is now a cache hit

    def broken(*_: object) -> None:
        raise RuntimeError("bad frontmatter")

    monkeypatch.setattr(courses, "catalog", broken)
    courses.warm_catalog()  # logged, not raised: startup must survive


def test_semantic_failure_retries_after_backoff(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A transient embedding failure must not pin a link-less catalog until a .md changes."""
    pytest.importorskip("numpy")
    import time

    import shared.embeddings

    def boom() -> None:
        raise OSError("cache locked")

    monkeypatch.setattr(shared.embeddings, "compute_embeddings", boom)
    monkeypatch.setattr(courses, "_semantic_failed_at", None)
    assert _REAL_NEIGHBOURS(["some lesson"], ["hybrid-search"]) is None
    assert courses._semantic_failed_at is not None

    courses._load.cache_clear()
    courses.catalog()
    assert courses._load.cache_info().currsize == 1
    courses.catalog()  # inside the back-off window: served from cache
    assert courses._load.cache_info().hits >= 1

    monkeypatch.setattr(
        courses, "_semantic_failed_at", time.monotonic() - courses.SEMANTIC_RETRY_S - 1
    )
    courses.catalog()  # window passed: the cache is dropped and the catalog rebuilt
    info = courses._load.cache_info()  # cache_clear() also resets the counters
    assert (info.hits, info.misses) == (0, 1)
    assert courses._semantic_failed_at is None


def test_semantic_skips_ambiguous_page_stems(monkeypatch: pytest.MonkeyPatch) -> None:
    """compute_embeddings keys by stem over all of data/wiki/ (private/ included); a stem
    present twice can't be attributed to the visible page, so it is never a candidate."""
    np = pytest.importorskip("numpy")
    import shared.embeddings

    vecs = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    monkeypatch.setattr(
        shared.embeddings, "compute_embeddings", lambda: (["foo", "foo", "bar"], vecs)
    )
    monkeypatch.setattr(
        shared.embeddings, "encode_texts_cached", lambda texts, _p: np.array([[0.8, 0.6]])
    )
    out = _REAL_NEIGHBOURS(["a lesson"], ["foo", "bar"])
    assert out is not None
    assert [pid for pid, _ in out[0]] == ["bar"]


def test_requests_get_last_catalog_while_a_rebuild_runs(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A wiki edit triggers a multi-second rebuild; requests must not queue behind it."""
    built = courses.catalog()
    assert courses._current is built
    assert courses._LOAD_LOCK.acquire(timeout=5)  # stand-in for a rebuild in progress
    try:
        assert courses.catalog() is built  # returned immediately, without the lock
    finally:
        courses._LOAD_LOCK.release()


def test_cold_start_waits_for_the_first_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(courses, "_current", None)
    sentinel = object()
    monkeypatch.setattr(courses, "_load", lambda *_: sentinel)
    assert courses.catalog() is sentinel
