"""`ops schedule`: the loop the compose `backup` service runs, one backup a day at a fixed UTC time."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from librarian.config import Settings
from librarian.log_config import get_logger
from librarian.ops.backup import run_backup
from librarian.ops.runner import run_with_alert

log = get_logger(__name__)


def next_run(now: datetime, at: str) -> datetime:
    """The next `HH:MM` UTC strictly after `now`."""
    hour, minute = (int(p) for p in at.split(":"))
    candidate = now.astimezone(UTC).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return candidate if candidate > now else candidate + timedelta(days=1)


def loop(
    settings: Settings,
    *,
    once: bool = False,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> None:
    """Sleep to the next slot, back up, repeat. A failed backup alerts and the loop carries on."""
    while True:
        due = next_run(clock(), settings.backup_at)
        wait = (due - clock()).total_seconds()
        log.info("ops.schedule.wait", next=due.isoformat(), seconds=round(wait))
        sleep(max(wait, 0.0))
        run_with_alert(settings, "backup", lambda: run_backup(settings))
        if once:
            return
