"""Phase 3 check: two people sign in through the full app and never see each other's study.

The owner signs in with Google, invites Bob, Bob signs in with an emailed link, and both use
the course routes through their own cookie session. Providers and mail are faked.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian.accounts import mailer, oauth
from librarian.api.security import CSRF_COOKIE, auth_limiter
from librarian.config import get_settings
from librarian.courses import catalog as courses

BASE = "https://testserver"
OWNER = "owner@example.com"
BOB = "bob@example.com"
MOD = "gen-ai/01-rag"
QUIZ = "---\nquestions:\n- {id: q1, prompt: 'Which?', options: [a, b], answer: b}\n---\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class Providers:
    def __init__(self) -> None:
        self.mail: list[dict[str, Any]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("oauth2.googleapis.com/token"):
            return httpx.Response(200, json={"access_token": "at", "token_type": "bearer"})
        if url.endswith("/v1/userinfo"):
            return httpx.Response(200, json={"email": OWNER, "email_verified": True})
        if url == mailer.RESEND_URL:
            self.mail.append(json.loads(request.content))
            return httpx.Response(200, json={"id": "m1"})
        return httpx.Response(404)


@pytest.fixture()
def fake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Providers]:
    f = Providers()
    transport = httpx.MockTransport(f.handler)
    monkeypatch.setattr(oauth, "transport", transport)
    monkeypatch.setattr(mailer, "transport", transport)
    monkeypatch.delenv("LIBRARIAN_API_TOKEN", raising=False)
    for k, v in {
        "LIBRARIAN_OWNER_EMAIL": OWNER,
        "LIBRARIAN_PUBLIC_URL": BASE,
        "LIBRARIAN_SESSION_SECRET": "s" * 40,
        "GOOGLE_CLIENT_ID": "gid",
        "GOOGLE_CLIENT_SECRET": "gsecret",
        "RESEND_API_KEY": "re_test",
        "EMAIL_FROM": "Librarian <login@example.com>",
    }.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()

    root = tmp_path / "courses"
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\n---\n")
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\n---\n")
    _write(root / "gen-ai" / "01-rag" / "intro.md", "---\ntitle: Intro\n---\n\nBody.\n")
    _write(root / "gen-ai" / "01-rag" / "_quiz.md", QUIZ)
    _write(
        root / "gen-ai" / "01-rag" / "_flashcards.md", "---\ncards:\n- {front: F, back: B}\n---\n"
    )
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    courses._load.cache_clear()
    auth_limiter.reset()
    yield f
    auth_limiter.reset()
    courses._load.cache_clear()
    monkeypatch.undo()
    get_settings.cache_clear()


def _browser() -> TestClient:
    return TestClient(main_module.app, base_url=BASE, follow_redirects=False)


def _csrf(c: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": c.cookies[CSRF_COOKIE], "Origin": BASE}


def test_two_people_study_side_by_side(fake: Providers) -> None:
    with _browser() as owner, _browser() as bob:
        # Owner: Google sign-in, then an invite for Bob.
        start = owner.get("/auth/login/google", params={"next": "/#/study"})
        state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
        assert (
            owner.get("/auth/callback/google", params={"code": "c", "state": state}).status_code
            == 303
        )
        assert owner.get("/api/me").json()["email"] == OWNER
        assert owner.post("/api/admin/invites", json={"email": BOB}, headers=_csrf(owner)).json()[
            "added"
        ]

        # Bob: not signed in, then an emailed link.
        assert bob.get("/api/me").status_code == 401
        assert bob.post("/auth/email", json={"email": BOB, "next": "/#/study"}).json() == {
            "sent": True
        }
        link = urlsplit(fake.mail[-1]["text"].split("\n\n")[1])
        form = {k: v[0] for k, v in parse_qs(link.query).items()}
        landed = bob.post("/auth/email/verify", data=form, headers={"Origin": BASE})
        assert (landed.status_code, landed.headers["location"]) == (303, "/#/study")
        me = bob.get("/api/me").json()
        assert (me["email"], me["role"]) == (BOB, "member")

        # Bob studies: a finished lesson, a missed card, a wrong answer.
        h = _csrf(bob)
        bob.post(
            "/api/courses/progress", json={"lesson": f"{MOD}/intro", "state": "done"}, headers=h
        )
        card = {"deck": MOD, "card": "0", "result": "missed"}
        assert bob.post("/api/courses/flashcard-results", json=card, headers=h).json() == {
            "logged": True
        }
        answer = {"quiz": MOD, "question": "q1", "choice": "a"}
        assert (
            bob.post("/api/courses/quiz-results", json=answer, headers=h).json()["correct"] is False
        )

        # The owner's history is untouched, and Bob's is his.
        assert owner.get("/api/courses/progress").json()["done"] == 0
        assert bob.get("/api/courses/progress").json()["done"] == 1
        assert owner.get("/api/courses/study").json()["new"] == 2
        assert bob.get("/api/courses/study").json()["new"] == 0

        # Bob is a member: no admin pages, and no write without the CSRF header.
        assert bob.get("/api/admin/users").status_code == 403
        no_csrf = bob.post(
            "/api/courses/progress", json={"lesson": f"{MOD}/intro", "state": "opened"}
        )
        assert no_csrf.status_code == 403

        # The owner sees both people; signing Bob out does not sign the owner out.
        assert {u["email"] for u in owner.get("/api/admin/users").json()} == {OWNER, BOB}
        assert bob.post("/auth/logout", headers=_csrf(bob)).status_code in (200, 204, 303)
        assert bob.get("/api/me").status_code == 401
        assert owner.get("/api/me").status_code == 200
