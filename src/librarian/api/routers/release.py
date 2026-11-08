"""The content release the API serves: GET /api/release, POST /admin/reload, the poller and the
`X-Librarian-Release` header.

With LIBRARIAN_RELEASE_URL set, each worker pulls on start and every LIBRARIAN_RELEASE_POLL_S
(the release lock lets one worker install; the rest find it current). POST /admin/reload pulls
now: CI calls it with an HMAC signature after it rewrites `latest`, or an admin calls it signed
in. Every response carries the release name, so the UI can refetch when it changes.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from librarian import accounts, release, retrieval
from librarian.api.security import authenticate
from librarian.config import get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger

log = get_logger(__name__)

router = APIRouter()

RELEASE_HEADER = "X-Librarian-Release"
TIMESTAMP_HEADER = "X-Librarian-Timestamp"
SIGNATURE_HEADER = "X-Librarian-Signature"
# A signed request older (or newer) than this is refused, so a captured one can't be replayed later.
SIGNATURE_MAX_SKEW_S = 300
# The header reads a symlink; a request burst shares one read.
_NAME_TTL_S = 2.0
_name_cache: tuple[float, str | None] = (0.0, None)


def sign(secret: str, timestamp: str, body: bytes) -> str:
    """The `X-Librarian-Signature` value for a body sent at `timestamp` (unix seconds)."""
    mac = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def _signature_ok(request: Request, body: bytes, secret: str) -> bool:
    ts = request.headers.get(TIMESTAMP_HEADER, "")
    given = request.headers.get(SIGNATURE_HEADER, "")
    try:
        skew = abs(time.time() - int(ts))
    except ValueError:
        return False
    if skew > SIGNATURE_MAX_SKEW_S:
        return False
    return hmac.compare_digest(given, sign(secret, ts, body))


def served_release() -> str | None:
    global _name_cache
    now = time.monotonic()
    if now - _name_cache[0] > _NAME_TTL_S:
        _name_cache = (now, release.current_name())
    return _name_cache[1]


def _pull_and_swap() -> dict[str, Any]:
    """Pull (release mode), then make this worker's index handle follow `index/current` now.

    The handle's reload result, plus `release` (what the pull did) in release mode.
    """
    pulled = None
    if get_settings().release_url:
        pulled = release.pull().as_dict()
        global _name_cache
        _name_cache = (0.0, None)
    handle = retrieval.get_handle()
    if handle is None:
        raise HTTPException(status_code=503, detail="no index handle")
    out: dict[str, Any] = dict(handle.reload())
    if pulled is not None:
        out["release"] = pulled
    return out


@router.get("/api/release")
def get_release() -> dict[str, Any]:
    """The release being served (None on a dev checkout reading data/) and its manifest."""
    manifest = release.current_manifest()
    return {
        "release": release.current_name(),
        "pinned": release.pinned() is not None,
        "created_at": manifest.get("created_at") if manifest else None,
        "git_sha": manifest.get("git_sha") if manifest else None,
        "source": "release" if get_settings().release_url else "data",
    }


@router.post("/admin/reload")
async def admin_reload(request: Request) -> dict[str, Any]:
    """Pull the latest (or pinned) release and swap the index in. Same as SIGHUP without a release.

    A public path: the caller is a webhook with a valid signature, or a signed-in admin. Requests
    already running finish on the old content; later ones see the new.
    """
    secret = get_settings().release_webhook_secret
    user_id: str | None = None
    if secret and SIGNATURE_HEADER in request.headers:
        if not _signature_ok(request, await request.body(), secret):
            log.warning("release.webhook_refused", client=request.client and request.client.host)
            raise HTTPException(status_code=401, detail="Bad or stale signature.")
    else:
        user = await run_in_threadpool(authenticate, request)
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Admins only.")
        user_id = user.id
    try:
        result = await run_in_threadpool(_pull_and_swap)
    except release.ReleaseError as e:
        log.error("release.reload_failed", error=str(e))
        raise HTTPException(status_code=502, detail=f"Release not installed: {e}") from e
    accounts.audit(get_engine(), "admin_reload", user_id=user_id, target=served_release())
    return result


class ReleaseHeaderMiddleware:
    """Adds `X-Librarian-Release: <name>` to every HTTP response while a release is served."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        name = served_release() if scope["type"] == "http" else None
        if name is None:
            await self.app(scope, receive, send)
            return
        value = name.encode()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), (b"x-librarian-release", value)]
            await send(message)

        await self.app(scope, receive, send_wrapper)


async def poll_releases() -> None:
    """Pull now, then every `release_poll_s` (0: only at start). Failures are logged, never raised."""
    interval = get_settings().release_poll_s
    while True:
        try:
            result = await asyncio.to_thread(release.pull)
            if result.changed:
                handle = retrieval.get_handle()
                if handle is not None:
                    handle.reload()
                global _name_cache
                _name_cache = (0.0, None)
        except asyncio.CancelledError:
            raise
        except Exception as e:  # a bad release or an unreachable store: keep serving
            log.error("release.poll_failed", error=str(e), error_type=type(e).__name__)
        if interval <= 0:
            return
        await asyncio.sleep(interval)
