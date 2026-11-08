"""The MCP tools over HTTP, for `librarian mcp` in remote mode (LIBRARIAN_API_KEY set).

    GET /api/tools                 the MCP tool names
    GET /api/tools/{name}?arg=...  run one: the same text the local stdio server returns

The tools come from the shared registry (`librarian.agent.tools`, MCP surface), so the remote
server and the local one answer the same. Every tool is read-only, hence GET: a read key is
enough. Arguments are the query string; pydantic coerces "10" and "true".
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse

from librarian.agent.tools import MCP, ToolContext, tools_for
from librarian.api.security import SignedIn

router = APIRouter()

_TOOLS = {t.name: t for t in tools_for(MCP) if t.read_only}


@router.get("/api/tools")
def list_tools(_: SignedIn) -> list[str]:
    return list(_TOOLS)


@router.get("/api/tools/{name}", response_class=PlainTextResponse)
def run_tool(name: str, request: Request, _: SignedIn) -> str:
    tool = _TOOLS.get(name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"No MCP tool named {name!r}.")
    return tool.run(dict(request.query_params), ToolContext(surface=MCP))
