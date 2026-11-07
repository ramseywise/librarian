"""The built image, from outside: the auth gate, the probes and the bundled UI.

Run by `make e2e-container` and the `e2e-container` CI job, which start the image with a token
(E2E_TOKEN) on E2E_API_URL; skipped when nothing answers there. Every request is anonymous or
carries the token explicitly, so this file also passes against a server with no token only for
the "serves the UI" checks, and fails loudly on the 401 ones: it tests a deployment, not dev.
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("E2E_API_URL", "http://localhost:8000")
TOKEN = os.environ.get("E2E_TOKEN", "")

pytestmark = pytest.mark.e2e

# Read routes under /api, one per router, so a router left out of the auth dependency shows here.
API_ROUTES = ["/api/graph", "/api/wiki/health", "/api/courses/practice", "/api/graph/curriculum"]


def _auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture(scope="module", autouse=True)
def _need_token() -> None:
    if not TOKEN:
        pytest.skip("E2E_TOKEN not set: this file tests a server that requires a token")


def test_probes_are_open() -> None:
    assert httpx.get(f"{BASE}/healthz", timeout=10).status_code == 200
    r = httpx.get(f"{BASE}/readyz", timeout=30)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "ready"


@pytest.mark.parametrize("route", API_ROUTES)
def test_api_without_token_is_401(route: str) -> None:
    r = httpx.get(f"{BASE}{route}", timeout=30)
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_api_with_wrong_token_is_401() -> None:
    r = httpx.get(f"{BASE}/api/graph", headers={"Authorization": "Bearer nope"}, timeout=30)
    assert r.status_code == 401


@pytest.mark.parametrize("route", API_ROUTES)
def test_api_with_token_is_200(route: str) -> None:
    r = httpx.get(f"{BASE}{route}", headers=_auth(), timeout=60)
    assert r.status_code == 200, r.text


def test_graph_has_pages() -> None:
    r = httpx.get(f"{BASE}/api/graph", headers=_auth(), timeout=60)
    assert len(r.json()["nodes"]) > 0


def test_root_serves_the_ui_without_a_token() -> None:
    r = httpx.get(f"{BASE}/", timeout=10)
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert '<div id="root"' in r.text


def test_private_content_is_absent() -> None:
    """The tmpfs masks hide data/wiki/private and data/courses/private from the container."""
    r = httpx.get(f"{BASE}/api/graph", headers=_auth(), timeout=60)
    ids = {n["data"].get("id", "") for n in r.json()["nodes"]}
    assert not any("private/" in i for i in ids)
