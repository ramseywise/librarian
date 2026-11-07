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
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete

from librarian.api.routers import courses as courses_routes
from librarian.courses import attempts, leitner
from librarian.courses import catalog as courses
from librarian.db import get_engine, tables

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
    app.include_router(courses_routes.router)
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


def test_lesson_links_pages_compiled_from_it() -> None:
    raw = "data/raw/repos/learn-ai-engineering/basics--01-m--notes--stats.md"
    wiki = {
        "bayes": courses.WikiRef("bayes", "Bayes", "", "foundations", (raw,)),
        "other": courses.WikiRef("other", "Other", "", "foundations", ("data/raw/x/stats.md",)),
    }

    assert courses._compiled_from(wiki) == {"basics/01-m/notes/stats": ["bayes"]}


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
    """CI installs no extras: numpy / librarian.retrieval.embeddings are not importable. The real
    neighbour function must return None and the catalog keep explicit + mention links."""
    for mod in ("numpy", "librarian.retrieval.embeddings", "sentence_transformers"):
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
    import librarian.retrieval.embeddings

    def boom() -> None:
        raise OSError("cache locked")

    monkeypatch.setattr(librarian.retrieval.embeddings, "compute_embeddings", boom)
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

    import librarian.retrieval.embeddings

    def boom() -> None:
        raise OSError("cache locked")

    monkeypatch.setattr(librarian.retrieval.embeddings, "compute_embeddings", boom)
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
    import librarian.retrieval.embeddings

    vecs = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    monkeypatch.setattr(
        librarian.retrieval.embeddings, "compute_embeddings", lambda: (["foo", "foo", "bar"], vecs)
    )
    monkeypatch.setattr(
        librarian.retrieval.embeddings,
        "encode_texts_cached",
        lambda texts, _p: np.array([[0.8, 0.6]]),
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


# ── flashcards ───────────────────────────────────────────────────────────────


def _write_cards(cards: str) -> None:
    _write(
        courses.COURSES_DIR / "gen-ai" / "01-rag" / "_flashcards.md",
        f"---\ncards:\n{cards}---\n",
    )


def test_flashcards_module_and_lesson_decks(client: TestClient) -> None:
    _write_cards(
        "- {front: 'What is **hybrid**?', back: 'Both `bm25` and vectors.', "
        "lesson: gen-ai/01-rag/intro}\n"
        "- {front: Module card, back: No lesson.}\n"
        "- {front: Bad lesson, back: Falls back., lesson: gen-ai/01-rag/gone}\n"
        "- {front: No back}\n"
    )
    module = client.get("/api/courses/flashcards/gen-ai/01-rag").json()
    assert module["title"] == "RAG" and module["course"] == "gen-ai"
    assert [c["front"] for c in module["cards"]] == [
        "What is **hybrid**?",
        "Module card",
        "Bad lesson",
    ]
    assert module["cards"][0]["lessonTitle"] == "Intro"
    assert module["cards"][2]["lesson"] is None

    lesson = client.get("/api/courses/flashcards/gen-ai/01-rag/intro").json()
    assert lesson["title"] == "Intro"
    assert [c["back"] for c in lesson["cards"]] == ["Both `bm25` and vectors."]

    catalog = {c["id"]: c for c in client.get("/api/courses").json()}
    rag = next(m for m in catalog["gen-ai"]["modules"] if m["id"] == "01-rag")
    assert rag["flashcardCount"] == 3
    assert next(x for x in rag["lessons"] if x["title"] == "Intro")["flashcardCount"] == 1
    assert client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()["flashcardCount"] == 1


def test_flashcard_result_logs_catalog_text_with_its_lesson(client: TestClient) -> None:
    _write_cards(
        "  - {front: Why hybrid?, back: Recall, lesson: gen-ai/01-rag/intro}\n  - {front: Loose, back: B}\n"
    )
    courses._load.cache_clear()
    body = {"deck": "gen-ai/01-rag", "card": "0", "result": "missed", "front": "ignored"}
    assert client.post("/api/courses/flashcard-results", json=body).json() == {"logged": True}
    body = {"deck": "gen-ai/01-rag", "card": "1", "result": "knew"}
    assert client.post("/api/courses/flashcard-results", json=body).json() == {"logged": True}
    first, second = attempts.attempts(["flashcard"])
    assert (first.payload["front"], first.payload["lesson"], first.result) == (
        "Why hybrid?",
        "gen-ai/01-rag/intro",
        "missed",
    )
    assert (second.payload["front"], second.payload["lesson"], second.payload["source"]) == (
        "Loose",
        None,
        "",
    )


def _log_review(front: str, deck: str, result: str, days_ago: int) -> None:
    ts = datetime.now(UTC) - timedelta(days=days_ago)
    key = leitner.card_key(deck, front)
    assert attempts.record(
        "flashcard", key, deck, result, payload={"front": front}, ts=ts.isoformat()
    )


def test_flashcard_result_logs_a_stable_card_key(client: TestClient) -> None:
    _write_cards("  - {front: Why hybrid?, back: Recall, lesson: gen-ai/01-rag/intro}\n")
    for deck in ("gen-ai/01-rag", "gen-ai/01-rag/intro"):
        body = {"deck": deck, "card": "0", "result": "knew"}
        assert client.post("/api/courses/flashcard-results", json=body).json() == {"logged": True}
    first, second = attempts.attempts(["flashcard"])
    assert first.item == second.item == leitner.card_key("gen-ai/01-rag", "Why hybrid?")
    assert {"lesson", "source", "front"} <= set(first.payload)


def test_deck_carries_each_cards_schedule_and_counts(client: TestClient) -> None:
    _write_cards(
        "  - {front: Fresh, back: B}\n"
        "  - {front: Reviewed today, back: B}\n"
        "  - {front: Overdue, back: B, lesson: gen-ai/01-rag/intro}\n"
        "  - {front: Missed yesterday, back: B}\n"
    )
    _log_review("Reviewed today", "gen-ai/01-rag", "knew", 0)
    # Graded from the lesson deck: the same card as in the module deck.
    _log_review("Overdue", "gen-ai/01-rag/intro", "knew", 5)
    _log_review("Missed yesterday", "gen-ai/01-rag", "missed", 1)

    deck = client.get("/api/courses/flashcards/gen-ai/01-rag").json()
    by_front = {c["front"]: c for c in deck["cards"]}
    assert by_front["Fresh"]["status"] == "new" and by_front["Fresh"]["box"] is None
    assert by_front["Reviewed today"]["status"] == "later"
    assert by_front["Reviewed today"]["box"] == 2
    assert by_front["Overdue"]["status"] == "due" and by_front["Overdue"]["box"] == 2
    assert by_front["Missed yesterday"]["status"] == "due"
    assert by_front["Missed yesterday"]["box"] == 1
    assert (deck["dueCount"], deck["newCount"]) == (2, 1)

    lesson = client.get("/api/courses/flashcards/gen-ai/01-rag/intro").json()
    assert (lesson["dueCount"], lesson["newCount"]) == (1, 0)

    # The catalog is cached: a schedule must not stick to it once the store is gone.
    with get_engine().begin() as conn:
        conn.execute(delete(tables.attempts))
    deck = client.get("/api/courses/flashcards/gen-ai/01-rag").json()
    assert {c["status"] for c in deck["cards"]} == {"new"}


def test_flashcards_due_counts_module_decks_only(client: TestClient) -> None:
    _write_cards(
        "  - {front: Fresh, back: B, lesson: gen-ai/01-rag/intro}\n"
        "  - {front: Overdue, back: B}\n"
        "  - {front: Reviewed today, back: B}\n"
    )
    _log_review("Overdue", "gen-ai/01-rag", "knew", 5)
    _log_review("Reviewed today", "gen-ai/01-rag", "knew", 0)
    # A card no deck holds any more, and a line the old log can't parse, must not count.
    _log_review("Deleted card", "gen-ai/01-rag", "knew", 9)
    attempts.LEGACY_FLASHCARD_LOG.write_text("{broken\n")

    body = client.get("/api/courses/flashcards-due").json()
    assert (body["due"], body["new"]) == (1, 1)
    assert body["modules"] == [{"deck": "gen-ai/01-rag", "title": "RAG", "due": 1, "new": 1}]


def test_flashcards_due_with_no_log_or_cards(client: TestClient) -> None:
    body = client.get("/api/courses/flashcards-due").json()
    assert (body["due"], body["new"], body["modules"]) == (0, 0, [])


def test_flashcard_result_rejects_unknown_cards_and_grades(client: TestClient) -> None:
    _write_cards("  - {front: Q, back: A}\n")
    courses._load.cache_clear()
    url = "/api/courses/flashcard-results"
    assert (
        client.post(url, json={"deck": "gen-ai/01-rag", "card": "9", "result": "knew"}).status_code
        == 404
    )
    assert client.post(url, json={"deck": "nope", "card": "0", "result": "knew"}).status_code == 404
    assert (
        client.post(url, json={"deck": "gen-ai/01-rag", "card": "0", "result": "maybe"}).status_code
        == 422
    )
    assert attempts.attempts() == []


def test_flashcard_result_survives_a_failed_write(client: TestClient, tmp_path: Path) -> None:
    _write_cards("  - {front: Q, back: A}\n")
    courses._load.cache_clear()
    blocker = tmp_path / "state"
    blocker.write_text("a file where the state folder should be")
    body = {"deck": "gen-ai/01-rag", "card": "0", "result": "knew"}
    assert client.post("/api/courses/flashcard-results", json=body).json() == {"logged": False}


def test_flashcards_file_is_not_a_lesson_and_missing_deck_is_404(client: TestClient) -> None:
    before = client.get("/api/courses").json()
    assert all("flashcardCount" not in m for c in before for m in c["modules"])
    assert client.get("/api/courses/flashcards/gen-ai/01-rag").status_code == 404
    _write_cards("- {front: F, back: B}\n")
    assert client.get("/api/courses/lessons/gen-ai/01-rag/_flashcards").status_code == 404
    assert client.get("/api/courses/flashcards/gen-ai/01-rag/intro").status_code == 404
    assert client.get("/api/courses/flashcards/gen-ai/01-rag").status_code == 200


def test_module_with_order_zero_sorts_first(client: TestClient) -> None:
    module = courses.COURSES_DIR / "gen-ai" / "00-start-here"
    _write(module / "_module.md", "---\ntitle: Start Here\norder: 0\n---\n")
    _write(module / "welcome.md", "---\ntitle: Welcome\norder: 1\n---\nBody.\n")
    gen_ai = next(c for c in client.get("/api/courses").json() if c["id"] == "gen-ai")
    assert gen_ai["modules"][0]["id"] == "00-start-here"
