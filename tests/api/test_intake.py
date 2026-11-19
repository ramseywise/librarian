"""The intake routes: a sitting from profile to placement, resume, isolation, retake and override."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update

import librarian.api.main as main_module
import librarian.api.routers.intake as intake_routes
from librarian import accounts
from librarian.config import get_settings
from librarian.courses import catalog as courses
from librarian.courses import intake
from librarian.db import get_engine, tables

TOKEN = "bootstrap-token-0123456789abcdef"
RIGHT, WRONG = "a", "b"
SECRET = "Only in the private overlay?"


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _quiz(prompts: list[tuple[str, str]]) -> str:
    rows = "".join(
        f"- {{prompt: '{p}', options: [a, b], answer: a, depth: {d}, explanation: Because.}}\n"
        for p, d in prompts
    )
    return f"---\nquestions:\n{rows}---\n"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    root = tmp_path / "courses"
    for course in ("ds", "thin"):
        _write(root / course / "_course.md", f"---\ntitle: {course.upper()}\n---\n")
        for module in ("01-one", "02-two"):
            _write(root / course / module / "_module.md", f"---\ntitle: {module}\n---\n")
            _write(root / course / module / "note.md", "---\ntitle: Note\norder: 1\n---\n\nBody.\n")
    for module in ("01-one", "02-two"):
        _write(
            root / "ds" / module / "_quiz.md",
            _quiz([(f"{module} {d} {i}?", d) for d in ("intro", "core", "deep") for i in range(4)]),
        )
    _write(root / "thin" / "01-one" / "_quiz.md", _quiz([("Thin core?", "core")]))
    _write(root / "private" / "ds" / "01-one" / "_quiz.md", _quiz([(SECRET, "core")] * 1))
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    monkeypatch.setenv("LIBRARIAN_INTAKE_SUBJECTS", "ds,thin,absent")
    # Empty, not unset: unset would fall through to a real key in the local .env.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    # Startup refuses chat enabled without a key (api/startup.py), so the app starts with chat
    # off; the free-text tests turn it on after startup with `_chat_on`.
    monkeypatch.setenv("LIBRARIAN_CHAT_ENABLED", "false")
    get_settings.cache_clear()
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    courses._load.cache_clear()
    monkeypatch.setattr(intake, "_pool_cache", None)
    with TestClient(main_module.app) as c:
        yield c
    courses._load.cache_clear()
    monkeypatch.undo()
    get_settings.cache_clear()


def _member(email: str) -> dict[str, str]:
    engine = get_engine()
    accounts.add_user(engine, email)
    return _auth(accounts.create_key(engine, email, scopes="read write")[1])


def _chat_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_CHAT_ENABLED", "true")
    get_settings.cache_clear()


def _profile(**over: Any) -> dict[str, Any]:  # noqa: ANN401
    base: dict[str, Any] = {
        "role": "analyst",
        "goal": "do-the-work",
        "subjects": ["ds"],
        "experience": {"ds": "use-at-work"},
    }
    return base | over


def _answer(client: TestClient, me: dict[str, str], block: dict[str, Any], right: int) -> dict:
    answers = [
        {"key": q["key"], "choice": RIGHT if i < right else WRONG, "ms": 1000}
        for i, q in enumerate(block["questions"])
    ]
    resp = client.post("/api/intake/answers", json={"answers": answers}, headers=me)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _sit(client: TestClient, me: dict[str, str], first: int, second: int, **over: Any) -> dict:  # noqa: ANN401
    state = client.post("/api/intake/profile", json=_profile(**over), headers=me).json()
    state = _answer(client, me, state["block"], first)
    if state["block"]:
        state = _answer(client, me, state["block"], second)
    return state


def _placed(client: TestClient, me: dict[str, str]) -> dict[str, dict[str, Any]]:
    body = client.get("/api/placement", headers=me).json()
    return {p["subject"]: p for p in body["placements"]}


def test_nothing_is_offered_that_the_catalog_does_not_serve(client: TestClient) -> None:
    body = client.get("/api/intake", headers=_auth(TOKEN)).json()
    assert body["state"] == "none" and body["block"] is None
    assert body["offered"] == [
        {"subject": "ds", "title": "DS", "testable": True},
        {"subject": "thin", "title": "THIN", "testable": False},
    ]
    assert client.get("/api/me", headers=_auth(TOKEN)).json()["intake"] == "none"


def test_a_sitting_runs_from_profile_to_a_placement(client: TestClient) -> None:
    me = _auth(TOKEN)
    state = client.post("/api/intake/profile", json=_profile(), headers=me).json()
    assert state["state"] == "in_progress"
    block = state["block"]
    assert (block["subject"], block["block"], len(block["questions"])) == ("ds", 1, 4)
    assert all(" core " in q["prompt"] for q in block["questions"])
    assert client.get("/api/me", headers=me).json()["intake"] == "in_progress"

    state = _answer(client, me, block, 4)
    assert state["block"]["block"] == 2
    assert all(" deep " in q["prompt"] for q in state["block"]["questions"])
    state = _answer(client, me, state["block"], 4)
    assert state["state"] == "done" and state["block"] is None and state["retakeAt"]

    ds = _placed(client, me)["ds"]
    assert (ds["suggested"], ds["chosen"], ds["source"]) == ("specialist", "specialist", "test")
    assert ds["selfRating"] == "use-at-work" and ds["borderlineWith"] is None
    review = client.get("/api/placement", headers=me).json()["review"]
    assert len(review) == 8 and {r["answer"] for r in review} == {"a"}
    assert client.get("/api/me", headers=me).json()["intake"] == "done"


def test_no_key_or_explanation_is_sent_before_the_sitting_is_complete(client: TestClient) -> None:
    me = _auth(TOKEN)
    state = client.post("/api/intake/profile", json=_profile(), headers=me).json()
    assert all(set(q) == {"key", "prompt", "options"} for q in state["block"]["questions"])
    assert "Because" not in json.dumps(state)
    assert client.get("/api/placement", headers=me).json() == {"placements": [], "review": []}
    assert "Because" not in json.dumps(_answer(client, me, state["block"], 2))


def test_private_questions_are_never_served(client: TestClient) -> None:
    for i in range(6):
        me = _member(f"m{i}@example.com")
        state = client.post("/api/intake/profile", json=_profile(), headers=me).json()
        assert SECRET not in json.dumps(state)
        assert SECRET not in json.dumps(_answer(client, me, state["block"], 2))


def test_a_sitting_resumes_with_the_same_block(client: TestClient) -> None:
    me = _auth(TOKEN)
    first = client.post("/api/intake/profile", json=_profile(), headers=me).json()["block"]
    assert client.get("/api/intake", headers=me).json()["block"] == first
    second = _answer(client, me, first, 3)["block"]
    assert client.get("/api/intake", headers=me).json()["block"] == second
    # The block already answered is not accepted again, nor is part of the waiting one.
    stale = [{"key": q["key"], "choice": RIGHT} for q in first["questions"]]
    assert (
        client.post("/api/intake/answers", json={"answers": stale}, headers=me).status_code == 422
    )
    part = [{"key": second["questions"][0]["key"], "choice": RIGHT}]
    assert client.post("/api/intake/answers", json={"answers": part}, headers=me).status_code == 422


def test_dont_know_counts_as_not_right_and_is_stored_apart(client: TestClient) -> None:
    me = _auth(TOKEN)
    block = client.post("/api/intake/profile", json=_profile(), headers=me).json()["block"]
    answers = [{"key": q["key"], "choice": None} for q in block["questions"]]
    state = client.post("/api/intake/answers", json={"answers": answers}, headers=me).json()
    assert all(" intro " in q["prompt"] for q in state["block"]["questions"])
    with get_engine().connect() as conn:
        results = conn.execute(select(tables.intake_responses.c.result)).scalars().all()
    assert sorted(r or "" for r in results) == [""] * 4 + ["dont_know"] * 4
    bad = [{"key": q["key"], "choice": "z"} for q in state["block"]["questions"]]
    assert client.post("/api/intake/answers", json={"answers": bad}, headers=me).status_code == 422


def test_someone_new_starts_on_intro_and_stops_there_without_a_pass(client: TestClient) -> None:
    me = _auth(TOKEN)
    state = client.post(
        "/api/intake/profile", json=_profile(experience={"ds": "never"}), headers=me
    ).json()
    assert all(" intro " in q["prompt"] for q in state["block"]["questions"])
    state = _answer(client, me, state["block"], 1)
    assert state["state"] == "done"
    assert _placed(client, me)["ds"]["suggested"] == "foundations"


def test_a_borderline_result_names_the_neighbour_and_either_choice_is_no_override(
    client: TestClient,
) -> None:
    me = _auth(TOKEN)
    _sit(client, me, 4, 2)
    ds = _placed(client, me)["ds"]
    assert (ds["suggested"], ds["chosen"], ds["borderlineWith"]) == (
        "practitioner",
        "practitioner",
        "specialist",
    )
    put = client.put("/api/placement/ds", json={"tier": "specialist"}, headers=me).json()
    assert (put["placements"][0]["chosen"], put["placements"][0]["source"]) == (
        "specialist",
        "test",
    )
    put = client.put("/api/placement/ds", json={"tier": "foundations"}, headers=me).json()
    assert (put["placements"][0]["chosen"], put["placements"][0]["source"]) == (
        "foundations",
        "override",
    )
    assert put["placements"][0]["suggested"] == "practitioner"
    assert client.put("/api/placement/ds", json={"tier": "guru"}, headers=me).status_code == 422
    assert (
        client.put("/api/placement/nope", json={"tier": "foundations"}, headers=me).status_code
        == 404
    )


def test_skipped_and_thin_subjects_are_placed_from_the_goal(client: TestClient) -> None:
    me = _auth(TOKEN)
    profile = _profile(
        goal="go-deep",
        subjects=["ds", "thin"],
        experience={"ds": "read-about", "thin": "could-teach"},
        untested=["ds"],
    )
    state = client.post("/api/intake/profile", json=profile, headers=me).json()
    assert state["state"] == "done" and state["block"] is None
    placed = _placed(client, me)
    assert {s: (p["chosen"], p["source"]) for s, p in placed.items()} == {
        "ds": ("specialist", "goal"),
        "thin": ("specialist", "goal"),
    }


@pytest.mark.parametrize(
    "over",
    [
        {"role": "wizard"},
        {"goal": "win"},
        {"subjects": ["absent"], "experience": {"absent": "never"}},
        {"experience": {}},
        {"untested": ["thin"]},
        {"hoursPerWeek": 0},
        {"subjects": ["ds", "ds"]},
    ],
)
def test_a_bad_profile_is_refused(client: TestClient, over: dict[str, Any]) -> None:
    me = _auth(TOKEN)
    assert client.post("/api/intake/profile", json=_profile(**over), headers=me).status_code == 422
    assert client.get("/api/intake", headers=me).json()["state"] == "none"


def test_the_profile_can_change_until_the_first_answer(client: TestClient) -> None:
    me = _auth(TOKEN)
    client.post("/api/intake/profile", json=_profile(), headers=me)
    state = client.post("/api/intake/profile", json=_profile(role="engineer"), headers=me).json()
    assert state["profile"]["role"] == "engineer"
    _answer(client, me, state["block"], 4)
    assert client.post("/api/intake/profile", json=_profile(), headers=me).status_code == 409


def test_a_retake_waits_and_then_draws_unseen_questions_first(client: TestClient) -> None:
    me = _auth(TOKEN)
    _sit(client, me, 0, 0)
    with get_engine().connect() as conn:
        seen = set(conn.execute(select(tables.intake_responses.c.question_key)).scalars())
    assert client.post("/api/intake/profile", json=_profile(), headers=me).status_code == 409
    long_ago = datetime.now(UTC) - timedelta(days=8)
    with get_engine().begin() as conn:
        conn.execute(update(tables.intakes).values(completed_at=long_ago, started_at=long_ago))
    state = client.post("/api/intake/profile", json=_profile(), headers=me).json()
    assert state["state"] == "in_progress"
    assert not {q["key"] for q in state["block"]["questions"]} & seen
    # The earlier placement stands until the new sitting is finished.
    assert _placed(client, me)["ds"]["suggested"] == "foundations"
    state = _answer(client, me, state["block"], 4)
    _answer(client, me, state["block"], 4)
    assert _placed(client, me)["ds"]["suggested"] == "specialist"


def test_two_users_do_not_see_or_change_each_other(client: TestClient) -> None:
    ann, bob = _member("ann@example.com"), _member("bob@example.com")
    _sit(client, ann, 4, 4)
    assert client.get("/api/intake", headers=bob).json()["state"] == "none"
    assert client.get("/api/placement", headers=bob).json() == {"placements": [], "review": []}
    block = client.post("/api/intake/profile", json=_profile(), headers=bob).json()["block"]
    _answer(client, bob, block, 0)
    client.put("/api/placement/ds", json={"tier": "foundations"}, headers=bob)
    assert _placed(client, ann)["ds"]["chosen"] == "specialist"
    assert client.get("/api/intake", headers=ann).json()["state"] == "done"


def test_the_routes_need_a_signed_in_caller(client: TestClient) -> None:
    assert client.get("/api/intake").status_code == 401
    assert client.get("/api/placement").status_code == 401
    assert client.post("/api/intake/profile", json=_profile()).status_code == 401


def test_free_text_is_kept_uninterpreted_without_a_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _chat_on(monkeypatch)
    me = _auth(TOKEN)
    profile = _profile(interestsText="  Causal inference for pricing.  ")
    state = client.post("/api/intake/profile", json=profile, headers=me).json()
    assert state["interests"] == {"modules": [], "restatement": "", "interpreted": False}
    assert state["profile"]["interestsText"] == "Causal inference for pricing."


def test_interests_are_mapped_to_public_modules_only(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    sent: list[str] = []

    class _Block:
        type = "text"
        text = json.dumps(
            {"modules": ["ds/02-two", "private/ds/x", "nope"], "restatement": "Wants stats."}
        )

    class _Messages:
        async def create(self, **kwargs: Any) -> Any:  # noqa: ANN401
            sent.append(kwargs["messages"][0]["content"])
            return type("Resp", (), {"content": [_Block()], "usage": None})()

    monkeypatch.setattr(
        intake_routes, "_get_client", lambda: type("C", (), {"messages": _Messages()})()
    )
    _chat_on(monkeypatch)
    me = _auth(TOKEN)
    profile = _profile(interestsText="Statistics.")
    state = client.post("/api/intake/profile", json=profile, headers=me).json()
    assert state["interests"] == {
        "modules": ["ds/02-two"],
        "restatement": "Wants stats.",
        "interpreted": True,
    }
    assert len(sent) == 1 and "ds/01-one" in sent[0] and "thin/01-one" in sent[0]


def test_a_reply_that_cannot_be_read_is_no_interests() -> None:
    modules = {"ds/01-one": "One"}
    assert intake.parse_interests("no json here", modules) is None
    assert intake.parse_interests('{"modules": "ds/01-one"}', modules) is None
    assert intake.parse_interests('Sure: {"modules": ["ds/01-one", "ds/01-one"]}', modules) == {
        "modules": ["ds/01-one"],
        "restatement": "",
        "interpreted": True,
    }
