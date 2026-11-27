"""The voice process's HTTP surface: one session at a time, on 127.0.0.1, for this person's browser.

Holds the slot, the refusals and the origin checks, and leaves everything else to a `LiveSession`,
so all of it can be tested without Pipecat or a microphone. The browser reaches this through the
API's broker, and sends SDP there. The handshake has no CORS on purpose: nothing but the app's own
origin, seen through the broker, has any reason to open a session on this machine.
"""

from __future__ import annotations

import asyncio
import os
import threading
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from typing import Any, Protocol
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from librarian.courses.catalog import catalog as courses_catalog
from librarian.log_config import get_logger

from .config import ALLOWED_HOSTS, VoiceConfig
from .policy import HOSTED_PROVIDER, Refusal, SessionPlan, SessionRequest, resolve_session

log = get_logger(__name__)

# Set by the API's broker (`api/routers/voice.py`) from the signed-in user.
USER_HEADER = "x-librarian-user"


class LiveSession(Protocol):
    async def offer(self, body: dict[str, Any]) -> dict[str, Any]: ...
    async def ice(self, body: dict[str, Any]) -> None: ...
    async def close(self) -> None: ...


class ModelState(Protocol):
    stt: str  # loading, ready or failed
    tts: str

    def start_loading(self) -> None: ...


SessionFactory = Callable[[SessionPlan, Callable[[], None]], LiveSession]
CatalogGetter = Callable[[], Any]


@dataclass
class _Slot:
    id: str
    plan: SessionPlan
    live: LiveSession
    reserved_at: float
    offered: bool = False


def host_allowed(host_header: str | None) -> bool:
    """A DNS-rebinding page would arrive with its own hostname here."""
    if not host_header:
        return False
    return urlsplit(f"//{host_header}").hostname in ALLOWED_HOSTS


def require_local_models(plan: SessionPlan, models: ModelState) -> None:
    """Fail closed: while what this session needs isn't ready, it doesn't start at all."""
    needed = []
    if plan.stt != HOSTED_PROVIDER:
        needed.append(("speech recognition", models.stt))
    if plan.tts != HOSTED_PROVIDER:
        needed.append(("voice", models.tts))
    for what, state in needed:
        if state == "failed":
            raise Refusal(
                503,
                f"The local {what} model failed to load, so voice is refused rather than sending "
                "audio to a hosted service.",
            )
        if state != "ready":
            raise Refusal(503, f"The local {what} model is still loading. Try again in a moment.")


def create_app(
    cfg: VoiceConfig,
    models: ModelState,
    session_factory: SessionFactory,
    catalog: CatalogGetter = courses_catalog,
    now: Callable[[], float] = time.monotonic,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        models.start_loading()
        # Warmed now, as the first grade would otherwise build it during a turn.
        threading.Thread(target=catalog, name="voice-catalog-warm", daemon=True).start()
        yield

    app = FastAPI(
        title="Librarian voice", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
    )
    state: dict[str, _Slot | None] = {"slot": None}
    lock = asyncio.Lock()

    @app.middleware("http")
    async def _only_this_machine(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not host_allowed(request.headers.get("host")):
            return JSONResponse({"detail": "voice only serves this machine"}, status_code=403)
        origin = request.headers.get("origin")
        if origin is not None and origin.rstrip("/") not in cfg.allowed_origins:
            return JSONResponse({"detail": "that origin may not use voice"}, status_code=403)
        return await call_next(request)

    @app.exception_handler(Refusal)
    async def _refused(_request: Request, exc: Refusal) -> JSONResponse:
        log.info("voice.session.refused", status=exc.status)
        return JSONResponse({"detail": exc.message}, status_code=exc.status)

    @app.get("/status")
    async def status() -> dict[str, Any]:
        return {
            "running": True,
            "stt": models.stt,
            "tts": models.tts,
            "sessionActive": state["slot"] is not None,
        }

    def _release(session_id: str) -> None:
        slot = state["slot"]
        if slot is not None and slot.id == session_id:
            state["slot"] = None
            log.info("voice.session.ended", mode=slot.plan.mode)

    async def _discard_expired_reservation() -> None:
        """A reservation nobody connected to costs nothing, but mustn't block the next session."""
        slot = state["slot"]
        if slot is not None and not slot.offered and now() - slot.reserved_at > cfg.offer_timeout_s:
            state["slot"] = None
            await slot.live.close()

    @app.post("/session")
    async def open_session(req: SessionRequest, request: Request) -> dict[str, Any]:
        plan = resolve_session(req, await asyncio.to_thread(catalog), cfg)
        # The broker names the signed-in user; the grades of this session are theirs.
        plan = replace(plan, user_id=request.headers.get(USER_HEADER) or None)
        require_local_models(plan, models)
        if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
            raise Refusal(503, "ANTHROPIC_API_KEY is not set for the voice server.")
        async with lock:
            await _discard_expired_reservation()
            if state["slot"] is not None:
                raise Refusal(409, "A voice session is already running. End it first.")
            session_id = uuid.uuid4().hex
            live = session_factory(plan, lambda: _release(session_id))
            state["slot"] = _Slot(session_id, plan, live, now())
        log.info("voice.session.opened", mode=plan.mode, stt=plan.stt, tts=plan.tts)
        return {
            "sessionId": session_id,
            "offer": f"/api/voice/session/{session_id}/offer",
            "mode": plan.mode,
            "localOnly": plan.local_only,
            "stt": plan.stt,
            "tts": plan.tts,
        }

    def _slot(session_id: str) -> _Slot:
        slot = state["slot"]
        if slot is None or slot.id != session_id:
            raise HTTPException(status_code=404, detail="no such voice session")
        return slot

    @app.post("/session/{session_id}/offer")
    async def offer(session_id: str, request: Request) -> dict[str, Any]:
        slot = _slot(session_id)
        body = await request.json()
        restarting = bool(body.get("restart_pc"))
        if slot.offered and not (restarting and body.get("pc_id")):
            raise Refusal(409, "This voice session is already connected.")
        slot.offered = True
        try:
            return await asyncio.wait_for(slot.live.offer(body), cfg.offer_timeout_s)
        except (Refusal, TimeoutError) as e:
            state["slot"] = None
            await slot.live.close()
            if isinstance(e, Refusal):
                raise
            raise Refusal(504, "The voice connection took too long to set up.") from e

    @app.patch("/session/{session_id}/offer")
    async def ice(session_id: str, request: Request) -> dict[str, str]:
        await _slot(session_id).live.ice(await request.json())
        return {"status": "ok"}

    @app.delete("/session/{session_id}")
    async def end_session(session_id: str) -> dict[str, bool]:
        """Idempotent: a tab closing and a disconnect can both get here."""
        slot = state["slot"]
        if slot is not None and slot.id == session_id:
            state["slot"] = None
            await slot.live.close()
        return {"ended": True}

    return app
