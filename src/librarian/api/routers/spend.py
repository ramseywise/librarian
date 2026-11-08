"""GET /api/admin/spend: who spent what on chat, against the global cap (admins only).

Users appear by id and display name, never by email. Figures are estimates from the price table.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from librarian import spend
from librarian.api.security import Admin
from librarian.config import get_settings
from librarian.db import get_engine
from librarian.log_config import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.get("/api/admin/spend")
def admin_spend(_: Admin) -> dict[str, Any]:
    try:
        return spend.report(get_engine(), get_settings())
    except SQLAlchemyError as e:
        log.error("admin.spend_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Spend data unavailable.") from e
