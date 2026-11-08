"""`librarian api --workers 2`: two real uvicorn workers on one database answer the same.

Runs the CLI in a subprocess against a tiny content root (one wiki page, one course with a
two-card deck) and a SQLite file, then talks to it over fresh connections so the kernel spreads
requests over both workers. The request log carries each worker's pid, which proves both answered.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pytest

from librarian.api.security import ChatLimiter
from librarian.config import Settings
from librarian.db import engine as db_engine
from librarian.pricing import TokenUsage

pytest.importorskip("uvicorn")

WORKERS = 2
REQUESTS = 80


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _content_root(root: Path) -> None:
    _write(root / "pyproject.toml", "[project]\nname = 'fixture'\n")
    _write(
        root / "data/wiki/notes/alpha.md",
        "---\ntitle: Alpha\ntags: [rag, concept]\nsummary: A page.\nupdated: 2026-11-07\n"
        "sources: []\n---\n\n# Alpha\n\nAlpha talks about retrieval.\n",
    )
    _write(root / "data/courses/demo/_course.md", "---\ntitle: Demo\norder: 1\n---\n")
    _write(root / "data/courses/demo/m1/_module.md", "---\ntitle: Module one\norder: 1\n---\n")
    _write(
        root / "data/courses/demo/m1/l1.md",
        "---\ntitle: Lesson one\nsummary: The lesson.\norder: 1\n---\n\nBody.\n",
    )
    _write(
        root / "data/courses/demo/m1/_flashcards.md",
        "---\ncards:\n  - {front: Q1, back: A1}\n  - {front: Q2, back: A2}\n---\n",
    )


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, Path]]:
    root = tmp_path / "root"
    _content_root(root)
    url = f"sqlite:///{tmp_path / 'librarian.sqlite3'}"
    # Today's spend is over the budget before the workers start: every chat must be refused.
    monkeypatch.setattr(db_engine, "database_url", lambda: url)
    settings = Settings()
    ChatLimiter().record_usage(settings, TokenUsage(output=10_000_000))
    db_engine.reset_engines()

    port = _free_port()
    env = {
        **os.environ,
        "LIBRARIAN_ROOT": str(root),
        "LIBRARIAN_STATE_DIR": str(tmp_path / "var"),
        "DATABASE_URL": url,
        "LIBRARIAN_INDEX_AUTOBUILD": "0",
        "LIBRARIAN_SKIP_WARMUP": "1",
        "LIBRARIAN_API_TOKEN": "",
        "LIBRARIAN_CHAT_DAILY_BUDGET_USD": "1",
        "ANTHROPIC_API_KEY": "test-key",
    }
    log = tmp_path / "api.log"
    with log.open("w") as fh:
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "librarian.cli",
                "api",
                "--port",
                str(port),
                "--workers",
                str(WORKERS),
            ],
            env=env,
            stdout=fh,
            stderr=subprocess.STDOUT,
        )
        base = f"http://127.0.0.1:{port}"
        try:
            deadline = time.monotonic() + 60
            while True:
                try:
                    if httpx.get(f"{base}/healthz", timeout=2).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                if proc.poll() is not None or time.monotonic() > deadline:
                    pytest.fail(f"api did not start:\n{log.read_text()[-3000:]}")
                time.sleep(0.3)
            # Both workers up: each logs its own startup line.
            while log.read_text().count("api.startup.ready") < WORKERS:
                if time.monotonic() > deadline:
                    pytest.fail(f"only one worker started:\n{log.read_text()[-3000:]}")
                time.sleep(0.3)
            yield base, log
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()


def _fresh(method: str, url: str, **kwargs: object) -> httpx.Response:
    """One request on its own connection, so successive requests can land on either worker."""
    with httpx.Client(headers={"Connection": "close"}, timeout=10) as client:
        return client.request(method, url, **kwargs)  # type: ignore[arg-type]


def _due(base: str) -> list[dict[str, object]]:
    return _fresh("GET", f"{base}/api/courses/flashcards-due").json()["modules"]


def _concurrently[T](fn: Callable[[], T], n: int) -> list[T]:
    """`n` calls at once: back-to-back requests all reach whichever worker is idle first."""
    with ThreadPoolExecutor(max_workers=16) as pool:
        return list(pool.map(lambda _: fn(), range(n)))


def _pids(log: Path) -> set[int]:
    pids = set()
    for line in log.read_text().splitlines():
        if '"http.request"' in line:
            pids.add(json.loads(line)["pid"])
    return pids


def test_two_workers_share_attempts_and_spend(server: tuple[str, Path]) -> None:
    base, log = server

    before = _due(base)
    assert [(m["deck"], m["new"]) for m in before] == [("demo/m1", 2)]

    # A grade written through one worker...
    for card in ("0", "1"):
        body = {"deck": "demo/m1", "card": card, "result": "knew"}
        assert _fresh("POST", f"{base}/api/courses/flashcard-results", json=body).json() == {
            "logged": True
        }
    # ...is what every worker reads afterwards.
    seen = {json.dumps(m, sort_keys=True) for m in _concurrently(lambda: _due(base), REQUESTS)}
    assert seen == {json.dumps([], sort_keys=True)}

    # The daily budget is read from the database, so no worker lets a chat through.
    chat = {"query": "hello"}
    statuses = _concurrently(lambda: _fresh("POST", f"{base}/api/chat/stream", json=chat), 20)
    assert {r.status_code for r in statuses} == {429}
    assert all("budget" in r.json()["detail"] for r in statuses)

    assert len(_pids(log)) == WORKERS, "every request went to one worker"
