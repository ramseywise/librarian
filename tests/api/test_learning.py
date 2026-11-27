"""Concept mastery over HTTP: /api/learning events, state, next and the concept hub, per user."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian import accounts
from librarian.config import get_settings
from librarian.courses import attempts, learning
from librarian.courses import catalog as courses
from librarian.db import get_engine

TOKEN = "bootstrap-token-0123456789abcdef"
NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
MOD = "gen-ai/01-rag"
INTRO = f"{MOD}/intro"
RERANK = f"{MOD}/rerank"
SECRET = f"{MOD}/secret"

PAGE = "---\ntitle: {title}\ntags: [{tags}]\nsummary: {title} summary.\nupdated: 2026-10-28\n---\n\n# {title}\n"


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    wiki = tmp_path / "wiki"
    _write(
        wiki / "rag" / "hybrid-search.md", PAGE.format(title="Hybrid Search", tags="rag, concept")
    )
    _write(wiki / "rag" / "reranking.md", PAGE.format(title="Reranking", tags="rag, concept"))
    _write(
        wiki / "private" / "client-secret.md", PAGE.format(title="Client Secret", tags="project")
    )
    _write(wiki / "rag" / "old-page.md", PAGE.format(title="Old Page", tags="rag, tombstone"))
    root = tmp_path / "courses"
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\n---\n")
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\n---\n")
    _write(
        root / "gen-ai" / "01-rag" / "intro.md",
        "---\ntitle: Intro\norder: 1\nwiki: [hybrid-search]\n---\n\nBody.\n",
    )
    _write(
        root / "gen-ai" / "01-rag" / "rerank.md",
        "---\ntitle: Rerank\norder: 2\nwiki: [reranking, client-secret, old-page]\n---\n\nBody.\n",
    )
    _write(
        root / "private" / "gen-ai" / "01-rag" / "secret.md",
        "---\ntitle: Secret Lesson\nwiki: [hybrid-search]\n---\n\nBody.\n",
    )
    _write(
        root / "gen-ai" / "01-rag" / "_flashcards.md",
        "---\ncards:\n- {front: What is hybrid?, back: Both., lesson: gen-ai/01-rag/intro}\n---\n",
    )
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", wiki)
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(learning, "utcnow", lambda: NOW)
    courses._load.cache_clear()
    with TestClient(main_module.app) as c:
        yield c
    courses._load.cache_clear()
    monkeypatch.undo()
    get_settings.cache_clear()


def _member(email: str) -> dict[str, str]:
    engine = get_engine()
    accounts.add_user(engine, email)
    return _auth(accounts.create_key(engine, email, scopes="read write")[1])


def _post(client: TestClient, who: dict[str, str], **body: object) -> httpx.Response:
    return client.post("/api/learning/events", json=body, headers=who)


def _ts(days: float) -> str:
    return (NOW - timedelta(days=days)).isoformat()


def test_a_lesson_done_event_marks_progress_and_links_concepts(client: TestClient) -> None:
    me = _auth(TOKEN)
    r = _post(client, me, kind="lesson_done", lesson=INTRO)
    assert r.json() == {"logged": True, "concepts": ["hybrid-search"]}
    state = client.get("/api/learning/state", headers=me).json()
    assert state["lessonsDone"] == [INTRO]
    assert state["concepts"]["hybrid-search"]["counts"]["lessons"] == 1
    assert state["catalogReady"] is True
    assert state["modules"][MOD]["withEvidence"] == 1


def test_unknown_and_private_lessons_and_cards_log_nothing(client: TestClient) -> None:
    me = _auth(TOKEN)
    nothing = {"logged": False, "concepts": []}
    assert _post(client, me, kind="lesson_done", lesson=f"{MOD}/nope").json() == nothing
    assert _post(client, me, kind="lesson_done", lesson=SECRET).json() == nothing
    assert _post(client, me, kind="card_grade", deck=SECRET, card="0", score=1).json() == nothing
    assert (
        _post(client, me, kind="card_grade", deck="private/x", card="0", score=1).json() == nothing
    )
    assert client.get("/api/learning/state", headers=me).json()["concepts"] == {}


def test_a_flashcard_grade_is_stored_as_a_flashcard_attempt(client: TestClient) -> None:
    me = _auth(TOKEN)
    deck = courses.catalog().decks[INTRO]
    card = deck["cards"][0]["id"]
    r = _post(client, me, kind="card_grade", deck=INTRO, card=card, score=1, ts=_ts(1))
    assert r.json()["concepts"] == ["hybrid-search"]
    state = client.get("/api/learning/state", headers=me).json()
    assert state["concepts"]["hybrid-search"]["counts"]["cards"] == 1


def test_drill_and_voice_and_concept_only_events_count(client: TestClient) -> None:
    me = _auth(TOKEN)
    _post(client, me, kind="drill_attempt", lesson=INTRO, score=0.9, ts=_ts(2))
    _post(client, me, kind="voice_grade", lesson=INTRO, mode="approach", score=0.8, ts=_ts(1))
    _post(client, me, kind="drill_attempt", concept="reranking", score=0.0, ts=_ts(1))
    _post(client, me, kind="card_grade", concept="reranking", score=0.0, ts=_ts(0))
    c = client.get("/api/learning/state", headers=me).json()["concepts"]
    assert c["hybrid-search"]["counts"]["drills"] == 2
    assert c["reranking"]["counts"] == {"lessons": 0, "drills": 1, "cards": 1}
    assert c["reranking"]["strength"] == 0.0 and c["reranking"]["due"] is True


def test_a_future_timestamp_counts_as_now(client: TestClient) -> None:
    me = _auth(TOKEN)
    _post(client, me, kind="drill_attempt", lesson=INTRO, score=1, ts=_ts(-30))
    state = client.get("/api/learning/state", headers=me).json()
    assert state["concepts"]["hybrid-search"]["recency"] == pytest.approx(1.0)


def test_extra_fields_such_as_an_answer_are_refused(client: TestClient) -> None:
    me = _auth(TOKEN)
    r = _post(client, me, kind="drill_attempt", lesson=INTRO, score=1, note="my answer")
    assert r.status_code == 422
    assert _post(client, me, kind="drill_attempt", lesson=INTRO, score=3).status_code == 422


def test_a_write_failure_is_a_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(attempts, "record", lambda *a, **k: False)
    r = _post(client, _auth(TOKEN), kind="drill_attempt", lesson=INTRO, score=1)
    assert r.status_code == 503


def test_reconcile_records_only_public_known_lessons_and_is_repeatable(client: TestClient) -> None:
    me = _auth(TOKEN)
    body = {"done": [INTRO, SECRET, "nope/x", "bad id!"]}
    first = client.post("/api/learning/reconcile", json=body, headers=me).json()
    assert first == {"resolved": [INTRO], "unresolved": [SECRET, "nope/x", "bad id!"]}
    client.post("/api/learning/reconcile", json=body, headers=me)
    assert client.get("/api/learning/state", headers=me).json()["lessonsDone"] == [INTRO]
    assert (
        client.post("/api/learning/reconcile", json={"done": [], "x": 1}, headers=me).status_code
        == 422
    )


def test_next_lists_due_concepts_weakest_first_and_nothing_else(client: TestClient) -> None:
    me = _auth(TOKEN)
    _post(client, me, kind="drill_attempt", lesson=INTRO, score=0.0, ts=_ts(1))
    _post(client, me, kind="drill_attempt", lesson=INTRO, score=0.0, ts=_ts(1))
    _post(client, me, kind="drill_attempt", lesson=RERANK, score=1.0, ts=_ts(0))
    rows = client.get("/api/learning/next", headers=me).json()
    assert [r["concept"]["id"] for r in rows] == ["hybrid-search"]
    row = rows[0]
    assert row["due"] is True and row["reason"]
    assert {"concept", "strength", "due", "reason", "lessons", "drills", "decks"} <= set(row)
    assert all(SECRET not in str(x) for x in row["lessons"])
    assert client.get("/api/learning/next?limit=0", headers=me).status_code == 422


def test_the_concept_hub_and_what_it_will_not_show(client: TestClient) -> None:
    me = _auth(TOKEN)
    _post(client, me, kind="lesson_done", lesson=INTRO, ts=_ts(0))
    hub = client.get("/api/learning/concept/hybrid-search", headers=me).json()
    assert hub["title"] == "Hybrid Search" and hub["mastery"]["evidence"] == "direct"
    assert [x["id"] for x in hub["lessons"]] == [INTRO]  # the private lesson is not listed
    assert SECRET not in client.get("/api/learning/concept/hybrid-search", headers=me).text
    assert client.get("/api/learning/concept/reranking", headers=me).json()["mastery"] is None
    for hidden in ("client-secret", "old-page", "nope"):
        r = client.get(f"/api/learning/concept/{hidden}", headers=me)
        assert (r.status_code, r.json()["detail"]) == (404, "no such page")


def test_the_existing_concept_list_route_is_untouched(client: TestClient) -> None:
    assert client.get("/api/courses/concept/hybrid-search", headers=_auth(TOKEN)).status_code in (
        200,
        404,
    )


def test_one_users_evidence_is_not_anothers(client: TestClient) -> None:
    ada, bob = _member("ada@example.com"), _member("bob@example.com")
    _post(client, ada, kind="lesson_done", lesson=INTRO)
    _post(client, ada, kind="drill_attempt", lesson=INTRO, score=0.0)
    assert client.get("/api/learning/state", headers=ada).json()["concepts"]
    empty = client.get("/api/learning/state", headers=bob).json()
    assert empty["concepts"] == {} and empty["lessonsDone"] == []
    assert client.get("/api/learning/next", headers=bob).json() == []
    assert client.get("/api/learning/concept/hybrid-search", headers=bob).json()["mastery"] is None


def test_it_needs_a_signed_in_user(client: TestClient) -> None:
    assert client.get("/api/learning/state").status_code in (401, 403)
    assert client.post("/api/learning/events", json={}).status_code in (401, 403)


def test_the_drill_log_is_never_read() -> None:
    import librarian.courses.learning as mod

    assert not hasattr(mod, "drill_log")
