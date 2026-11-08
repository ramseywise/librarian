"""Run an operation; on failure log it and email the owner, then return None for the exit code."""

from __future__ import annotations

from collections.abc import Callable

from librarian.config import Settings, get_release
from librarian.log_config import get_logger
from librarian.ops.alert import send_alert
from librarian.ops.proc import OpsError

log = get_logger(__name__)


def run_with_alert[T](settings: Settings, name: str, op: Callable[[], T]) -> T | None:
    """`op()`'s result, or None after alerting. The caller decides the exit code from None."""
    try:
        return op()
    except OpsError as e:
        reason = str(e)
    except Exception as e:  # a failed backup must alert whatever broke; the type goes in the log
        log.exception("ops.failed", op=name)
        reason = f"{type(e).__name__} (details are in the container log)"
    log.error("ops.failed", op=name, error=reason)
    send_alert(
        settings,
        f"Librarian {name} failed",
        f"The {name} job failed on release {get_release()}.\n\n{reason}\n",
    )
    return None
