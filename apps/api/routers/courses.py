"""/api/courses: the course catalog, lessons, search, practice drills and flashcards."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from librarian.courses import catalog as lib
from librarian.courses import sources

router = APIRouter(prefix="/api/courses")


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
def search(q: str, limit: int = 30) -> list[dict[str, Any]]:
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


@router.get("/files/{file_path:path}")
def course_file(file_path: str) -> FileResponse:
    target = lib.asset_path(file_path)
    if target is None:
        raise HTTPException(status_code=400, detail="invalid path")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(target)


@router.get("/sources/{file_path:path}")
def course_source(file_path: str) -> FileResponse:
    """A file from COURSE_SOURCES_DIR (the PDF library). Local only: 404 when serving is off,
    the dir is missing, or the path is not a regular file inside it."""
    target = sources.source_file(file_path)
    if target is None:
        raise HTTPException(status_code=404, detail="source unavailable")
    return FileResponse(target)
