"""Librarian MCP Server

Exposes the compiled wiki and the course lessons in data/courses/ to any MCP client —
Claude Code, playground agents, or other tools. Read-only.

Tools:
  search_wiki          — hybrid search (FTS + semantic) over wiki pages, with course lessons
  read_page            — read a specific wiki page by filename or title
  list_domain          — list all pages in a domain directory
  list_pages           — list pages by domain tag, directory, or all
  get_domain_briefing  — return all pages in a domain as a structured reference briefing

This module is only the FastMCP setup and the tool wrappers; indexing, ranking and rendering
live in `librarian.retrieval` (see its docstring), shared with the chat agent and the evals.

Usage:
    uv run librarian mcp [--rebuild]
"""

from __future__ import annotations

from dotenv import load_dotenv
from fastmcp import FastMCP

from librarian import retrieval
from librarian.config import get_settings
from librarian.log_config import configure_logging, get_logger
from librarian.mcp.codemap_tools import register_codemap_tools
from librarian.retrieval import corpus, embeddings

load_dotenv(get_settings().dotenv_file)
configure_logging()  # installs the secret-redaction processor
log = get_logger(__name__)

mcp = FastMCP("librarian")


@mcp.tool()
def search_wiki(query: str, domain: str = "", limit: int = 10, expand: bool = False) -> str:
    """Search the wiki and course lessons using hybrid search (BM25 + semantic).

    Results are ranked by an equal blend of BM25 relevance and semantic closeness
    (if sentence-transformers is installed). Backlinks are not a ranking signal.

    Args:
        query:  Search terms
        domain: Optional domain to scope the search — any directory under
                data/wiki/ (e.g. 'rag', 'langgraph', 'patterns') or a domain tag.
                'course' searches all course lessons, 'course/<subject>' one course
                (e.g. 'course/ai-engineering'). Omitted: results are ranked wiki pages,
                followed by a short separate list of the best-matching lessons.
        limit:  Max results (default 10)
        expand: SPIKE — also return pages one typed relationship hop from the
                results (`prerequisite-for` / `extends`). Answers "what else do
                I need to understand these hits?" Off by default.

    Returns:
        Matching pages with title, summary, path, backlink count, and a snippet.
        Leads with a warning line when retrieval ran degraded (full-text search
        unavailable, or the index is behind the files on disk).
    """
    return retrieval.search(query, domain=domain, limit=limit, expand=expand)


@mcp.tool()
def read_page(path_or_title: str) -> str:
    """Read a specific wiki page or course lesson by file path or title.

    Args:
        path_or_title: A relative path like 'data/wiki/rag/rag-retrieval-strategies.md',
                       a page title like 'RAG Retrieval Strategies', or a lesson as
                       'course/<subject>/<module>/<lesson>.md'. Titles resolve to wiki pages only.

    Returns:
        Full page content, or an error message if not found.
    """
    return retrieval.read_page(path_or_title)


@mcp.tool()
def list_domain(domain: str) -> str:
    """List all pages in a domain directory, ordered by backlink count.

    This is an O(1) filesystem operation — no embedding or search needed.

    Args:
        domain: Domain directory name — any directory under data/wiki/
                (e.g. rag, langgraph, context, interview). 'course' lists the courses,
                'course/<subject>' its modules, 'course/<subject>/<module>' its lessons.

    Returns:
        All pages in the domain with title, tags, summary, and backlink count.
    """
    return retrieval.list_domain(domain)


@mcp.tool()
def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages and course lessons, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        directory: Subdirectory to list — any domain directory under data/wiki/
                   (e.g. rag, langgraph, context, interview), or 'course' or
                   'course/<subject>' for lessons. Omitted: the wiki, then all lessons.

    Returns:
        List of pages with title, tags, summary, and backlink count.
    """
    return retrieval.list_pages(tag=tag, directory=directory)


@mcp.tool()
def get_domain_briefing(domain: str) -> str:
    """Return a structured build briefing for a domain — all pages concatenated.

    Use this before starting work in a domain to load all accumulated patterns,
    decisions, and tradeoffs into context.

    Args:
        domain: Domain directory name — any directory under data/wiki/
                (e.g. rag, langgraph, context, interview)

                'course/<subject>/<module>' briefs one course module. Larger course scopes
                are refused when they exceed COURSE_BRIEFING_MAX_CHARS.

    Returns:
        Full content of all pages in the domain, ordered: decisions → patterns → concepts.
    """
    return retrieval.domain_briefing(domain)


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
        retrieval.rebuild_index()
        return 0

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
