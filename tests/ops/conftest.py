"""Fixtures for the ops tests: a migrated SQLite database with rows, settings, and a fake age."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from librarian.config import Settings
from librarian.db.migrate import upgrade
from librarian.ops import backup, proc


@pytest.fixture
def db_url(tmp_path: Path) -> Iterator[str]:
    url = f"sqlite:///{tmp_path / 'live.sqlite3'}"
    engine = create_engine(url)
    upgrade(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (id, email, role, timezone, created_at) "
                "VALUES ('u1', 'a@example.com', 'admin', 'UTC', '2026-01-01T00:00:00+00:00')"
            )
        )
        conn.execute(text("INSERT INTO meta (key, value) VALUES ('k', 'v')"))
    engine.dispose()
    yield url


@pytest.fixture
def bucket(tmp_path: Path) -> Path:
    return tmp_path / "bucket"


@pytest.fixture
def settings(bucket: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("LIBRARIAN_BACKUP_URL", f"file://{bucket}")
    monkeypatch.setenv("LIBRARIAN_BACKUP_AGE_RECIPIENT", "age1testrecipient")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setattr(backup, "get_release", lambda: "sha-test")
    return Settings()


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Every external command, recorded. `age` is faked as a byte copy so encrypt/decrypt round trip."""
    seen: list[list[str]] = []

    def fake_run(cmd, *, env=None, timeout=0.0):  # noqa: ANN001, ANN202
        seen.append(list(cmd))
        if cmd[0] == "age":
            src, out = Path(cmd[-1]), Path(cmd[cmd.index("--output") + 1])
            out.write_bytes(
                b"AGE:" + src.read_bytes() if "--recipient" in cmd else src.read_bytes()[4:]
            )
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(proc, "run", fake_run)
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    return seen
