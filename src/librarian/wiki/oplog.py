"""The telemetry files: tracked jsonl rows, atomic writes, the metrics snapshot and the operation log roll-up."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from librarian.wiki.pages import REPO_ROOT

METRICS_FILE = "metrics.jsonl"
OPERATIONS_FILE = "operations.jsonl"
ASKED_FILE = "asked.jsonl"
GAPS_FILE = "gaps.md"
# Every other *.jsonl here counts as tracked, so a new one is leak-checked by default.
UNTRACKED_TELEMETRY = {ASKED_FILE}
METRICS_MAX_ROWS = 36
OPERATIONS_KEEP_FULL = 30
_OP_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class TelemetryFileError(Exception):
    """A tracked telemetry file can't be parsed, so rewriting it would lose rows."""


def _read_tracked_jsonl(path: Path) -> list[dict[str, Any]]:
    """Rows of a tracked file. A bad line stops the run: rewriting would drop it."""
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as e:
            raise TelemetryFileError(f"{_display(path)}:{number} is not valid JSON") from e
        if not isinstance(row, dict):
            raise TelemetryFileError(f"{_display(path)}:{number} is not a JSON object")
        rows.append(row)
    return rows


def _read_loose_jsonl(path: Path) -> list[dict[str, Any]]:
    """Rows of a log nobody rewrites here: unreadable lines are skipped."""
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(errors="replace") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_text(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def write_snapshot(stats: dict[str, Any], telemetry_dir: Path) -> None:
    """One row per day, oldest first, capped; a same-day re-run replaces that day's row."""
    path = telemetry_dir / METRICS_FILE
    rows = [r for r in _read_tracked_jsonl(path) if r.get("date") != stats["date"]]
    rows.append(stats)
    rows.sort(key=lambda r: str(r.get("date")))
    _write_jsonl(path, rows[-METRICS_MAX_ROWS:])


def roll_operations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Last ~30 entries in full; older ones become one `{month, count, ops}` row per month."""
    rollups = {r["month"]: r for r in rows if "month" in r}
    entries = [r for r in rows if "month" not in r]
    overflow = entries[:-OPERATIONS_KEEP_FULL] if len(entries) > OPERATIONS_KEEP_FULL else []
    for entry in overflow:
        month = str(entry.get("date"))[:7]
        rollup = rollups.setdefault(month, {"month": month, "count": 0, "ops": {}})
        op = str(entry.get("op"))
        rollup["count"] += 1
        rollup["ops"][op] = rollup["ops"].get(op, 0) + 1
    ordered = [rollups[m] for m in sorted(rollups)]
    return ordered + entries[len(overflow) :]
