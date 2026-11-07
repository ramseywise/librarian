"""Startup refusal, docs gating, watcher and websocket cleanup, startup checks, limit bounds."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import librarian.api.main as main_module
from librarian import cli
from librarian.agent.tools import _McpSearch
from librarian.api.startup import find_problems
from librarian.config import Settings, get_settings


@pytest.fixture()
def settings_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    get_settings.cache_clear()
    yield monkeypatch  # type: ignore[misc]
    monkeypatch.undo()
    get_settings.cache_clear()


# ── F2: fail closed ────────────────────────────────────────────────────────


def test_api_refuses_a_public_bind_without_a_token(
    settings_env: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    settings_env.setenv("LIBRARIAN_API_TOKEN", "")
    assert cli.main(["api", "--host", "0.0.0.0"]) == 1
    assert "--insecure" in capsys.readouterr().err


def test_api_starts_on_a_public_bind_with_a_token_or_insecure(
    settings_env: pytest.MonkeyPatch,
) -> None:
    import uvicorn

    import librarian.log_config as log_config

    settings_env.setattr(log_config, "configure_logging", lambda: None)  # keep global logging as is
    ran: list[str] = []
    settings_env.setattr(uvicorn, "run", lambda *a, **k: ran.append(k["host"]))
    settings_env.setenv("LIBRARIAN_API_TOKEN", "tok")
    assert cli.main(["api", "--host", "0.0.0.0"]) == 0
    settings_env.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    assert cli.main(["api", "--host", "0.0.0.0", "--insecure"]) == 0
    assert cli.main(["api", "--host", "127.0.0.1"]) == 0
    assert ran == ["0.0.0.0", "0.0.0.0", "127.0.0.1"]


def test_docs_are_not_served_by_default() -> None:
    client = TestClient(main_module.app)
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404


def test_expose_docs_setting_defaults_off() -> None:
    assert Settings().expose_docs is False


# ── startup checks ─────────────────────────────────────────────────────────


def test_find_problems_names_each_problem(tmp_path: Path) -> None:
    s = Settings(
        override_wiki_dir=tmp_path / "nowiki",
        override_courses_dir=tmp_path,
        anthropic_model="claude-nope",
        anthropic_api_key="",
    )
    errors, warnings = find_problems(s)
    assert len(errors) == 3
    assert any("wiki directory" in e for e in errors)
    assert any("claude-nope" in e and "price table" in e for e in errors)
    assert any("ANTHROPIC_API_KEY" in e for e in errors)
    assert warnings == []


def test_api_check_exits_1_on_errors_and_0_when_clean(
    settings_env: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    settings_env.setenv("WIKI_DIR", str(tmp_path / "missing"))
    assert cli.main(["api", "--check"]) == 1
    assert "wiki directory missing" in capsys.readouterr().err
    (tmp_path / "wiki").mkdir()
    (tmp_path / "courses").mkdir()
    settings_env.setenv("WIKI_DIR", str(tmp_path / "wiki"))
    settings_env.setenv("COURSES_DIR", str(tmp_path / "courses"))
    get_settings.cache_clear()
    assert cli.main(["api", "--check"]) == 0


# ── F12: watcher and websocket ─────────────────────────────────────────────


def test_watcher_survives_a_failed_broadcast(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    async def awatch(_: str) -> AsyncIterator[object]:
        for i in range(2):
            yield i

    async def flaky() -> None:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("parse failed")

    monkeypatch.setattr(main_module, "_broadcast_graph", flaky)
    asyncio.run(main_module._watch_and_broadcast(awatch))
    assert len(calls) == 2


def test_watcher_restarts_after_the_watch_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    starts: list[int] = []

    async def awatch(_: str) -> AsyncIterator[object]:
        starts.append(1)
        if len(starts) == 1:
            raise OSError("inotify gone")
        yield 1

    async def ok() -> None:
        return None

    monkeypatch.setattr(main_module, "_broadcast_graph", ok)
    monkeypatch.setattr(main_module, "WATCHER_RESTART_DELAY_S", 0.0)
    asyncio.run(main_module._watch_and_broadcast(awatch))
    assert len(starts) == 2


def test_websocket_client_is_removed_when_the_connection_breaks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom() -> dict[str, Any]:
        raise RuntimeError("parse failed")

    monkeypatch.setattr(main_module, "parse_wiki", boom)
    main_module._ws_clients.clear()
    with TestClient(main_module.app) as client:
        try:
            with client.websocket_connect("/ws") as ws:
                ws.receive_json()
        except Exception:
            pass
    assert main_module._ws_clients == []


# ── F19: limits ────────────────────────────────────────────────────────────


def test_mcp_search_limit_is_bounded() -> None:
    assert _McpSearch(query="x", limit=50).limit == 50
    for bad in (0, 51):
        with pytest.raises(ValidationError):
            _McpSearch(query="x", limit=bad)
