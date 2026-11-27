"""/api/learning: concept mastery for the signed-in user.

    POST /api/learning/events           one study event
    POST /api/learning/reconcile        merge a browser's locally stored done marks
    GET  /api/learning/state            mastery per concept and module, lessons done
    GET  /api/learning/next?limit=      the Due list, weakest first
    GET  /api/learning/concept/{id}     a public wiki page's hub: mastery plus what links to it

Every route is per user (`SignedIn`); the maths and the stores live in `librarian.courses.learning`.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from librarian.api.security import SignedIn
from librarian.courses import catalog as courses
from librarian.courses import learning

router = APIRouter(prefix="/api/learning")


# Sync routes (threadpool): the first call builds the catalog.
@router.post("/events")
def post_event(user: SignedIn, body: learning.EventIn) -> dict[str, Any]:
    try:
        return learning.record_event(user.id, body)
    except learning.LearningError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/reconcile")
def post_reconcile(user: SignedIn, body: learning.ReconcileIn) -> dict[str, list[str]]:
    try:
        return learning.reconcile(user.id, body)
    except learning.LearningError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.get("/state")
def get_state(user: SignedIn) -> dict[str, Any]:
    return learning.build_state(user.id, courses.catalog(), learning.utcnow())


@router.get("/next")
def get_next(user: SignedIn, limit: int = Query(5, ge=1, le=20)) -> list[dict[str, Any]]:
    return learning.build_next(user.id, courses.catalog(), learning.utcnow(), limit)


@router.get("/concept/{page_id}")
def get_concept(user: SignedIn, page_id: str) -> dict[str, Any]:
    found = learning.build_concept(user.id, courses.catalog(), page_id, learning.utcnow())
    if found is None:
        raise HTTPException(status_code=404, detail="no such page")
    return found
