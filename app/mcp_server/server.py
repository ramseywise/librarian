"""Librarian MCP Server

Exposes the compiled wiki to any MCP client — Claude Code, playground agents,
or other tools. Read-only.

Tools:
  search_wiki          — full-text search over wiki/ pages, optionally scoped to a domain
  read_page            — read a specific wiki page by filename or title
  list_domain          — list all pages in a domain directory
  list_pages           — list pages by domain tag, directory, or all
  get_domain_briefing  — return all pages in a domain as a structured reference briefing

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

DOMAINS = [
    "rag", "langgraph", "adk", "infra", "patterns",
    "eval", "deep-agents", "memory", "mcp", "meta", "projects",
]

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
            meta["tags"] = re.findall(r"[\w-]+", val)
        else:
            meta[key] = val.strip("\"'")
    return meta


def get_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(DB_PATH))
    build_index(con)
    return con


def _resolve_domain_dir(domain: str) -> Path | None:
    """Return the wiki subdirectory for a domain name, or None if not found."""
    candidate = WIKI_DIR / domain
    if candidate.is_dir():
        return candidate
    # Fuzzy: allow 'deep_agents' → 'deep-agents'
    slug = domain.replace("_", "-").lower()
    candidate = WIKI_DIR / slug
    if candidate.is_dir():
        return candidate
    return None


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_wiki(query: str, domain: str = "", limit: int = 10) -> str:
    """Search the wiki with full-text search, optionally scoped to a domain.

    Args:
        query:  Search terms
        domain: Optional domain directory to scope the search
                (e.g. 'rag', 'langgraph', 'adk', 'infra', 'patterns',
                 'eval', 'deep-agents', 'memory', 'mcp', 'meta', 'projects')
        limit:  Max results (default 10)

    Returns:
        Matching pages with title, summary, path, and a snippet.
    """
    con = get_con()

    tag_filter = ""
    params: list = [query, query, query]

    if domain:
        domain_dir = _resolve_domain_dir(domain)
        if domain_dir:
            # Scope by path prefix (exact directory match)
            tag_filter = "AND path LIKE ?"
            params.append(str(domain_dir) + "/%")
        else:
            # Fall back to tag match
            tag_filter = "AND lower(tags) LIKE '%' || lower(?) || '%'"
            params.append(domain)

    sql = f"""
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
    """

    params += [query, limit]
    rows = con.execute(sql, params).fetchall()
    con.close()

    if not rows:
        suffix = f" in domain '{domain}'" if domain else ""
        return f"No wiki pages found for: {query!r}{suffix}"

    results = []
    for path, title, tags, summary, content in rows:
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
        path_or_title: Either a relative path like 'wiki/rag/rag-retrieval-strategies.md'
                       or a page title like 'RAG Retrieval Strategies'

    Returns:
        Full page content, or an error message if not found.
    """
    candidate = Path(path_or_title)
    if candidate.exists():
        return candidate.read_text(encoding="utf-8")

    wiki_candidate = WIKI_DIR / path_or_title
    if wiki_candidate.exists():
        return wiki_candidate.read_text(encoding="utf-8")

    # Fuzzy title match
    slug = re.sub(r"[^a-z0-9]+", "-", path_or_title.lower()).strip("-")
    matches = list(WIKI_DIR.rglob(f"*{slug}*.md"))
    if not matches:
        words = path_or_title.lower().split()
        for word in words:
            matches = list(WIKI_DIR.rglob(f"*{word}*.md"))
            if matches:
                break

    if not matches:
        return f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    if len(matches) == 1:
        return matches[0].read_text(encoding="utf-8")

    paths = "\n".join(f"  - {m}" for m in matches[:10])
    return f"Multiple pages match {path_or_title!r}. Be more specific:\n{paths}"


@mcp.tool()
def list_domain(domain: str) -> str:
    """List all pages in a domain directory.

    This is an O(1) filesystem operation — no embedding or search needed.

    Args:
        domain: Domain directory name — one of:
                rag, langgraph, adk, infra, patterns, eval,
                deep-agents, memory, mcp, meta, projects

    Returns:
        All pages in the domain with title, tags, and summary.
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(DOMAINS)
        return f"Unknown domain: {domain!r}. Valid domains: {valid}"

    pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    results = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        page_tags = meta.get("tags", [])
        results.append(
            f"- **{meta.get('title', page.stem)}** (`{page}`)\n"
            f"  Tags: {', '.join(page_tags) or 'none'}\n"
            f"  {meta.get('summary', '')}"
        )

    header = f"**{len(results)} page(s) in `wiki/{domain}/`**:\n\n"
    return header + "\n".join(results)


@mcp.tool()
def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        directory: Subdirectory to list — use domain names:
                   rag, langgraph, adk, infra, patterns, eval,
                   deep-agents, memory, mcp, meta, projects

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
            "No pages found"
            + (f" with tag '{tag}'" if tag else "")
            + (f" in '{directory}'" if directory else "")
        )

    header = f"**{len(results)} page(s)**" + (f" tagged '{tag}'" if tag else "") + ":\n\n"
    return header + "\n".join(results)


@mcp.tool()
def get_domain_briefing(domain: str) -> str:
    """Return a structured build briefing for a domain — all pages concatenated.

    Use this before starting work in a domain to load all accumulated patterns,
    decisions, and tradeoffs into context. Equivalent to the adk-context skill
    but generalized to any domain.

    Args:
        domain: Domain directory name — one of:
                rag, langgraph, adk, infra, patterns, eval,
                deep-agents, memory, mcp, meta, projects

    Returns:
        Full content of all pages in the domain, separated by dividers,
        ordered by type (decisions first, then patterns, then concepts).
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(DOMAINS)
        return f"Unknown domain: {domain!r}. Valid domains: {valid}"

    pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    # Parse all pages and sort: decisions first, then by type tag order
    type_order = {"decision": 0, "pattern": 1, "comparison": 2, "concept": 3, "reference": 4, "project": 5}
    parsed = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        tags = meta.get("tags", [])
        type_tag = next((t for t in tags if t in type_order), "concept")
        parsed.append((type_order.get(type_tag, 3), meta.get("title", page.stem), text))

    parsed.sort(key=lambda x: (x[0], x[1]))

    sections = []
    for _, title, content in parsed:
        sections.append(f"{'=' * 60}\n# {title}\n{'=' * 60}\n\n{content}")

    header = (
        f"# Domain Briefing: {domain.upper()}\n"
        f"{len(parsed)} pages · use read_page for any individual page\n\n"
    )
    return header + "\n\n".join(sections)


if __name__ == "__main__":
    log.info("starting_mcp_server", wiki_dir=str(WIKI_DIR))
    mcp.run()
