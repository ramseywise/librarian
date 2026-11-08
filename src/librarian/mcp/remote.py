"""Remote mode for `librarian mcp`: the wiki tools answered by a deployed API.

With LIBRARIAN_API_KEY set, each tool call is `GET {LIBRARIAN_API_URL}/api/tools/<name>` with
the key as a bearer token, and nothing local is opened: no index, no wiki files. The API runs
the same registry tool (`librarian.api.routers.tools`), so the answer is the same text. Failures
come back as text too, so the MCP client sees why rather than a protocol error.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from librarian.config import Settings
from librarian.log_config import get_logger

log = get_logger(__name__)

TIMEOUT_S = 60.0  # a domain briefing can be large
# Tests replace this with an httpx.MockTransport; None is the real network.
transport: httpx.BaseTransport | None = None


def call(settings: Settings, name: str, args: Mapping[str, Any]) -> str:
    """Run tool `name` on the API; the response text, or a one-line reason it failed."""
    base = settings.remote_api_url.rstrip("/")
    params = {k: str(v).lower() if isinstance(v, bool) else v for k, v in args.items()}
    try:
        with httpx.Client(timeout=TIMEOUT_S, transport=transport) as client:
            resp = client.get(
                f"{base}/api/tools/{name}",
                params=params,
                headers={"Authorization": f"Bearer {settings.remote_api_key}"},
            )
    except httpx.HTTPError as e:
        log.warning("mcp.remote.unreachable", url=base, error=str(e))
        return f"Librarian API unreachable at {base}: {e}"
    if resp.status_code == 401:
        return "The Librarian API refused LIBRARIAN_API_KEY (unknown or revoked key)."
    if resp.status_code != 200:
        log.warning("mcp.remote.failed", tool=name, status=resp.status_code)
        return f"The Librarian API answered {resp.status_code} for {name}."
    return resp.text
