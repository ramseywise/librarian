"""Skip e2e tests whose live server isn't up, instead of failing with ConnectError.

Each module names the server it needs as `BASE` (API) or `UI_URL` (frontend).
`make test-e2e` with `make app` running still exercises everything.
"""

from __future__ import annotations

import socket
from functools import cache
from urllib.parse import urlparse

import pytest


@cache
def _reachable(url: str) -> bool:
    u = urlparse(url)
    try:
        with socket.create_connection((u.hostname or "localhost", u.port or 80), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.fixture(autouse=True)
def _require_live_server(request: pytest.FixtureRequest) -> None:
    url = getattr(request.module, "BASE", None) or getattr(request.module, "UI_URL", None)
    if url and not _reachable(url):
        pytest.skip(f"{url} not reachable — start it (make app) to run e2e tests")
