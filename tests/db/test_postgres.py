"""The same repository and limiter checks on Postgres. Runs only when LIBRARIAN_TEST_DATABASE_URL is set.

docker run --rm -d -p 55432:5432 -e POSTGRES_PASSWORD=pw postgres:17
LIBRARIAN_TEST_DATABASE_URL=postgresql://postgres:pw@localhost:55432/postgres uv run pytest tests/db/test_postgres.py
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi import HTTPException
from sqlalchemy import Engine, create_engine, text

from librarian import accounts
from librarian.api.security import ChatLimiter
from librarian.config import Settings, get_settings
from librarian.courses import attempts, progress
from librarian.db import engine as db_engine
from librarian.db import get_engine
from librarian.db.migrate import upgrade
from librarian.pricing import TokenUsage

URL = os.environ.get("LIBRARIAN_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(not URL, reason="LIBRARIAN_TEST_DATABASE_URL is not set")

TS = "2026-01-01T12:00:00+00:00"


@pytest.fixture(autouse=True)
def pg(monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    url = db_engine.normalize_url(URL)
    monkeypatch.setattr(db_engine, "database_url", lambda: url)
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    upgrade(engine)
    upgrade(engine)  # idempotent
    yield engine
    engine.dispose()


def test_attempts_round_trip_and_dedupe(pg: Engine) -> None:
    me = accounts.ensure_owner(pg, get_settings().owner_email).id
    assert attempts.record(me, "flashcard", "m:a", "c/m", "knew", payload={"front": "F"}, ts=TS)
    assert attempts.record(me, "flashcard", "m:a", "c/m", "knew", payload={"front": "F"}, ts=TS)
    assert attempts.record(me, "mcq", "m:q:x", "c/m", "wrong", ts="2026-01-02T00:00:00+00:00")
    rows = attempts.attempts(me)
    assert [(a.kind, a.result) for a in rows] == [("flashcard", "knew"), ("mcq", "wrong")]
    assert rows[0].ts.isoformat() == TS and rows[0].payload == {"front": "F"}
    other = accounts.add_user(pg, "b@example.com").id
    assert attempts.attempts(other) == []


def test_progress_done_is_not_downgraded(pg: Engine) -> None:
    me = accounts.ensure_owner(pg, get_settings().owner_email).id
    assert progress.mark(me, "c/m/a", "done")
    assert progress.mark(me, "c/m/a", "opened")
    assert progress.mark(me, "c/m/b", "opened")
    assert {k: s for k, (s, _) in progress.lessons(me).items()} == {
        "c/m/a": "done",
        "c/m/b": "opened",
    }


def test_spend_cap_holds_across_two_engines() -> None:
    settings = Settings(  # type: ignore[call-arg]
        LIBRARIAN_CHAT_DAILY_BUDGET_USD=0.05,
        LIBRARIAN_CHAT_RATE_LIMIT=0,
        ANTHROPIC_MODEL="claude-sonnet-5-5",
    )
    a, b = ChatLimiter(create_engine(db_engine.database_url())), ChatLimiter(get_engine())
    a.record_usage(settings, TokenUsage(output=3000))
    b.record_usage(settings, TokenUsage(output=3000))
    for limiter in (a, b):
        with pytest.raises(HTTPException):
            limiter.admit(settings)
    assert ChatLimiter(create_engine(db_engine.database_url())).spent_usd() == pytest.approx(0.06)
