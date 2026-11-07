"""Librarian MCP Server

Exposes the compiled wiki and the course lessons in data/courses/ to any MCP client —
Claude Code, playground agents, or other tools. Read-only.

Tools:
  search_wiki          — hybrid search (FTS + semantic) over wiki pages, with course lessons
  read_page            — read a specific wiki page by filename or title
  list_domain          — list all pages in a domain directory
  list_pages           — list pages by domain tag, directory, or all
  get_domain_briefing  — return all pages in a domain as a structured reference briefing

This module is only the FastMCP setup; the wiki tools come from the shared registry
(`librarian.agent.tools`) and the code tools from `apps.mcp.codemap_tools`; indexing, ranking and rendering
live in `librarian.retrieval` (see its docstring), shared with the chat agent and the evals.

Usage:
    uv run librarian mcp [--rebuild]
"""

from __future__ import annotations

import inspect
from typing import Annotated, Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

from librarian import retrieval
from librarian.agent.tools import MCP, Tool, ToolContext, tools_for
from librarian.config import get_settings
from librarian.log_config import configure_logging, get_logger
from librarian.mcp.codemap_tools import register_codemap_tools
from librarian.retrieval import corpus, embeddings

load_dotenv(get_settings().dotenv_file)
configure_logging()  # installs the secret-redaction processor
log = get_logger(__name__)

mcp = FastMCP("librarian")


def _register(tool: Tool) -> None:
    """Expose a registry tool through FastMCP.

    FastMCP builds the schema from a function signature, so each tool gets a thin adapter
    whose signature is rebuilt from the tool's parameter model: one definition, same schema.
    """

    def adapter(**kwargs: Any) -> str:  # noqa: ANN401
        return tool.run(kwargs, ToolContext(surface=MCP))

    fields = {
        name: Annotated[f.annotation, Field(description=f.description)]
        for name, f in tool.params.model_fields.items()
    }
    required = {name for name, f in tool.params.model_fields.items() if f.is_required()}
    defaults = {name: f.default for name, f in tool.params.model_fields.items()}
    adapter.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        [
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=inspect.Parameter.empty if name in required else defaults[name],
                annotation=ann,
            )
            for name, ann in fields.items()
        ],
        return_annotation=str,
    )
    adapter.__annotations__ = fields | {"return": str}
    adapter.__name__ = tool.name
    adapter.__doc__ = tool.description
    mcp.tool(name=tool.name, description=tool.description)(adapter)


for _tool in tools_for(MCP):
    _register(_tool)

register_codemap_tools(mcp)


def main(argv: list[str] | None = None) -> int:
    """Run the MCP server over stdio; `--rebuild` drops and re-embeds the index instead."""
    import argparse

    ap = argparse.ArgumentParser(prog="librarian mcp", description="Wiki MCP server (stdio).")
    ap.add_argument(
        "--rebuild", action="store_true", help="force a full drop and re-embed of the index"
    )
    args = ap.parse_args(argv)
    if args.rebuild:
        print(retrieval.rebuild_index())
        return 0

    # The same read-only handle the API serves from. With no built index (or autobuild on, the
    # dev default) it builds one first; the stdio server has nothing to answer before it exists.
    handle = retrieval.IndexHandle(autobuild=get_settings().index_autobuild)
    handle.start(wait=True)
    retrieval.set_handle(handle)
    if handle.state != "ready":
        log.error("mcp_index_unavailable", **handle.status(), hint="run: librarian index build")

    log.info(
        "starting_mcp_server",
        wiki_dir=str(corpus.WIKI_DIR),
        courses_dir=str(corpus.COURSES_DIR),
        hybrid_search=embeddings.HAS_EMBEDDINGS,
    )
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
