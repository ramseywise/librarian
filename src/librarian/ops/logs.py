"""Retention for the agent log (`logs/agent.jsonl`): drop lines older than the window.

The file holds each answer's query text and user id (personal data), so it is not kept forever.
Only that one file under the logs directory is touched: never `data/raw/`, never `data/wiki/`,
and not the other logs (retrieval telemetry rotates by size in `retrieval.corpus`).

The prune rewrites the file through a temporary sibling and an atomic rename. It takes a lock
file so two workers do not rewrite at once, and it copies back any line appended while it ran,
so the only loss window is the instant between that copy and the rename. Lines it cannot read
(no valid `ts`) are kept: it deletes only what it can prove is old.
"""

from __future__ import annotations

import contextlib
import fcntl
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from librarian.log_config import get_logger

log = get_logger(__name__)

# The same name `librarian.agent.loop.AGENT_LOG_NAME` writes (ops sits below agent in the layers).
AGENT_LOG_NAME = "agent.jsonl"
_LOCK_NAME = ".agent.jsonl.prune.lock"


@dataclass(frozen=True)
class PruneResult:
    removed: int
    kept: int
    unreadable: int  # kept lines with no usable timestamp
    skipped: bool = False  # another prune held the lock


def _line_ts(line: bytes) -> datetime | None:
    import json

    try:
        row = json.loads(line)
        ts = datetime.fromisoformat(str(row["ts"]))
    except (ValueError, KeyError, TypeError):
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)


def prune_agent_log(
    logs_dir: Path, days: int, *, now: datetime | None = None, dry_run: bool = False
) -> PruneResult:
    """Remove `agent.jsonl` lines older than `days` days. `days < 1` keeps everything."""
    path = logs_dir / AGENT_LOG_NAME
    if days < 1 or not path.is_file():
        return PruneResult(0, 0, 0)
    cutoff = (now or datetime.now(UTC)) - timedelta(days=days)
    with (logs_dir / _LOCK_NAME).open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return PruneResult(0, 0, 0, skipped=True)
        return _prune_locked(path, cutoff, dry_run)


def _prune_locked(path: Path, cutoff: datetime, dry_run: bool) -> PruneResult:
    data = path.read_bytes()
    end = data.rfind(b"\n") + 1  # a half-written last line is left for the next run
    keep: list[bytes] = []
    removed = unreadable = 0
    for line in data[:end].splitlines(keepends=True):
        ts = _line_ts(line)
        if ts is not None and ts < cutoff:
            removed += 1
            continue
        if ts is None and line.strip():
            unreadable += 1
        keep.append(line)
    result = PruneResult(removed, len(keep), unreadable)
    if removed == 0 or dry_run:
        return result
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".agent.jsonl.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            out.writelines(keep)
            with path.open("rb") as src:  # lines appended since the read
                src.seek(end)
                out.write(src.read())
            out.flush()
            os.fsync(out.fileno())
        tmp.chmod(path.stat().st_mode & 0o777)
        tmp.replace(path)
    except BaseException:
        with contextlib.suppress(OSError):
            tmp.unlink()
        raise
    log.info("agent_log.pruned", removed=removed, kept=len(keep))
    return result
