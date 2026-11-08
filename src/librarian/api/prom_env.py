"""Multiprocess setup for the Prometheus client. Imports no `prometheus_client`.

`prometheus_client` reads `PROMETHEUS_MULTIPROC_DIR` once, when it is first imported, so the
variable has to be in the environment before any worker imports `librarian.api.prom`. `librarian
api` (the supervisor, which spawns the workers) calls `prepare` before `uvicorn.run`; the workers
inherit the variable. The supervisor is the only caller: a worker that wiped the directory would
erase its siblings' counters.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from librarian.config import Settings

ENV_VAR = "PROMETHEUS_MULTIPROC_DIR"


def prepare(settings: Settings, workers: int) -> Path | None:
    """With `--workers N` (N > 1) and metrics on, point the client at an empty directory.

    Returns the directory, or None when metrics are off or one process serves everything (the
    default registry is then exact). An operator-set PROMETHEUS_MULTIPROC_DIR is respected but
    still emptied: files from a previous run would add their counts to this one.
    """
    if not settings.metrics_token or workers < 2:
        return None
    # Not under var/: replicas (`--scale librarian=N`) share that volume, and each supervisor
    # empties its directory at start, which would erase a sibling's counters.
    path = Path(os.environ.get(ENV_VAR) or Path(tempfile.gettempdir()) / "librarian-prometheus")
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    os.environ[ENV_VAR] = str(path)
    return path
