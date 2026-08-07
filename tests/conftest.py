from __future__ import annotations

from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring live servers")
    config.addinivalue_line("markers", "unit: fast unit tests, no servers needed")


@pytest.fixture(autouse=True)
def _isolate_retrieval_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep test traffic out of the real retrieval telemetry (LIB-114 F10).

    logs/retrieval.jsonl feeds /compact-wiki's evidence pass — pytest queries
    polluting it skew which pages look retrieval-hot. Per-test patches in
    tests/app/ remain but are now redundant.
    """
    from app.mcp_server import server

    monkeypatch.setattr(server, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(server, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
