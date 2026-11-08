"""The shared sign-in limit: counted in the database, so workers do not multiply it."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import HTTPException
from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.exc import OperationalError
from starlette.requests import Request

from librarian.accounts import rate_limits
from librarian.api.security import AuthLimiter
from librarian.config import get_settings
from librarian.db import tables
from librarian.db.migrate import upgrade


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    e = create_engine(f"sqlite:///{tmp_path / 'rl.sqlite3'}", connect_args={"timeout": 30})
    upgrade(e)
    yield e
    e.dispose()


def _two_workers(tmp_path: Path, engine: Engine) -> tuple[Engine, Engine]:
    """Two engines on one file: separate pools, like two processes."""
    b = create_engine(f"sqlite:///{tmp_path / 'rl.sqlite3'}", connect_args={"timeout": 30})
    return engine, b


def test_two_workers_together_allow_exactly_the_limit(tmp_path: Path, engine: Engine) -> None:
    a, b = _two_workers(tmp_path, engine)
    limit, window = 10, 60
    allowed = 0
    for i in range(30):
        w = rate_limits.hit(a if i % 2 else b, "auth:1.2.3.4", window, now=1000.0 + i)
        allowed += w.hits <= limit
    assert allowed == limit
    b.dispose()


def test_concurrent_threads_do_not_lose_counts(tmp_path: Path, engine: Engine) -> None:
    a, b = _two_workers(tmp_path, engine)
    seen: list[int] = []

    def worker(e: Engine) -> None:
        for _ in range(10):
            seen.append(rate_limits.hit(e, "auth:x", 60, now=500.0).hits)

    threads = [Thread(target=worker, args=(e,)) for e in (a, b)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(seen) == list(range(1, 21))
    b.dispose()


def test_window_expires_with_a_patched_clock(engine: Engine) -> None:
    clock = [1000.0]
    for _ in range(3):
        w = rate_limits.hit(engine, "k", 60, clock=lambda: clock[0])
    assert w.hits == 3
    clock[0] = 1059.0
    assert rate_limits.hit(engine, "k", 60, clock=lambda: clock[0]).hits == 4
    assert rate_limits.hit(engine, "k", 60, clock=lambda: clock[0]).retry_after_s == 1
    clock[0] = 1060.0  # the window opened at 1000 has passed
    assert rate_limits.hit(engine, "k", 60, clock=lambda: clock[0]).hits == 1
    assert rate_limits.hit(engine, "other", 60, clock=lambda: clock[0]).hits == 1


def test_expired_rows_are_pruned(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rate_limits.random, "randrange", lambda n: 0)
    rate_limits.hit(engine, "old", 60, now=0.0)
    rate_limits.hit(engine, "new", 60, now=1000.0)
    with engine.connect() as conn:
        keys = set(conn.execute(select(tables.rate_limits.c.key)).scalars())
        assert keys == {"new"}
        assert conn.execute(select(func.count()).select_from(tables.rate_limits)).scalar() == 1


def _request(host: str) -> Request:
    return cast(Request, SimpleNamespace(client=SimpleNamespace(host=host)))


def test_two_auth_limiters_share_the_limit(
    tmp_path: Path, engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_AUTH_RATE_LIMIT", "10")
    get_settings.cache_clear()
    a, b = _two_workers(tmp_path, engine)
    workers = [AuthLimiter(a), AuthLimiter(b)]
    admitted = 0
    for i in range(30):
        try:
            workers[i % 2](_request("9.9.9.9"))
            admitted += 1
        except HTTPException as e:
            assert e.status_code == 429 and "Retry-After" in (e.headers or {})
    assert admitted == 10
    workers[0].reset()
    workers[1].reset()
    workers[1](_request("9.9.9.9"))  # reset cleared the shared rows too
    b.dispose()
    get_settings.cache_clear()


def test_auth_limiter_fails_open_when_the_database_is_down(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_AUTH_RATE_LIMIT", "3")
    get_settings.cache_clear()

    def boom(*_: object, **__: object) -> None:
        raise OperationalError("stmt", {}, Exception("down"))

    monkeypatch.setattr(rate_limits, "hit", boom)
    limiter = AuthLimiter(engine)
    for _ in range(3):
        limiter(_request("8.8.8.8"))  # admitted
    with pytest.raises(HTTPException) as exc:  # the per-process guard still holds
        limiter(_request("8.8.8.8"))
    assert exc.value.status_code == 429
    get_settings.cache_clear()
