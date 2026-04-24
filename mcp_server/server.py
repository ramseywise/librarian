"""Librarian MCP Server

Exposes the compiled wiki to any MCP client — Claude Code, playground agents,
or other tools. Read-only.

Tools:
  search_wiki   — full-text search over wiki/ pages
  read_page     — read a specific wiki page by filename or title
  list_pages    — list pages by tag, directory, or all

Usage:
    uv run python mcp_server/server.py
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()
log = structlog.get_logger()

WIKI_DIR = Path("wiki")
DB_PATH = Path(".wiki_index.duckdb")

mcp = FastMCP("librarian")


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------


def build_index(con: duckdb.DuckDBPyConnection) -> None:
    """Build or rebuild the DuckDB FTS index over wiki/ pages."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            path      TEXT PRIMARY KEY,
            title     TEXT,
            tags      TEXT,
            summary   TEXT,
            updated   TEXT,
            content   TEXT
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS pages_path ON pages (path)")

    # Install and load FTS extension
    try:
        con.execute("INSTALL fts")
        con.execute("LOAD fts")
    except Exception:
        pass  # already installed

    pages = list(WIKI_DIR.rglob("*.md"))
    rows = []
    for page in pages:
        if page.name.startswith("."):
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        rows.append((
            str(page),
            meta.get("title", page.stem),
            " ".join(meta.get("tags", [])),
            meta.get("summary", ""),
            meta.get("updated", ""),
            text,
        ))

    con.executemany(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    log.info("index_built", page_count=len(rows))


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter (basic — handles our known fields)."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()
    meta: dict = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if key == "tags":
            # Parse [tag1, tag2] or bare list
            meta["tags"] = re.findall(r"[\w-]+", val)
        else:
            meta[key] = val.strip("\"'")
    return meta


def get_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(DB_PATH))
    build_index(con)
    return con


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_wiki(query: str, tag: str = "", limit: int = 10) -> str:
    """Search the wiki with full-text search.

    Args:
        query: Search terms
        tag:   Optional domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        limit: Max results (default 10)

    Returns:
        Matching pages with title, summary, path, and a snippet.
    """
    con = get_con()

    sql = """
        SELECT path, title, tags, summary, content
        FROM pages
        WHERE (
            lower(content) LIKE '%' || lower(?) || '%'
            OR lower(title) LIKE '%' || lower(?) || '%'
            OR lower(summary) LIKE '%' || lower(?) || '%'
        )
        {tag_filter}
        ORDER BY
            CASE WHEN lower(title) LIKE '%' || lower(?) || '%' THEN 0 ELSE 1 END,
            updated DESC
        LIMIT ?
    """.format(
        tag_filter="AND lower(tags) LIKE '%' || lower(?) || '%'" if tag else ""
    )

    params: list = [query, query, query]
    if tag:
        params.append(tag)
    params += [query, limit]

    rows = con.execute(sql, params).fetchall()
    con.close()

    if not rows:
        return f"No wiki pages found for: {query!r}" + (f" (tag: {tag})" if tag else "")

    results = []
    for path, title, tags, summary, content in rows:
        # Extract a snippet around the first match
        idx = content.lower().find(query.lower())
        snippet = ""
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(content), idx + 160)
            snippet = content[start:end].replace("\n", " ").strip()

        results.append(
            f"**{title}**\n"
            f"Path: `{path}`\n"
            f"Tags: {tags}\n"
            f"Summary: {summary}\n"
            + (f"Snippet: ...{snippet}..." if snippet else "")
        )

    return f"Found {len(rows)} result(s):\n\n" + "\n\n---\n\n".join(results)


@mcp.tool()
def read_page(path_or_title: str) -> str:
    """Read a specific wiki page by file path or title.

    Args:
        path_or_title: Either a relative path like 'wiki/concepts/foo.md'
                       or a page title like 'Google ADK Overview'

    Returns:
        Full page content, or an error message if not found.
    """
    # Try direct path first
    candidate = Path(path_or_title)
    if candidate.exists():
        return candidate.read_text(encoding="utf-8")

    # Try under wiki/
    wiki_candidate = WIKI_DIR / path_or_title
    if wiki_candidate.exists():
        return wiki_candidate.read_text(encoding="utf-8")

    # Fuzzy title match
    slug = re.sub(r"[^a-z0-9]+", "-", path_or_title.lower()).strip("-")
    matches = list(WIKI_DIR.rglob(f"*{slug}*.md"))
    if not matches:
        # Try any word
        words = path_or_title.lower().split()
        for word in words:
            matches = list(WIKI_DIR.rglob(f"*{word}*.md"))
            if matches:
                break

    if not matches:
        return f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    if len(matches) == 1:
        return matches[0].read_text(encoding="utf-8")

    # Multiple matches — return list
    paths = "\n".join(f"  - {m}" for m in matches[:10])
    return f"Multiple pages match {path_or_title!r}. Be more specific:\n{paths}"


@mcp.tool()
def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag', 'memory')
        directory: Subdirectory to list (e.g. 'concepts', 'agents', 'decisions')

    Returns:
        List of pages with title, tags, and summary.
    """
    search_dir = WIKI_DIR / directory if directory else WIKI_DIR
    pages = [p for p in search_dir.rglob("*.md") if not p.name.startswith("_")]

    results = []
    for page in sorted(pages):
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        page_tags = meta.get("tags", [])

        if tag and tag not in page_tags:
            continue

        results.append(
            f"- **{meta.get('title', page.stem)}** (`{page}`)\n"
            f"  Tags: {', '.join(page_tags) or 'none'}\n"
            f"  {meta.get('summary', '')}"
        )

    if not results:
        return (
            f"No pages found"
            + (f" with tag '{tag}'" if tag else "")
            + (f" in '{directory}'" if directory else "")
        )

    header = f"**{len(results)} page(s)**" + (f" tagged '{tag}'" if tag else "") + ":\n\n"
    return header + "\n".join(results)


if __name__ == "__main__":
    log.info("starting_mcp_server", wiki_dir=str(WIKI_DIR))
    mcp.run()
