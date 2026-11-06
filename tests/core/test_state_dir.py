"""LIBRARIAN_STATE_DIR moves every writable path under one directory; unset keeps the defaults."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.config import Settings


def test_state_dir_holds_every_writable_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in ("WIKI_DB_PATH", "EMBEDDINGS_CACHE_PATH", "CODE_INDEX_PATH", "LIBRARIAN_LOGS_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LIBRARIAN_STATE_DIR", str(tmp_path / "var"))
    s = Settings()
    state = tmp_path / "var"
    for path in (
        s.wiki_db_path,
        s.embeddings_cache_path,
        s.code_index_path,
        s.logs_dir,
        s.cache_dir,
        s.flashcard_log,
        s.retrieval_log,
        s.curriculum_snapshot,
        s.lesson_vec_cache,
    ):
        assert path.is_relative_to(state), path


def test_defaults_are_unchanged_without_a_state_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("LIBRARIAN_STATE_DIR", "WIKI_DB_PATH", "LIBRARIAN_LOGS_DIR"):
        monkeypatch.delenv(name, raising=False)
    s = Settings()
    assert s.wiki_db_path == s.root / ".wiki_index.duckdb"
    assert s.logs_dir == s.root / "logs"
    assert s.cache_dir == s.root / ".cache"
