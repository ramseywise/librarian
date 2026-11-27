"""/api/voice: the browser's one origin for the voice process.

The API never imports `librarian.voice` or Pipecat (an import-linter contract). This only forwards
over HTTP, so the API and the rest of the app run the same whether `make voice` is running or
not, and its absence is one clear 503. The signed-in user goes along as a header, so the voice
process records the session's grades for them.

A page on another origin must not be able to send a WebRTC offer, whatever CORS would say about
reading the answer: the request itself is what starts a billed session. Both this and the voice
process check the origin and the host.
"""

from __future__ import annotations

import os
from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from librarian.api.security import SignedIn
from librarian.log_config import get_logger

log = get_logger(__name__)

NOT_RUNNING = "voice server not running, start with make voice"
DEFAULT_VOICE_URL = "http://127.0.0.1:8200"
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1"})
USER_HEADER = "x-librarian-user"  # the same name as `librarian.voice.server.USER_HEADER`
STATUS_TIMEOUT_S = 2.0
# The voice process has its own offer timeout, and this must outlast it to carry its message.
REQUEST_TIMEOUT_S = 40.0

router = APIRouter(prefix="/api/voice", tags=["voice"])


def _voice_url() -> str:
    return os.environ.get("VOICE_URL", DEFAULT_VOICE_URL).rstrip("/")


def _allowed_origins() -> set[str]:
    raw = os.environ.get("VOICE_ALLOWED_ORIGINS", "") or DEFAULT_ORIGINS
    return {o.strip().rstrip("/") for o in raw.split(",") if o.strip()}


def _check_request(request: Request) -> None:
    """An absent Origin means no browser page sent this. Any page that did, says where from."""
    origin = request.headers.get("origin")
    if origin is not None and origin.rstrip("/") not in _allowed_origins():
        raise HTTPException(status_code=403, detail="that origin may not use voice")
    if urlsplit(f"//{request.headers.get('host', '')}").hostname not in ALLOWED_HOSTS:
        raise HTTPException(status_code=403, detail="voice only serves this machine")


async def _forward(
    method: str,
    path: str,
    body: object = None,
    timeout: float = REQUEST_TIMEOUT_S,
    user_id: str | None = None,
) -> JSONResponse:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # No Origin goes along: this request has passed the check, and the voice process
            # rejects a page that reaches it directly, by the Origin that page must send.
            headers = {USER_HEADER: user_id} if user_id else {}
            response = await client.request(
                method, f"{_voice_url()}{path}", json=body, headers=headers
            )
    except httpx.TransportError as e:
        log.info("voice.broker.unreachable", error=type(e).__name__)
        return JSONResponse({"detail": NOT_RUNNING}, status_code=503)
    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": "the voice server sent an unreadable reply"}
    return JSONResponse(payload, status_code=response.status_code)


@router.get("/status")
async def status(request: Request) -> JSONResponse:
    _check_request(request)
    return await _forward("GET", "/status", timeout=STATUS_TIMEOUT_S)


@router.post("/session")
async def open_session(request: Request, user: SignedIn) -> JSONResponse:
    _check_request(request)
    return await _forward("POST", "/session", await request.json(), user_id=user.id)


@router.post("/session/{session_id}/offer")
async def offer(session_id: str, request: Request) -> JSONResponse:
    _check_request(request)
    return await _forward("POST", f"/session/{session_id}/offer", await request.json())


@router.patch("/session/{session_id}/offer")
async def ice(session_id: str, request: Request) -> JSONResponse:
    _check_request(request)
    return await _forward("PATCH", f"/session/{session_id}/offer", await request.json())


@router.delete("/session/{session_id}")
async def end_session(session_id: str, request: Request) -> JSONResponse:
    _check_request(request)
    return await _forward("DELETE", f"/session/{session_id}")
