"""GET /api/wiki/health: the newest row of the wiki's telemetry file, verbatim."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from librarian.wiki import health

router = APIRouter(prefix="/api/wiki")


@router.get("/health")
def wiki_health() -> dict[str, Any]:
    return health.latest_snapshot(health.METRICS_FILE)
