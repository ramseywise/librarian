"""Per-user lesson progress (phase 3 wave C): GET/POST /api/courses/progress and the /api/me summary."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian import accounts
from librarian.config import get_settings
from librarian.courses import catalog as courses
from librarian.db import get_engine

TOKEN = "bootstrap-token-0123456789abcdef"
MOD = "gen-ai/01-rag"
URL = "/api/courses/progress"


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    root = tmp_path / "courses"
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\n---\n")
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\n---\n")
    for order, name in enumerate(("intro", "chunking", "rerank"), 1):
        _write(
            root / "gen-ai" / "01-rag" / f"{name}.md",
            f"---\ntitle: {name.title()}\norder: {order}\n---\n\nBody.\n",
        )
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
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


def test_done_is_not_undone_by_opening_again(client: TestClient) -> None:
    me = _auth(TOKEN)
    lesson = f"{MOD}/intro"
    assert client.post(URL, json={"lesson": lesson, "state": "done"}, headers=me).json() == {
        "logged": True
    }
    client.post(URL, json={"lesson": lesson, "state": "opened"}, headers=me)
    assert client.get(URL, headers=me).json()["lessons"][lesson]["state"] == "done"


def test_an_unknown_lesson_or_state_is_refused(client: TestClient) -> None:
    me = _auth(TOKEN)
    assert (
        client.post(URL, json={"lesson": f"{MOD}/nope", "state": "done"}, headers=me).status_code
        == 404
    )
    assert (
        client.post(URL, json={"lesson": f"{MOD}/intro", "state": "half"}, headers=me).status_code
        == 422
    )
    assert client.get(URL, headers=me).json()["lessons"] == {}


def test_the_summary_counts_modules_and_the_last_lesson(client: TestClient) -> None:
    me = _auth(TOKEN)
    client.post(URL, json={"lesson": f"{MOD}/intro", "state": "done"}, headers=me)
    client.post(URL, json={"lesson": f"{MOD}/chunking", "state": "opened"}, headers=me)
    body = client.get(URL, headers=me).json()
    assert body["done"] == 1
    assert body["modules"] == [{"module": MOD, "done": 1, "total": 3}]
    assert (body["last"]["id"], body["last"]["state"]) == (f"{MOD}/chunking", "opened")
    me_body = client.get("/api/me", headers=me).json()
    assert me_body["progress"] == {"done": 1, "modules": body["modules"], "last": body["last"]}


def test_one_users_progress_is_not_anothers(client: TestClient) -> None:
    ada, bob = _member("ada@example.com"), _member("bob@example.com")
    client.post(URL, json={"lesson": f"{MOD}/intro", "state": "done"}, headers=ada)
    assert client.get(URL, headers=ada).json()["done"] == 1
    assert client.get(URL, headers=bob).json() == {
        "lessons": {},
        "modules": [],
        "done": 0,
        "last": None,
    }
    assert client.get("/api/me", headers=bob).json()["progress"]["last"] is None
