"""Reader feedback.

POST   /api/feedback               rate an answer, report a page or lesson (201 {id})
GET    /api/feedback/mine          the caller's rows, newest first (at most 200)
DELETE /api/feedback/{id}          delete one of the caller's rows (404 for anyone else's)
GET    /api/admin/feedback/summary the top ten of each signal (admins only; no emails or user ids)
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from librarian import experiments, feedback
from librarian.accounts import rate_limits
from librarian.agent.loop import AGENT_LOG_NAME
from librarian.api.routers.release import served_release
from librarian.api.security import Admin, SignedIn
from librarian.config import get_release, get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger
from librarian.retrieval import corpus

log = get_logger(__name__)

router = APIRouter()


class NewFeedback(BaseModel):
    # `unanswered` rows are written by the chat route, never by the client.
    kind: Literal["answer", "page", "lesson"]
    target: str = Field(min_length=1, max_length=feedback.MAX_TARGET)
    rating: Literal[1, -1] | None = None
    body: str | None = Field(default=None, max_length=feedback.MAX_BODY * 2)


def _json(f: feedback.Feedback) -> dict[str, Any]:
    return {
        "id": f.id,
        "ts": f.ts.isoformat(),
        "kind": f.kind,
        "target": f.target,
        "rating": f.rating,
        "body": f.body,
        "release": f.release,
        "experiment": f.experiment,
    }


def _admit(user_id: str) -> None:
    """429 when the caller has written too many rows in the window (counted across workers)."""
    settings = get_settings()
    limit, window = settings.feedback_rate_limit, settings.feedback_rate_window_s
    if limit <= 0:
        return
    try:
        shared = rate_limits.hit(get_engine(), f"feedback:{user_id}", window)
    except SQLAlchemyError as e:
        log.error("feedback.rate_limit_unavailable", error=str(e), fail="open")
        return
    if shared.hits > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Too much feedback: {limit} per {window}s. Retry in {shared.retry_after_s}s.",
            headers={"Retry-After": str(shared.retry_after_s)},
        )


@router.post("/api/feedback", status_code=201)
def post_feedback(body: NewFeedback, user: SignedIn, request: Request) -> dict[str, str]:
    """Store one signal. The release and experiment variant are filled in here, not by the client."""
    _admit(user.id)
    settings = get_settings()
    variant = experiments.resolve(
        settings,
        user.id,
        is_admin=user.is_admin,
        override=request.headers.get(experiments.VARIANT_HEADER),
    )
    try:
        row_id = feedback.record(
            get_engine(),
            user_id=user.id,
            kind=body.kind,
            target=body.target,
            rating=body.rating,
            body=body.body,
            release=served_release() or get_release(),
            experiment=variant,
        )
    except feedback.FeedbackError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return {"id": row_id}


@router.get("/api/feedback/mine")
def my_feedback(user: SignedIn) -> list[dict[str, Any]]:
    return [_json(f) for f in feedback.mine(get_engine(), user.id)]


@router.delete("/api/feedback/{feedback_id}", status_code=204)
def delete_feedback(feedback_id: str, user: SignedIn) -> None:
    if not feedback.delete(get_engine(), user.id, feedback_id):
        raise HTTPException(status_code=404, detail="No feedback of yours with that id.")


@router.get("/api/admin/feedback/summary")
def feedback_summary(_: Admin) -> dict[str, list[dict[str, Any]]]:
    return feedback.summary(get_engine(), corpus.LOGS_DIR / AGENT_LOG_NAME)
