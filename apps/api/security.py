"""Access control for the API: bearer token, chat rate limit, daily spend cap, request logs.

All state is in-process, which is right for one instance serving one user. A restart resets
the rate window and the day's spend.
"""

from __future__ import annotations

import hmac
import time
from collections import deque
from datetime import UTC, datetime

from fastapi import HTTPException, WebSocketException
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from librarian.config import Settings, get_settings
from librarian.log_config import get_logger

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
    """Sliding-window request limit plus a per-UTC-day spend estimate for the chat route."""

    def __init__(self) -> None:
        self._hits: deque[float] = deque()
        self._day = ""
        self._spent_usd = 0.0

    def _roll_day(self) -> None:
        today = datetime.now(UTC).date().isoformat()
        if today != self._day:
            self._day, self._spent_usd = today, 0.0

    @property
    def spent_usd(self) -> float:
        self._roll_day()
        return self._spent_usd

    def admit(self, settings: Settings, now: float | None = None) -> None:
        """Count one chat request, or raise 429 saying which limit was hit."""
        now = time.monotonic() if now is None else now
        budget = settings.chat_daily_budget_usd
        if budget > 0 and self.spent_usd >= budget:
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

    def record_usage(self, settings: Settings, input_tokens: int, output_tokens: int) -> None:
        self._roll_day()
        self._spent_usd += (
            input_tokens * settings.chat_input_usd_per_mtok
            + output_tokens * settings.chat_output_usd_per_mtok
        ) / 1_000_000

    def reset(self) -> None:
        self._hits.clear()
        self._day, self._spent_usd = "", 0.0


chat_limiter = ChatLimiter()


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
