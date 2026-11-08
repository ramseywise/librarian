"""`librarian mcp` remote mode: the MCP tools over `GET /api/tools/<name>` with an `lk_` key."""

from __future__ import annotations

from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian import accounts, retrieval
from librarian.agent.tools import MCP, ToolContext, tools_for
from librarian.config import get_settings
from librarian.db import get_engine
from librarian.mcp import remote

TOKEN = "bootstrap-token-for-tests"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # The plumbing is under test, not retrieval: the listing tools answer without an index.
    monkeypatch.setattr(retrieval, "list_domain", lambda d: f"# {d}\n- **Page** (`/x.md`)")
    monkeypatch.setattr(retrieval, "list_pages", lambda tag, directory: f"pages in {directory}")
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    with TestClient(main_module.app) as c:
        yield c
    monkeypatch.undo()
    get_settings.cache_clear()


@pytest.fixture()
def read_key(client: TestClient) -> str:
    engine = get_engine()
    accounts.add_user(engine, "ada@example.com")
    _, key = accounts.create_key(engine, "ada@example.com", scopes="read")
    return key


def _via(client: TestClient) -> httpx.MockTransport:
    """Send the remote client's requests to the in-process API."""

    def handler(request: httpx.Request) -> httpx.Response:
        resp = client.get(
            request.url.path, params=dict(request.url.params), headers=dict(request.headers)
        )
        return httpx.Response(resp.status_code, text=resp.text)

    return httpx.MockTransport(handler)


def test_the_route_lists_and_runs_the_mcp_tools(client: TestClient, read_key: str) -> None:
    bearer = {"Authorization": f"Bearer {read_key}"}
    names = client.get("/api/tools", headers=bearer).json()
    assert names == [t.name for t in tools_for(MCP)]
    local = tools_for(MCP, ["list_domain"])[0].run({"domain": "rag"}, ToolContext(surface=MCP))
    resp = client.get("/api/tools/list_domain", params={"domain": "rag"}, headers=bearer)
    assert (resp.status_code, resp.text) == (200, local)
    assert client.get("/api/tools/nope", headers=bearer).status_code == 404
    assert client.get("/api/tools/list_domain", params={"domain": "rag"}).status_code == 401


def test_bad_arguments_come_back_as_text(client: TestClient, read_key: str) -> None:
    resp = client.get(
        "/api/tools/search_wiki",
        params={"limit": "x"},
        headers={"Authorization": f"Bearer {read_key}"},
    )
    assert resp.status_code == 200 and resp.text.startswith("Invalid arguments for search_wiki")


def test_remote_call_returns_what_the_api_returns(
    client: TestClient, read_key: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(remote, "transport", _via(client))
    monkeypatch.setenv("LIBRARIAN_API_KEY", read_key)
    monkeypatch.setenv("LIBRARIAN_API_URL", "http://testserver/")
    get_settings.cache_clear()
    settings = get_settings()
    local = tools_for(MCP, ["list_pages"])[0].run({"directory": "rag"}, ToolContext(surface=MCP))
    assert remote.call(settings, "list_pages", {"directory": "rag", "tag": ""}) == local


def test_remote_call_says_why_it_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_API_KEY", "lk_revoked")
    get_settings.cache_clear()
    settings = get_settings()
    monkeypatch.setattr(remote, "transport", httpx.MockTransport(lambda r: httpx.Response(401)))
    assert "refused LIBRARIAN_API_KEY" in remote.call(settings, "read_page", {"path_or_title": "x"})

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    monkeypatch.setattr(remote, "transport", httpx.MockTransport(down))
    assert remote.call(settings, "read_page", {"path_or_title": "x"}).startswith(
        "Librarian API unreachable"
    )
    get_settings.cache_clear()


def test_booleans_go_as_lowercase_query_values(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[httpx.QueryParams] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.params)
        return httpx.Response(200, text="ok")

    monkeypatch.setattr(remote, "transport", httpx.MockTransport(handler))
    monkeypatch.setenv("LIBRARIAN_API_KEY", "lk_x")
    get_settings.cache_clear()
    remote.call(get_settings(), "search_wiki", {"query": "rrf", "expand": True, "limit": 5})
    assert dict(seen[0]) == {"query": "rrf", "expand": "true", "limit": "5"}
    get_settings.cache_clear()
