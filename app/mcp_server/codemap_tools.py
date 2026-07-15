"""Codemap MCP tools — thin HTTP client over the Codemap Query API.

These tools never open the code-index DuckDB file directly: indexing runs
as a separate, centrally-owned process (see tools/codemap/), and this
module only queries it over HTTP. That split is what lets the index be
indexed centrally and queried by any number of MCP clients without each
one needing repo credentials or local write access.

Requires the Codemap Query API to be running (make codemap-api).
"""

from __future__ import annotations

import os

import httpx
import structlog
from fastmcp import FastMCP

log = structlog.get_logger()

CODEMAP_API_URL = os.environ.get("CODEMAP_API_URL", "http://localhost:8100")


def register_codemap_tools(mcp: FastMCP) -> None:
    """Register codemap tools on the given FastMCP instance."""

    @mcp.tool()
    def find_symbol(name: str, repo: str = "", limit: int = 20) -> str:
        """Find function/class/method symbols by name across indexed repos.

        Args:
            name:  Symbol name or substring to search for
            repo:  Optional repo slug to scope the search (see list_repos)
            limit: Max results (default 20)

        Returns:
            Matching symbols with kind, signature, file path, line range, and docstring.
        """
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

    @mcp.tool()
    def get_file_symbols(repo: str, rel_path: str) -> str:
        """List all symbols (functions/classes/methods) defined in one file.

        Args:
            repo:     Repo slug (see list_repos)
            rel_path: File path relative to the repo root, e.g. 'etl/manifest.py'

        Returns:
            Ordered list of symbols with kind, signature, and line range.
        """
        results = _get(f"/api/files/{repo}/{rel_path}/symbols", not_found_ok=True)
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

    @mcp.tool()
    def find_references(symbol_or_path: str, repo: str = "") -> str:
        """Find files that import a given file, or files defining a given symbol name.

        Args:
            symbol_or_path: A symbol name or a repo-relative file path
            repo:           Optional repo slug to scope the search

        Returns:
            Files/symbols that reference the target, ranked by edge weight.
        """
        results = _get("/api/references", {"symbol_or_path": symbol_or_path, "repo": repo})
        if results is None:
            return _api_down_message()
        if not results:
            return f"No references found for: {symbol_or_path!r}"

        lines = [
            f"- `{r['rel_path']}` (repo: {r['repo_id']}, weight: {r['weight']})" for r in results
        ]
        return f"{len(results)} reference(s) to {symbol_or_path!r}:\n\n" + "\n".join(lines)

    @mcp.tool()
    def repo_map(repo: str, limit: int = 50) -> str:
        """Return a ranked structural overview of a repo — most-referenced files first.

        Mirrors Aider's repo-map: a compact, high-signal orientation view for an
        agent starting work in an unfamiliar codebase, ranked by inbound import weight.

        Args:
            repo:  Repo slug (see list_repos)
            limit: Max files to include (default 50)

        Returns:
            Files ranked by inbound reference weight, each with its top symbols.
        """
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

    @mcp.tool()
    def find_callers(symbol_name: str, repo: str = "") -> str:
        """Find symbols that call a given symbol name, ranked by weight.

        Complements find_references (file-level, import-based) with
        function-level "who calls this" answers. Ambiguous callee names
        (e.g. multiple classes defining the same method name) fan out to
        multiple results rather than being silently dropped.

        Args:
            symbol_name: The called function/method name to look up
            repo:        Optional repo slug to scope the search

        Returns:
            Calling symbols with their kind, file, and edge weight.
        """
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

    @mcp.tool()
    def semantic_find_symbol(query: str, repo: str = "", limit: int = 10) -> str:
        """Fuzzy/conceptual symbol search using embeddings — a fallback for
        when find_symbol's exact/substring name match misses relevant results.

        Only available if the Codemap Query API was started in an environment
        with sentence-transformers installed (uv sync --extra api --extra codemap).
        Falls back to a clear message if unavailable — use find_symbol instead.

        Args:
            query: Natural-language or conceptual description of what to find
            repo:  Optional repo slug to scope the search
            limit: Max results (default 10)

        Returns:
            Symbols ranked by embedding cosine similarity to the query.
        """
        try:
            resp = httpx.get(
                f"{CODEMAP_API_URL}/api/symbols/semantic_search",
                params={"query": query, "repo": repo, "limit": limit},
                timeout=15.0,
            )
            if resp.status_code == 501:
                return (
                    "Semantic search is not available on this Codemap API instance — "
                    "try find_symbol instead."
                )
            resp.raise_for_status()
            results = resp.json()
        except httpx.HTTPError as e:
            log.warning(
                "codemap_tools.api_request_failed",
                path="/api/symbols/semantic_search",
                error=str(e),
            )
            return _api_down_message()

        if not results:
            return f"No semantically similar symbols found for: {query!r}"

        lines = [
            f"**{s['name']}** ({s['kind']}, score={s['score']})\n"
            f"File: `{s['file_id']}` lines {s['start_line']}-{s['end_line']}\n"
            f"Signature: `{s['signature']}`"
            for s in results
        ]
        return (
            f"Found {len(results)} semantically similar symbol(s):\n\n" + "\n\n---\n\n".join(lines)
        )

    @mcp.tool()
    def list_repos() -> str:
        """List all repos currently indexed by codemap, with last-indexed timestamp.

        Returns:
            Repo slugs, root paths, languages, and staleness (last_indexed_at).
        """
        results = _get("/api/repos")
        if results is None:
            return _api_down_message()
        if not results:
            return (
                "No repos indexed yet. Configure tools/codemap/repos.txt and run: "
                "make codemap-reindex"
            )

        lines = [
            f"- **{r['repo_id']}** (`{r['root_path']}`) · {r['language']} "
            f"· last indexed {r['last_indexed_at']}"
            for r in results
        ]
        return f"{len(results)} indexed repo(s):\n\n" + "\n".join(lines)


def _get(path: str, params: dict | None = None, not_found_ok: bool = False) -> list | None:
    try:
        resp = httpx.get(f"{CODEMAP_API_URL}{path}", params=params, timeout=10.0)
        if not_found_ok and resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        log.warning("codemap_tools.api_request_failed", path=path, error=str(e))
        return None


def _api_down_message() -> str:
    return (
        f"Codemap Query API unreachable at {CODEMAP_API_URL}. "
        "Start it with: make codemap-api"
    )
