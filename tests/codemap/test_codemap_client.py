"""The codemap tools in the registry: MCP and /api/tools only, read-only, same text as before."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable

import httpx
import pytest

from librarian.agent.tools import CHAT, MCP, ToolContext, tools_for
from librarian.tools.codemap import client

NAMES = [
    "find_symbol",
    "get_file_symbols",
    "find_references",
    "repo_map",
    "find_callers",
    "semantic_find_symbol",
    "list_repos",
]

SYMBOL = {
    "name": "load",
    "kind": "function",
    "file_id": "r:a.py",
    "start_line": 1,
    "end_line": 3,
    "signature": "def load()",
    "docstring": "Loads.",
    "score": 0.9,
}


def _serve(
    monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], httpx.Response]
) -> list[httpx.Request]:
    seen: list[httpx.Request] = []

    def wrapped(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    monkeypatch.setattr(client, "transport", httpx.MockTransport(wrapped))
    return seen


def _run(name: str, args: dict) -> str:
    return tools_for(MCP, [name])[0].run(args, ToolContext(surface=MCP))


def test_codemap_tools_are_mcp_only_read_only_and_modelled() -> None:
    assert {t.name for t in tools_for(MCP)} >= set(NAMES)
    assert not {t.name for t in tools_for(CHAT)} & set(NAMES)
    for tool in tools_for(MCP, NAMES):
        assert tool.read_only is True
        assert tool.remote_proxy is False
        assert tool.input_schema["type"] == "object"


def test_schemas_keep_the_parameters_the_hand_registered_tools_had() -> None:
    def props(name: str) -> tuple[list[str], list[str]]:
        schema = tools_for(MCP, [name])[0].input_schema
        return list(schema["properties"]), schema.get("required", [])

    assert props("find_symbol") == (["name", "repo", "limit"], ["name"])
    assert props("get_file_symbols") == (["repo", "rel_path"], ["repo", "rel_path"])
    assert props("find_references") == (["symbol_or_path", "repo"], ["symbol_or_path"])
    assert props("repo_map") == (["repo", "limit"], ["repo"])
    assert props("find_callers") == (["symbol_name", "repo"], ["symbol_name"])
    assert props("semantic_find_symbol") == (["query", "repo", "limit"], ["query"])
    assert props("list_repos") == ([], [])


def test_mcp_server_serves_the_same_seven_names() -> None:
    # A subprocess for the same reason as in test_agent_tools: the server configures logging.
    code = (
        "import asyncio, json; from librarian.mcp.server import mcp; "
        "print(json.dumps([t.name for t in asyncio.run(mcp.list_tools())]))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout
    assert set(NAMES) <= set(json.loads(out))


def test_find_symbol_formats_and_passes_query(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _serve(monkeypatch, lambda r: httpx.Response(200, json=[SYMBOL]))
    text = _run("find_symbol", {"name": "load"})
    assert text == (
        "Found 1 symbol(s):\n\n**load** (function)\nFile: `r:a.py` lines 1-3\n"
        "Signature: `def load()`\nDoc: Loads."
    )
    assert dict(seen[0].url.params) == {"name": "load", "repo": "", "limit": "20"}


def test_empty_and_unreachable_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    _serve(monkeypatch, lambda r: httpx.Response(200, json=[]))
    assert _run("find_symbol", {"name": "zz"}) == "No symbols found for: 'zz'"
    assert _run("list_repos", {}).startswith("No repos indexed yet.")

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    _serve(monkeypatch, down)
    assert _run("repo_map", {"repo": "r"}).startswith("Codemap Query API unreachable at ")


def test_semantic_search_reports_unavailable_on_501(monkeypatch: pytest.MonkeyPatch) -> None:
    _serve(monkeypatch, lambda r: httpx.Response(501))
    assert "not available on this Codemap API instance" in _run(
        "semantic_find_symbol", {"query": "loader"}
    )


def test_file_symbols_404_is_empty_and_path_cannot_climb(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _serve(monkeypatch, lambda r: httpx.Response(404))
    assert _run("get_file_symbols", {"repo": "r", "rel_path": "etl/m.py"}) == (
        "No symbols found in r:etl/m.py"
    )
    assert seen[0].url.path == "/api/files/r/etl/m.py/symbols"
    _run("get_file_symbols", {"repo": "../x", "rel_path": "../../etc/passwd"})
    assert ".." not in seen[1].url.raw_path.decode().split("/")


def test_bad_arguments_come_back_as_text() -> None:
    assert _run("repo_map", {"limit": 3}).startswith("Invalid arguments for repo_map")
