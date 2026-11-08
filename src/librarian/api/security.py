"""Access control for the API: who the caller is, CSRF, rate limits, daily spend caps, request logs.

A caller is a bearer credential (an `lk_` key, or the bootstrap token) or a session cookie set by
a login. Cookie-authenticated writes must echo the CSRF cookie in a header (double submit), and a
cookie-authenticated WebSocket must come from our own origin; a bearer credential is never sent by
the browser on its own, so it needs neither.

The day's spend is a row of `chat_usage` in the database, so the cap holds across workers and
restarts. The sign-in limit is shared too (`accounts.rate_limits`); the chat requests-per-window
limit is a per-process burst guard: in memory, each worker counts its own.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import time
from collections import deque
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated, Any, NoReturn
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, WebSocketException
from sqlalchemy import Engine, Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import HTTPConnection, Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from librarian import accounts
from librarian.accounts import User, rate_limits
from librarian.config import Settings, get_settings
from librarian.db import get_engine, tables, upsert
from librarian.log_config import get_logger
from librarian.pricing import PRICES, TokenUsage, cost_usd, price_for

log = get_logger(__name__)

# Open without a credential: orchestrator probes, and the sign-in routes themselves.
# /admin/reload checks its own credential: a webhook signature, or an admin (api/main.py).
PUBLIC_PATHS = frozenset(
    {"/healthz", "/readyz", "/api/auth/config", "/api/legal/third-party", "/admin/reload"}
)
PUBLIC_PREFIXES = ("/auth/",)
SESSION_COOKIE = "lb_session"
# Readable by the page (not HttpOnly): the client copies it into CSRF_HEADER on every write.
CSRF_COOKIE = "lb_csrf"
CSRF_HEADER = "x-csrf-token"
# Browsers cannot set headers on a WebSocket, so the client sends the token as a subprotocol:
# `new WebSocket(url, ["bearer", token])`. The server accepts with "bearer".
WS_SUBPROTOCOL = "bearer"
_WS_POLICY_VIOLATION = 1008
_WS_INTERNAL_ERROR = 1011


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


_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _supplied_credential(conn: HTTPConnection) -> str | None:
    if conn.scope["type"] == "websocket":
        return _bearer_from_subprotocols(conn.headers.get("sec-websocket-protocol", ""))
    return _bearer_from_header(conn.headers.get("authorization", ""))


def _deny(conn: HTTPConnection, status: int, detail: str) -> NoReturn:
    if conn.scope["type"] == "websocket":
        code = _WS_POLICY_VIOLATION if status < 500 else _WS_INTERNAL_ERROR
        raise WebSocketException(code=code, reason=detail)
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    raise HTTPException(status_code=status, detail=detail, headers=headers)


def _resolve_user(conn: HTTPConnection, settings: Settings) -> tuple[User, bool]:
    """(user, by cookie). A bearer credential wins over a cookie.

    An `lk_` key is that key's user, the bootstrap token the owner, a session cookie its user.
    Open mode (no token, no login configured) is the owner whatever is sent.
    """
    supplied = _supplied_credential(conn)
    engine = get_engine()
    if supplied is not None and accounts.is_api_key(supplied):
        user = accounts.resolve_key(engine, supplied)
        if user is None:
            _deny(conn, 401, "Unknown or revoked API key.")
        return user, False
    if settings.open_mode or (settings.api_token and token_matches(supplied, settings.api_token)):
        return accounts.ensure_owner(engine, settings.owner_email), False
    if supplied is not None:
        _deny(conn, 401, "Missing or invalid API token.")
    cookie = conn.cookies.get(SESSION_COOKIE)
    user = accounts.resolve_session(engine, cookie) if cookie else None
    if user is None:
        _deny(conn, 401, "Not signed in.")
    return user, True


def _csrf_ok(conn: HTTPConnection) -> bool:
    cookie = conn.cookies.get(CSRF_COOKIE)
    return bool(cookie) and token_matches(conn.headers.get(CSRF_HEADER), cookie)


def same_origin(conn: HTTPConnection, settings: Settings) -> bool:
    """The Origin header names this host, the public URL, or a CORS origin. No Origin is not ours."""
    origin = conn.headers.get("origin")
    if not origin:
        return False
    allowed = {o.rstrip("/") for o in settings.cors_origin_list}
    if settings.public_url:
        allowed.add(settings.public_url.rstrip("/"))
    return origin.rstrip("/") in allowed or urlsplit(origin).netloc == conn.headers.get("host")


def is_public(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES)


def current_user(conn: HTTPConnection) -> User | None:
    """App-level dependency: the request's `User`, also set as `request.state.user`.

    401 (HTTP) or a refused handshake (WebSocket) without a valid credential; 403 for a write
    (any method but GET, HEAD, OPTIONS) with a read-only key, or by cookie without the CSRF
    header; a refused handshake for a cookie WebSocket from another origin. None on the public
    paths. Settings are read on each call so a test or a restart-less env change applies. A plain
    function, so FastAPI runs its database lookups in the threadpool.
    """
    if is_public(conn.url.path):
        return None
    return authenticate(conn)


def authenticate(conn: HTTPConnection) -> User:
    """`current_user` without the public-path exemption, for a public route that may also be
    called by a signed-in user (POST /admin/reload: a webhook signature, or an admin)."""
    settings = get_settings()
    try:
        user, by_cookie = _resolve_user(conn, settings)
    except SQLAlchemyError as e:
        log.error("auth.lookup_failed", error=str(e))
        _deny(conn, 503, "Accounts database unavailable.")
    writes = conn.scope["type"] == "http" and conn.scope["method"] not in _SAFE_METHODS
    if writes and "write" not in user.scopes:
        _deny(conn, 403, "This API key is read-only.")
    if by_cookie and writes and not _csrf_ok(conn):
        _deny(conn, 403, "Missing or wrong CSRF token.")
    if by_cookie and conn.scope["type"] == "websocket" and not same_origin(conn, settings):
        _deny(conn, 403, "Cross-origin WebSocket refused.")
    try:
        accounts.touch_seen(get_engine(), user)
    except SQLAlchemyError as e:
        log.warning("auth.touch_failed", error=str(e))
    conn.state.user = user
    return user


def require_user(user: Annotated[User | None, Depends(current_user)]) -> User:
    """Route dependency: the signed-in user (FastAPI resolves `current_user` once per request)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    return user


def require_admin(user: Annotated[User, Depends(require_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only.")
    return user


# Route parameter types: `def route(user: SignedIn)`.
SignedIn = Annotated[User, Depends(require_user)]
Admin = Annotated[User, Depends(require_admin)]


class ChatLimiter:
    """Per-process burst guard plus the shared per-UTC-day spend caps for the chat route.

    The requests-per-window limit (`_hits`) is per process on purpose: with N workers a client can
    send up to N times the limit. The spend caps, which bound the cost, are the shared ones.

    Spend is a row per user and day; the global cap is their sum. The engine is looked up on
    each call unless one is given, so two limiters on one database behave as two workers.
    """

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine
        self._hits: deque[float] = deque()

    def _db(self) -> Engine:
        return self._engine or get_engine()

    @staticmethod
    def _today() -> date:
        return datetime.now(UTC).date()

    def _read(self, stmt: Select[Any]) -> float:
        try:
            with self._db().connect() as conn:
                return float(conn.execute(stmt).scalar() or 0.0)
        except SQLAlchemyError as e:
            log.error("chat.spend_read_failed", error=str(e))
            return 0.0

    def spent_usd(self, user_id: str | None = None) -> float:
        """One user's spend today from the database; 0.0 when it cannot be read (logged)."""
        t = tables.chat_usage
        return self._read(
            select(t.c.usd).where(t.c.user_key == (user_id or ""), t.c.day == self._today())
        )

    def total_spent_usd(self) -> float:
        """Everyone's spend today, for the global cap."""
        t = tables.chat_usage
        return self._read(select(func.sum(t.c.usd)).where(t.c.day == self._today()))

    def admit(
        self,
        settings: Settings,
        now: float | None = None,
        *,
        user_id: str | None = None,
        user_cap: bool = False,
    ) -> None:
        """Count one chat request, or raise 429 saying which limit was hit.

        `user_cap` applies the per-user budget to `user_id` (members; admins have only the global cap).
        """
        now = time.monotonic() if now is None else now
        budget = settings.chat_daily_budget_usd
        if budget > 0 and self.total_spent_usd() >= budget:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Daily chat budget of ${budget:.2f} is spent (estimated). "
                    "It resets at 00:00 UTC."
                ),
            )
        mine = settings.chat_user_daily_budget_usd
        if user_cap and mine > 0 and self.spent_usd(user_id) >= mine:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Your daily chat budget of ${mine:.2f} is spent (estimated). "
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


class AuthLimiter:
    """Requests per client address per window to the sign-in routes, counted across all workers.

    The count is a row in the database (`accounts.rate_limits`), so `--workers N` and replicas
    share one limit instead of multiplying it. A small in-process window sits in front as a burst
    guard: it answers floods without a query and still holds when the database is down.

    The address is the TCP peer, or the forwarded one when uvicorn trusts the proxy
    (LIBRARIAN_FORWARDED_ALLOW_IPS). The key is the address for the whole /auth/* group.

    Fail open: if the shared count cannot be read, the request is admitted (logged), and only the
    per-process guard applies. Sign-in needs the same database to create a session, so a flood
    during an outage cannot get anyone in; refusing every sign-in on a limiter fault would turn a
    counter problem into a full login outage.
    """

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine
        self._hits: dict[str, deque[float]] = {}

    def _db(self) -> Engine:
        return self._engine or get_engine()

    def _deny(self, wait: int) -> NoReturn:
        raise HTTPException(
            status_code=429,
            detail=f"Too many sign-in requests. Retry in {wait}s.",
            headers={"Retry-After": str(wait)},
        )

    def __call__(self, request: Request) -> None:
        """Route dependency: 429 with Retry-After when the caller's address is over the limit."""
        settings = get_settings()
        limit, window = settings.auth_rate_limit, settings.auth_rate_window_s
        if limit <= 0:
            return
        addr = request.client.host if request.client else ""
        now = time.monotonic()
        for a in [a for a, q in self._hits.items() if not q or now - q[-1] >= window]:
            del self._hits[a]
        hits = self._hits.setdefault(addr, deque())
        while hits and now - hits[0] >= window:
            hits.popleft()
        if len(hits) >= limit:
            self._deny(max(1, int(window - (now - hits[0])) + 1))
        hits.append(now)
        try:
            shared = rate_limits.hit(self._db(), f"auth:{addr}", window)
        except SQLAlchemyError as e:
            log.error("auth.rate_limit_unavailable", error=str(e), fail="open")
            return
        if shared.hits > limit:
            self._deny(shared.retry_after_s)

    def reset(self) -> None:
        """Forget both the in-process window and the shared counters."""
        self._hits.clear()
        try:
            rate_limits.clear(self._db())
        except SQLAlchemyError as e:
            log.warning("auth.rate_limit_reset_failed", error=str(e))


auth_limiter = AuthLimiter()


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
    """One `http.request` event per HTTP request: method, path, status, duration, user id.

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
                pid=os.getpid(),  # which worker, with --workers N
                user_id=getattr(scope.get("state", {}).get("user"), "id", None),
            )
