"""The newest row of the wiki's telemetry file, verbatim (served by GET /api/wiki/health).

librarian.wiki.telemetry owns the numbers and their statuses, and this recomputes nothing.
That file is built from public pages only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from librarian.config import get_settings
from librarian.log_config import get_logger

log = get_logger(__name__)

METRICS_FILE = get_settings().metrics_file
NO_SNAPSHOT: dict[str, Any] = {"date": None, "metrics": {}}


def latest_snapshot(path: Path) -> dict[str, Any]:
    """The last row of `path`, or NO_SNAPSHOT when it is missing, empty or unreadable."""
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        return dict(NO_SNAPSHOT)
    except (OSError, UnicodeDecodeError) as e:
        log.warning("wiki_health.unreadable", error=str(e))
        return dict(NO_SNAPSHOT)
    if not lines:
        return dict(NO_SNAPSHOT)
    try:
        row = json.loads(lines[-1])
    except json.JSONDecodeError as e:
        log.warning("wiki_health.corrupt_row", error=str(e))
        return dict(NO_SNAPSHOT)
    if not isinstance(row, dict):
        log.warning("wiki_health.corrupt_row", error="row is not an object")
        return dict(NO_SNAPSHOT)
    return row
