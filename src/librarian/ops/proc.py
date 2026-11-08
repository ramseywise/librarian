"""Run external tools (`pg_dump`, `age`, `aws`, ...) with a clear error when one is missing or fails."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Mapping, Sequence

from librarian.log_config import get_logger

log = get_logger(__name__)

_TAIL_CHARS = 500


class OpsError(RuntimeError):
    """An operation failed in a way the operator should read; the message carries no secrets."""


def require(*tools: str) -> None:
    """OpsError naming every tool that is not on PATH."""
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        raise OpsError(f"required tool not found on PATH: {', '.join(missing)}")


def run(
    cmd: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
    timeout: float = 3600.0,
) -> subprocess.CompletedProcess[str]:
    """Run `cmd` (no shell). A non-zero exit raises OpsError with the tail of stderr.

    `env` is added to the current environment. It is where passwords go, never into `cmd`.
    """
    import os

    require(cmd[0])
    full_env = {**os.environ, **env} if env else None
    log.debug("ops.proc.run", tool=cmd[0], argc=len(cmd))
    try:
        done = subprocess.run(
            list(cmd), capture_output=True, text=True, timeout=timeout, check=False, env=full_env
        )
    except subprocess.TimeoutExpired as e:
        raise OpsError(f"{cmd[0]} timed out after {timeout:.0f}s") from e
    if done.returncode != 0:
        tail = (done.stderr or "").strip()[-_TAIL_CHARS:]
        raise OpsError(f"{cmd[0]} exited {done.returncode}: {tail}")
    return done
