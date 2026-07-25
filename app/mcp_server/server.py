"""Librarian MCP Server

Exposes the compiled wiki to any MCP client — Claude Code, playground agents,
or other tools. Read-only.

Tools:
  search_wiki          — hybrid search (FTS + semantic) with backlink-weighted ranking
  read_page            — read a specific wiki page by filename or title
  list_domain          — list all pages in a domain directory
  list_pages           — list pages by domain tag, directory, or all
  get_domain_briefing  — return all pages in a domain as a structured reference briefing

Hybrid search: blends DuckDB FTS with cosine similarity (sentence-transformers).
Falls back to FTS-only if sentence-transformers is not installed.
Backlink counts are indexed and used as a ranking signal alongside relevance.

Usage:
    uv run python mcp_server/server.py
"""

from __future__ import annotations

import json
import re
import struct
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

from app.log_config import configure_logging

load_dotenv()
configure_logging()  # installs the secret-redaction processor
log = structlog.get_logger()

WIKI_DIR = Path("wiki")
PRIVATE_DIR = WIKI_DIR / "private"
DB_PATH = Path(".wiki_index.duckdb")
LOGS_DIR = Path("logs")
RETRIEVAL_LOG = LOGS_DIR / "retrieval.jsonl"
SCHEMA_VERSION = "2"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")

DOMAINS = [
    "rag",
    "langgraph",
    "adk",
    "infra",
    "patterns",
    "eval",
    "deep-agents",
    "memory",
    "mcp",
    "meta",
    "projects",
]

mcp = FastMCP("librarian")

# Optional semantic search — gracefully absent if sentence-transformers not installed
try:
    from sentence_transformers import SentenceTransformer

    _emb_model: SentenceTransformer | None = None
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

# Optional FTS — installed at index-build time; absence is non-fatal but logged
HAS_FTS = False


def _get_emb_model() -> SentenceTransformer:
    global _emb_model
    if _emb_model is None:
        _emb_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _emb_model


def _vec_to_blob(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _blob_to_vec(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


def is_under_private(path: Path | str, private_dir: Path) -> bool:
    """True if path lies under private_dir — never indexed, never served.

    Buyi invariant "wiki/private/ never leaves the machine", clause (b). Resolved
    before comparison so ../ traversal and absolute paths cannot slip past.

    private_dir is a parameter, not this module's PRIVATE_DIR, because callers
    anchor their wiki root differently: the server uses a relative Path("wiki")
    while app/backend/agent.py derives an absolute path from __file__. Sharing the
    resolution logic while each caller supplies its own root keeps a second copy
    from drifting, without making one caller's cwd decide the other's filter.
    """
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError):
        return True  # unresolvable path — refuse rather than risk serving it
    root = private_dir.resolve()
    return resolved == root or root in resolved.parents


def _is_private(path: Path | str) -> bool:
    """is_under_private bound to this module's PRIVATE_DIR (read at call time)."""
    return is_under_private(path, PRIVATE_DIR)


def _log_retrieval(tool: str, **fields: object) -> None:
    """Append one JSON line of retrieval telemetry to logs/retrieval.jsonl.

    Never raises — telemetry must not break retrieval. Consumed by /compact-wiki
    as merge/retire evidence (see .claude/docs/plans/2026-07-17-knowledge-compaction.md).
    """
    try:
        LOGS_DIR.mkdir(exist_ok=True)
        entry = {"ts": datetime.now(UTC).isoformat(), "tool": tool, **fields}
        with RETRIEVAL_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log.warning("telemetry_failed", error=str(e))


# ---------------------------------------------------------------------------
# Index freshness check
# ---------------------------------------------------------------------------


def _index_needs_rebuild(con: duckdb.DuckDBPyConnection) -> bool:
    """Return True if the index is absent, stale, or schema-mismatched."""
    try:
        version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
        if not version or version[0] != SCHEMA_VERSION:
            return True
        built_at = float(con.execute("SELECT val FROM meta WHERE key = 'built_at'").fetchone()[0])
        # Rebuild if any wiki page is newer than the index
        return any(
            p.stat().st_mtime > built_at for p in WIKI_DIR.rglob("*.md") if not _is_private(p)
        )
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Index build
# ---------------------------------------------------------------------------


def _compute_backlinks(pages: list[tuple]) -> dict[str, int]:
    """Count inbound wikilinks for each page slug."""
    slug_to_path: dict[str, str] = {}
    for path, title, *_ in pages:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        slug_to_path[slug] = path
        # also register by stem
        stem = Path(path).stem
        slug_to_path[stem] = path

    counts: dict[str, int] = {p[0]: 0 for p in pages}
    for path, *__, content in pages:
        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
            target = slug_to_path.get(slug) or slug_to_path.get(raw.lower().replace(" ", "-"))
            if target and target != path and target in counts:
                counts[target] += 1
    return counts


def build_index(con: duckdb.DuckDBPyConnection) -> None:
    """Build or rebuild the DuckDB FTS index over wiki/ pages."""
    if not _index_needs_rebuild(con):
        return

    log.info("rebuilding_index")

    con.execute("DROP TABLE IF EXISTS meta")
    con.execute("DROP TABLE IF EXISTS pages")

    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, val TEXT)")

    con.execute("""
        CREATE TABLE pages (
            path      TEXT PRIMARY KEY,
            title     TEXT,
            tags      TEXT,
            summary   TEXT,
            updated   TEXT,
            content   TEXT,
            backlinks INTEGER DEFAULT 0,
            embedding BLOB
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS pages_path ON pages (path)")

    global HAS_FTS
    try:
        con.execute("INSTALL fts")
        con.execute("LOAD fts")
        HAS_FTS = True
    except Exception as exc:
        log.warning("fts_install_failed", error=str(exc))

    # Collect all pages
    raw_pages: list[tuple] = []
    for page in sorted(WIKI_DIR.rglob("*.md")):
        if page.name.startswith("."):
            continue
        # wiki/private/ is never indexed — Buyi confidentiality invariant
        if _is_private(page):
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        # Tombstones stay followable via read_page but never rank in search
        if "tombstone" in meta.get("tags", []):
            continue
        raw_pages.append(
            (
                str(page),
                meta.get("title", page.stem),
                " ".join(meta.get("tags", [])),
                meta.get("summary", ""),
                meta.get("updated", ""),
                text,
            )
        )

    backlinks = _compute_backlinks(raw_pages)

    # Compute embeddings if available
    embeddings: dict[str, bytes] = {}
    if HAS_EMBEDDINGS:
        try:
            model = _get_emb_model()
            texts = [f"{r[1]}. {r[3]}\n\n{r[5][:600]}" for r in raw_pages]
            vecs = model.encode(texts, normalize_embeddings=True)
            for i, row in enumerate(raw_pages):
                embeddings[row[0]] = _vec_to_blob(vecs[i].tolist())
        except Exception as e:
            log.warning("embedding_failed", error=str(e))

    rows = [
        (
            path,
            title,
            tags,
            summary,
            updated,
            content,
            backlinks.get(path, 0),
            embeddings.get(path),
        )
        for path, title, tags, summary, updated, content in raw_pages
    ]

    con.executemany(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )

    import time

    con.execute("INSERT INTO meta VALUES ('schema_version', ?)", [SCHEMA_VERSION])
    con.execute("INSERT INTO meta VALUES ('built_at', ?)", [str(time.time())])

    log.info("index_built", page_count=len(rows), with_embeddings=bool(embeddings))


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
    """Return the wiki subdirectory for a domain name, or None if not found.

    Resolves to None for wiki/private/ so list_domain and get_domain_briefing
    cannot address it as a domain.
    """
    candidate = WIKI_DIR / domain
    if candidate.is_dir() and not _is_private(candidate):
        return candidate
    slug = domain.replace("_", "-").lower()
    candidate = WIKI_DIR / slug
    if candidate.is_dir() and not _is_private(candidate):
        return candidate
    return None


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_wiki(query: str, domain: str = "", limit: int = 10) -> str:
    """Search the wiki using hybrid search (FTS + semantic similarity + backlink rank).

    Results are ranked by a blend of: text match relevance, semantic closeness
    (if sentence-transformers is installed), and inbound backlink count.

    Args:
        query:  Search terms
        domain: Optional domain directory to scope the search
                (e.g. 'rag', 'langgraph', 'adk', 'infra', 'patterns',
                 'eval', 'deep-agents', 'memory', 'mcp', 'meta', 'projects')
        limit:  Max results (default 10)

    Returns:
        Matching pages with title, summary, path, backlink count, and a snippet.
    """
    con = get_con()

    tag_filter = ""
    params: list = [query, query, query]

    if domain:
        domain_dir = _resolve_domain_dir(domain)
        if domain_dir:
            tag_filter = "AND path LIKE ?"
            params.append(str(domain_dir) + "/%")
        else:
            tag_filter = "AND lower(tags) LIKE '%' || lower(?) || '%'"
            params.append(domain)

    # Fetch candidates — title match first, then recency, then backlinks
    sql = f"""
        SELECT path, title, tags, summary, content, backlinks, embedding
        FROM pages
        WHERE (
            lower(content) LIKE '%' || lower(?) || '%'
            OR lower(title) LIKE '%' || lower(?) || '%'
            OR lower(summary) LIKE '%' || lower(?) || '%'
        )
        {tag_filter}
        ORDER BY
            CASE WHEN lower(title) LIKE '%' || lower(?) || '%' THEN 0 ELSE 1 END,
            backlinks DESC,
            updated DESC
        LIMIT ?
    """
    params += [query, limit * 3]  # fetch 3× for re-ranking
    try:
        rows = con.execute(sql, params).fetchall()
    finally:
        con.close()

    if not rows:
        _log_retrieval("search_wiki", query=query, domain=domain, n_results=0, top_paths=[])
        suffix = f" in domain '{domain}'" if domain else ""
        return f"No wiki pages found for: {query!r}{suffix}"

    # Hybrid re-ranking: blend FTS rank + cosine similarity + backlink boost
    if HAS_EMBEDDINGS and len(rows) > 1:
        try:
            model = _get_emb_model()
            q_vec = model.encode([query], normalize_embeddings=True)[0].tolist()
            max_backlinks = max(r[5] for r in rows) or 1

            scored: list[tuple[float, tuple]] = []
            for i, row in enumerate(rows):
                path, title, tags, summary, content, bl, emb_blob = row
                # FTS rank: position in result set (0=best), normalised 0–1
                fts_score = 1.0 - (i / len(rows))
                # Backlink score: normalised 0–1
                bl_score = bl / max_backlinks
                # Semantic score
                sem_score = 0.0
                if emb_blob:
                    page_vec = _blob_to_vec(emb_blob)
                    sem_score = _cosine(q_vec, page_vec)
                # Weighted blend
                final = 0.5 * fts_score + 0.3 * sem_score + 0.2 * bl_score
                scored.append((final, row))

            scored.sort(key=lambda x: x[0], reverse=True)
            rows = [r for _, r in scored[:limit]]
        except Exception as e:
            log.warning("hybrid_rerank_failed", error=str(e))
            rows = rows[:limit]
    else:
        rows = rows[:limit]

    results = []
    for path, title, tags, summary, content, backlinks, _ in rows:
        idx = content.lower().find(query.lower())
        snippet = ""
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(content), idx + 160)
            snippet = content[start:end].replace("\n", " ").strip()

        results.append(
            f"**{title}**\n"
            f"Path: `{path}`\n"
            f"Tags: {tags} · Backlinks: {backlinks}\n"
            f"Summary: {summary}\n" + (f"Snippet: ...{snippet}..." if snippet else "")
        )

    _log_retrieval(
        "search_wiki",
        query=query,
        domain=domain,
        n_results=len(rows),
        top_paths=[r[0] for r in rows[:5]],
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
    # Private pages are indistinguishable from missing ones — a distinct "denied"
    # message would itself confirm the page exists.
    not_found = f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    candidate = Path(path_or_title)
    if candidate.exists():
        if _is_private(candidate):
            _log_retrieval("read_page", path=str(candidate), found=False, private=True)
            return not_found
        _log_retrieval("read_page", path=str(candidate), found=True)
        return candidate.read_text(encoding="utf-8")

    wiki_candidate = WIKI_DIR / path_or_title
    if wiki_candidate.exists():
        if _is_private(wiki_candidate):
            _log_retrieval("read_page", path=str(wiki_candidate), found=False, private=True)
            return not_found
        _log_retrieval("read_page", path=str(wiki_candidate), found=True)
        return wiki_candidate.read_text(encoding="utf-8")

    slug = re.sub(r"[^a-z0-9]+", "-", path_or_title.lower()).strip("-")
    matches = [p for p in WIKI_DIR.rglob(f"*{slug}*.md") if not _is_private(p)]
    if not matches:
        words = path_or_title.lower().split()
        for word in words:
            matches = [p for p in WIKI_DIR.rglob(f"*{word}*.md") if not _is_private(p)]
            if matches:
                break

    if not matches:
        _log_retrieval("read_page", path=path_or_title, found=False)
        return not_found

    if len(matches) == 1:
        _log_retrieval("read_page", path=str(matches[0]), found=True)
        return matches[0].read_text(encoding="utf-8")

    _log_retrieval(
        "read_page", path=path_or_title, found=False, ambiguous=True, n_matches=len(matches)
    )
    paths = "\n".join(f"  - {m}" for m in matches[:10])
    return f"Multiple pages match {path_or_title!r}. Be more specific:\n{paths}"


@mcp.tool()
def list_domain(domain: str) -> str:
    """List all pages in a domain directory, ordered by backlink count.

    This is an O(1) filesystem operation — no embedding or search needed.

    Args:
        domain: Domain directory name — one of:
                rag, langgraph, adk, infra, patterns, eval,
                deep-agents, memory, mcp, meta, projects

    Returns:
        All pages in the domain with title, tags, summary, and backlink count.
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(DOMAINS)
        return f"Unknown domain: {domain!r}. Valid domains: {valid}"

    pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    # Load backlink counts from index
    con = get_con()
    bl_map: dict[str, int] = {}
    try:
        for path, bl in con.execute("SELECT path, backlinks FROM pages").fetchall():
            bl_map[path] = bl
    except Exception:
        pass
    finally:
        con.close()

    results = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        page_tags = meta.get("tags", [])
        bl = bl_map.get(str(page), 0)
        results.append(
            (
                bl,
                (
                    f"- **{meta.get('title', page.stem)}** (`{page}`) · ↑{bl} backlinks\n"
                    f"  Tags: {', '.join(page_tags) or 'none'}\n"
                    f"  {meta.get('summary', '')}"
                ),
            )
        )

    results.sort(key=lambda x: x[0], reverse=True)
    _log_retrieval("list_domain", domain=domain, n_results=len(results))
    header = f"**{len(results)} page(s) in `wiki/{domain}/`** (sorted by backlinks):\n\n"
    return header + "\n".join(r[1] for r in results)


@mcp.tool()
def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        directory: Subdirectory to list — use domain names:
                   rag, langgraph, adk, infra, patterns, eval,
                   deep-agents, memory, mcp, meta, projects

    Returns:
        List of pages with title, tags, summary, and backlink count.
    """
    search_dir = WIKI_DIR / directory if directory else WIKI_DIR
    pages = [
        p for p in search_dir.rglob("*.md") if not p.name.startswith("_") and not _is_private(p)
    ]

    con = get_con()
    bl_map: dict[str, int] = {}
    try:
        for path, bl in con.execute("SELECT path, backlinks FROM pages").fetchall():
            bl_map[path] = bl
    except Exception:
        pass
    finally:
        con.close()

    results = []
    for page in sorted(pages):
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        page_tags = meta.get("tags", [])

        if tag and tag not in page_tags:
            continue

        bl = bl_map.get(str(page), 0)
        results.append(
            f"- **{meta.get('title', page.stem)}** (`{page}`) · ↑{bl}\n"
            f"  Tags: {', '.join(page_tags) or 'none'}\n"
            f"  {meta.get('summary', '')}"
        )

    if not results:
        return (
            "No pages found"
            + (f" with tag '{tag}'" if tag else "")
            + (f" in '{directory}'" if directory else "")
        )

    _log_retrieval("list_pages", tag=tag, directory=directory, n_results=len(results))
    header = f"**{len(results)} page(s)**" + (f" tagged '{tag}'" if tag else "") + ":\n\n"
    return header + "\n".join(results)


@mcp.tool()
def get_domain_briefing(domain: str) -> str:
    """Return a structured build briefing for a domain — all pages concatenated.

    Use this before starting work in a domain to load all accumulated patterns,
    decisions, and tradeoffs into context.

    Args:
        domain: Domain directory name — one of:
                rag, langgraph, adk, infra, patterns, eval,
                deep-agents, memory, mcp, meta, projects

    Returns:
        Full content of all pages in the domain, ordered: decisions → patterns → concepts.
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(DOMAINS)
        return f"Unknown domain: {domain!r}. Valid domains: {valid}"

    pages = sorted(p for p in domain_dir.glob("*.md") if not p.name.startswith("_"))
    if not pages:
        return f"No pages found in domain '{domain}'"

    type_order = {
        "decision": 0,
        "pattern": 1,
        "comparison": 2,
        "concept": 3,
        "reference": 4,
        "project": 5,
    }
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

    _log_retrieval("get_domain_briefing", domain=domain, n_pages=len(parsed))
    header = (
        f"# Domain Briefing: {domain.upper()}\n"
        f"{len(parsed)} pages · use read_page for any individual page\n\n"
    )
    return header + "\n\n".join(sections)


from app.mcp_server.codemap_tools import register_codemap_tools  # noqa: E402

register_codemap_tools(mcp)


if __name__ == "__main__":
    log.info("starting_mcp_server", wiki_dir=str(WIKI_DIR), hybrid_search=HAS_EMBEDDINGS)
    mcp.run()
