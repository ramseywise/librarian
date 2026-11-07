"""Security headers: the API adds a CSP and friends, never clobbers a route's own CSP, and the
CSP hashes the real inline script of app/index.html. HSTS and proxying live in docker/Caddyfile."""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian.api.security import SecurityHeadersMiddleware, build_csp, inline_script_hashes

REPO = Path(__file__).resolve().parents[2]
EXPECTED = (
    "content-security-policy",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "x-frame-options",
)


def _client(csp: str = "default-src 'self'") -> TestClient:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, csp=csp)

    @app.get("/plain")
    def plain() -> PlainTextResponse:
        return PlainTextResponse("ok")

    @app.get("/asset")
    def asset() -> PlainTextResponse:
        return PlainTextResponse(
            "x", headers={"Content-Security-Policy": "sandbox", "X-Content-Type-Options": "nosniff"}
        )

    @app.get("/docs-like")
    def docs_like() -> PlainTextResponse:
        return PlainTextResponse("x")

    return TestClient(app)


def test_headers_added() -> None:
    res = _client("default-src 'self'").get("/plain")
    for name in EXPECTED:
        assert name in res.headers, name
    assert res.headers["content-security-policy"] == "default-src 'self'"
    assert res.headers["x-content-type-options"] == "nosniff"


def test_route_csp_is_not_overwritten() -> None:
    res = _client().get("/asset")
    assert res.headers.get_list("content-security-policy") == ["sandbox"]
    assert res.headers.get_list("x-content-type-options") == ["nosniff"]


def test_real_app_sends_headers_on_health() -> None:
    with TestClient(main_module.app) as client:
        res = client.get("/healthz")
    for name in EXPECTED:
        assert name in res.headers, name
    assert "frame-ancestors 'none'" in res.headers["content-security-policy"]


def test_csp_shape() -> None:
    csp = build_csp(["'sha256-abc'"])
    directives = dict(d.split(" ", 1) for d in csp.split("; "))
    assert directives["script-src"] == "'self' 'sha256-abc'"
    assert "'unsafe-inline'" not in directives["script-src"]
    assert directives["frame-ancestors"] == "'none'"
    assert directives["object-src"] == "'none'"
    assert "blob:" in directives["img-src"]


def test_hashes_cover_every_inline_script_of_the_app() -> None:
    html = (REPO / "app" / "index.html").read_text()
    bodies = [
        m.group(1)
        for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
        if m.group(1).strip()
    ]
    assert bodies, "app/index.html lost its inline theme script; revisit the CSP"
    want = {
        "'sha256-" + base64.b64encode(hashlib.sha256(b.encode()).digest()).decode() + "'"
        for b in bodies
    }
    assert set(inline_script_hashes(REPO / "app" / "index.html")) == want


def test_missing_index_gives_no_hashes(tmp_path: Path) -> None:
    assert inline_script_hashes(tmp_path / "nope.html") == []


def test_module_script_with_src_is_not_hashed(tmp_path: Path) -> None:
    page = tmp_path / "index.html"
    page.write_text('<script type="module" src="/a.js"></script><script>1+1</script>')
    assert len(inline_script_hashes(page)) == 1


@pytest.fixture()
def caddyfile() -> str:
    return (REPO / "docker" / "Caddyfile").read_text()


def test_caddyfile_has_hsts_sse_and_ws_proxy(caddyfile: str) -> None:
    assert "Strict-Transport-Security" in caddyfile
    assert "{$LIBRARIAN_DOMAIN:localhost}" in caddyfile
    assert re.search(
        r"handle /api/chat/stream \{\s*reverse_proxy librarian:8000 \{\s*flush_interval -1",
        caddyfile,
    )
    assert "reverse_proxy librarian:8000" in caddyfile


def test_caddyfile_leaves_csp_to_the_api(caddyfile: str) -> None:
    # A proxy-level CSP would overwrite the course asset CSP and miss the inline-script hash.
    code = "\n".join(line for line in caddyfile.splitlines() if not line.lstrip().startswith("#"))
    assert "Content-Security-Policy" not in code
