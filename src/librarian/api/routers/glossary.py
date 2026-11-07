"""/api/glossary: terms as a graph layer, and where each is mentioned."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from librarian.courses import glossary as lib

router = APIRouter(prefix="/api/glossary")


# Sync routes (threadpool): a cold call reads every page.
@router.get("")
def get_glossary() -> dict[str, Any]:
    return {"terms": lib.public_terms()}


@router.get("/mentions")
def get_mentions() -> dict[str, list[str]]:
    """Term id → pages mentioning it: the edges of the term layer. Separate from the terms
    themselves because it is much larger and only the focused view and search need it."""
    return lib.term_mentions()
