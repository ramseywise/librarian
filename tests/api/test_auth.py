"""Sign-in (phase 3 wave B): OAuth with Google and GitHub, email links, sessions, CSRF, invites.

The providers and Resend are httpx.MockTransports; nothing leaves the process.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import librarian.api.main as main_module
from librarian import accounts, cli
from librarian.accounts import login_tokens, mailer, oauth
from librarian.api.security import CSRF_COOKIE, SESSION_COOKIE, auth_limiter
from librarian.api.startup import find_problems
from librarian.config import get_settings
from librarian.db import get_engine

BASE = "https://testserver"
OWNER = "owner@example.com"


class Providers:
    """Fake Google, GitHub and Resend. `who` is what the next userinfo call says."""

    def __init__(self) -> None:
        self.who: dict[str, Any] = {"email": "ada@example.com", "email_verified": True}
        self.github_emails: list[dict[str, Any]] = []
        self.token_requests: list[dict[str, list[str]]] = []
        self.mail: list[dict[str, Any]] = []
        self.token_status = 200

    def handler(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith(("oauth2.googleapis.com/token", "login/oauth/access_token")):
            self.token_requests.append(parse_qs(request.content.decode()))
            if self.token_status != 200:
                return httpx.Response(self.token_status, json={"error": "invalid_grant"})
            return httpx.Response(200, json={"access_token": "at", "token_type": "bearer"})
        if url.endswith("/v1/userinfo"):
            return httpx.Response(200, json=self.who)
        if url.endswith("api.github.com/user"):
            return httpx.Response(200, json={"login": "ada", "name": None})
        if url.endswith("api.github.com/user/emails"):
            return httpx.Response(200, json=self.github_emails)
        if url == mailer.RESEND_URL:
            self.mail.append(json.loads(request.content))
            return httpx.Response(200, json={"id": "m1"})
        return httpx.Response(404)


@pytest.fixture()
def fake(monkeypatch: pytest.MonkeyPatch) -> Providers:
    f = Providers()
    transport = httpx.MockTransport(f.handler)
    monkeypatch.setattr(oauth, "transport", transport)
    monkeypatch.setattr(mailer, "transport", transport)
    return f


@pytest.fixture()
def configure(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., None]]:
    def apply(**env: str) -> None:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        get_settings.cache_clear()

    monkeypatch.delenv("LIBRARIAN_API_TOKEN", raising=False)
    apply(
        LIBRARIAN_OWNER_EMAIL=OWNER,
        LIBRARIAN_PUBLIC_URL=BASE,
        LIBRARIAN_SESSION_SECRET="s" * 40,
        GOOGLE_CLIENT_ID="gid",
        GOOGLE_CLIENT_SECRET="gsecret",
        GITHUB_CLIENT_ID="hid",
        GITHUB_CLIENT_SECRET="hsecret",
        RESEND_API_KEY="re_test",
        EMAIL_FROM="Librarian <login@example.com>",
    )
    auth_limiter.reset()
    yield apply
    auth_limiter.reset()
    monkeypatch.undo()
    get_settings.cache_clear()


@pytest.fixture()
def client(configure: Callable[..., None], fake: Providers) -> Iterator[TestClient]:
    with TestClient(main_module.app, base_url=BASE, follow_redirects=False) as c:
        yield c


def _oauth_login(
    c: TestClient, provider: str = "google", next_path: str = "/#/study"
) -> httpx.Response:
    start = c.get(f"/auth/login/{provider}", params={"next": next_path})
    assert start.status_code == 303
    query = parse_qs(urlsplit(start.headers["location"]).query)
    return c.get(f"/auth/callback/{provider}", params={"code": "c0de", "state": query["state"][0]})


def _csrf(c: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": c.cookies[CSRF_COOKIE], "Origin": BASE}


# ── configuration ──────────────────────────────────────────────────────────


def test_login_turns_open_mode_off_and_lists_the_methods(client: TestClient) -> None:
    assert client.get("/api/auth/config").json() == {
        "methods": ["google", "github", "email"],
        "open": False,
    }
    assert client.get("/api/me").status_code == 401


def test_the_third_party_notice_is_public(client: TestClient) -> None:
    resp = client.get("/api/legal/third-party")
    assert resp.status_code == 200 and resp.text.startswith("# Third-party material")


def test_login_needs_the_public_url_and_a_session_secret(configure: Callable[..., None]) -> None:
    configure(LIBRARIAN_PUBLIC_URL="", LIBRARIAN_SESSION_SECRET="short")
    errors, _ = find_problems(get_settings())
    assert any("LIBRARIAN_PUBLIC_URL" in e for e in errors)
    assert any("LIBRARIAN_SESSION_SECRET" in e for e in errors)


def test_an_unconfigured_provider_is_404(
    client: TestClient, configure: Callable[..., None]
) -> None:
    configure(GITHUB_CLIENT_SECRET="")
    assert client.get("/auth/login/github").status_code == 404
    assert client.get("/auth/login/myspace").status_code == 404


# ── OAuth ──────────────────────────────────────────────────────────────────


def test_the_redirect_carries_state_and_a_pkce_challenge(client: TestClient) -> None:
    start = client.get("/auth/login/google")
    url = urlsplit(start.headers["location"])
    query = parse_qs(url.query)
    assert url.netloc == "accounts.google.com"
    assert query["redirect_uri"] == [f"{BASE}/auth/callback/google"]
    assert query["code_challenge_method"] == ["S256"] and query["code_challenge"][0]
    assert query["state"][0]
    assert "httponly" in start.headers["set-cookie"].lower()


def test_an_invited_email_signs_in_and_the_cookie_is_the_session(
    client: TestClient, fake: Providers
) -> None:
    accounts.invite(get_engine(), "Ada@Example.com")
    done = _oauth_login(client, next_path="/#/study")
    assert (done.status_code, done.headers["location"]) == (303, "/#/study")
    cookies = done.headers.get_list("set-cookie")
    session = next(c for c in cookies if c.startswith(SESSION_COOKIE))
    assert all(part in session.lower() for part in ("httponly", "samesite=lax", "secure"))
    assert fake.token_requests[0]["code_verifier"][0]  # PKCE verifier sent with the code
    me = client.get("/api/me").json()
    assert (me["email"], me["role"]) == ("ada@example.com", "member")
    events = [e.action for e in accounts.audit_events(get_engine())]
    assert events[0] == "login"


def test_an_email_that_is_not_invited_is_refused(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": "mallory@example.com", "email_verified": True}
    done = _oauth_login(client)
    assert done.headers["location"] == "/#/login?error=not_invited"
    assert SESSION_COOKIE not in client.cookies
    assert accounts.get_user(get_engine(), "mallory@example.com") is None
    assert accounts.audit_events(get_engine())[0].action == "login_refused"


def test_the_owner_needs_no_invite(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    assert client.get("/api/me").json()["role"] == "admin"


def test_an_unverified_email_or_a_refused_code_is_refused(
    client: TestClient, fake: Providers
) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    fake.who = {"email": "ada@example.com", "email_verified": False}
    assert _oauth_login(client).headers["location"] == "/#/login?error=provider"
    fake.who["email_verified"] = True
    fake.token_status = 400
    assert _oauth_login(client).headers["location"] == "/#/login?error=provider"


def test_a_state_that_does_not_match_the_cookie_is_refused(client: TestClient) -> None:
    client.get("/auth/login/google")
    done = client.get("/auth/callback/google", params={"code": "c", "state": "forged"})
    assert done.headers["location"] == "/#/login?error=expired"


def test_next_never_leaves_the_site(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    assert _oauth_login(client, next_path="//evil.example").headers["location"] == "/"


def test_github_uses_the_verified_primary_email(client: TestClient, fake: Providers) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    fake.github_emails = [
        {"email": "old@example.com", "verified": True, "primary": False},
        {"email": "ada@example.com", "verified": True, "primary": True},
    ]
    _oauth_login(client, "github")
    me = client.get("/api/me").json()
    assert (me["email"], me["name"]) == ("ada@example.com", "ada")
    client.cookies.clear()
    fake.github_emails = [{"email": "ada@example.com", "verified": False, "primary": True}]
    assert _oauth_login(client, "github").headers["location"] == "/#/login?error=provider"


# ── CSRF, sign-out, WebSocket ──────────────────────────────────────────────


def test_a_cookie_write_needs_the_csrf_header(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    body = {"name": "laptop"}
    assert client.post("/api/me/keys", json=body).status_code == 403
    assert client.post("/api/me/keys", json=body, headers={"X-CSRF-Token": "x"}).status_code == 403
    assert client.post("/api/me/keys", json=body, headers=_csrf(client)).status_code == 201


def test_logout_ends_the_session(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    cookie = client.cookies[SESSION_COOKIE]
    assert client.post("/auth/logout").status_code == 403  # no CSRF header
    assert client.post("/auth/logout", headers=_csrf(client)).status_code == 204
    assert accounts.resolve_session(get_engine(), cookie) is None
    client.cookies.set(SESSION_COOKIE, cookie)
    assert client.get("/api/me").status_code == 401


def test_a_cookie_websocket_must_come_from_our_origin(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    # TestClient dials ws://, where httpx drops a Secure cookie; a browser sends it over wss://.
    cookie = {"Cookie": f"{SESSION_COOKIE}={client.cookies[SESSION_COOKIE]}"}
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws", headers={**cookie, "Origin": "https://evil.example"}) as ws,
    ):
        ws.receive_text()
    with client.websocket_connect("/ws", headers={**cookie, "Origin": BASE}) as ws:
        assert ws.receive_json()["type"] == "graph_update"


def test_an_expired_session_is_not_signed_in(client: TestClient) -> None:
    engine = get_engine()
    owner = accounts.ensure_owner(engine, OWNER)
    client.cookies.set(SESSION_COOKIE, accounts.create_session(engine, owner.id, days=-1))
    assert client.get("/api/me").status_code == 401


# ── email links ────────────────────────────────────────────────────────────


def _link(fake: Providers) -> str:
    return fake.mail[-1]["text"].split("\n\n")[1]


def test_an_email_link_signs_in_once(client: TestClient, fake: Providers) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    assert client.post(
        "/auth/email", json={"email": "Ada@example.com", "next": "/#/study"}
    ).json() == {"sent": True}
    assert fake.mail[-1]["to"] == ["ada@example.com"]
    link = urlsplit(_link(fake))
    page = client.get(f"{link.path}?{link.query}")  # what a mail scanner fetches: spends nothing
    assert page.status_code == 200 and 'method="post"' in page.text
    form = {k: v[0] for k, v in parse_qs(link.query).items()}
    done = client.post("/auth/email/verify", data=form, headers={"Origin": BASE})
    assert (done.status_code, done.headers["location"]) == (303, "/#/study")
    assert client.get("/api/me").json()["email"] == "ada@example.com"
    again = client.post("/auth/email/verify", data=form, headers={"Origin": BASE})
    assert again.headers["location"] == "/#/login?error=link_expired"


def test_a_cross_origin_verify_is_refused(client: TestClient, fake: Providers) -> None:
    token = login_tokens.issue(get_engine(), OWNER)
    done = client.post(
        "/auth/email/verify", data={"token": token}, headers={"Origin": "https://evil.example"}
    )
    assert done.status_code == 403
    assert login_tokens.consume(get_engine(), token) == OWNER  # still unused


def test_no_mail_for_an_address_that_may_not_sign_in(client: TestClient, fake: Providers) -> None:
    assert client.post("/auth/email", json={"email": "mallory@example.com"}).json() == {
        "sent": True
    }
    assert fake.mail == []


def test_links_per_address_per_hour_are_capped(
    client: TestClient, fake: Providers, configure: Callable[..., None]
) -> None:
    configure(LIBRARIAN_EMAIL_LINKS_PER_HOUR="2")
    for _ in range(4):
        client.post("/auth/email", json={"email": OWNER})
    assert len(fake.mail) == 2


def test_an_expired_link_is_refused(client: TestClient) -> None:
    from datetime import timedelta

    token = login_tokens.issue(get_engine(), OWNER, ttl=timedelta(seconds=-1))
    done = client.post("/auth/email/verify", data={"token": token}, headers={"Origin": BASE})
    assert done.headers["location"] == "/#/login?error=link_expired"


def test_the_auth_routes_are_rate_limited(
    client: TestClient, configure: Callable[..., None]
) -> None:
    configure(LIBRARIAN_AUTH_RATE_LIMIT="3")
    codes = [client.get("/auth/login/google").status_code for _ in range(5)]
    assert codes == [303, 303, 303, 429, 429]


# ── keys, invites, roles, audit ────────────────────────────────────────────


def test_my_keys_work_as_bearer_and_revoke(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    made = client.post("/api/me/keys", json={"name": "mcp"}, headers=_csrf(client)).json()
    assert made["scopes"] == ["read"] and made["key"].startswith("lk_")
    bearer = {"Authorization": f"Bearer {made['key']}"}
    with TestClient(main_module.app, base_url=BASE) as other:
        assert other.get("/api/me", headers=bearer).json()["email"] == OWNER
        assert [k["id"] for k in client.get("/api/me/keys").json()] == [made["id"]]
        assert client.delete(f"/api/me/keys/{made['id']}", headers=_csrf(client)).status_code == 204
        assert other.get("/api/me", headers=bearer).status_code == 401
    actions = [e.action for e in accounts.audit_events(get_engine())]
    assert actions[:2] == ["key_revoke", "key_create"]


def test_admins_invite_and_see_users_and_the_audit(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    h = _csrf(client)
    assert client.post(
        "/api/admin/invites", json={"email": "Bob@Example.com"}, headers=h
    ).json() == {
        "email": "bob@example.com",
        "added": True,
    }
    assert [i["email"] for i in client.get("/api/admin/invites").json()] == ["bob@example.com"]
    users = client.get("/api/admin/users").json()
    assert users[0]["email"] == OWNER and users[0]["last_seen_at"]
    assert "chat_spent_today_usd" in users[0]
    audit = client.get("/api/admin/audit").json()
    assert [e["action"] for e in audit[:2]] == ["invite", "login"]
    assert audit[0]["email"] == OWNER and audit[0]["target"] == "bob@example.com"


def test_members_get_403_on_admin_routes_and_can_be_promoted(
    client: TestClient, fake: Providers
) -> None:
    engine = get_engine()
    accounts.invite(engine, "ada@example.com")
    _oauth_login(client)
    h = _csrf(client)
    for path in ("/api/admin/users", "/api/admin/invites", "/api/admin/audit"):
        assert client.get(path).status_code == 403
    assert (
        client.post("/api/admin/invites", json={"email": "x@example.com"}, headers=h).status_code
        == 403
    )
    assert client.post("/admin/reload", headers=h).status_code == 403
    assert cli.main(["users", "promote", "ada@example.com"]) == 0
    assert client.get("/api/admin/users").status_code == 401  # a role change ends the session
    _oauth_login(client)
    assert client.get("/api/admin/users").status_code == 200


def test_the_owner_cannot_be_demoted(client: TestClient, fake: Providers) -> None:
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    done = client.post(
        f"/api/admin/users/{OWNER}/role", json={"role": "member"}, headers=_csrf(client)
    )
    assert done.status_code == 409


def test_cli_invite_lists_and_refuses_a_duplicate(
    configure: Callable[..., None], capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["users", "invite", "Bob@Example.com"]) == 0
    assert cli.main(["users", "invite", "bob@example.com"]) == 0
    assert cli.main(["users", "invites"]) == 0
    out = capsys.readouterr().out
    assert "invited bob@example.com" in out and "already invited" in out
    assert "bob@example.com\topen" in out
    assert cli.main(["users", "promote", "nobody@example.com"]) == 1


# ── session lifetime, rotation, disable (phase 5) ──────────────────────────


def _age_session(token: str, *, created_days: float = 0, used_days: float | None = None) -> None:
    """Move a session's clocks into the past."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from librarian.db import tables

    now = datetime.now(UTC)
    values: dict[str, Any] = {"created_at": now - timedelta(days=created_days)}
    if used_days is not None:
        values["last_used_at"] = now - timedelta(days=used_days)
    s = tables.sessions
    with get_engine().begin() as conn:
        conn.execute(update(s).where(s.c.id == accounts.sessions._hash(token)).values(**values))


def _user(email: str = "ada@example.com") -> accounts.User:
    u = accounts.get_user(get_engine(), email) or accounts.add_user(get_engine(), email)
    return u


def test_a_session_ends_when_idle_too_long(configure: Callable[..., None]) -> None:
    configure(LIBRARIAN_SESSION_IDLE_DAYS="7")
    engine = get_engine()
    token = accounts.create_session(engine, _user().id)
    assert accounts.resolve_session(engine, token) is not None
    _age_session(token, used_days=6.9)
    assert accounts.resolve_session(engine, token) is not None
    _age_session(token, used_days=7.1)
    assert accounts.resolve_session(engine, token) is None


def test_use_pushes_the_idle_deadline_but_not_the_absolute_one(
    configure: Callable[..., None],
) -> None:
    configure(LIBRARIAN_SESSION_IDLE_DAYS="7")
    engine = get_engine()
    token = accounts.create_session(engine, _user().id, days=30)
    _age_session(token, created_days=6, used_days=6)  # used 6 days ago: still live, and touched
    assert accounts.resolve_session(engine, token) is not None
    _age_session(token, created_days=6, used_days=0.001)
    assert accounts.resolve_session(engine, token) is not None
    # absolute expiry ignores recent use
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from librarian.db import tables

    s = tables.sessions
    with engine.begin() as conn:
        conn.execute(update(s).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
    assert accounts.resolve_session(engine, token) is None


def test_idle_days_zero_turns_the_idle_timeout_off(configure: Callable[..., None]) -> None:
    configure(LIBRARIAN_SESSION_IDLE_DAYS="0")
    engine = get_engine()
    token = accounts.create_session(engine, _user().id)
    _age_session(token, used_days=400)
    assert accounts.resolve_session(engine, token) is not None


def test_a_session_from_before_the_migration_idles_from_its_creation(
    configure: Callable[..., None],
) -> None:
    from sqlalchemy import update

    from librarian.db import tables

    configure(LIBRARIAN_SESSION_IDLE_DAYS="7")
    engine = get_engine()
    token = accounts.create_session(engine, _user().id)
    with engine.begin() as conn:
        conn.execute(update(tables.sessions).values(last_used_at=None))
    _age_session(token, created_days=8)
    assert accounts.resolve_session(engine, token) is None


def test_creating_a_session_sweeps_dead_ones(configure: Callable[..., None]) -> None:
    from sqlalchemy import func, select

    from librarian.db import tables

    configure(LIBRARIAN_SESSION_IDLE_DAYS="7")
    engine = get_engine()
    old = accounts.create_session(engine, _user().id)
    _age_session(old, used_days=8)
    accounts.create_session(engine, _user().id)
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(tables.sessions)).scalar() == 1


def test_login_gives_a_new_session_id_and_ends_the_old_one(
    client: TestClient, fake: Providers
) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    _oauth_login(client)
    first = client.cookies[SESSION_COOKIE]
    assert accounts.resolve_session(get_engine(), first) is not None
    _oauth_login(client)
    second = client.cookies[SESSION_COOKIE]
    assert second != first
    assert accounts.resolve_session(get_engine(), first) is None
    assert accounts.resolve_session(get_engine(), second) is not None


def test_a_planted_session_cookie_does_not_survive_login(
    client: TestClient, fake: Providers
) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    planted = accounts.create_session(get_engine(), _user("eve@example.com").id)
    client.cookies.set(SESSION_COOKIE, planted)
    _oauth_login(client)
    assert accounts.resolve_session(get_engine(), planted) is None


def test_a_role_change_ends_sessions_but_a_no_op_does_not(
    client: TestClient, fake: Providers
) -> None:
    accounts.invite(get_engine(), "ada@example.com")
    _oauth_login(client)
    token = client.cookies[SESSION_COOKIE]
    accounts.set_role(get_engine(), "ada@example.com", "member")  # already a member
    assert accounts.resolve_session(get_engine(), token) is not None
    accounts.set_role(get_engine(), "ada@example.com", "admin")
    assert accounts.resolve_session(get_engine(), token) is None
    _oauth_login(client)
    token = client.cookies[SESSION_COOKIE]
    accounts.set_role(get_engine(), "ada@example.com", "member")  # demotion
    assert accounts.resolve_session(get_engine(), token) is None


def test_disable_ends_sessions_and_keys_and_blocks_sign_in(
    client: TestClient, fake: Providers
) -> None:
    engine = get_engine()
    accounts.invite(engine, "ada@example.com")
    _oauth_login(client)
    ada = _user()
    key = accounts.create_key(engine, ada.email)[1]
    token = client.cookies[SESSION_COOKIE]
    user, ended, revoked = accounts.disable_user(engine, ada.email, owner_email=OWNER)
    assert (ended, revoked) == (1, 1) and user.disabled_at is not None
    assert accounts.resolve_session(engine, token) is None
    assert accounts.resolve_key(engine, key) is None
    assert client.get("/api/me").status_code == 401
    assert accounts.may_sign_in(engine, ada.email, OWNER) is False
    refused = _oauth_login(client)
    assert "login_error" in refused.headers["location"] or "error" in refused.headers["location"]
    assert SESSION_COOKIE not in client.cookies or client.get("/api/me").status_code == 401
    accounts.enable_user(engine, ada.email)
    assert accounts.may_sign_in(engine, ada.email, OWNER) is True
    assert accounts.resolve_key(engine, key) is None  # revoked keys stay revoked
    _oauth_login(client)
    assert client.get("/api/me").status_code == 200


def test_the_owner_cannot_be_disabled() -> None:
    engine = get_engine()
    accounts.ensure_owner(engine, OWNER)
    with pytest.raises(accounts.AccountError, match="owner"):
        accounts.disable_user(engine, OWNER, owner_email=OWNER)


def test_admin_disable_route_and_cli(
    client: TestClient, fake: Providers, capsys: pytest.CaptureFixture[str]
) -> None:
    engine = get_engine()
    accounts.invite(engine, "ada@example.com")
    accounts.ensure_owner(engine, OWNER)
    fake.who = {"email": OWNER, "email_verified": True}
    _oauth_login(client)
    h = _csrf(client)
    assert client.post("/api/admin/users/nobody@example.com/disable", headers=h).status_code == 404
    assert client.post(f"/api/admin/users/{OWNER}/disable", headers=h).status_code == 409
    _user()
    done = client.post("/api/admin/users/ada@example.com/disable", headers=h)
    assert done.status_code == 200 and done.json()["keys_revoked"] == 0
    assert client.post("/api/admin/users/ada@example.com/enable", headers=h).status_code == 200
    assert cli.main(["users", "disable", "ada@example.com"]) == 0
    assert "disabled ada@example.com" in capsys.readouterr().out
    assert cli.main(["users", "disable", OWNER]) == 1
    assert cli.main(["users", "enable", "ada@example.com"]) == 0
    actions = [e["action"] for e in client.get("/api/admin/audit").json()]
    assert "user_disable" in actions and "user_enable" in actions
