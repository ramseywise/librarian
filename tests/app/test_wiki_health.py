"""GET /api/wiki/health returns the telemetry file's newest row and recomputes nothing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routers import wiki_health as wiki_health_routes
from librarian.wiki import health as wiki_health

ROW = {
    "date": "2026-11-05",
    "pages": 900,
    # Deliberately inconsistent with any band: a recomputed status would not be "broken".
    "metrics": {"orphan_rate": {"value": 0.0, "status": "broken"}},
}


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(wiki_health, "METRICS_FILE", tmp_path / "metrics.jsonl")
    app = FastAPI()
    app.include_router(wiki_health_routes.router)
    return TestClient(app)


def test_returns_the_last_line_verbatim(client: TestClient) -> None:
    older = {"date": "2026-01-01", "metrics": {}}
    wiki_health.METRICS_FILE.write_text(f"{json.dumps(older)}\n{json.dumps(ROW)}\n\n")
    assert client.get("/api/wiki/health").json() == ROW


def test_missing_file(client: TestClient) -> None:
    assert client.get("/api/wiki/health").json() == {"date": None, "metrics": {}}


@pytest.mark.parametrize("content", ["", "\n  \n", "{broken\n", "[1, 2]\n"])
def test_empty_or_corrupt_file(client: TestClient, content: str) -> None:
    wiki_health.METRICS_FILE.write_text(content)
    assert client.get("/api/wiki/health").json() == {"date": None, "metrics": {}}


def test_undecodable_file(client: TestClient) -> None:
    wiki_health.METRICS_FILE.write_bytes(b"\xff\xfe\xff")
    assert client.get("/api/wiki/health").json() == {"date": None, "metrics": {}}
