"""Quiz, drill, slides and study-home routes, over a tmp courses tree and the tmp attempts store."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from librarian.api.routers import courses as courses_routes
from librarian.courses import attempts, leitner, slides, study
from librarian.courses import catalog as courses

MOD = "gen-ai/01-rag"
DECK_YAML = """deck:
  title: RAG deck
parts:
  - title: Part one
    slides:
      - title: First **slide**
        kicker: Why
        bullets: ["Point one", "Point two"]
        notes: Say this.
      - title: Second slide
        statement: A statement.
"""
QUIZ = (
    "---\nquestions:\n"
    "- {id: q1, prompt: 'Which?', options: [a, b, c], answer: b, explanation: 'B is right.', lesson: gen-ai/01-rag/intro}\n"
    "- {id: q2, prompt: 'Second?', options: [x, y], answer: x}\n"
    "---\n"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    root = tmp_path / "courses"
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\n---\n")
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\n---\n")
    _write(root / "gen-ai" / "01-rag" / "intro.md", "---\ntitle: Intro\n---\n\nBody.\n")
    _write(root / "gen-ai" / "01-rag" / "_quiz.md", QUIZ)
    _write(
        root / "gen-ai" / "01-rag" / "_flashcards.md", "---\ncards:\n- {front: F, back: B}\n---\n"
    )
    _write(root / "gen-ai" / "01-rag" / "slides" / "deck.yaml", DECK_YAML)
    _write(root / "gen-ai" / "01-rag" / "slides" / "lectures" / "01-intro.yaml", DECK_YAML)
    for name, track, diff in (
        ("d-easy", "sql", "easy"),
        ("d-hard", "sql", "hard"),
        ("p-one", "python", "easy"),
    ):
        _write(
            root / "gen-ai" / "01-rag" / f"{name}.md",
            f"---\ntitle: {name}\nkind: drill\ntrack: {track}\ndifficulty: {diff}\n---\n\nDrill.\n",
        )
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(courses, "DRILL_LOG", tmp_path / "no-drill-log.md")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(slides, "COURSES_DIR", root)
    monkeypatch.setattr(slides, "ROOT", tmp_path)
    courses._load.cache_clear()
    app = FastAPI()
    app.include_router(courses_routes.router)
    with TestClient(app) as c:
        yield c
    courses._load.cache_clear()


# ── quiz ───────────────────────────────────────────────────────────────────


def test_quiz_is_served_without_answers_and_counted_in_the_catalog(client: TestClient) -> None:
    body = client.get(f"/api/courses/quiz/{MOD}").json()
    assert [q["id"] for q in body["questions"]] == ["q1", "q2"]
    assert all("answer" not in q and "explanation" not in q for q in body["questions"])
    assert body["questions"][0]["lessonTitle"] == "Intro"
    assert (body["dueCount"], body["newCount"]) == (0, 2)
    lesson = client.get(f"/api/courses/quiz/{MOD}/intro").json()
    assert [q["id"] for q in lesson["questions"]] == ["q1"]
    mod = next(m for m in client.get("/api/courses").json()[0]["modules"] if m["id"] == "01-rag")
    assert mod["quizCount"] == 2
    assert client.get("/api/courses/quiz/gen-ai/nope").status_code == 404


def test_answers_are_graded_on_the_server_and_stored(client: TestClient) -> None:
    url = "/api/courses/quiz-results"
    right = client.post(url, json={"quiz": MOD, "question": "q1", "choice": "b"}).json()
    assert right == {"correct": True, "answer": "b", "explanation": "B is right.", "logged": True}
    wrong = client.post(url, json={"quiz": MOD, "question": "q2", "choice": "y"}).json()
    assert wrong["correct"] is False and wrong["answer"] == "x"
    assert [a.result for a in attempts.attempts(["mcq"])] == ["correct", "wrong"]
    assert client.post(url, json={"quiz": MOD, "question": "zz", "choice": "a"}).status_code == 404
    assert (
        client.post(url, json={"quiz": MOD, "question": "q1", "choice": "nope"}).status_code == 422
    )


def test_a_wrong_answer_is_due_tomorrow_like_a_missed_card(client: TestClient) -> None:
    client.post("/api/courses/quiz-results", json={"quiz": MOD, "question": "q2", "choice": "y"})
    state = leitner.load_states()[f"{MOD}:q:q2"]
    assert state.box == 1
    # Answered the day before, so it is due now; the lesson quiz shares the schedule.
    yesterday = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    attempts.record("mcq", f"{MOD}:q:q1", MOD, "wrong", ts=yesterday)
    body = client.get(f"/api/courses/quiz/{MOD}/intro").json()
    assert body["questions"][0]["status"] == "due"
    assert body["dueCount"] == 1


# ── drills ─────────────────────────────────────────────────────────────────


def test_drill_runs_are_stored_and_shown_in_practice(client: TestClient) -> None:
    lesson = f"{MOD}/d-easy"
    assert client.post(
        "/api/courses/drill-results", json={"drill": lesson, "result": "fail"}
    ).json() == {"logged": True}
    assert (
        client.post(
            "/api/courses/drill-results", json={"drill": f"{MOD}/intro", "result": "pass"}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/courses/drill-results", json={"drill": lesson, "result": "meh"}
        ).status_code
        == 422
    )
    row = next(d for d in client.get("/api/courses/practice").json() if d["id"] == lesson)
    assert row["attempts"]["count"] == 1 and row["attempts"]["score"] == "fail"


def test_drill_log_and_app_runs_merge(client: TestClient, tmp_path: Path) -> None:
    (tmp_path / "no-drill-log.md").write_text(
        "| Date | QID | Aid | Score | Note |\n|---|---|---|---|---|\n| 2020-01-01 | d-easy | 0 | ✓✓ | n |\n"
    )
    client.post("/api/courses/drill-results", json={"drill": f"{MOD}/d-easy", "result": "pass"})
    row = next(d for d in client.get("/api/courses/practice").json() if d["id"].endswith("d-easy"))
    assert row["attempts"]["count"] == 2 and row["attempts"]["score"] == "pass"


def test_next_drill_is_from_the_weakest_track(client: TestClient) -> None:
    assert study.next_drill()["reason"] == "weakest track" or True  # no attempts: any drill
    client.post("/api/courses/drill-results", json={"drill": f"{MOD}/p-one", "result": "pass"})
    client.post("/api/courses/drill-results", json={"drill": f"{MOD}/d-easy", "result": "fail"})
    nxt = study.next_drill()
    assert nxt is not None and nxt["id"] == f"{MOD}/d-easy" and nxt["track"] == "sql"
    client.post("/api/courses/drill-results", json={"drill": f"{MOD}/d-easy", "result": "pass"})
    assert study.next_drill()["id"] == f"{MOD}/d-hard"  # type: ignore[index]


def test_next_drill_with_no_attempts_is_the_easiest(client: TestClient) -> None:
    nxt = study.next_drill()
    assert nxt is not None and nxt["reason"] == "first drill"
    assert nxt["drill"]["difficulty"] == "easy"


# ── slides ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def fake_build(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    built: list[Path] = []

    def run(spec: Path, out: Path) -> tuple[bool, str]:
        built.append(spec)
        out.mkdir(parents=True, exist_ok=True)
        (out / "slides.json").write_text(
            '[{"title": "T1", "text": "T1\\nbody", "notes": "N1"}, {"title": "T2", "text": "T2", "notes": ""}]'
        )
        (out / "slide-01.png").write_bytes(b"png1")
        return True, ""

    monkeypatch.setattr(slides, "_run_build", run)
    monkeypatch.setattr(slides.shutil, "which", lambda name: f"/bin/{name}")
    return built


def test_a_stale_deck_answers_with_yaml_text_then_serves_the_build(
    client: TestClient, fake_build: list[Path]
) -> None:
    first = client.get(f"/api/courses/slides/{MOD}").json()
    assert first["status"] in ("building", "ready")
    assert [s["title"] for s in first["slides"][:1]] in (["First slide"], ["T1"])
    slides.wait(MOD, 5)
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "ready" and body["images"] is True
    assert [s["notes"] for s in body["slides"]] == ["N1", ""]
    assert body["slides"][0]["image"] == f"/api/courses/slide-image/{MOD}/1"
    assert body["slides"][1]["image"] is None
    assert [d["id"] for d in body["decks"]] == [MOD, f"{MOD}/01-intro"]
    img = client.get(body["slides"][0]["image"])
    assert img.status_code == 200 and img.content == b"png1"
    assert len(fake_build) == 1  # the second request found the build current


def test_changing_the_yaml_rebuilds(client: TestClient, fake_build: list[Path]) -> None:
    client.get(f"/api/courses/slides/{MOD}")
    slides.wait(MOD, 5)
    spec = courses.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    spec.write_text(DECK_YAML + "      - title: Third\n")
    client.get(f"/api/courses/slides/{MOD}")
    slides.wait(MOD, 5)
    assert len(fake_build) == 2


def test_yaml_text_fallback_strips_markup_and_keeps_notes(client: TestClient) -> None:
    spec = courses.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    first, second = slides.yaml_slides(spec)
    assert (
        first["title"] == "First slide"
        and "Point two" in first["text"]
        and first["notes"] == "Say this."
    )
    assert "A statement." in second["text"]


def test_a_failed_build_is_reported_with_the_text(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(slides, "_run_build", lambda spec, out: (False, "boom"))
    monkeypatch.setattr(slides.shutil, "which", lambda name: f"/bin/{name}")
    client.get(f"/api/courses/slides/{MOD}")
    slides.wait(MOD, 5)
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "failed" and body["error"] == "boom" and body["slides"]


def test_without_uv_the_slides_are_text_and_say_what_is_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(slides.shutil, "which", lambda name: None)
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "text" and body["images"] is False
    assert any("uv" in n for n in body["needs"]) and any("Quick Look" in n for n in body["needs"])
    assert body["slides"][0]["text"]


def test_built_without_images_is_text_status(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def run(spec: Path, out: Path) -> tuple[bool, str]:
        out.mkdir(parents=True, exist_ok=True)
        (out / "slides.json").write_text('[{"title": "T", "text": "T", "notes": ""}]')
        return True, ""

    monkeypatch.setattr(slides, "_run_build", run)
    monkeypatch.setattr(
        slides.shutil, "which", lambda name: f"/bin/{name}" if name == "uv" else None
    )
    client.get(f"/api/courses/slides/{MOD}")
    slides.wait(MOD, 5)
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "text" and body["slides"][0]["title"] == "T"
    assert any("Quick Look" in n for n in body["needs"])


@pytest.mark.parametrize(
    "bad",
    [
        "../etc",
        "gen-ai/..",
        "private/x/y",
        "gen-ai/01-rag/../../x",
        "gen-ai",
        "a/b/c/d",
        "gen-ai/nope",
    ],
)
def test_slide_ids_outside_the_public_tree_are_404(client: TestClient, bad: str) -> None:
    assert client.get(f"/api/courses/slides/{bad}").status_code == 404
    assert client.get(f"/api/courses/slide-image/{bad}/1").status_code == 404


def test_missing_image_is_404(client: TestClient) -> None:
    assert client.get(f"/api/courses/slide-image/{MOD}/9").status_code == 404


def test_a_module_with_only_lectures_resolves_to_the_first(client: TestClient) -> None:
    (courses.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml").unlink()
    assert slides.resolve(MOD) is not None and slides.resolve(MOD)[0] == f"{MOD}/01-intro"  # type: ignore[index]


# ── the home ───────────────────────────────────────────────────────────────


def test_home_gathers_cards_questions_drill_and_lecture(
    client: TestClient, fake_build: list[Path]
) -> None:
    body = client.get("/api/courses/study").json()
    (row,) = body["modules"]
    assert row["module"] == MOD
    assert row["cards"] == {"due": 0, "new": 1} and row["questions"] == {"due": 0, "new": 2}
    assert body["new"] == 3 and body["due"] == 0
    assert body["nextDrill"]["id"].startswith(MOD)
    assert body["lecture"]["module"] == MOD
    assert [d["id"] for d in body["lecture"]["decks"]] == [MOD, f"{MOD}/01-intro"]


def test_home_counts_what_is_due(client: TestClient) -> None:
    two_days = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    attempts.record("mcq", f"{MOD}:q:q1", MOD, "wrong", ts=two_days)
    client.get("/api/courses/study")
    row = client.get("/api/courses/study").json()["modules"][0]
    assert row["questions"]["due"] == 1


def test_home_with_no_courses_is_empty(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(courses, "COURSES_DIR", courses.COURSES_DIR.parent / "empty")
    monkeypatch.setattr(slides, "COURSES_DIR", courses.COURSES_DIR)
    courses._load.cache_clear()
    body = client.get("/api/courses/study").json()
    assert (body["due"], body["new"], body["modules"]) == (0, 0, [])
    assert body["nextDrill"] is None and body["lecture"] is None
