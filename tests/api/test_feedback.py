"""Phase 4b backend: reader feedback routes, the admin summary, sticky experiments, the done event."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Response

import librarian.api.main as main_module
from librarian import accounts, experiments, feedback
from librarian.agent import loop as agent
from librarian.api.routers import chat as chat_router
from librarian.config import Settings, get_settings
from librarian.db import get_engine
from librarian.observability import experiment, set_variant
from librarian.pricing import TokenUsage
from librarian.retrieval import corpus

TOKEN = "bootstrap-token-0123456789abcdef"


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    with TestClient(main_module.app) as c:
        yield c
    monkeypatch.undo()
    get_settings.cache_clear()


def _member(email: str) -> dict[str, str]:
    engine = get_engine()
    accounts.add_user(engine, email)
    return _auth(accounts.create_key(engine, email, scopes="read write")[1])


def _uid(email: str) -> str:
    user = accounts.get_user(get_engine(), email)
    assert user is not None
    return user.id


def _post(client: TestClient, headers: dict[str, str], **body: object) -> Response:
    return client.post("/api/feedback", json=body, headers=headers)


# -- routes -------------------------------------------------------------------------------------


def test_post_stores_a_row_and_fills_release_and_experiment(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_EXPERIMENTS", "ranking=hybrid-union")
    get_settings.cache_clear()
    a = _member("a@example.com")
    r = _post(client, a, kind="page", target="rag-chunking", body="  Outdated.  ")
    assert r.status_code == 201
    [row] = client.get("/api/feedback/mine", headers=a).json()
    assert row["id"] == r.json()["id"]
    assert (row["kind"], row["target"], row["body"]) == ("page", "rag-chunking", "Outdated.")
    assert row["rating"] is None
    assert row["experiment"] == "ranking=hybrid-union"
    assert row["release"]


def test_validation(client: TestClient) -> None:
    a = _member("a@example.com")
    assert _post(client, a, kind="nope", target="x").status_code == 422
    assert _post(client, a, kind="unanswered", target="x").status_code == 422  # server-written
    assert _post(client, a, kind="answer", target="x").status_code == 422  # rating required
    assert _post(client, a, kind="answer", target="x", rating=2).status_code == 422
    assert _post(client, a, kind="page", target="x", rating=1).status_code == 422
    assert _post(client, a, kind="page", target="x", body="y" * 2001).status_code == 422
    assert _post(client, a, kind="page", target="").status_code == 422


def test_rating_an_answer_again_replaces_the_first_rating(client: TestClient) -> None:
    a, b = _member("a@example.com"), _member("b@example.com")
    _post(client, a, kind="answer", target="abc", rating=1)
    _post(client, a, kind="answer", target="abc", rating=-1, body="wrong")
    _post(client, b, kind="answer", target="abc", rating=1)
    mine = client.get("/api/feedback/mine", headers=a).json()
    assert [(r["rating"], r["body"]) for r in mine] == [(-1, "wrong")]
    assert len(client.get("/api/feedback/mine", headers=b).json()) == 1


def test_only_the_author_deletes_a_row(client: TestClient) -> None:
    a, b = _member("a@example.com"), _member("b@example.com")
    row_id = _post(client, a, kind="lesson", target="gen-ai/01-rag/intro", body="typo").json()["id"]
    assert client.delete(f"/api/feedback/{row_id}", headers=b).status_code == 404
    assert len(client.get("/api/feedback/mine", headers=a).json()) == 1
    assert client.delete(f"/api/feedback/{row_id}", headers=a).status_code == 204
    assert client.get("/api/feedback/mine", headers=a).json() == []
    assert client.delete(f"/api/feedback/{row_id}", headers=a).status_code == 404


def test_a_read_only_key_cannot_write(client: TestClient) -> None:
    accounts.add_user(get_engine(), "ro@example.com")
    ro = _auth(accounts.create_key(get_engine(), "ro@example.com", scopes="read")[1])
    assert _post(client, ro, kind="page", target="x").status_code == 403


def test_feedback_is_rate_limited(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_FEEDBACK_RATE_LIMIT", "2")
    get_settings.cache_clear()
    a = _member("a@example.com")
    assert [_post(client, a, kind="page", target=f"p{i}").status_code for i in range(3)] == [
        201,
        201,
        429,
    ]


# -- admin summary --------------------------------------------------------------------------------


def _agent_row(**fields: object) -> str:
    return json.dumps({"source": "chat", "pages_read": [], "cited": [], "ungrounded": [], **fields})


def test_summary_is_admin_only_and_carries_no_identities(client: TestClient) -> None:
    a = _member("alice@example.com")
    for i in range(6):  # six attempts on one lesson, four of them missed
        accounts_attempt = "missed" if i < 4 else "knew"
        from librarian.courses import attempts

        attempts.record(
            _uid("alice@example.com"),
            kind="flashcard",
            item=f"c{i}",
            scope="m/l1",
            result=accounts_attempt,
        )
    _post(client, a, kind="answer", target="ans1", rating=-1, body="no sources")
    _post(client, a, kind="page", target="rag-chunking", body="stale")
    _post(client, a, kind="lesson", target="m/l1", body="unclear")
    feedback.record(
        get_engine(), user_id=_uid("alice@example.com"), kind="unanswered", target="what is x?"
    )
    corpus.LOGS_DIR.mkdir(exist_ok=True)
    (corpus.LOGS_DIR / agent.AGENT_LOG_NAME).write_text(
        "\n".join(
            [
                _agent_row(pages_read=["p1"], cited=["p1", "p2"], ungrounded=["p2"]),
                _agent_row(pages_read=["p1"], cited=["p1"]),
                _agent_row(source="eval", pages_read=["p9"]),
                "not json",
            ]
        )
    )

    assert client.get("/api/admin/feedback/summary", headers=a).status_code == 403
    body = client.get("/api/admin/feedback/summary", headers=_auth(TOKEN)).json()
    assert set(body) == {
        "answers_down",
        "pages_reported",
        "lessons_reported",
        "unanswered",
        "lesson_miss_rates",
        "page_reads",
    }
    assert body["answers_down"] == [{"target": "ans1", "count": 1, "notes": ["no sources"]}]
    assert body["pages_reported"][0]["notes"] == ["stale"]
    assert body["unanswered"][0]["target"] == "what is x?"
    assert body["lesson_miss_rates"] == [
        {"target": "m/l1", "count": 6, "misses": 4, "miss_rate": 0.667, "notes": []}
    ]
    by_page = {p["target"]: p for p in body["page_reads"]}
    assert by_page["p1"]["read"] == 2 and by_page["p1"]["cited"] == 2
    assert by_page["p2"]["read"] == 0 and by_page["p2"]["ungrounded"] == 1
    assert "p9" not in by_page
    text = json.dumps(body)
    assert "alice@example.com" not in text and _uid("alice@example.com") not in text


def test_summary_notes_are_the_three_newest(client: TestClient) -> None:
    a = _member("a@example.com")
    for i in range(5):
        _post(client, a, kind="page", target="p", body=f"note {i}")
    notes = client.get("/api/admin/feedback/summary", headers=_auth(TOKEN)).json()[
        "pages_reported"
    ][0]["notes"]
    assert notes == ["note 4", "note 3", "note 2"]


def test_lessons_with_few_attempts_have_no_miss_rate(client: TestClient) -> None:
    from librarian.courses import attempts

    a = _member("a@example.com")
    for i in range(4):
        attempts.record(
            _uid("a@example.com"), kind="mcq", item=f"q{i}", scope="m/l2", result="wrong"
        )
    body = client.get("/api/admin/feedback/summary", headers=_auth(TOKEN)).json()
    assert body["lesson_miss_rates"] == []
    assert a


# -- retention ------------------------------------------------------------------------------------


def test_prune_deletes_only_old_rows(client: TestClient) -> None:
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from librarian.db import tables

    a = _member("a@example.com")
    old = _post(client, a, kind="page", target="old").json()["id"]
    _post(client, a, kind="page", target="new")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            update(tables.feedback)
            .where(tables.feedback.c.id == old)
            .values(ts=datetime.now(UTC) - timedelta(days=181))
        )
    assert feedback.prune(engine, 180) == 1
    assert [r["target"] for r in client.get("/api/feedback/mine", headers=a).json()] == ["new"]


# -- experiments ----------------------------------------------------------------------------------


SPEC = "ranking=control,hybrid-union;prompt=v1,v2,v3"


def _settings(monkeypatch: pytest.MonkeyPatch, spec: str = SPEC) -> Settings:
    monkeypatch.setenv("LIBRARIAN_EXPERIMENTS", spec)
    return Settings(_env_file=None)


def test_assignment_is_sticky_and_spreads_users(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _settings(monkeypatch)
    first = {u: experiments.resolve(s, u) for u in (f"user{i}" for i in range(200))}
    assert first == {u: experiments.resolve(s, u) for u in first}
    assert {v.split(";")[0] for v in first.values()} == {"ranking=control", "ranking=hybrid-union"}
    assert len({v.split(";")[1] for v in first.values()}) == 3
    # each experiment is hashed on its own, so ranking does not decide prompt
    assert len(set(first.values())) > 4


def test_only_admins_may_override(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _settings(monkeypatch)
    pin = "ranking=hybrid-union"
    assert experiments.resolve(s, "u", is_admin=True, override=pin).split(";")[0] == pin
    member = experiments.resolve(s, "u", is_admin=False, override=pin)
    assert member == experiments.resolve(s, "u")
    # unknown names and variants are ignored
    junk = "ranking=nope;other=x"
    assert experiments.resolve(s, "u", is_admin=True, override=junk) == member


def test_without_experiments_the_env_value_is_the_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_EXPERIMENT", "hybrid-union")
    s = _settings(monkeypatch, "")
    assert experiments.resolve(s, "u") == "hybrid-union"
    assert experiment() == "hybrid-union"


def test_me_and_header_override(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_EXPERIMENTS", "ranking=control,hybrid-union")
    get_settings.cache_clear()
    a = _member("a@example.com")
    mine = client.get("/api/me", headers=a).json()["experiment"]
    assert mine in {"ranking=control", "ranking=hybrid-union"}
    pin = {"X-Librarian-Variant": "ranking=hybrid-union"}
    other = "ranking=control" if mine == "ranking=hybrid-union" else "ranking=hybrid-union"
    # a member's header changes nothing
    assert (
        client.get("/api/me", headers={**a, **{"X-Librarian-Variant": other}}).json()["experiment"]
        == mine
    )
    assert client.get("/api/me", headers={**_auth(TOKEN), **pin}).json()["experiment"] == (
        "ranking=hybrid-union"
    )
    row = _post(client, {**_auth(TOKEN), **pin}, kind="page", target="p").json()["id"]
    [stored] = client.get("/api/feedback/mine", headers=_auth(TOKEN)).json()
    assert stored["id"] == row and stored["experiment"] == "ranking=hybrid-union"


def test_the_variant_switches_the_hybrid_path_for_that_request() -> None:
    from librarian.retrieval import ranking

    assert ranking.HYBRID_EXPERIMENT not in experiment()
    set_variant("ranking=hybrid-union")
    try:
        assert ranking.HYBRID_EXPERIMENT in experiment()
    finally:
        set_variant(None)
    set_variant("ranking=control")
    try:
        assert ranking.HYBRID_EXPERIMENT not in experiment()
    finally:
        set_variant(None)


# -- chat -----------------------------------------------------------------------------------------


def _events(resp: Response) -> list[dict[str, Any]]:
    return [json.loads(ln[6:]) for ln in resp.text.splitlines() if ln.startswith("data: ")]


def test_chat_passes_user_and_variant_and_records_unanswered(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_EXPERIMENTS", "ranking=control,hybrid-union")
    get_settings.cache_clear()
    seen: dict[str, Any] = {}

    async def run(
        query: str, history: list[Any], on_usage: Callable[[TokenUsage], None], **kw: object
    ) -> AsyncIterator[dict[str, Any]]:
        seen.update(kw)
        seen["during"] = experiment()
        yield {"type": "grounding", "cited": [], "pages_read": [], "ungrounded": []}
        yield {"type": "done", "answer_id": "a" * 32}

    monkeypatch.setattr(chat_router, "run_agent_stream", run)
    a = _member("a@example.com")
    resp = client.post("/api/chat/stream", json={"query": "q" * 400}, headers=a)
    assert _events(resp)[-1] == {"type": "done", "answer_id": "a" * 32}
    assert seen["user_id"] == _uid("a@example.com")
    assert (
        seen["variant"] == seen["during"] == client.get("/api/me", headers=a).json()["experiment"]
    )
    [row] = client.get("/api/feedback/mine", headers=a).json()
    assert row["kind"] == "unanswered" and row["target"] == "q" * 300
    assert row["experiment"] == seen["variant"]


def test_a_grounded_answer_records_no_unanswered_row(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def run(*_: object, **__: object) -> AsyncIterator[dict[str, Any]]:
        yield {"type": "grounding", "cited": ["p"], "pages_read": ["p"], "ungrounded": []}
        yield {"type": "done", "answer_id": "b" * 32}

    monkeypatch.setattr(chat_router, "run_agent_stream", run)
    a = _member("a@example.com")
    client.post("/api/chat/stream", json={"query": "hi"}, headers=a)
    assert client.get("/api/feedback/mine", headers=a).json() == []


async def test_done_carries_the_answer_id_that_the_log_row_has(
    fake_anthropic: type, tmp_path: Path
) -> None:
    client = fake_anthropic([fake_anthropic.text_turn("Hi.")])
    events = [
        e
        async for e in agent.run_agent_stream(
            "q", client=client, user_id="u1", variant="ranking=control"
        )
    ]
    done = events[-1]
    assert done["type"] == "done" and len(done["answer_id"]) == 32
    row = json.loads((corpus.LOGS_DIR / agent.AGENT_LOG_NAME).read_text().splitlines()[-1])
    assert (row["answer_id"], row["experiment"], row["user_id"]) == (
        done["answer_id"],
        "ranking=control",
        "u1",
    )
    assert row["release"] and row["usage"]["input"] >= 0 and "answer" not in row
    assert "cost_usd" in row
