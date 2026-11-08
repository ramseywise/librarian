"""The database layer: migrations, the attempts repository, the SQLite import, the shared spend cap."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import Engine, create_engine, inspect, select

from librarian import accounts
from librarian.accounts import User
from librarian.api.security import ChatLimiter
from librarian.config import Settings, get_settings
from librarian.courses import attempts, drill_log
from librarian.courses.imports import main as import_main
from librarian.courses.leitner import card_key
from librarian.courses.quiz import question_key
from librarian.db import engine as db_engine
from librarian.db import get_engine, tables
from librarian.db.attempt_rows import import_sqlite_attempts
from librarian.db.cli import main as db_main
from librarian.db.migrate import upgrade
from librarian.pricing import TokenUsage

TS = "2026-01-01T12:00:00+00:00"


@pytest.fixture
def raw_engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_engine(f"sqlite:///{tmp_path / 'raw.sqlite3'}")
    yield engine
    engine.dispose()


def test_migrations_upgrade_from_empty_and_are_idempotent(raw_engine: Engine) -> None:
    upgrade(raw_engine)
    upgrade(raw_engine)
    names = set(inspect(raw_engine).get_table_names())
    assert {
        "attempts",
        "meta",
        "chat_usage",
        "users",
        "sessions",
        "api_keys",
        "progress",
        "invites",
        "login_tokens",
        "audit",
        "rate_limits",
        "feedback",
        "alembic_version",
    } <= names
    with raw_engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar() == "0007"
    assert "last_seen_at" in {c["name"] for c in inspect(raw_engine).get_columns("users")}
    cols = {c["name"]: c for c in inspect(raw_engine).get_columns("attempts")}
    assert {"user_id", "ts", "event_key"} <= set(cols)
    assert cols["user_id"]["nullable"] is False
    fks = inspect(raw_engine).get_foreign_keys("attempts")
    assert [(f["referred_table"], f["constrained_columns"]) for f in fks] == [
        ("users", ["user_id"])
    ]


def test_attempts_from_before_accounts_become_the_owners(raw_engine: Engine) -> None:
    upgrade(raw_engine, "0003")
    with raw_engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO attempts (user_id, ts, kind, item, scope, result, event_key) "
            "VALUES (NULL, '2026-01-01 12:00:00.000000', 'mcq', 'm:q:x', 'c/m', 'wrong', 'old')"
        )
    upgrade(raw_engine)
    owner = accounts.get_user(raw_engine, get_settings().owner_email)
    assert owner is not None and owner.role == "admin"
    with raw_engine.connect() as conn:
        (row,) = conn.execute(select(tables.attempts)).all()
    assert row.user_id == owner.id
    assert row.event_key == tables.event_key(owner.id, TS, "mcq", "m:q:x", "wrong")


def test_default_url_is_sqlite_in_the_state_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(LIBRARIAN_STATE_DIR="/tmp/lib-state", DATABASE_URL="")  # type: ignore[call-arg]
    assert settings.database_url_or_default == "sqlite:////tmp/lib-state/librarian.sqlite3"
    pg = Settings(DATABASE_URL="postgresql://u:p@h/db")  # type: ignore[call-arg]
    assert pg.database_url_or_default == "postgresql://u:p@h/db"


@pytest.mark.parametrize("given", ["postgres://u:p@h/db", "postgresql://u:p@h/db"])
def test_postgres_urls_get_the_psycopg_driver(given: str) -> None:
    assert db_engine.normalize_url(given) == "postgresql+psycopg://u:p@h/db"
    assert db_engine.normalize_url("sqlite:///x.db") == "sqlite:///x.db"


def test_attempts_round_trip_on_the_default_database(owner: User) -> None:
    assert attempts.record(
        owner.id, "flashcard", "m:a", "c/m", "knew", payload={"front": "F"}, ts=TS
    )
    (row,) = attempts.attempts(owner.id)
    assert (row.kind, row.item, row.result, row.payload) == (
        "flashcard",
        "m:a",
        "knew",
        {"front": "F"},
    )
    assert row.ts.isoformat() == TS
    with get_engine().connect() as conn:
        assert conn.execute(select(tables.attempts.c.user_id)).scalar() == owner.id


def test_equivalent_timestamps_are_the_same_event(owner: User) -> None:
    attempts.record(owner.id, "flashcard", "k", "c/m", "knew", ts="2026-01-01T12:00:00Z")
    attempts.record(owner.id, "flashcard", "k", "c/m", "knew", ts="2026-01-01T13:00:00+01:00")
    assert len(attempts.attempts(owner.id)) == 1


def _old_attempts_file(path: Path, *rows: tuple[str, str, str, str, str, str | None]) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(
            "CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, "
            "kind TEXT NOT NULL, item TEXT NOT NULL, scope TEXT NOT NULL, result TEXT NOT NULL, "
            "payload TEXT);"
        )
        conn.executemany(
            "INSERT INTO attempts (ts, kind, item, scope, result, payload) VALUES (?,?,?,?,?,?)",
            rows,
        )
    conn.close()


def test_import_copies_the_old_file_once_and_leaves_it_alone(tmp_path: Path, owner: User) -> None:
    old = tmp_path / "attempts.sqlite3"
    _old_attempts_file(
        old,
        (TS, "flashcard", "m:a", "c/m", "knew", '{"front": "F"}'),
        ("2026-01-02T00:00:00Z", "mcq", "m:q:x", "c/m", "wrong", None),
        ("not a date", "flashcard", "m:b", "c/m", "knew", None),
    )
    before = old.read_bytes()
    engine = get_engine()
    assert import_sqlite_attempts(old, user_id=owner.id, engine=engine) == (3, 2, 1)
    assert import_sqlite_attempts(old, user_id=owner.id, engine=engine) == (3, 0, 1)
    assert old.read_bytes() == before
    rows = attempts.attempts(owner.id)
    assert [(a.kind, a.result) for a in rows] == [("flashcard", "knew"), ("mcq", "wrong")]
    assert rows[0].payload == {"front": "F"}


def test_db_cli_upgrade_and_import(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], owner: User
) -> None:
    old = tmp_path / "old.sqlite3"
    _old_attempts_file(old, (TS, "drill", "d/x", "d/x", "pass", None))
    assert db_main(["upgrade"]) == 0
    assert import_main(["import-attempts", "--from", str(old)]) == 0
    assert import_main(["import-attempts", "--from", str(old)]) == 0
    out = capsys.readouterr().out
    assert "1 added" in out and "1 already there" in out and owner.email in out
    assert import_main(["import-attempts", "--from", str(tmp_path / "missing")]) == 1
    assert len(attempts.attempts(owner.id)) == 1


def test_import_names_whose_history_it_becomes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], owner: User
) -> None:
    other = accounts.add_user(get_engine(), "b@example.com")
    log = tmp_path / "drill-log.md"
    log.write_text(DRILL_LOG)
    args = ["import-drill-log", "--from", str(log)]
    assert import_main([*args, "--user", "b@example.com"]) == 0
    assert "-> b@example.com: 4 rows read, 3 added, 0 already there, 1 skipped" in (
        capsys.readouterr().out
    )
    assert len(attempts.attempts(other.id, ["drill"])) == 3
    assert attempts.attempts(owner.id) == []
    assert import_main([*args, "--user", "nobody@example.com"]) == 1


# -- the drill log ---------------------------------------------------------------------------

DRILL_LOG = (
    "Some notes above the table.\n\n"
    "| Date | QID | Aid | Score | Note |\n|---|---|---|---|---|\n"
    "| 2026-01-01 | two-sum | 0 | ✓✓ | private thought one |\n"
    "| 2026-01-01 | two-sum | 1 | ✓✗ | private thought two |\n"
    "| 2026-01-02 | lru | 0 | ✓ | |\n"
    "| someday | lru | 0 | ✓ | no date |\n"
)


def test_the_drill_log_import_is_idempotent_and_never_stores_the_note(
    tmp_path: Path, owner: User
) -> None:
    log = tmp_path / "drill-log.md"
    log.write_text(DRILL_LOG)
    before = log.read_bytes()
    assert drill_log.import_log(log, owner.id) == (4, 3, 1)
    assert drill_log.import_log(log, owner.id) == (4, 0, 1)
    assert log.read_bytes() == before
    rows = attempts.attempts(owner.id, ["drill"])
    assert [(a.item, a.result) for a in rows] == [
        ("two-sum", "pass"),
        ("two-sum", "fail"),
        ("lru", "pass"),
    ]
    assert [a.ts.isoformat() for a in rows[:2]] == [
        "2026-01-01T12:00:00+00:00",
        "2026-01-01T12:00:01+00:00",
    ]
    assert rows[1].payload == {"score": "✓✗", "aid": "1", "source": "drill-log"}
    with get_engine().connect() as conn:
        stored = " ".join(str(v) for r in conn.execute(select(tables.attempts)).all() for v in r)
    assert "private thought" not in stored
    log.write_text(DRILL_LOG + "| 2026-01-03 | lru | 0 | ✗ | |\n")
    assert drill_log.import_log(log, owner.id) == (5, 1, 1)


def test_keys_do_not_depend_on_the_tree() -> None:
    assert card_key("private/programming/drills/lesson", "Q") == card_key(
        "programming/drills/lesson", "Q"
    )
    assert question_key("private/programming/drills", "abc") == question_key(
        "programming/drills", "abc"
    )
    assert question_key("programming/drills/x", "abc") == "programming/drills:q:abc"


# -- the spend cap lives in the database, so two workers share it ---------------------------


def _settings(budget: float = 0.05, rate: int = 0) -> Settings:
    return Settings(  # type: ignore[call-arg]
        LIBRARIAN_CHAT_DAILY_BUDGET_USD=budget,
        LIBRARIAN_CHAT_RATE_LIMIT=rate,
        ANTHROPIC_MODEL="claude-sonnet-5-5",
    )


def _worker(tmp_path: Path) -> ChatLimiter:
    """A limiter with its own engine on the shared file: what a second worker process has."""
    return ChatLimiter(create_engine(db_engine.database_url()))


def test_spend_cap_holds_across_two_limiters(tmp_path: Path) -> None:
    get_engine()  # migrate
    settings = _settings()
    a, b = _worker(tmp_path), _worker(tmp_path)
    a.admit(settings)
    a.record_usage(settings, TokenUsage(output=3000))  # $0.03
    b.admit(settings)  # under the cap
    b.record_usage(settings, TokenUsage(output=3000))  # $0.06 together
    for limiter in (a, b):
        with pytest.raises(HTTPException) as e:
            limiter.admit(settings)
        assert e.value.status_code == 429
        assert "Daily chat budget" in e.value.detail


def test_a_restart_keeps_the_days_spend(tmp_path: Path) -> None:
    get_engine()
    settings = _settings()
    _worker(tmp_path).record_usage(settings, TokenUsage(output=6000))  # $0.06
    restarted = _worker(tmp_path)
    assert restarted.spent_usd() == pytest.approx(0.06)
    with pytest.raises(HTTPException):
        restarted.admit(settings)


def test_usage_rows_accumulate_into_one_row_per_day(tmp_path: Path) -> None:
    get_engine()
    limiter = _worker(tmp_path)
    for _ in range(3):
        limiter.record_usage(_settings(), TokenUsage(input=100, output=10))
    with get_engine().connect() as conn:
        (row,) = conn.execute(select(tables.chat_usage)).all()
    assert (row.requests, row.input_tokens, row.output_tokens, row.user_id) == (3, 300, 30, None)


def test_burst_guard_is_per_process(tmp_path: Path) -> None:
    get_engine()
    settings = _settings(budget=0, rate=1)
    a, b = _worker(tmp_path), _worker(tmp_path)
    a.admit(settings)
    b.admit(settings)  # a different worker has its own window
    with pytest.raises(HTTPException) as e:
        a.admit(settings)
    assert "Too many chat requests" in e.value.detail
