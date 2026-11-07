"""The shared tool registry: well-formed definitions, one set of names for chat and MCP."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter

import jsonschema
import pytest

from librarian.agent import tools
from librarian.agent.tools import CHAT, MCP, TOOLS, Tool, ToolContext, tools_for


def test_registry_is_not_empty_and_covers_both_surfaces() -> None:
    assert tools_for(CHAT)
    assert tools_for(MCP)


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: f"{sorted(t.surfaces)[0]}:{t.name}")
def test_every_tool_is_well_formed(tool: Tool) -> None:
    assert tool.name
    assert tool.description.strip()
    assert callable(tool.fn)
    assert tool.surfaces <= {CHAT, MCP}
    assert tool.read_only is True  # no write tools exist
    schema = tool.input_schema
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["type"] == "object"
    assert tool.log_arg in schema["properties"]
    assert "title" not in schema
    assert all("title" not in spec for spec in schema["properties"].values())
    spec = tool.anthropic_spec()
    assert set(spec) == {"name", "description", "input_schema"}


@pytest.mark.parametrize("surface", [CHAT, MCP])
def test_names_are_unique_per_surface(surface: str) -> None:
    names = [t.name for t in tools_for(surface)]
    assert len(names) == len(set(names))


def test_chat_and_mcp_expose_the_same_shared_tools() -> None:
    chat = {t.name for t in tools_for(CHAT)}
    mcp_names = {t.name for t in tools_for(MCP)}
    shared = {"search_wiki", "read_page", "get_domain_briefing"}
    assert shared <= chat
    assert shared <= mcp_names
    # Counts of each name across the whole registry: at most one variant per surface.
    assert max(Counter(t.name for t in TOOLS).values()) <= 2


def test_mcp_server_registers_the_registry_tools() -> None:
    # A subprocess: importing the server calls configure_logging(), which would leave
    # structlog caching loggers for the rest of this test session.
    code = (
        "import asyncio, json; from librarian.mcp.server import mcp; "
        "print(json.dumps([t.name for t in asyncio.run(mcp.list_tools())]))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout
    served = set(json.loads(out.strip().splitlines()[-1]))
    assert {t.name for t in tools_for(MCP)} <= served
    assert {t.name for t in tools_for(CHAT)} & {t.name for t in tools_for(MCP)} <= served


def test_tools_for_rejects_unknown_names() -> None:
    with pytest.raises(KeyError):
        tools_for(CHAT, ["no_such_tool"])
    assert [t.name for t in tools_for(CHAT, ["read_page"])] == ["read_page"]


def test_run_reports_bad_arguments_as_text() -> None:
    [tool] = tools_for(CHAT, ["read_page"])
    assert tool.run({}, ToolContext()).startswith("Invalid arguments for read_page")


def test_chat_schema_matches_the_old_hand_written_one() -> None:
    [tool] = tools_for(CHAT, ["search_wiki"])
    assert tool.input_schema == {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query using key terms from the question",
            }
        },
        "required": ["query"],
    }
    assert tools.MAX_BRIEFING_CHARS == 40_000
