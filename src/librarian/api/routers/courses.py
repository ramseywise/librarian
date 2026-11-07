"""/api/courses: the course catalog, lessons, search, practice drills, flashcards, quizzes and slides."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from librarian.courses import catalog as lib
from librarian.courses import slides, sources, study

router = APIRouter(prefix="/api/courses")

# Files are served same-origin. An SVG carrying script would run if opened directly, so image
# responses get a CSP that forbids script and sandboxes the document; <img> use is unaffected.
_NOSNIFF = {"X-Content-Type-Options": "nosniff"}
_ASSET_CSP = "default-src 'none'; style-src 'unsafe-inline'; sandbox"


@router.get("")
def list_courses() -> list[dict[str, Any]]:
    return lib.list_courses()


@router.get("/lessons/{lesson_id:path}")
def get_lesson(lesson_id: str) -> dict[str, Any]:
    detail = lib.lesson_detail(lesson_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="lesson not found")
    return detail


@router.get("/search")
def search(q: str, limit: int = Query(30, ge=1, le=50)) -> list[dict[str, Any]]:
    return lib.search_lessons(q, limit)


@router.get("/concept/{page_id}")
def lessons_for_concept(page_id: str) -> list[dict[str, Any]]:
    return lib.lessons_for_concept(page_id)


@router.get("/practice")
def practice(
    track: str | None = None, difficulty: str | None = None, concept: str | None = None
) -> list[dict[str, Any]]:
    return lib.practice_drills(track, difficulty, concept)


@router.get("/flashcards/{deck_id:path}")
def flashcards(deck_id: str) -> dict[str, Any]:
    deck = lib.study_deck(deck_id)
    if deck is None:
        raise HTTPException(status_code=404, detail="no flashcards here")
    return deck


@router.get("/flashcards-due")
def flashcards_due() -> dict[str, Any]:
    return lib.flashcards_due()


class CardResult(BaseModel):
    deck: str
    card: str
    result: Literal["knew", "missed"]


@router.post("/flashcard-results")
def flashcard_result(body: CardResult) -> dict[str, bool]:
    """A failed write returns logged=false rather than an error: it must not interrupt studying."""
    logged = lib.log_flashcard_result(body.deck, body.card, body.result)
    if logged is None:
        raise HTTPException(status_code=404, detail="no such card")
    return {"logged": logged}


@router.get("/quiz/{quiz_id:path}")
def quiz_deck(quiz_id: str) -> dict[str, Any]:
    """A module's or lesson's multiple-choice questions, without the answers."""
    found = study.quiz_deck(quiz_id)
    if found is None:
        raise HTTPException(status_code=404, detail="no quiz here")
    return found


class QuizAnswer(BaseModel):
    quiz: str
    question: str
    choice: str


@router.post("/quiz-results")
def quiz_result(body: QuizAnswer) -> dict[str, Any]:
    """Grade one answer on the server. A failed write returns logged=false, never an error."""
    try:
        graded = study.answer_question(body.quiz, body.question, body.choice)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    if graded is None:
        raise HTTPException(status_code=404, detail="no such question")
    return graded


class DrillResult(BaseModel):
    drill: str
    result: Literal["pass", "fail", "revealed"]


@router.post("/drill-results")
def drill_result(body: DrillResult) -> dict[str, bool]:
    logged = study.record_drill(body.drill, body.result)
    if logged is None:
        raise HTTPException(status_code=404, detail="no such drill")
    return {"logged": logged}


@router.get("/study")
def study_home() -> dict[str, Any]:
    """The study queue: cards and questions due, the next drill, the current module's lecture."""
    return study.home()


@router.get("/slides/{deck_id:path}")
def slide_deck(deck_id: str) -> dict[str, Any]:
    """A module's deck or one lecture: slide text, notes and image URLs.

    Read-only, from prebuilt files: `stale` says a dev build is due; POST .../build starts it (dev only).
    """
    found = slides.deck(deck_id)
    if found is None:
        raise HTTPException(status_code=404, detail="no slides here")
    return found


@router.post("/slides/{deck_id:path}/build")
def slide_deck_build(deck_id: str) -> dict[str, Any]:
    """Start a background build if the deck is missing or stale, and answer as the GET does.

    Dev only: 404 unless LIBRARIAN_DEV_BUILD_SLIDES is on. A deployment has no such route, rather
    than one that refuses (403 would say the route exists and the caller lacks a right to it).
    """
    if not slides.build_enabled():
        raise HTTPException(status_code=404, detail="not found")
    found = slides.build_deck(deck_id)
    if found is None:
        raise HTTPException(status_code=404, detail="no slides here")
    return found


@router.get("/slide-image/{deck_id:path}/{n}")
def slide_image(deck_id: str, n: int) -> FileResponse:
    target = slides.image_path(deck_id, n)
    if target is None:
        raise HTTPException(status_code=404, detail="no such slide image")
    return FileResponse(target, media_type="image/png", headers=_NOSNIFF)


@router.get("/files/{file_path:path}")
def course_file(file_path: str) -> FileResponse:
    if lib.is_private_asset(file_path):
        raise HTTPException(status_code=404, detail="not found")
    target = lib.asset_path(file_path)
    if target is None:
        raise HTTPException(status_code=400, detail="invalid path")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(target, headers={**_NOSNIFF, "Content-Security-Policy": _ASSET_CSP})


@router.get("/sources/{file_path:path}")
def course_source(file_path: str) -> FileResponse:
    """A file from COURSE_SOURCES_DIR (the PDF library). Local only: 404 when serving is off,
    the dir is missing, or the path is not a regular file inside it."""
    target = sources.source_file(file_path)
    if target is None:
        raise HTTPException(status_code=404, detail="source unavailable")
    return FileResponse(target, headers=_NOSNIFF)
