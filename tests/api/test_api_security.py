"""Token auth, chat limits, health probes and request logs of the API (phase 5 steps 3-4)."""

from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from structlog.testing import capture_logs

import librarian.agent.loop as agent_module
import librarian.api.main as main_module
from librarian import retrieval
from librarian.api.security import chat_limiter
from librarian.config import get_settings
from librarian.retrieval import embeddings

TOKEN = "s3cret-token-0123456789abcdef"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture(autouse=True)
def _fresh(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    chat_limiter.reset()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()
    chat_limiter.reset()


@pytest.fixture()
def secured(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    with TestClient(main_module.app) as client:
        yield client


def test_api_route_is_open_without_a_configured_token() -> None:
    with TestClient(main_module.app) as client:
        assert client.get("/api/graph").status_code == 200


def test_401_without_token_and_with_a_wrong_one(secured: TestClient) -> None:
    resp = secured.get("/api/graph")
    assert resp.status_code == 401
    assert resp.headers["www-authenticate"] == "Bearer"
    assert secured.get("/api/graph", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert secured.get("/api/graph", headers={"Authorization": TOKEN}).status_code == 401
    assert secured.post("/api/chat/stream", json={"query": "hi"}).status_code == 401


def test_200_with_the_token(secured: TestClient) -> None:
    assert secured.get("/api/graph", headers=AUTH).status_code == 200


def test_websocket_requires_the_token(secured: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect), secured.websocket_connect("/ws"):
        pass
    with (
        pytest.raises(WebSocketDisconnect),
        secured.websocket_connect("/ws", subprotocols=["bearer", "wrong"]),
    ):
        pass
    with secured.websocket_connect("/ws", subprotocols=["bearer", TOKEN]) as ws:
        assert ws.receive_json()["type"] == "graph_update"


def _handle_with(monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    """Make the lifespan's index handle report `state` (no real index needed)."""
    monkeypatch.setattr(retrieval.IndexHandle, "state", property(lambda self: state))


def test_probes_need_no_token(secured: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    _handle_with(monkeypatch, "ready")
    assert secured.get("/healthz").json() == {"status": "ok"}
    resp = secured.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["checks"] == {"index": True, "embeddings": True}
    assert resp.json()["index"] == "ready"


def test_readyz_is_503_until_the_model_is_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main_module.retrieval, "index_is_built", lambda: True)
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "_model", None)
    with TestClient(main_module.app) as client:
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["checks"]["embeddings"] is False


def test_readyz_is_503_when_the_index_will_not_open(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> bool:
        raise RuntimeError("locked")

    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    monkeypatch.setattr(main_module.retrieval, "index_is_built", boom)
    with TestClient(main_module.app) as client:
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["checks"]["index"] is False


def test_readyz_is_503_while_the_index_is_building(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    _handle_with(monkeypatch, "building")
    with TestClient(main_module.app) as client:
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["checks"]["index"] is False
    assert resp.json()["index"] == "building"


def _fake_model(monkeypatch: pytest.MonkeyPatch, fake_anthropic: type) -> None:
    turn = fake_anthropic.text_turn("hello")
    turn.usage = SimpleNamespace(
        input_tokens=1000,
        output_tokens=1000,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )

    class Client(fake_anthropic):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            super().__init__(turns=[turn])

        def _stream(self, **kwargs):  # noqa: ANN003, ANN202
            self.turns = [turn]
            return super()._stream(**kwargs)

    client = Client()
    client.messages.stream = client._stream  # type: ignore[attr-defined]
    monkeypatch.setattr(agent_module, "_client", client)


def test_chat_is_rate_limited_with_429(
    monkeypatch: pytest.MonkeyPatch, fake_anthropic: type
) -> None:
    monkeypatch.setenv("LIBRARIAN_CHAT_RATE_LIMIT", "2")
    get_settings.cache_clear()
    _fake_model(monkeypatch, fake_anthropic)
    with TestClient(main_module.app) as client:
        for _ in range(2):
            ok = client.post("/api/chat/stream", json={"query": "hi"})
            assert ok.status_code == 200
            assert '"type": "done"' in ok.text
        blocked = client.post("/api/chat/stream", json={"query": "hi"})
    assert blocked.status_code == 429
    assert "Too many chat requests" in blocked.json()["detail"]
    assert int(blocked.headers["retry-after"]) >= 1


def test_chat_stops_at_the_daily_budget(
    monkeypatch: pytest.MonkeyPatch, fake_anthropic: type
) -> None:
    # One reply bills 1000 in + 1000 out = $0.012 on Sonnet 5.5 ($2 / $10 per MTok).
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("LIBRARIAN_CHAT_DAILY_BUDGET_USD", "0.01")
    get_settings.cache_clear()
    _fake_model(monkeypatch, fake_anthropic)
    with TestClient(main_module.app) as client:
        assert client.post("/api/chat/stream", json={"query": "hi"}).status_code == 200
        blocked = client.post("/api/chat/stream", json={"query": "hi"})
    assert blocked.status_code == 429
    assert "Daily chat budget" in blocked.json()["detail"]


def test_request_log_has_method_path_status_and_never_the_token_or_query(
    secured: TestClient,
) -> None:
    with capture_logs() as logs:
        secured.get("/api/graph?edges=all&q=private-question", headers=AUTH)
    events = [e for e in logs if e["event"] == "http.request"]
    assert events
    event = events[-1]
    assert (event["method"], event["path"], event["status"]) == ("GET", "/api/graph", 200)
    assert "duration_ms" in event
    assert TOKEN not in str(logs)
    assert "private-question" not in str(logs)


def test_shutdown_cancels_the_watcher() -> None:
    import asyncio

    async def run() -> bool:
        async def forever() -> None:
            await asyncio.sleep(3600)

        task = asyncio.create_task(forever())
        await main_module._shutdown(task)
        return task.cancelled()

    assert asyncio.run(run())


def test_static_ui_is_mounted_after_the_api(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: ANN001
    (tmp_path / "index.html").write_text("<html>ui</html>")
    monkeypatch.setenv("LIBRARIAN_WEB_DIR", str(tmp_path))
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    import importlib

    app = importlib.reload(main_module).app
    try:
        with TestClient(app) as client:
            assert client.get("/").text == "<html>ui</html>"
            assert client.get("/healthz").status_code == 200
            assert client.get("/api/graph").status_code == 401
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
        importlib.reload(main_module)


# --- Unhandled errors, compute-route limits, the spend cap failing closed, the tools switch ---


def test_unhandled_exception_is_a_generic_500_and_logged(monkeypatch: pytest.MonkeyPatch) -> None:
    from librarian.api.routers import graph as graph_router

    def boom() -> None:
        raise RuntimeError("secret-detail-/etc/passwd")

    monkeypatch.setattr(graph_router, "parse_wiki", boom)
    with (
        TestClient(main_module.app, raise_server_exceptions=False) as client,
        capture_logs() as logs,
    ):
        resp = client.get("/api/graph")
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error."}
    assert "secret-detail" not in resp.text
    event = next(e for e in logs if e["event"] == "api.unhandled_exception")
    assert event["error"] == "secret-detail-/etc/passwd" and event["path"] == "/api/graph"


def test_umap_503_carries_no_exception_text(monkeypatch: pytest.MonkeyPatch) -> None:
    import librarian.api.umap_layout as umap_layout

    def missing(*_: object) -> None:
        raise ImportError("numba-secret-detail")

    monkeypatch.setattr(umap_layout, "compute_umap_positions", missing)
    with TestClient(main_module.app) as client:
        resp = client.post("/api/layout/umap")
    assert resp.status_code == 503
    assert "numba-secret-detail" not in resp.text


def test_compute_routes_are_rate_limited_per_user(monkeypatch: pytest.MonkeyPatch) -> None:
    import librarian.api.umap_layout as umap_layout
    from librarian.api.routers import graph as graph_router

    monkeypatch.setenv("LIBRARIAN_COMPUTE_RATE_LIMIT", "2")
    monkeypatch.setenv("LIBRARIAN_UMAP_RATE_LIMIT", "1")
    get_settings.cache_clear()
    empty = {"nodes": [], "edges": [], "domains": [], "areas": []}
    monkeypatch.setattr(graph_router, "parse_wiki", lambda: empty)
    monkeypatch.setattr(umap_layout, "compute_umap_positions", dict)
    with TestClient(main_module.app) as client:
        assert [client.get("/api/graph").status_code for _ in range(2)] == [200, 200]
        blocked = client.get("/api/graph")
        assert blocked.status_code == 429
        assert int(blocked.headers["retry-after"]) >= 1
        # Each group has its own budget.
        assert [client.get("/api/tools").status_code for _ in range(2)] == [200, 200]
        assert client.get("/api/tools/search_wiki").status_code == 429
        assert client.post("/api/layout/umap").status_code == 200
        assert client.post("/api/layout/umap").status_code == 429


def test_atlas_and_semantic_edges_are_rate_limited_per_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from librarian.api.routers import graph as graph_router
    from librarian.retrieval import embeddings

    monkeypatch.setenv("LIBRARIAN_COMPUTE_RATE_LIMIT", "2")
    get_settings.cache_clear()
    empty = {"nodes": [], "edges": [], "domains": [], "areas": []}
    monkeypatch.setattr(graph_router, "parse_wiki", lambda: empty)
    monkeypatch.setattr(embeddings, "semantic_edges", lambda *_a, **_k: [])
    with TestClient(main_module.app) as client:
        assert [client.get("/api/graph/atlas").status_code for _ in range(2)] == [200, 200]
        blocked = client.get("/api/graph/atlas")
        assert blocked.status_code == 429
        assert int(blocked.headers["retry-after"]) >= 1
        assert [client.get("/api/edges/semantic").status_code for _ in range(2)] == [200, 200]
        assert client.get("/api/edges/semantic").status_code == 429
        # Each route keeps its own budget: /api/graph is untouched by the two above.
        assert client.get("/api/graph").status_code == 200


def test_compute_rate_limit_zero_turns_it_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIBRARIAN_COMPUTE_RATE_LIMIT", "0")
    get_settings.cache_clear()
    with TestClient(main_module.app) as client:
        assert all(client.get("/api/tools").status_code == 200 for _ in range(5))


def _unreachable_engine():  # noqa: ANN202 - sqlalchemy Engine
    from sqlalchemy import create_engine

    return create_engine("sqlite:////nonexistent-dir/librarian.sqlite3")


def test_spend_cap_fails_closed_when_spend_cannot_be_read(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import HTTPException

    from librarian.api.security import ChatLimiter

    limiter = ChatLimiter(_unreachable_engine())
    with pytest.raises(HTTPException) as err:
        limiter.admit(get_settings(), user_id="u1", user_cap=True)
    assert err.value.status_code == 503
    assert "sqlite" not in str(err.value.detail).lower()
    # A display of the figure still degrades to 0.0 instead of failing the page.
    assert limiter.spent_usd("u1") == 0.0
    # With both caps off there is nothing to read, so the database is not needed.
    monkeypatch.setenv("LIBRARIAN_CHAT_DAILY_BUDGET_USD", "0")
    monkeypatch.setenv("LIBRARIAN_CHAT_USER_DAILY_BUDGET_USD", "0")
    get_settings.cache_clear()
    limiter.admit(get_settings(), user_id="u1", user_cap=True)


def test_chat_is_refused_with_503_when_spend_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch, fake_anthropic: type
) -> None:
    _fake_model(monkeypatch, fake_anthropic)
    monkeypatch.setattr(chat_limiter, "_engine", _unreachable_engine())
    with TestClient(main_module.app) as client:
        resp = client.post("/api/chat/stream", json={"query": "hi"})
    assert resp.status_code == 503
    assert resp.json() == {"detail": "Chat is unavailable right now. Try again shortly."}


def _routes_with(tools_enabled: str) -> list[str]:
    import json
    import os
    import subprocess
    import sys

    code = (
        "import json; import librarian.api.main as m; "
        "print(json.dumps(sorted(m.app.openapi()['paths'])))"
    )
    env = {**os.environ, "LIBRARIAN_TOOLS_ENABLED": tools_enabled}
    out = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True
    )
    return json.loads(out.stdout.splitlines()[-1])


def test_tools_router_is_gated_by_the_setting() -> None:
    assert "/api/tools" in _routes_with("true")
    assert "/api/tools" not in _routes_with("false")
