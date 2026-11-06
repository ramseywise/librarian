"""/api/graph/curriculum: which wiki pages each course and module covers."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from librarian.courses import curriculum as lib

router = APIRouter(prefix="/api/graph")


# Sync route (threadpool): with no snapshot yet it waits on the catalog build.
@router.get("/curriculum")
def get_curriculum() -> dict[str, Any]:
    return lib.current_curriculum()
