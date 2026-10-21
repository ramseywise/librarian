"""Module-level path constants must resolve inside this repo.

Moving a module up or down a directory without fixing its `Path(__file__).parent...`
chain points it outside the repo, and every consumer then sees an empty or missing
directory instead of an error. That happened when shared/embeddings.py, core/cron.py
and core/enrich.py moved one level up: the relinker embedded zero pages and the cron
synced session notes into ~/workspace/raw/ for weeks without a failure.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

CASES = [
    ("core.cron", "_REPO_ROOT", REPO_ROOT),
    ("core.cron", "LIBRARIAN_RAW_SESSIONS", REPO_ROOT / "data" / "raw" / "sessions"),
    ("core.cron", "LIBRARIAN_WIKI_DIR", REPO_ROOT / "data" / "wiki"),
    ("core.enrich", "LIBRARIAN_RAW_SESSIONS", REPO_ROOT / "data" / "raw" / "sessions"),
    ("core.relinker", "WIKI_DIR", REPO_ROOT / "data" / "wiki"),
    ("shared.embeddings", "WIKI_DIR", REPO_ROOT / "data" / "wiki"),
    ("shared.embeddings", "CACHE_DB", REPO_ROOT / ".embeddings_cache.duckdb"),
]


@pytest.mark.parametrize(("module", "attr", "expected"), CASES)
def test_path_constant_resolves_inside_repo(module: str, attr: str, expected: Path) -> None:
    try:
        mod = importlib.import_module(module)
    except ImportError as exc:  # optional extras (e.g. duckdb) not installed
        pytest.skip(f"{module} not importable: {exc}")
    assert Path(getattr(mod, attr)).resolve() == expected.resolve()
