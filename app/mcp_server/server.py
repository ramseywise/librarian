"""Librarian MCP Server

Exposes the compiled wiki to any MCP client — Claude Code, playground agents,
or other tools. Read-only.

Tools:
  search_wiki          — hybrid search (FTS + semantic) with backlink-weighted ranking
  read_page            — read a specific wiki page by filename or title
  list_domain          — list all pages in a domain directory
  list_pages           — list pages by domain tag, directory, or all
  get_domain_briefing  — return all pages in a domain as a structured reference briefing

Hybrid search: BM25 candidates (DuckDB fts extension) re-ranked with cosine
similarity (sentence-transformers) and backlink count. Falls back to a tokenized
per-term LIKE match when the fts extension is unavailable, and to text-only
ranking when sentence-transformers is not installed.

Usage:
    uv run python mcp_server/server.py
"""

from __future__ import annotations

import json
import os
import re
import struct
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

from app.log_config import configure_logging
from app.mcp_server.graph_expansion import build_typed_edges, expand_one_hop

load_dotenv()
configure_logging()  # installs the secret-redaction processor
log = structlog.get_logger()

# Anchored on __file__, not cwd — `make api` runs from app/ and must still find
# the same wiki root and index as `make mcp` running from the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_DIR = Path(os.getenv("WIKI_DIR", str(REPO_ROOT / "data" / "wiki")))
PRIVATE_DIR = WIKI_DIR / "private"
DB_PATH = Path(os.getenv("WIKI_DB_PATH", str(REPO_ROOT / ".wiki_index.duckdb")))
LOGS_DIR = Path("logs")
RETRIEVAL_LOG = LOGS_DIR / "retrieval.jsonl"
SCHEMA_VERSION = "4"  # 3→4: paths stored absolute + BM25 fts index added
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")


def _domains() -> list[str]:
    """Domain names derived from disk: directories under data/wiki/, minus private/.

    Replaces a hardcoded list that had drifted (6 directories missing, 1 phantom).
    Read at call time so tests can repoint WIKI_DIR.
    """
    if not WIKI_DIR.is_dir():
        return []
    return sorted(d.name for d in WIKI_DIR.iterdir() if d.is_dir() and d.name != "private")


mcp = FastMCP("librarian")

# Optional semantic search — gracefully absent if sentence-transformers not installed
try:
    from sentence_transformers import SentenceTransformer

    _emb_model: SentenceTransformer | None = None
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

# Optional FTS — installed per connection; absence is non-fatal but logged
HAS_FTS = False


def _ensure_fts(con: duckdb.DuckDBPyConnection) -> bool:
    """Install/load the DuckDB fts extension on this connection.

    Returns True when fts is usable. The single seam for disabling BM25 in
    tests (monkeypatch to `lambda con: False`) — search then takes the
    tokenized-LIKE fallback.
    """
    global HAS_FTS
    try:
        con.execute("INSTALL fts")
        con.execute("LOAD fts")
        HAS_FTS = True
    except Exception as exc:
        log.warning("fts_install_failed", error=str(exc))
        HAS_FTS = False
    return HAS_FTS


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
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb + 1e-9)


def is_under_private(path: Path | str, private_dir: Path) -> bool:
    """True if path lies under private_dir — never indexed, never served.

    Buyi invariant "data/wiki/private/ never leaves the machine", clause (b). Resolved
    before comparison so ../ traversal and absolute paths cannot slip past.

    private_dir is a parameter, not this module's PRIVATE_DIR, so callers and
    tests can supply their own root; `_is_private` binds it to PRIVATE_DIR read
    at call time.
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
    """Build or rebuild the DuckDB FTS index over data/wiki/ pages."""
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

    _ensure_fts(con)

    # Collect all pages
    raw_pages: list[tuple] = []
    for page in sorted(WIKI_DIR.rglob("*.md")):
        if page.name.startswith((".", "_")):
            continue
        # data/wiki/private/ is never indexed — Buyi confidentiality invariant
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

    global HAS_FTS
    if HAS_FTS:
        try:
            con.execute(
                "PRAGMA create_fts_index('pages', 'path', 'title', 'summary', 'content', "
                "overwrite=1)"
            )
        except Exception as exc:
            log.warning("fts_index_failed", error=str(exc))
            HAS_FTS = False

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

    Resolves to None for data/wiki/private/ so list_domain and get_domain_briefing
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
# Search core — shared by the MCP tool, the chat agent, and the eval harness
# ---------------------------------------------------------------------------


def _domain_filter(domain: str) -> tuple[str, list]:
    """SQL fragment + params scoping a query to a domain (directory OR tag).

    Match on directory OR domain tag, not either/or: a page can live in one
    subject directory while carrying another domain's tag (e.g. an interview
    guide filed under foundations/ but tagged `interview`). Filtering by path
    alone silently drops those from a --domain search.
    """
    if not domain:
        return "", []
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir:
        return (
            "AND (path LIKE ? OR lower(tags) LIKE '%' || lower(?) || '%')",
            [str(domain_dir) + "/%", domain],
        )
    return "AND lower(tags) LIKE '%' || lower(?) || '%'", [domain]


def _like_candidates(
    con: duckdb.DuckDBPyConnection,
    query: str,
    tag_filter: str,
    tag_params: list,
    limit: int,
) -> list[tuple]:
    """Tokenized per-term OR LIKE fallback when fts is unavailable or matches nothing.

    Each whitespace-separated term matches independently, so a multi-word query
    like "compaction strategies" still finds "strategies for compacting context"
    — the old whole-phrase LIKE required the exact phrase to appear verbatim.
    """
    terms = query.lower().split() or [query.lower()]
    term_cond = " OR ".join(
        ["(lower(content) LIKE ? OR lower(title) LIKE ? OR lower(summary) LIKE ?)"] * len(terms)
    )
    title_cond = " OR ".join(["lower(title) LIKE ?"] * len(terms))
    like_params: list = []
    for t in terms:
        like_params += [f"%{t}%"] * 3
    sql = f"""
        SELECT path, title, tags, summary, content, backlinks, embedding, NULL AS score
        FROM pages
        WHERE ({term_cond})
        {tag_filter}
        ORDER BY
            CASE WHEN ({title_cond}) THEN 0 ELSE 1 END,
            backlinks DESC,
            updated DESC
        LIMIT ?
    """
    params = like_params + tag_params + [f"%{t}%" for t in terms] + [limit * 3]
    return con.execute(sql, params).fetchall()


def _rerank(query: str, rows: list[tuple], limit: int) -> list[tuple]:
    """Blend text relevance, semantic similarity, and backlink count.

    rows are 8-tuples (path, title, tags, summary, content, backlinks, embedding,
    score); returns 7-tuples with the blended score in place of the embedding.
    BM25 rows carry a real relevance score (normalised against the max); fallback
    rows have score NULL, so position in the SQL ordering stands in.
    """
    raw_scores = [r[7] for r in rows]
    max_bm25 = max((s for s in raw_scores if s is not None), default=0.0)

    def text_score(i: int) -> float:
        s = raw_scores[i]
        if s is not None and max_bm25 > 0:
            return s / max_bm25
        return 1.0 - (i / len(rows))

    if HAS_EMBEDDINGS and len(rows) > 1:
        try:
            model = _get_emb_model()
            q_vec = model.encode([query], normalize_embeddings=True)[0].tolist()
            max_backlinks = max(r[5] for r in rows) or 1

            scored: list[tuple[float, tuple]] = []
            for i, row in enumerate(rows):
                bl, emb_blob = row[5], row[6]
                sem_score = _cosine(q_vec, _blob_to_vec(emb_blob)) if emb_blob else 0.0
                final = 0.5 * text_score(i) + 0.3 * sem_score + 0.2 * (bl / max_backlinks)
                scored.append((final, row))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [(*row[:6], score) for score, row in scored[:limit]]
        except Exception as e:
            log.warning("hybrid_rerank_failed", error=str(e))

    return [(*row[:6], text_score(i)) for i, row in enumerate(rows[:limit])]


def _search_rows(
    query: str, domain: str = "", limit: int = 10, tool: str = "search_wiki"
) -> list[tuple]:
    """Ranked wiki search returning raw rows — the single search core.

    Returns up to `limit` 7-tuples (path, title, tags, summary, content,
    backlinks, score), best first. Candidates come from BM25 (DuckDB fts);
    falls back to a tokenized per-term LIKE match when fts is unavailable or
    matches nothing. Logs retrieval telemetry under `tool`.
    """
    tag_filter, tag_params = _domain_filter(domain)

    con = get_con()
    try:
        rows: list[tuple] = []
        if _ensure_fts(con):
            # DuckDB permits SELECT aliases in WHERE, so `score` filters directly
            sql = f"""
                SELECT path, title, tags, summary, content, backlinks, embedding,
                       fts_main_pages.match_bm25(path, ?) AS score
                FROM pages
                WHERE score IS NOT NULL
                {tag_filter}
                ORDER BY score DESC
                LIMIT ?
            """
            try:
                rows = con.execute(sql, [query, *tag_params, limit * 3]).fetchall()
            except Exception as e:
                log.warning("fts_query_failed", error=str(e))
                rows = []

        if not rows:
            rows = _like_candidates(con, query, tag_filter, tag_params, limit)
    finally:
        con.close()

    if not rows:
        _log_retrieval(tool, query=query, domain=domain, n_results=0, top_paths=[])
        return []

    ranked = _rerank(query, rows, limit)
    _log_retrieval(
        tool,
        query=query,
        domain=domain,
        n_results=len(ranked),
        top_paths=[r[0] for r in ranked[:5]],
    )
    return ranked


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_wiki(query: str, domain: str = "", limit: int = 10, expand: bool = False) -> str:
    """Search the wiki using hybrid search (BM25 + semantic similarity + backlink rank).

    Results are ranked by a blend of: BM25 relevance, semantic closeness
    (if sentence-transformers is installed), and inbound backlink count.

    Args:
        query:  Search terms
        domain: Optional domain to scope the search — any directory under
                data/wiki/ (e.g. 'rag', 'langgraph', 'patterns') or a domain tag
        limit:  Max results (default 10)
        expand: SPIKE — also return pages one typed relationship hop from the
                results (`prerequisite-for` / `extends`). Answers "what else do
                I need to understand these hits?" Off by default.

    Returns:
        Matching pages with title, summary, path, backlink count, and a snippet.
    """
    rows = _search_rows(query, domain=domain, limit=limit)

    if not rows:
        suffix = f" in domain '{domain}'" if domain else ""
        return f"No wiki pages found for: {query!r}{suffix}"

    results = []
    for path, title, tags, summary, content, backlinks, _score in rows:
        lower = content.lower()
        idx = lower.find(query.lower())
        if idx < 0:
            # BM25 matches on stems, so the verbatim phrase may be absent —
            # snippet around the first individual term that does appear
            for term in query.lower().split():
                idx = lower.find(term)
                if idx >= 0:
                    break
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

    body = f"Found {len(rows)} result(s):\n\n" + "\n\n---\n\n".join(results)

    if expand:
        body += _expansion_section([r[0] for r in rows])

    return body


def _expansion_section(seed_paths: list[str]) -> str:
    """Render the one-hop typed-relationship neighbourhood of a result set.

    Returns an empty string when nothing is one hop away, so a wiki region with
    no typed annotations degrades to plain search rather than an empty header.
    """
    con = get_con()
    try:
        pages = con.execute("SELECT path, title, content FROM pages").fetchall()
        edges = build_typed_edges(pages)
        neighbours = expand_one_hop(seed_paths, edges)
        if not neighbours:
            return ""

        meta = {
            path: (title, summary)
            for path, title, summary in con.execute(
                "SELECT path, title, summary FROM pages"
            ).fetchall()
        }
    finally:
        con.close()

    lines = [
        f"- **{meta.get(path, (path, ''))[0]}** (`{path}`) "
        f"— {rel} of `{Path(seed).stem}`\n"
        f"  {meta.get(path, ('', ''))[1]}"
        for path, rel, seed in neighbours
    ]
    return (
        f"\n\n---\n\n**{len(neighbours)} page(s) one typed hop away** "
        f"(prerequisite-for / extends):\n\n" + "\n".join(lines)
    )


def _read_page_text(path_or_title: str) -> str:
    """Resolve a page by path, wiki-relative path, slug, or title and return its text.

    The single page-read core — the read_page MCP tool and the chat agent both
    call this, so private exclusion and telemetry are enforced in one place.
    """
    # Private pages are indistinguishable from missing ones — a distinct "denied"
    # message would itself confirm the page exists.
    not_found = f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    candidate = Path(path_or_title)
    if candidate.exists():
        if not candidate.resolve().is_relative_to(WIKI_DIR.resolve()):
            _log_retrieval("read_page", path=str(candidate), found=False, outside_wiki=True)
            return not_found
        if _is_private(candidate):
            _log_retrieval("read_page", path=str(candidate), found=False, private=True)
            return not_found
        _log_retrieval("read_page", path=str(candidate), found=True)
        return candidate.read_text(encoding="utf-8")

    wiki_candidate = WIKI_DIR / path_or_title
    if wiki_candidate.exists():
        if not wiki_candidate.resolve().is_relative_to(WIKI_DIR.resolve()):
            _log_retrieval("read_page", path=str(wiki_candidate), found=False, outside_wiki=True)
            return not_found
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
def read_page(path_or_title: str) -> str:
    """Read a specific wiki page by file path or title.

    Args:
        path_or_title: Either a relative path like 'data/wiki/rag/rag-retrieval-strategies.md'
                       or a page title like 'RAG Retrieval Strategies'

    Returns:
        Full page content, or an error message if not found.
    """
    return _read_page_text(path_or_title)


@mcp.tool()
def list_domain(domain: str) -> str:
    """List all pages in a domain directory, ordered by backlink count.

    This is an O(1) filesystem operation — no embedding or search needed.

    Args:
        domain: Domain directory name — any directory under data/wiki/
                (e.g. rag, langgraph, context, interview)

    Returns:
        All pages in the domain with title, tags, summary, and backlink count.
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(_domains())
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
    header = f"**{len(results)} page(s) in `data/wiki/{domain}/`** (sorted by backlinks):\n\n"
    return header + "\n".join(r[1] for r in results)


@mcp.tool()
def list_pages(tag: str = "", directory: str = "") -> str:
    """List wiki pages, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        directory: Subdirectory to list — any domain directory under data/wiki/
                   (e.g. rag, langgraph, context, interview)

    Returns:
        List of pages with title, tags, summary, and backlink count.
    """
    if directory:
        if ".." in directory or directory.startswith("/"):
            raise ValueError(f"Invalid directory: {directory!r}")
        search_dir = WIKI_DIR / directory
        if not search_dir.resolve().is_relative_to(WIKI_DIR.resolve()):
            raise ValueError(f"Directory escapes wiki root: {directory!r}")
    else:
        search_dir = WIKI_DIR
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
        domain: Domain directory name — any directory under data/wiki/
                (e.g. rag, langgraph, context, interview)

    Returns:
        Full content of all pages in the domain, ordered: decisions → patterns → concepts.
    """
    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        valid = ", ".join(_domains())
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
