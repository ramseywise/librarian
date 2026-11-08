"""Accounts (phase 3 wave A): users, API keys, current_user, scopes, roles, per-user chat caps."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from starlette.websockets import WebSocketDisconnect
from structlog.testing import capture_logs

import librarian.api.main as main_module
from librarian import accounts, cli
from librarian.accounts import keys as keys_module
from librarian.api.routers import chat as chat_router
from librarian.api.security import chat_limiter
from librarian.config import get_settings
from librarian.db import get_engine, tables
from librarian.pricing import TokenUsage

TOKEN = "bootstrap-token-0123456789abcdef"


def _auth(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


@pytest.fixture(autouse=True)
def _fresh(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    monkeypatch.setenv("LIBRARIAN_OWNER_EMAIL", "Owner@Example.com")
    get_settings.cache_clear()
    chat_limiter.reset()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()
    chat_limiter.reset()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(main_module.app) as c:
        yield c


def _member(email: str, scopes: str = "read write") -> str:
    engine = get_engine()
    accounts.add_user(engine, email, name=email.split("@")[0])
    return accounts.create_key(engine, email, scopes=scopes)[1]


# ── who the caller is ──────────────────────────────────────────────────────


def test_the_bootstrap_token_is_the_owner_and_an_admin(client: TestClient) -> None:
    me = client.get("/api/me", headers=_auth(TOKEN)).json()
    assert (me["email"], me["role"], me["scopes"]) == (
        "owner@example.com",
        "admin",
        ["read", "write"],
    )
    assert me["chat"]["daily_budget_usd"] is None  # admins have only the global cap
    assert client.get("/api/me", headers=_auth(TOKEN)).json()["id"] == me["id"]  # one row


def test_open_mode_acts_as_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    with TestClient(main_module.app) as c:
        assert c.get("/api/me").json()["role"] == "admin"


def test_a_key_is_its_user(client: TestClient) -> None:
    key = _member("ada@example.com")
    assert key.startswith("lk_")
    me = client.get("/api/me", headers=_auth(key)).json()
    assert (me["email"], me["role"]) == ("ada@example.com", "member")
    assert me["chat"]["daily_budget_usd"] == get_settings().chat_user_daily_budget_usd
    assert client.get("/api/graph", headers=_auth(key)).status_code == 200


def test_an_unknown_or_revoked_key_is_401_even_in_open_mode(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = _member("ada@example.com")
    key_id = key.removeprefix("lk_").split("_")[0]
    assert accounts.revoke_key(get_engine(), key_id)
    assert not accounts.revoke_key(get_engine(), key_id)  # already revoked
    resp = client.get("/api/me", headers=_auth(key))
    assert resp.status_code == 401
    assert resp.headers["www-authenticate"] == "Bearer"
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    assert client.get("/api/me", headers=_auth(key)).status_code == 401
    assert client.get("/api/me", headers=_auth("lk_nope_nope")).status_code == 401


def test_no_credential_or_a_wrong_token_is_401(client: TestClient) -> None:
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/me", headers=_auth("wrong")).status_code == 401


def test_a_read_only_key_cannot_write(client: TestClient) -> None:
    key = _member("ada@example.com", scopes="read")
    assert client.get("/api/me", headers=_auth(key)).json()["scopes"] == ["read"]
    resp = client.post("/api/chat/stream", json={"query": "hi"}, headers=_auth(key))
    assert resp.status_code == 403
    assert "read-only" in resp.json()["detail"]


def test_admin_routes_are_403_for_members(client: TestClient) -> None:
    key = _member("ada@example.com")
    assert client.get("/api/admin/users", headers=_auth(key)).status_code == 403
    users = client.get("/api/admin/users", headers=_auth(TOKEN)).json()
    assert {u["email"] for u in users} == {"ada@example.com", "owner@example.com"}


def test_websocket_takes_a_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from librarian.api.routers import graph as graph_router

    monkeypatch.setattr(graph_router, "parse_wiki", lambda: {"nodes": [], "edges": []})
    key = _member("ada@example.com")
    with client.websocket_connect("/ws", subprotocols=["bearer", key]) as ws:
        assert ws.receive_json()["type"] == "graph_update"
    accounts.revoke_key(get_engine(), key)  # the whole key works as the id too
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws", subprotocols=["bearer", key]),
    ):
        pass


def test_the_request_log_names_the_user_never_the_key(client: TestClient) -> None:
    key = _member("ada@example.com")
    user = accounts.get_user(get_engine(), "ada@example.com")
    assert user is not None
    with capture_logs() as logs:
        client.get("/api/me", headers=_auth(key))
    event = [e for e in logs if e["event"] == "http.request"][-1]
    assert event["user_id"] == user.id
    assert key not in str(logs)


def test_last_used_is_written_at_most_once_per_window() -> None:
    engine = get_engine()
    key = _member("ada@example.com")
    k = tables.api_keys

    def last_used() -> datetime | None:
        with engine.connect() as conn:
            return conn.execute(select(k.c.last_used_at)).scalar()

    assert last_used() is None
    accounts.resolve_key(engine, key)
    first = last_used()
    assert first is not None
    accounts.resolve_key(engine, key)
    assert last_used() == first
    old = datetime.now(UTC) - keys_module.LAST_USED_RESOLUTION - timedelta(seconds=1)
    with engine.begin() as conn:
        conn.execute(update(k).values(last_used_at=old))
    accounts.resolve_key(engine, key)
    assert last_used() != old.replace(tzinfo=None)


# ── chat caps per user ─────────────────────────────────────────────────────


def _fake_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    async def run(
        query: str,
        history: list[Any],
        on_usage: Callable[[TokenUsage], None],
        **_: object,
    ) -> AsyncIterator[dict[str, Any]]:
        on_usage(TokenUsage(output=1000))
        yield {"type": "done"}

    monkeypatch.setattr(chat_router, "run_agent_stream", run)


def test_one_members_cap_trips_without_stopping_another(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Sonnet 5.5 bills $10 per million output tokens.
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("LIBRARIAN_CHAT_USER_DAILY_BUDGET_USD", "0.05")
    get_settings.cache_clear()
    _fake_agent(monkeypatch)
    a, b = _member("a@example.com"), _member("b@example.com")
    a_id = accounts.get_user(get_engine(), "a@example.com").id  # type: ignore[union-attr]
    chat_limiter.record_usage(get_settings(), TokenUsage(output=10_000), a_id)  # $0.10
    blocked = client.post("/api/chat/stream", json={"query": "hi"}, headers=_auth(a))
    assert blocked.status_code == 429
    assert "Your daily chat budget" in blocked.json()["detail"]
    assert (
        client.post("/api/chat/stream", json={"query": "hi"}, headers=_auth(b)).status_code == 200
    )
    # The owner is an admin: no per-user cap.
    assert (
        client.post("/api/chat/stream", json={"query": "hi"}, headers=_auth(TOKEN)).status_code
        == 200
    )
    spent_b = client.get("/api/me", headers=_auth(b)).json()["chat"]["spent_today_usd"]
    assert spent_b > 0


def test_the_global_cap_is_everyones_spend_together(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("LIBRARIAN_CHAT_DAILY_BUDGET_USD", "0.05")
    monkeypatch.setenv("LIBRARIAN_CHAT_USER_DAILY_BUDGET_USD", "0")
    get_settings.cache_clear()
    _fake_agent(monkeypatch)
    for email in ("a@example.com", "b@example.com"):
        _member(email)
        uid = accounts.get_user(get_engine(), email).id  # type: ignore[union-attr]
        chat_limiter.record_usage(get_settings(), TokenUsage(output=3000), uid)  # $0.03 each
    c = _member("c@example.com")
    blocked = client.post("/api/chat/stream", json={"query": "hi"}, headers=_auth(c))
    assert blocked.status_code == 429
    assert blocked.json()["detail"].startswith("Daily chat budget")


# ── the store ──────────────────────────────────────────────────────────────


def test_users_are_unique_by_lowercased_email_and_validated() -> None:
    engine = get_engine()
    accounts.add_user(engine, " Ada@Example.com ")
    with pytest.raises(accounts.AccountError, match="exists"):
        accounts.add_user(engine, "ada@example.com")
    with pytest.raises(accounts.AccountError, match="email"):
        accounts.add_user(engine, "not-an-email")
    with pytest.raises(accounts.AccountError, match="timezone"):
        accounts.add_user(engine, "b@example.com", timezone="Mars/Olympus")
    with pytest.raises(accounts.AccountError, match="scopes"):
        accounts.create_key(engine, "ada@example.com", scopes="admin")
    with pytest.raises(accounts.AccountError, match="no user"):
        accounts.create_key(engine, "nobody@example.com")


def test_the_owner_is_kept_an_admin() -> None:
    engine = get_engine()
    accounts.add_user(engine, "owner@example.com", role="member")
    assert accounts.ensure_owner(engine, "owner@example.com").role == "admin"
    assert accounts.get_user(engine, "owner@example.com").role == "admin"  # type: ignore[union-attr]


def test_users_and_keys_cli(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from librarian.accounts import cli as accounts_cli

    monkeypatch.setattr(
        accounts_cli, "configure_logging", lambda: None
    )  # keep global logging as is
    assert cli.main(["users", "add", "ada@example.com", "--timezone", "Europe/Copenhagen"]) == 0
    assert cli.main(["users", "add", "ada@example.com"]) == 1
    assert "exists" in capsys.readouterr().err
    assert cli.main(["users", "list"]) == 0
    assert "ada@example.com\tmember\tEurope/Copenhagen" in capsys.readouterr().out

    assert cli.main(["keys", "create", "ada@example.com", "--scopes", "read", "--name", "mcp"]) == 0
    out = capsys.readouterr()
    key = out.out.splitlines()[-1]
    assert key.startswith("lk_") and "shown once" in out.err
    assert accounts.resolve_key(get_engine(), key) is not None

    assert cli.main(["keys", "list"]) == 0
    listing = capsys.readouterr().out
    assert "live" in listing and key not in listing  # the secret is never shown again
    key_id = listing.split("\t")[0]
    assert cli.main(["keys", "revoke", key_id]) == 0
    assert cli.main(["keys", "revoke", key_id]) == 1
    assert accounts.resolve_key(get_engine(), key) is None
