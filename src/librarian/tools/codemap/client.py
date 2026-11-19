"""Codemap tools — a thin HTTP client over the Codemap Query API.

These functions never open the code-index DuckDB file directly: indexing runs as a separate,
centrally-owned process (see this package), and the tools only query it over HTTP. That split
lets the index be built centrally and queried by any number of MCP clients without each one
needing repo credentials or local write access. Every call is a GET, so every tool is read-only.

The registry (`librarian.agent.tools`) wraps these as the seven codemap tools, offered on the
MCP surface and `/api/tools` but not to the chat agent. Requires the Codemap Query API to be
running (make codemap-api); `CODEMAP_API_URL` says where, read on each call.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx
import structlog

from librarian.config import get_settings

log = structlog.get_logger()

# Tests replace this with an httpx.MockTransport; None is the real network.
transport: httpx.BaseTransport | None = None


def _base() -> str:
    return get_settings().codemap_api_url


def _fetch(path: str, params: dict[str, Any] | None, timeout: float) -> httpx.Response:
    with httpx.Client(timeout=timeout, transport=transport) as client:
        return client.get(f"{_base()}{path}", params=params)


def _get(path: str, params: dict | None = None, not_found_ok: bool = False) -> list | None:
    try:
        resp = _fetch(path, params, 10.0)
        if not_found_ok and resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.warning("codemap_tools.api_request_failed", path=path, error=str(e))
        return None


def _api_down_message() -> str:
    return f"Codemap Query API unreachable at {_base()}. Start it with: make codemap-api"


def _file_path(repo: str, rel_path: str) -> str:
    """URL path for one file's symbols. The tool is reachable over `/api/tools`, so a repo or
    file name must not be able to climb out of `/api/files/`: `..` segments are encoded away."""
    segs = ["%2E%2E" if s == ".." else quote(s, safe="") for s in rel_path.split("/")]
    return f"/api/files/{quote(repo, safe='')}/{'/'.join(segs)}/symbols"


def find_symbol(name: str, repo: str, limit: int) -> str:
    results = _get("/api/symbols/find", {"name": name, "repo": repo, "limit": limit})
    if results is None:
        return _api_down_message()
    if not results:
        return f"No symbols found for: {name!r}"

    lines = []
    for s in results:
        lines.append(
            f"**{s['name']}** ({s['kind']})\n"
            f"File: `{s['file_id']}` lines {s['start_line']}-{s['end_line']}\n"
            f"Signature: `{s['signature']}`\n"
            + (f"Doc: {s['docstring']}" if s["docstring"] else "")
        )
    return f"Found {len(results)} symbol(s):\n\n" + "\n\n---\n\n".join(lines)


def get_file_symbols(repo: str, rel_path: str) -> str:
    results = _get(_file_path(repo, rel_path), not_found_ok=True)
    if results is None:
        return _api_down_message()
    if not results:
        return f"No symbols found in {repo}:{rel_path}"

    lines = [
        f"- **{s['name']}** ({s['kind']}) lines {s['start_line']}-{s['end_line']}"
        + (f" — {s['docstring']}" if s["docstring"] else "")
        for s in results
    ]
    return f"{len(results)} symbol(s) in `{repo}:{rel_path}`:\n\n" + "\n".join(lines)


def find_references(symbol_or_path: str, repo: str) -> str:
    results = _get("/api/references", {"symbol_or_path": symbol_or_path, "repo": repo})
    if results is None:
        return _api_down_message()
    if not results:
        return f"No references found for: {symbol_or_path!r}"

    lines = [f"- `{r['rel_path']}` (repo: {r['repo_id']}, weight: {r['weight']})" for r in results]
    return f"{len(results)} reference(s) to {symbol_or_path!r}:\n\n" + "\n".join(lines)


def repo_map(repo: str, limit: int) -> str:
    results = _get("/api/repo_map", {"repo": repo, "limit": limit})
    if results is None:
        return _api_down_message()
    if not results:
        return f"No indexed files found for repo: {repo!r}"

    lines = []
    for f in results:
        syms = ", ".join(f"{s['name']} ({s['kind']})" for s in f["symbols"][:6])
        lines.append(f"- `{f['rel_path']}` (↑{f['inbound_weight']}) — {syms}")
    return f"Repo map for {repo!r} ({len(results)} files):\n\n" + "\n".join(lines)


def find_callers(symbol_name: str, repo: str) -> str:
    results = _get("/api/callers", {"symbol_name": symbol_name, "repo": repo})
    if results is None:
        return _api_down_message()
    if not results:
        return f"No callers found for: {symbol_name!r}"

    lines = [
        f"- **{r['caller_name'] or '(module-level)'}** ({r['caller_kind'] or 'call'}) "
        f"in `{r['rel_path']}` (repo: {r['repo_id']}, weight: {r['weight']})"
        for r in results
    ]
    return f"{len(results)} caller(s) of {symbol_name!r}:\n\n" + "\n".join(lines)


def semantic_find_symbol(query: str, repo: str, limit: int) -> str:
    path = "/api/symbols/semantic_search"
    try:
        resp = _fetch(path, {"query": query, "repo": repo, "limit": limit}, 15.0)
        if resp.status_code == 501:
            return (
                "Semantic search is not available on this Codemap API instance — "
                "try find_symbol instead."
            )
        resp.raise_for_status()
        results = resp.json()
    except httpx.HTTPError as e:
        log.warning("codemap_tools.api_request_failed", path=path, error=str(e))
        return _api_down_message()

    if not results:
        return f"No semantically similar symbols found for: {query!r}"

    lines = [
        f"**{s['name']}** ({s['kind']}, score={s['score']})\n"
        f"File: `{s['file_id']}` lines {s['start_line']}-{s['end_line']}\n"
        f"Signature: `{s['signature']}`"
        for s in results
    ]
    return f"Found {len(results)} semantically similar symbol(s):\n\n" + "\n\n---\n\n".join(lines)


def list_repos() -> str:
    results = _get("/api/repos")
    if results is None:
        return _api_down_message()
    if not results:
        return (
            "No repos indexed yet. Configure src/librarian/tools/codemap/repos.txt and run: "
            "make codemap-reindex"
        )

    lines = [
        f"- **{r['repo_id']}** (`{r['root_path']}`) · {r['language']} "
        f"· last indexed {r['last_indexed_at']}"
        for r in results
    ]
    return f"{len(results)} indexed repo(s):\n\n" + "\n".join(lines)
