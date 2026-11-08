"""Retries, Notion status checks, Linear pagination and manifest atomicity/locking (mocked HTTP)."""

from __future__ import annotations

import json
import multiprocessing
import os
import threading
import time
from pathlib import Path

import httpx
import pytest

import librarian.ingest.manifest as manifest_module
from librarian.ingest import base, ingest_linear, ingest_notion
from librarian.ingest.manifest import ManifestSession


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    recorded: list[float] = []
    monkeypatch.setattr(base.time, "sleep", recorded.append)
    return recorded


def _client(handler: httpx.MockTransport | object) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))  # pyright: ignore[reportArgumentType]


# ---------------------------------------------------------------------------
# request_with_retry
# ---------------------------------------------------------------------------


def test_retries_5xx_then_succeeds(sleeps: list[float]) -> None:
    codes = iter([503, 500, 200])
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(next(codes), text="ok")

    with _client(handler) as client:
        resp = base.request_with_retry(client, "GET", "https://example.test/x")
    assert resp.text == "ok"
    assert len(calls) == 3
    assert len(sleeps) == 2
    assert sleeps[1] > sleeps[0] * 0.9  # exponential, jitter only adds


def test_retries_timeout_then_succeeds(sleeps: list[float]) -> None:
    state = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] == 1:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200)

    with _client(handler) as client:
        assert base.request_with_retry(client, "GET", "https://example.test/x").status_code == 200
    assert len(sleeps) == 1


def test_retry_after_is_honoured(sleeps: list[float]) -> None:
    responses = iter([httpx.Response(429, headers={"Retry-After": "7"}), httpx.Response(200)])

    with _client(lambda request: next(responses)) as client:
        base.request_with_retry(client, "GET", "https://example.test/x")
    assert sleeps == [7.0]


def test_no_retry_on_404(sleeps: list[float]) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(404)

    with _client(handler) as client, pytest.raises(httpx.HTTPStatusError):
        base.request_with_retry(client, "GET", "https://example.test/x")
    assert len(calls) == 1
    assert sleeps == []


def test_gives_up_after_max_attempts(sleeps: list[float]) -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(502)

    with _client(handler) as client, pytest.raises(httpx.HTTPStatusError):
        base.request_with_retry(client, "GET", "https://example.test/x")
    assert len(calls) == base.MAX_ATTEMPTS
    assert len(sleeps) == base.MAX_ATTEMPTS - 1


# ---------------------------------------------------------------------------
# Notion / Linear
# ---------------------------------------------------------------------------


def _patch_client(monkeypatch: pytest.MonkeyPatch, module: object, handler: object) -> None:
    real = httpx.Client

    def factory(**kwargs: object) -> httpx.Client:
        return real(transport=httpx.MockTransport(handler), **kwargs)  # pyright: ignore[reportArgumentType,reportCallIssue]

    monkeypatch.setattr(module.httpx, "Client", factory)  # pyright: ignore[reportAttributeAccessIssue]


def test_notion_error_status_raises(monkeypatch: pytest.MonkeyPatch, sleeps: list[float]) -> None:
    _patch_client(
        monkeypatch,
        ingest_notion,
        lambda request: httpx.Response(401, json={"object": "error", "message": "bad token"}),
    )
    with pytest.raises(httpx.HTTPStatusError):
        ingest_notion.fetch_page("page-id", "key")


def test_linear_follows_two_pages(monkeypatch: pytest.MonkeyPatch, sleeps: list[float]) -> None:
    seen_cursors: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = json.loads(request.content)["variables"]["after"]
        seen_cursors.append(cursor)
        if cursor is None:
            body = {"nodes": [{"id": "1"}], "pageInfo": {"hasNextPage": True, "endCursor": "c1"}}
        else:
            body = {"nodes": [{"id": "2"}], "pageInfo": {"hasNextPage": False, "endCursor": None}}
        return httpx.Response(200, json={"data": {"issues": body}})

    _patch_client(monkeypatch, ingest_linear, handler)
    issues = ingest_linear.fetch_issues("key")
    assert [i["id"] for i in issues] == ["1", "2"]
    assert seen_cursors == [None, "c1"]


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


@pytest.fixture
def manifest_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "manifest.jsonl"
    monkeypatch.setattr(manifest_module, "MANIFEST_PATH", path)
    monkeypatch.setattr(manifest_module, "REPO_ROOT", tmp_path)
    return path


def test_manifest_write_is_atomic(manifest_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest_path.write_text('{"path": "old.md"}\n')

    def boom(src: object, dst: object) -> None:
        raise OSError("disk gone")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        manifest_module._save({"new.md": {"path": "new.md"}})
    assert manifest_path.read_text() == '{"path": "old.md"}\n'
    assert [p.name for p in manifest_path.parent.iterdir() if p.suffix == ".tmp"] == []


def _hold_lock(path: str, ready: object, release: object) -> None:
    manifest_module.MANIFEST_PATH = Path(path)
    with manifest_module._lock():
        ready.set()  # pyright: ignore[reportAttributeAccessIssue]
        release.wait(5)  # pyright: ignore[reportAttributeAccessIssue]


def test_manifest_lock_serialises(manifest_path: Path) -> None:
    ctx = multiprocessing.get_context("fork")
    ready, release = ctx.Event(), ctx.Event()
    proc = ctx.Process(target=_hold_lock, args=(str(manifest_path), ready, release))
    proc.start()
    try:
        assert ready.wait(5)
        entered = threading.Event()

        def contender() -> None:
            with ManifestSession():
                entered.set()

        t = threading.Thread(target=contender)
        t.start()
        time.sleep(0.3)
        assert not entered.is_set()  # blocked while the other process holds the lock
        release.set()
        t.join(5)
        assert entered.is_set()
    finally:
        release.set()
        proc.join(5)
