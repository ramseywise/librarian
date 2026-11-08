"""Sign-in: Google and GitHub (OAuth with PKCE), email links, sign-out.

    GET  /api/auth/config            which methods are on (the login screen's buttons)
    GET  /auth/login/{provider}      redirect to the provider
    GET  /auth/callback/{provider}   back from it: verified email -> session cookie -> the app
    POST /auth/email                 send a sign-in link (always 202, whoever asks)
    GET  /auth/email/verify          a page with one button, so a mail scanner's GET spends nothing
    POST /auth/email/verify          use the link: session cookie -> the app
    POST /auth/logout                end this session

Every route here is public (`security.is_public`) and rate limited per client address. Only an
email the provider verified, or one that received the link, signs in, and only when it is the
owner's, an existing user's, or on the invite list. A refusal redirects to `/#/login?error=...`.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import json
import secrets
import time
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from librarian import accounts
from librarian.accounts import login_tokens, mailer, oauth
from librarian.accounts.users import User
from librarian.api.security import (
    CSRF_COOKIE,
    CSRF_HEADER,
    SESSION_COOKIE,
    auth_limiter,
    same_origin,
    token_matches,
)
from librarian.config import Settings, get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger

log = get_logger(__name__)

router = APIRouter()
auth = APIRouter(dependencies=[Depends(auth_limiter)])

STATE_COOKIE = "lb_oauth"
STATE_TTL_S = 600


def _base(settings: Settings) -> str:
    return settings.public_url.rstrip("/")


def safe_next(target: str | None) -> str:
    """A same-site path to return to after sign-in; anything else is "/"."""
    if not target or not target.startswith("/") or target.startswith(("//", "/\\")):
        return "/"
    return target


def _refused(error: str) -> RedirectResponse:
    return RedirectResponse(f"/#/login?error={error}", status_code=303)


def _cookie_args(settings: Settings) -> dict[str, Any]:
    return {"secure": settings.secure_cookies, "samesite": "lax", "path": "/"}


def _signed(settings: Settings, payload: dict[str, Any]) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    mac = hmac.new(settings.session_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{mac}"


def _unsigned(settings: Settings, value: str | None) -> dict[str, Any] | None:
    if not value or "." not in value:
        return None
    body, mac = value.rsplit(".", 1)
    good = hmac.new(settings.session_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, good):
        return None
    payload = json.loads(base64.urlsafe_b64decode(body))
    return payload if time.time() - payload.get("t", 0) < STATE_TTL_S else None


def _signed_in(
    settings: Settings, user: User, method: str, next_path: str, request: Request
) -> RedirectResponse:
    """Start a session for `user` and send them on to `next_path`.

    The session id is always new; the one behind any cookie this browser sent is ended, so a
    session id planted before sign-in (fixation) or left over from an earlier login is dead.
    """
    engine = get_engine()
    if old := request.cookies.get(SESSION_COOKIE):
        accounts.revoke_session(engine, old)
    token = accounts.create_session(engine, user.id, days=settings.session_days)
    accounts.audit(engine, "login", user_id=user.id, target=method)
    log.info("auth.login", user_id=user.id, method=method)
    resp = RedirectResponse(next_path, status_code=303)
    age = settings.session_days * 86400
    resp.set_cookie(SESSION_COOKIE, token, max_age=age, httponly=True, **_cookie_args(settings))
    resp.set_cookie(CSRF_COOKIE, secrets.token_urlsafe(24), max_age=age, **_cookie_args(settings))
    resp.delete_cookie(STATE_COOKIE, path="/auth/callback")
    return resp


def _sign_in_or_refuse(
    settings: Settings, email: str, name: str | None, method: str, next_path: str, request: Request
) -> RedirectResponse:
    engine = get_engine()
    user = accounts.sign_in(engine, email, owner_email=settings.owner_email, name=name)
    if user is None:
        accounts.audit(
            engine, "login_refused", target=f"{method}:{accounts.normalize_email(email)}"
        )
        log.info("auth.refused", method=method, reason="not_invited")
        return _refused("not_invited")
    return _signed_in(settings, user, method, next_path, request)


@router.get("/api/auth/config")
def auth_config() -> dict[str, Any]:
    """The sign-in methods that are on, and whether the API is open (local, no sign-in)."""
    settings = get_settings()
    return {"methods": settings.login_methods, "open": settings.open_mode}


def _provider(name: str, settings: Settings) -> oauth.Provider:
    if name not in settings.login_methods or name not in oauth.PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Sign-in with {name!r} is not configured.")
    return oauth.PROVIDERS[name]


@auth.get("/auth/login/{provider}")
def login(provider: str, next: str | None = None) -> RedirectResponse:
    settings = get_settings()
    p = _provider(provider, settings)
    state, verifier = secrets.token_urlsafe(24), oauth.new_verifier()
    redirect_uri = f"{_base(settings)}/auth/callback/{p.name}"
    resp = RedirectResponse(
        oauth.authorize_url(p, settings, redirect_uri, state, verifier), status_code=303
    )
    payload = {"s": state, "v": verifier, "p": p.name, "n": safe_next(next), "t": time.time()}
    resp.set_cookie(
        STATE_COOKIE,
        _signed(settings, payload),
        max_age=STATE_TTL_S,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/auth/callback",
    )
    return resp


@auth.get("/auth/callback/{provider}")
def callback(
    provider: str,
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    settings = get_settings()
    p = _provider(provider, settings)
    if error or not code or not state:
        return _refused("cancelled")
    saved = _unsigned(settings, request.cookies.get(STATE_COOKIE))
    if saved is None or saved["p"] != p.name or not hmac.compare_digest(saved["s"], state):
        log.info("auth.refused", method=p.name, reason="bad_state")
        return _refused("expired")
    redirect_uri = f"{_base(settings)}/auth/callback/{p.name}"
    try:
        who = oauth.identity(p, settings, redirect_uri, code, saved["v"])
    except oauth.OAuthError as e:
        log.warning("auth.oauth_failed", method=p.name, error=str(e))
        return _refused("provider")
    return _sign_in_or_refuse(settings, who.email, who.name, p.name, saved["n"], request)


class EmailRequest(BaseModel):
    email: str = Field(max_length=320)
    next: str | None = Field(default=None, max_length=512)


@auth.post("/auth/email", status_code=202)
def email_link(body: EmailRequest) -> dict[str, bool]:
    """Send a sign-in link to an address that may sign in. The answer is the same for any address."""
    settings = get_settings()
    if "email" not in settings.login_methods:
        raise HTTPException(status_code=404, detail="Email sign-in is not configured.")
    try:
        email = accounts.normalize_email(body.email)
    except accounts.AccountError as e:
        raise HTTPException(status_code=422, detail="Not an email address.") from e
    engine = get_engine()
    if not accounts.may_sign_in(engine, email, settings.owner_email):
        accounts.audit(engine, "login_refused", target=f"email:{email}")
        return {"sent": True}
    hour_ago = datetime.now(UTC) - timedelta(hours=1)
    if login_tokens.issued_since(engine, email, hour_ago) >= settings.email_links_per_hour:
        log.info("auth.email.throttled")
        return {"sent": True}
    token = login_tokens.issue(engine, email)
    query = {"token": token, **({"next": safe_next(body.next)} if body.next else {})}
    link = f"{_base(settings)}/auth/email/verify?{urlencode(query)}"
    try:
        mailer.send_sign_in_link(settings, email, link, int(login_tokens.TTL.total_seconds() // 60))
    except mailer.MailError as e:
        log.error("auth.email.failed", error=str(e))
        raise HTTPException(status_code=502, detail="The email could not be sent.") from e
    return {"sent": True}


_CONFIRM_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Sign in</title>
<style>body{{font:16px system-ui,sans-serif;max-width:28rem;margin:20vh auto;padding:0 1rem}}
button{{font:inherit;padding:.6rem 1.2rem}}</style></head>
<body><h1>Sign in to Librarian</h1>
<form method="post" action="/auth/email/verify">
<input type="hidden" name="token" value="{token}">
<input type="hidden" name="next" value="{next}">
<button type="submit">Continue</button></form></body></html>
"""


@auth.get("/auth/email/verify", response_class=HTMLResponse)
def email_confirm(token: str = "", next: str | None = None) -> HTMLResponse:
    return HTMLResponse(
        _CONFIRM_PAGE.format(token=html.escape(token), next=html.escape(safe_next(next))),
        headers={"Cache-Control": "no-store"},
    )


@auth.post("/auth/email/verify")
def email_verify(
    request: Request,
    token: Annotated[str, Form(max_length=128)],
    next: Annotated[str | None, Form(max_length=512)] = None,
) -> RedirectResponse:
    settings = get_settings()
    if "email" not in settings.login_methods:
        raise HTTPException(status_code=404, detail="Email sign-in is not configured.")
    if not same_origin(request, settings):
        raise HTTPException(status_code=403, detail="Cross-origin sign-in refused.")
    email = login_tokens.consume(get_engine(), token)
    if email is None:
        return _refused("link_expired")
    return _sign_in_or_refuse(settings, email, None, "email", safe_next(next), request)


@auth.post("/auth/logout", status_code=204)
def logout(request: Request) -> Response:
    """End this browser's session. Needs the CSRF header, like any cookie-authenticated write."""
    settings = get_settings()
    cookie = request.cookies.get(SESSION_COOKIE)
    csrf = request.cookies.get(CSRF_COOKIE)
    if cookie:
        if not csrf or not token_matches(request.headers.get(CSRF_HEADER), csrf):
            raise HTTPException(status_code=403, detail="Missing or wrong CSRF token.")
        engine = get_engine()
        user = accounts.resolve_session(engine, cookie)
        try:
            accounts.revoke_session(engine, cookie)
        except SQLAlchemyError as e:
            log.error("auth.logout_failed", error=str(e))
            raise HTTPException(status_code=503, detail="Accounts database unavailable.") from e
        if user is not None:
            accounts.audit(engine, "logout", user_id=user.id)
    resp = Response(status_code=204)
    for name in (SESSION_COOKIE, CSRF_COOKIE):
        resp.delete_cookie(name, path="/", secure=settings.secure_cookies, samesite="lax")
    return resp


router.include_router(auth)
