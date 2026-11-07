"""Access control for the API: bearer token, chat rate limit, daily spend cap, request logs.

The day's spend is a row of `chat_usage` in the database, so the cap holds across workers and
restarts. The requests-per-window limit is a per-process burst guard: it is in memory and each
worker counts its own.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import time
from collections import deque
from datetime import UTC, date, datetime
from pathlib import Path

from fastapi import HTTPException, WebSocketException
from sqlalchemy import Engine, select
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from librarian.config import Settings, get_settings
from librarian.db import get_engine, tables, upsert
from librarian.log_config import get_logger
from librarian.pricing import PRICES, TokenUsage, cost_usd, price_for

log = get_logger(__name__)

# Open without a token even when one is set: orchestrator probes carry no credentials.
PUBLIC_PATHS = frozenset({"/healthz", "/readyz"})
# Browsers cannot set headers on a WebSocket, so the client sends the token as a subprotocol:
# `new WebSocket(url, ["bearer", token])`. The server accepts with "bearer".
WS_SUBPROTOCOL = "bearer"
_WS_POLICY_VIOLATION = 1008


def _bearer_from_header(value: str) -> str | None:
    scheme, _, token = value.partition(" ")
    return token.strip() if scheme.lower() == "bearer" and token.strip() else None


def _bearer_from_subprotocols(value: str) -> str | None:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) == 2 and parts[0] == WS_SUBPROTOCOL and parts[1]:
        return parts[1]
    return None


def token_matches(supplied: str | None, expected: str) -> bool:
    """Constant-time comparison; a missing token never matches."""
    return supplied is not None and hmac.compare_digest(supplied.encode(), expected.encode())


async def require_token(conn: HTTPConnection) -> None:
    """App-level dependency: 401 (HTTP) or a refused handshake (WebSocket) without the token.

    Reads the token from settings on each call so a test or a restart-less env change applies.
    """
    expected = get_settings().api_token
    if not expected or conn.url.path in PUBLIC_PATHS:
        return
    if conn.scope["type"] == "websocket":
        supplied = _bearer_from_subprotocols(conn.headers.get("sec-websocket-protocol", ""))
        if not token_matches(supplied, expected):
            raise WebSocketException(code=_WS_POLICY_VIOLATION, reason="unauthorized")
        return
    if not token_matches(_bearer_from_header(conn.headers.get("authorization", "")), expected):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ChatLimiter:
    """Per-process burst guard plus the shared per-UTC-day spend cap for the chat route.

    `user_id` is None while there is one user; accounts will fill it in. The engine is looked up
    on each call unless one is given, so two limiters on one database behave as two workers.
    """

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine
        self._hits: deque[float] = deque()

    def _db(self) -> Engine:
        return self._engine or get_engine()

    @staticmethod
    def _today() -> date:
        return datetime.now(UTC).date()

    def spent_usd(self, user_id: str | None = None) -> float:
        """Today's estimated spend from the database; 0.0 when it cannot be read (logged)."""
        t = tables.chat_usage
        stmt = select(t.c.usd).where(t.c.user_key == (user_id or ""), t.c.day == self._today())
        try:
            with self._db().connect() as conn:
                return float(conn.execute(stmt).scalar() or 0.0)
        except SQLAlchemyError as e:
            log.error("chat.spend_read_failed", error=str(e))
            return 0.0

    def admit(self, settings: Settings, now: float | None = None) -> None:
        """Count one chat request, or raise 429 saying which limit was hit."""
        now = time.monotonic() if now is None else now
        budget = settings.chat_daily_budget_usd
        if budget > 0 and self.spent_usd() >= budget:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Daily chat budget of ${budget:.2f} is spent (estimated). "
                    "It resets at 00:00 UTC."
                ),
            )
        limit, window = settings.chat_rate_limit, settings.chat_rate_window_s
        if limit > 0:
            while self._hits and now - self._hits[0] >= window:
                self._hits.popleft()
            if len(self._hits) >= limit:
                wait = max(1, int(window - (now - self._hits[0])) + 1)
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many chat requests: {limit} per {window}s. Retry in {wait}s.",
                    headers={"Retry-After": str(wait)},
                )
            self._hits.append(now)

    def record_usage(
        self, settings: Settings, usage: TokenUsage, user_id: str | None = None
    ) -> None:
        """Add one model call's cost to today's row, each token class at its own rate.

        An unknown model is refused at startup; if one gets here anyway the dearest price in the
        table is used, so the cap errs towards stopping early. The write is an upsert, so
        concurrent workers do not lose adds.
        """
        model = settings.anthropic_model
        if price_for(model) is None:
            model = max(PRICES, key=lambda m: PRICES[m].output)
        usd = cost_usd(model, usage)
        engine, t = self._db(), tables.chat_usage
        stmt = upsert(engine, t).values(
            user_id=user_id,
            user_key=user_id or "",
            day=self._today(),
            requests=1,
            input_tokens=usage.input + usage.cache_read + usage.cache_write,
            output_tokens=usage.output,
            usd=usd,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_key", "day"],
            set_={
                "requests": t.c.requests + stmt.excluded.requests,
                "input_tokens": t.c.input_tokens + stmt.excluded.input_tokens,
                "output_tokens": t.c.output_tokens + stmt.excluded.output_tokens,
                "usd": t.c.usd + stmt.excluded.usd,
            },
        )
        try:
            with engine.begin() as conn:
                conn.execute(stmt)
        except SQLAlchemyError as e:
            log.error("chat.spend_write_failed", error=str(e), usd=round(usd, 4))

    def reset(self) -> None:
        """Forget the burst window. The day's spend is in the database and is not touched."""
        self._hits.clear()


chat_limiter = ChatLimiter()


_INLINE_SCRIPT_RE = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.S | re.I)


def inline_script_hashes(index_html: Path) -> list[str]:
    """CSP `'sha256-...'` sources for the classic inline scripts of the built index.html.

    The theme bootstrap in app/index.html must run before first paint, so it stays inline;
    hashing it keeps `script-src` free of `'unsafe-inline'`. Scripts with `src=` are
    same-origin files and need nothing. A missing file gives no hashes (inline scripts blocked).
    """
    try:
        html = index_html.read_text(encoding="utf-8")
    except OSError:
        return []
    hashes: list[str] = []
    for m in _INLINE_SCRIPT_RE.finditer(html):
        if "src=" in m["attrs"].lower() or not m["body"].strip():
            continue
        digest = base64.b64encode(hashlib.sha256(m["body"].encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    return hashes


def build_csp(script_hashes: list[str]) -> str:
    """CSP for the Vite app. Everything is same-origin (the bundle, KaTeX fonts, /api, /ws, SSE).

    `style-src 'unsafe-inline'` stays: React sets `style=` attributes and index.html has a
    <style> block. `img-src blob: data:` is for slide images (fetched with the bearer token and
    shown from a blob URL) and small inlined assets; `connect-src 'self'` covers fetch, SSE and
    the same-origin WebSocket.
    """
    return "; ".join(
        [
            "default-src 'self'",
            " ".join(["script-src 'self'", *script_hashes]),
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
    )


# The interactive docs (EXPOSE_DOCS) load their UI from a CDN; they are off by default.
_NO_CSP_PATHS = ("/docs", "/redoc")


class SecurityHeadersMiddleware:
    """Adds the standard security headers to every HTTP response that does not set them.

    Never overwrites: the course asset routes send their own, stricter CSP and keep it.
    HSTS is not here: it belongs to the TLS terminator (docker/Caddyfile).
    """

    def __init__(self, app: ASGIApp, csp: str) -> None:
        self.app = app
        self._headers = {
            b"content-security-policy": csp.encode(),
            b"x-content-type-options": b"nosniff",
            b"referrer-policy": b"no-referrer",
            b"permissions-policy": b"camera=(), microphone=(), geolocation=(), payment=(), usb=()",
            b"x-frame-options": b"DENY",
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        skip_csp = scope["path"].startswith(_NO_CSP_PATHS)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                present = {k.lower() for k, _ in message.get("headers", [])}
                extra = [
                    (k, v)
                    for k, v in self._headers.items()
                    if k not in present and not (skip_csp and k == b"content-security-policy")
                ]
                message["headers"] = [*message.get("headers", []), *extra]
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestLogMiddleware:
    """One `http.request` event per HTTP request: method, path, status, duration.

    The query string, headers and body are never logged, so neither the token nor a chat
    question can reach the log. Streaming responses are timed to their last byte.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            log.info(
                "http.request",
                method=scope["method"],
                path=scope["path"],
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1000, 1),
            )
