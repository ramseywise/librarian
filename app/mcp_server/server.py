"""Librarian MCP Server

Exposes the compiled wiki and the course lessons in data/courses/ to any MCP client —
Claude Code, playground agents, or other tools. Read-only.

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

Course lessons live in their own table and FTS index (`course_pages`), never in `pages`.
BM25 statistics, backlinks and typed edges are corpus-wide, so sharing a table would change
wiki rankings. Their domain is derived from the path: `course`, `course/<subject>`. An
unscoped search ranks the wiki only and lists the best lessons in a separate section.

Usage:
    uv run python mcp_server/server.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import struct
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import duckdb
import frontmatter
import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

from app.mcp_server.graph_expansion import build_typed_edges, expand_one_hop
from core.wiki_common import ANY_TYPED_LINK_RE, CANONICAL_LINK_TYPES, WIKILINK_RE, slugify
from shared.log_config import configure_logging

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

load_dotenv()
configure_logging()  # installs the secret-redaction processor
log = structlog.get_logger()

# Anchored on __file__, not cwd — `make api` runs from app/ and must still find
# the same wiki root and index as `make mcp` running from the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI_DIR = Path(os.getenv("WIKI_DIR", str(REPO_ROOT / "data" / "wiki")))
PRIVATE_DIR = WIKI_DIR / "private"
COURSES_DIR = Path(os.getenv("COURSES_DIR", str(REPO_ROOT / "data" / "courses")))
COURSE_DOMAIN = "course"
DB_PATH = Path(os.getenv("WIKI_DB_PATH", str(REPO_ROOT / ".wiki_index.duckdb")))
LOGS_DIR = Path("logs")
RETRIEVAL_LOG = LOGS_DIR / "retrieval.jsonl"
# 6→7: adds content_hash for incremental indexing (LIB-124). 7→8: adds course_pages.
SCHEMA_VERSION = "8"


def _domains() -> list[str]:
    """Domain names derived from disk: directories under data/wiki/, minus private/.

    Replaces a hardcoded list that had drifted (6 directories missing, 1 phantom).
    Read at call time so tests can repoint WIKI_DIR.
    """
    if not WIKI_DIR.is_dir():
        return []
    return sorted(d.name for d in WIKI_DIR.iterdir() if d.is_dir() and d.name != "private")


def _course_domain(path: Path | str) -> str:
    """`course/<subject>` for a lesson path. The path is the only source of a lesson's domain."""
    return f"{COURSE_DOMAIN}/{Path(path).relative_to(COURSES_DIR).parts[0]}"


def _course_ref(path: Path | str) -> str:
    """The `course/<relative path>` form of a lesson path, as read_page accepts it."""
    return f"{COURSE_DOMAIN}/{Path(path).relative_to(COURSES_DIR).as_posix()}"


def _course_domains() -> list[str]:
    """`course` plus one `course/<subject>` per directory under data/courses/."""
    if not COURSES_DIR.is_dir():
        return []
    subjects = sorted(d.name for d in COURSES_DIR.iterdir() if d.is_dir())
    return [COURSE_DOMAIN, *(f"{COURSE_DOMAIN}/{s}" for s in subjects)]


def _is_course_domain(domain: str) -> bool:
    return domain == COURSE_DOMAIN or domain.startswith(f"{COURSE_DOMAIN}/")


def _resolve_course_dir(domain: str) -> Path | None:
    """Directory for `course`, `course/<subject>` or deeper; None if absent or outside the root."""
    rel = domain.removeprefix(COURSE_DOMAIN).strip("/")
    candidate = COURSES_DIR / rel
    if (
        candidate.is_dir()
        and candidate.resolve().is_relative_to(COURSES_DIR.resolve())
        and not _is_private(candidate)
    ):
        return candidate
    return None


mcp = FastMCP("librarian")

# Optional semantic search — gracefully absent if sentence-transformers not installed.
# Checked, not imported: importing it pulls in torch, which took 4-13 s of API startup.
HAS_EMBEDDINGS = importlib.util.find_spec("sentence_transformers") is not None
_emb_model: SentenceTransformer | None = None

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


EMB_MODEL_ID = "all-MiniLM-L6-v2"


def _get_emb_model() -> SentenceTransformer:
    global _emb_model
    if _emb_model is None:
        from sentence_transformers import SentenceTransformer

        _emb_model = SentenceTransformer(EMB_MODEL_ID)
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


def _wiki_pages() -> list[Path]:
    """Indexable wiki pages: no private pages, no `_` or `.` files."""
    return [
        p
        for p in WIKI_DIR.rglob("*.md")
        if not p.name.startswith((".", "_")) and not _is_private(p)
    ]


def _course_pages(root: Path | None = None) -> list[Path]:
    """Indexable lessons under root (default all of data/courses/).

    `_course.md`, `_module.md` and `_flashcards.md` are skipped like any `_` file: the first
    two are frontmatter-only catalog metadata whose summary and titles reappear in lessons,
    and flashcards restate deck takeaways. A symlink leaving the course root is not a lesson.
    """
    courses_root = COURSES_DIR.resolve()
    if _is_private(courses_root):
        return []
    # Runs several times per search, so resolve only files that are symlinks: rglob's `**`
    # does not descend through directory symlinks, and resolving every path is most of the cost.
    return [
        p
        for p in (root or COURSES_DIR).rglob("*.md")
        if not p.name.startswith((".", "_"))
        and (not p.is_symlink() or p.resolve().is_relative_to(courses_root))
    ]


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
    """Return True if the index is absent or schema-mismatched (full rebuild required).

    Stale pages after a valid schema are handled by _stale_pages(), which uses
    content hashes for page-level change detection.
    """
    try:
        version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
        # Schema is valid when version matches — stale pages handled by _stale_pages()
        return not version or version[0] != SCHEMA_VERSION
    except Exception:
        return True


def _content_hash(path: Path) -> str:
    """SHA-256 of page bytes, first 16 hex chars — same convention as shared/embeddings.py."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _stale_pages(con: duckdb.DuckDBPyConnection) -> list[Path]:
    """Return paths of wiki pages and lessons whose content hash differs from the indexed hash.

    Returns an empty list when the index is fully fresh and no pages have been deleted.
    """
    try:
        indexed: dict[str, str] = {
            row[0]: row[1]
            for table in ("pages", "course_pages")
            for row in con.execute(f"SELECT path, content_hash FROM {table}").fetchall()
        }
    except Exception:
        return _wiki_pages() + _course_pages()

    return [p for p in _wiki_pages() + _course_pages() if indexed.get(str(p)) != _content_hash(p)]


def _has_deleted_pages(con: duckdb.DuckDBPyConnection) -> bool:
    """Return True if any page in the index no longer exists on disk."""
    try:
        indexed_paths = {
            r[0]
            for table in ("pages", "course_pages")
            for r in con.execute(f"SELECT path FROM {table}").fetchall()
        }
    except Exception:
        return False
    current_paths = {str(p) for p in _wiki_pages() + _course_pages()}
    return bool(indexed_paths - current_paths)


# ---------------------------------------------------------------------------
# Index build
# ---------------------------------------------------------------------------


def _compute_backlinks(pages: list[tuple]) -> dict[str, int]:
    """Count inbound wikilinks for each page slug."""
    slug_to_path: dict[str, str] = {}
    for path, title, *_ in pages:
        slug = slugify(title)
        slug_to_path[slug] = path
        # also register by stem
        stem = Path(path).stem
        slug_to_path[stem] = path

    counts: dict[str, int] = {p[0]: 0 for p in pages}
    for row in pages:
        path, content = row[0], row[5]
        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            slug = slugify(raw)
            target = slug_to_path.get(slug)
            if target and target != path and target in counts:
                counts[target] += 1
    return counts


def _read_pages(paths: list[Path]) -> list[tuple]:
    """Parse frontmatter + text for the given pages.

    Returns tuples of (path_str, title, tags, summary, updated, content, content_hash).
    Tombstone pages are excluded (same rule as _full_rebuild).
    """
    raw: list[tuple] = []
    for page in paths:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = _parse_frontmatter(text)
        if "tombstone" in meta.get("tags", []):
            continue
        chash = _content_hash(page)
        raw.append(
            (
                str(page),
                meta.get("title", page.stem),
                " ".join(meta.get("tags", [])),
                meta.get("summary", ""),
                meta.get("updated", ""),
                text,
                chash,
            )
        )
    return raw


def _full_rebuild(con: duckdb.DuckDBPyConnection) -> None:
    """Drop and recreate all index tables, then re-index every wiki page and lesson.

    Called when the schema version mismatches or the index is absent.
    After this runs, subsequent calls take the incremental path via _stale_pages().
    """
    log.info("rebuilding_index")

    con.execute("DROP TABLE IF EXISTS meta")
    con.execute("DROP TABLE IF EXISTS pages")
    con.execute("DROP TABLE IF EXISTS course_pages")
    con.execute("DROP TABLE IF EXISTS edges")

    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, val TEXT)")

    for table in ("pages", "course_pages"):
        con.execute(f"""
            CREATE TABLE {table} (
                path         TEXT PRIMARY KEY,
                title        TEXT,
                tags         TEXT,
                summary      TEXT,
                updated      TEXT,
                content      TEXT,
                backlinks    INTEGER DEFAULT 0,
                embedding    BLOB,
                content_hash TEXT
            )
        """)
    con.execute("CREATE INDEX IF NOT EXISTS pages_path ON pages (path)")
    con.execute("CREATE TABLE edges (source_path TEXT, target_path TEXT, relationship TEXT)")

    _ensure_fts(con)

    # Collect all pages
    raw_pages = _read_pages(sorted(_wiki_pages()))

    # raw_pages tuples: (path, title, tags, summary, updated, content, content_hash)
    backlinks = _compute_backlinks(raw_pages)

    # Materialize typed edges once at build time — expansion reads the table
    # instead of re-parsing every page body per call. Census annotations whose
    # type is not canonical so schema entropy is visible in the build log.
    typed_edges = build_typed_edges([(row[0], row[1], row[5]) for row in raw_pages])
    if typed_edges:
        con.executemany("INSERT INTO edges VALUES (?, ?, ?)", typed_edges)
    n_unrecognized = sum(
        1
        for row in raw_pages
        for m in ANY_TYPED_LINK_RE.finditer(row[5])
        if m.group(2) not in CANONICAL_LINK_TYPES
    )

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
            chash,
        )
        for path, title, tags, summary, updated, content, chash in raw_pages
    ]

    con.executemany(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

    n_lessons = _upsert_lessons(con, sorted(_course_pages()))

    con.execute("INSERT INTO meta VALUES ('schema_version', ?)", [SCHEMA_VERSION])
    con.execute("INSERT INTO meta VALUES ('built_at', ?)", [str(time.time())])

    log.info(
        "index_built",
        page_count=len(rows),
        lesson_count=n_lessons,
        with_embeddings=bool(embeddings),
        typed_edges=len(typed_edges),
        unrecognized_annotations=n_unrecognized,
    )


def _upsert_lessons(con: duckdb.DuckDBPyConnection, lessons: list[Path]) -> int:
    """Embed and write lessons to course_pages, prune removed ones, refresh their FTS index.

    Lessons carry no backlinks or edges: a wikilink from a lesson is not evidence about a
    wiki page, and a lesson's title or stem must not capture a wiki link's resolution.
    """
    raw = _read_pages(lessons)
    embeddings: dict[str, bytes] = {}
    if HAS_EMBEDDINGS and raw:
        try:
            texts = [f"{r[1]}. {r[3]}\n\n{r[5][:600]}" for r in raw]
            vecs = _get_emb_model().encode(texts, normalize_embeddings=True)
            embeddings = {r[0]: _vec_to_blob(vecs[i].tolist()) for i, r in enumerate(raw)}
        except Exception as e:
            log.warning("embedding_failed", error=str(e))
    if raw:
        con.executemany(
            "INSERT OR REPLACE INTO course_pages VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)",
            [
                (path, title, tags, summary, updated, content, embeddings.get(path), chash)
                for path, title, tags, summary, updated, content, chash in raw
            ],
        )

    current = {str(p) for p in _course_pages()}
    indexed = {r[0] for r in con.execute("SELECT path FROM course_pages").fetchall()}
    removed = indexed - current
    if removed:
        con.executemany("DELETE FROM course_pages WHERE path = ?", [(p,) for p in removed])
        log.info("course_index_pruned", removed_count=len(removed))

    if HAS_FTS:
        try:
            con.execute(
                "PRAGMA create_fts_index('course_pages', 'path', 'title', 'summary', 'content', "
                "overwrite=1)"
            )
        except Exception as exc:
            log.warning("fts_index_failed", table="course_pages", error=str(exc))
    return len(indexed - removed)


def _update_pages(con: duckdb.DuckDBPyConnection, pages: list[Path]) -> None:
    """Re-index a subset of pages without touching the rest of the corpus.

    Called for incremental updates when the schema is valid but some pages have
    changed content. Also handles deleted pages (tombstones in DB but not on disk).
    Lessons and wiki pages are refreshed independently: a course change leaves every
    `pages` row, the wiki FTS index and the edges table as they were.
    """
    lessons = [p for p in pages if p.is_relative_to(COURSES_DIR)]
    pages = [p for p in pages if not p.is_relative_to(COURSES_DIR)]
    indexed_lessons = {r[0] for r in con.execute("SELECT path FROM course_pages").fetchall()}
    if lessons or indexed_lessons - {str(p) for p in _course_pages()}:
        _ensure_fts(con)
        _upsert_lessons(con, lessons)
        log.info("incremental_course_update", stale_count=len(lessons))

    indexed_wiki = {r[0] for r in con.execute("SELECT path FROM pages").fetchall()}
    if not pages and not indexed_wiki - {str(p) for p in _wiki_pages()}:
        con.execute("UPDATE meta SET val = ? WHERE key = 'built_at'", [str(time.time())])
        return

    raw_pages = _read_pages(pages)
    if not raw_pages:
        # All changed pages were tombstones — skip re-embed, still prune deleted
        raw_pages = []

    # Recompute backlinks over full corpus — a page's backlink count depends on
    # all other pages' content. This is one dict comprehension, not re-embedding.
    all_raw = _read_pages(_wiki_pages())
    backlinks = _compute_backlinks(all_raw)

    # Embed only the changed pages
    embeddings: dict[str, bytes] = {}
    if HAS_EMBEDDINGS and raw_pages:
        try:
            model = _get_emb_model()
            texts = [f"{r[1]}. {r[3]}\n\n{r[5][:600]}" for r in raw_pages]
            vecs = model.encode(texts, normalize_embeddings=True)
            for i, row in enumerate(raw_pages):
                embeddings[row[0]] = _vec_to_blob(vecs[i].tolist())
        except Exception as e:
            log.warning("embedding_failed", error=str(e))

    if raw_pages:
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
                chash,
            )
            for path, title, tags, summary, updated, content, chash in raw_pages
        ]
        con.executemany("INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)

    # Update backlink counts for ALL pages whose count changed — handles the case
    # where an edited page removed a link to another page (R3 mitigation).
    indexed_paths = {r[0] for r in con.execute("SELECT path FROM pages").fetchall()}
    for path_str in indexed_paths:
        new_count = backlinks.get(path_str, 0)
        con.execute(
            "UPDATE pages SET backlinks = ? WHERE path = ? AND backlinks != ?",
            [new_count, path_str, new_count],
        )

    # Re-derive typed edges over the full corpus — an edited page's outbound links
    # change, and a new page can make other pages' links resolvable. Regex-only, cheap.
    con.execute("DELETE FROM edges")
    typed_edges = build_typed_edges([(row[0], row[1], row[5]) for row in all_raw])
    if typed_edges:
        con.executemany("INSERT INTO edges VALUES (?, ?, ?)", typed_edges)

    # Rebuild FTS index — DuckDB FTS has no row-level update API; overwrite=1 re-reads
    # indexed columns from the table (fast) but cannot be avoided.
    global HAS_FTS
    if HAS_FTS:
        try:
            con.execute(
                "PRAGMA create_fts_index('pages', 'path', 'title', 'summary', 'content', "
                "overwrite=1)"
            )
        except Exception as exc:
            log.warning("fts_index_failed", error=str(exc))

    # Prune deleted pages: in DB but not on disk
    removed = indexed_paths - {str(p) for p in _wiki_pages()}
    if removed:
        con.executemany("DELETE FROM pages WHERE path = ?", [(p,) for p in removed])
        for p in removed:
            con.execute("DELETE FROM edges WHERE source_path = ? OR target_path = ?", [p, p])
        log.info("index_pruned", removed_count=len(removed))

    con.execute("UPDATE meta SET val = ? WHERE key = 'built_at'", [str(time.time())])
    log.info("incremental_index_update", stale_count=len(pages))


def build_index(con: duckdb.DuckDBPyConnection, force: bool = False) -> None:
    """Build or incrementally update the DuckDB index over data/wiki/ and data/courses/.

    force=True drops and re-embeds the whole corpus (admin path: `make index-rebuild`).
    """
    if force or _index_needs_rebuild(con):
        _full_rebuild(con)
        return

    stale = _stale_pages(con)
    if not stale and not _has_deleted_pages(con):
        return  # index is fresh — nothing to do

    _update_pages(con, stale)


def _parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter via the same library wiki_parser and relinker use.

    Replaced a hand-rolled line parser that dropped YAML block-list tags
    (`tags:\\n  - rag`), indexing those pages with zero tags. Values are
    normalised to the shapes call sites rely on: `tags` is always a list of
    strings, every other value a string (`updated` parses as datetime.date
    otherwise and would leak into the DuckDB insert).
    """
    try:
        meta = dict(frontmatter.loads(text).metadata)
    except Exception:
        return {}
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    meta["tags"] = [str(t) for t in tags]
    for key, val in meta.items():
        if key != "tags" and not isinstance(val, str):
            meta[key] = "" if val is None else str(val)
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
    root = WIKI_DIR.resolve()
    for name in (domain, domain.replace("_", "-").lower()):
        candidate = WIKI_DIR / name
        if (
            candidate.is_dir()
            and candidate.resolve().is_relative_to(root)
            and not _is_private(candidate)
        ):
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
    table: str = "pages",
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
        FROM {table}
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


RRF_K = 60


def _rrf_ranks(order: list[int], k: int = RRF_K) -> dict[int, float]:
    """Map each row index to its 1/(k + rank) contribution for one channel.

    `order` is row indices best-first. Ties are not detected — callers sort on a
    channel's own scores, so equal scores take an arbitrary but stable order.
    """
    return {idx: 1.0 / (k + rank) for rank, idx in enumerate(order, start=1)}


def _rerank(query: str, rows: list[tuple], limit: int) -> list[tuple]:
    """Fuse BM25, semantic, and backlink channels with Reciprocal Rank Fusion.

    rows are 8-tuples (path, title, tags, summary, content, backlinks, embedding,
    score); returns 7-tuples with the fused score in place of the embedding.

    Each channel contributes 1/(RRF_K + rank) per row. RRF replaces the previous
    fixed 0.5/0.3/0.2 weighted blend of raw scores, whose weights only made sense
    when all three channels were on comparable scales — BM25 was max-normalised
    (so the top hit always scored 1.0 regardless of absolute relevance), cosine
    sat on its own [-1, 1], and backlinks were normalised against whatever the
    candidate set's maximum happened to be. Ranks are scale-free, so a channel
    can no longer dominate by having a wider numeric range.

    Channels are included only when they carry signal: the semantic channel needs
    embeddings, the backlink channel needs at least one non-zero count. A row
    absent from a channel contributes nothing for it rather than a zero rank,
    which is what keeps a missing embedding from being read as "maximally
    dissimilar".
    """
    if not rows:
        return []

    raw_scores = [r[7] for r in rows]
    have_bm25 = any(s is not None for s in raw_scores)

    channels: list[dict[int, float]] = []

    # Text channel: BM25 score order when fts ran, else the SQL fallback's own
    # ordering (title-match, backlinks, recency), which is already best-first.
    if have_bm25:
        text_order = sorted(
            range(len(rows)),
            key=lambda i: raw_scores[i] if raw_scores[i] is not None else float("-inf"),
            reverse=True,
        )
    else:
        text_order = list(range(len(rows)))
    channels.append(_rrf_ranks(text_order))

    if HAS_EMBEDDINGS and len(rows) > 1:
        try:
            model = _get_emb_model()
            q_vec = model.encode([query], normalize_embeddings=True)[0].tolist()
            sims = {i: _cosine(q_vec, _blob_to_vec(row[6])) for i, row in enumerate(rows) if row[6]}
            if sims:
                sem_order = sorted(sims, key=lambda i: sims[i], reverse=True)
                channels.append(_rrf_ranks(sem_order))
        except Exception as e:
            log.warning("hybrid_rerank_failed", error=str(e))

    # Backlinks only rank when they discriminate — an all-zero column would
    # otherwise inject an arbitrary tie-break order as if it were evidence.
    backlinks = {i: row[5] for i, row in enumerate(rows) if row[5]}
    if backlinks:
        bl_order = sorted(backlinks, key=lambda i: backlinks[i], reverse=True)
        channels.append(_rrf_ranks(bl_order))

    fused = [(sum(ch.get(i, 0.0) for ch in channels), i, row) for i, row in enumerate(rows)]
    # Sort on (score, -original index) so equal-scoring rows keep candidate order.
    fused.sort(key=lambda t: (t[0], -t[1]), reverse=True)
    return [(*row[:6], score) for score, _, row in fused[:limit]]


def _degradation_reasons(con: duckdb.DuckDBPyConnection, *, has_fts: bool) -> list[str]:
    """Names of the retrieval capabilities currently missing, best-effort.

    `get_con()` runs build_index(), so a stale index normally self-heals before
    any search. It stays stale only when that refresh failed (unreadable page,
    write error) — which is exactly the case worth surfacing, because results
    are then served from content that no longer matches disk.
    """
    reasons: list[str] = []
    if not has_fts:
        reasons.append("no_fts")
    try:
        if _stale_pages(con) or _has_deleted_pages(con):
            reasons.append("stale_index")
    except Exception as e:  # never let a health probe break retrieval
        log.warning("degradation_probe_failed", error=str(e))
    return reasons


def _search_rows(
    query: str, domain: str = "", limit: int = 10, tool: str = "search_wiki", expand: bool = False
) -> tuple[list[tuple], list[str]]:
    """Ranked search returning raw rows — the single search core.

    An empty `domain` searches the wiki only, as does any wiki directory or tag.
    `course` or `course/<subject>` searches lessons only. The corpora have separate
    BM25 statistics, so their scores are not comparable and are never merged here.

    Returns `(rows, degraded)`: up to `limit` 7-tuples (path, title, tags,
    summary, content, backlinks, score) best first, plus the names of any
    retrieval capabilities that were unavailable for this query (`no_fts`,
    `stale_index`) — empty when the pipeline ran at full strength. Callers that
    surface results to a model or a human are expected to pass that list on;
    silently serving LIKE-fallback results as if they were BM25-ranked is what
    this second element exists to prevent.

    Candidates come from BM25 (DuckDB fts); falls back to a tokenized per-term
    LIKE match when fts is unavailable or matches nothing. Logs retrieval
    telemetry under `tool`.

    expand=True additionally merges pages one typed hop from the results into
    the ranked rows (LIB-114 Step 2). Default off — production `search_wiki`
    keeps its prose expansion section; this path is exercised by the eval.
    """
    table = "pages"
    if _is_course_domain(domain):
        table = "course_pages"
        course_dir = _resolve_course_dir(domain)
        if course_dir is None:
            _log_retrieval(tool, query=query, domain=domain, n_results=0, top_paths=[], degraded=[])
            return [], []
        tag_filter, tag_params = "AND starts_with(path, ?)", [f"{course_dir.as_posix()}/"]
    else:
        tag_filter, tag_params = _domain_filter(domain)

    con = get_con()
    try:
        rows: list[tuple] = []
        fts_ok = _ensure_fts(con)
        degraded = _degradation_reasons(con, has_fts=fts_ok)
        if fts_ok:
            # A subquery, not an alias in WHERE: duckdb 2.0 rejects that form because
            # match_bm25 has side effects.
            sql = f"""
                SELECT * FROM (
                    SELECT path, title, tags, summary, content, backlinks, embedding,
                           fts_main_{table}.match_bm25(path, ?) AS score
                    FROM {table}
                    WHERE TRUE {tag_filter}
                )
                WHERE score IS NOT NULL
                ORDER BY score DESC
                LIMIT ?
            """
            try:
                rows = con.execute(sql, [query, *tag_params, limit * 3]).fetchall()
            except Exception as e:
                # fts loaded but the query failed — results are about to come
                # from LIKE, so this is the same degradation as no fts at all.
                log.warning("fts_query_failed", error=str(e))
                rows = []
                if "no_fts" not in degraded:
                    degraded.append("no_fts")

        if not rows:
            rows = _like_candidates(con, query, tag_filter, tag_params, limit, table)
    finally:
        con.close()

    if degraded:
        log.warning("retrieval_degraded", tool=tool, reasons=degraded)

    if not rows:
        _log_retrieval(
            tool, query=query, domain=domain, n_results=0, top_paths=[], degraded=degraded
        )
        return [], degraded

    ranked = _rerank(query, rows, limit)
    expansion_edges: list[tuple[str, str, str]] = []
    if expand:
        ranked, expansion_edges = _expand_rows(ranked, limit)
    extra = {"expansion_edges": expansion_edges} if expansion_edges else {}
    _log_retrieval(
        tool,
        query=query,
        domain=domain,
        n_results=len(ranked),
        top_paths=[r[0] for r in ranked[:5]],
        degraded=degraded,
        **extra,
    )
    return ranked, degraded


# Score multiplier for expanded pages relative to the best seed that reached
# them. Pre-registered at 0.5 (plan LIB-114, Open Question 4); the eval's
# sensitivity check overrides the module global, so read at call time.
EXPANSION_DECAY = 0.5


def _expand_rows(ranked: list[tuple], limit: int) -> tuple[list[tuple], list[tuple[str, str, str]]]:
    """Merge one-hop typed neighbours into ranked rows (LIB-114 Step 2).

    Each neighbour scores EXPANSION_DECAY × the best score among the seeds that
    reached it. The merge is a stable sort by score with direct rows first, so
    an expanded page never displaces a direct hit whose score meets or exceeds
    its own — it fills ranks after the last such hit. Returns the re-capped
    rows plus the fired edges as (seed, neighbour, relationship) triples.
    """
    seed_scores = {r[0]: r[6] for r in ranked}
    con = get_con()
    try:
        edges = con.execute("SELECT source_path, target_path, relationship FROM edges").fetchall()
        neighbours = expand_one_hop(list(seed_scores), edges, max_expansions=limit)
        if not neighbours:
            return ranked, []
        placeholders = ", ".join("?" for _ in neighbours)
        nb_rows = {
            row[0]: row
            for row in con.execute(
                f"SELECT path, title, tags, summary, content, backlinks FROM pages "
                f"WHERE path IN ({placeholders})",
                [path for path, _, _ in neighbours],
            ).fetchall()
        }
    finally:
        con.close()

    expanded: list[tuple] = []
    fired: list[tuple[str, str, str]] = []
    for nb_path, rel, seeds in neighbours:
        nb_row = nb_rows.get(nb_path)
        if nb_row is None:
            continue
        expanded.append((*nb_row, EXPANSION_DECAY * max(seed_scores[s] for s in seeds)))
        fired.extend((seed, nb_path, rel) for seed in sorted(seeds))

    # Stable sort: equal scores keep direct-before-expanded order, and expanded
    # rows keep expand_one_hop's distinct-seed-count ordering among themselves.
    merged = ranked + expanded
    merged.sort(key=lambda r: r[6], reverse=True)
    return merged[:limit], fired


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_wiki(query: str, domain: str = "", limit: int = 10, expand: bool = False) -> str:
    """Search the wiki and course lessons using hybrid search (BM25 + semantic + backlink rank).

    Results are ranked by a blend of: BM25 relevance, semantic closeness
    (if sentence-transformers is installed), and inbound backlink count.

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
    in_courses = _is_course_domain(domain)
    # /compact-wiki reads tool="search_wiki" telemetry as evidence about wiki pages.
    tool = "search_courses" if in_courses else "search_wiki"
    rows, degraded = _search_rows(query, domain=domain, limit=limit, tool=tool)
    warning = _degraded_notice(degraded)
    lessons = "" if domain else _course_lessons_section(query)

    if not rows:
        suffix = f" in domain '{domain}'" if domain else ""
        return f"{warning}No wiki pages found for: {query!r}{suffix}{lessons}"

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

        location = (
            f"Page: `{_course_ref(path)}`\nDomain: {_course_domain(path)}\n"
            if in_courses
            else f"Path: `{path}`\nTags: {tags} · Backlinks: {backlinks}\n"
        )
        results.append(
            f"**{title}**\n"
            f"{location}"
            f"Summary: {summary}\n" + (f"Snippet: ...{snippet}..." if snippet else "")
        )

    body = warning + f"Found {len(rows)} result(s):\n\n" + "\n\n---\n\n".join(results)

    if expand:
        body += _expansion_section([r[0] for r in rows])

    return body + lessons


UNSCOPED_LESSON_LIMIT = 3


def _course_lessons_section(query: str) -> str:
    """Best lessons for an unscoped search, kept out of the wiki ranking ('' if none)."""
    if not COURSES_DIR.is_dir():
        return ""
    rows, _ = _search_rows(
        query, domain=COURSE_DOMAIN, limit=UNSCOPED_LESSON_LIMIT, tool="search_courses"
    )
    if not rows:
        return ""
    lines = [f"- **{r[1]}** (`{_course_ref(r[0])}`)\n  {r[3]}" for r in rows]
    return (
        f"\n\n---\n\n**Course lessons** (read with read_page; "
        f'search with domain="{COURSE_DOMAIN}"):\n\n' + "\n".join(lines)
    )


# Degradation reason → what the caller loses. Phrased for a model reading the
# tool output: it should know to widen its query or re-read a page rather than
# treat a thin result set as evidence the wiki has nothing.
_DEGRADED_NOTES = {
    "no_fts": "full-text search is unavailable, so results come from a weaker "
    "substring match and ranking is less reliable",
    "stale_index": "the search index is behind the files on disk, so results may "
    "omit or misquote recent edits",
}


def _degraded_notice(degraded: list[str]) -> str:
    """Render a leading warning block for degraded retrieval ('' when healthy)."""
    if not degraded:
        return ""
    notes = [_DEGRADED_NOTES.get(r, r) for r in degraded]
    return "**DEGRADED RETRIEVAL** — " + "; ".join(notes) + ".\n\n"


def _expansion_section(seed_paths: list[str]) -> str:
    """Render the one-hop typed-relationship neighbourhood of a result set.

    Returns an empty string when nothing is one hop away, so a wiki region with
    no typed annotations degrades to plain search rather than an empty header.
    """
    con = get_con()
    try:
        edges = con.execute("SELECT source_path, target_path, relationship FROM edges").fetchall()
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
        f"— {rel} of `{Path(sorted(seeds)[0]).stem}`\n"
        f"  {meta.get(path, ('', ''))[1]}"
        for path, rel, seeds in neighbours
    ]
    return (
        f"\n\n---\n\n**{len(neighbours)} page(s) one typed hop away** "
        f"(prerequisite-for / extends):\n\n" + "\n".join(lines)
    )


def _read_lesson(ref: str, not_found: str) -> str:
    """Serve a `course/<relative path>` ref (`.md` optional) from inside the course root only.

    Only COURSES_DIR counts here, so `course/../wiki/...` fails even for a public wiki page.
    """
    # lstrip keeps `course//etc/passwd` relative: an absolute part would replace the root.
    target = COURSES_DIR / ref.removeprefix(COURSE_DOMAIN).lstrip("/")
    if target.suffix != ".md":
        target = target.with_name(f"{target.name}.md")
    try:
        inside = target.resolve().is_relative_to(COURSES_DIR.resolve())
        readable = inside and target.is_file() and not _is_private(target)
    except (OSError, RuntimeError, ValueError):
        readable = False
    if not readable:
        _log_retrieval("read_page", path=ref, found=False, course=True)
        return not_found
    _log_retrieval("read_page", path=str(target), found=True, course=True)
    return target.read_text(encoding="utf-8", errors="replace")


def _read_page_text(path_or_title: str) -> str:
    """Resolve a page by path, wiki-relative path, slug, or title and return its text.

    The single page-read core — the read_page MCP tool and the chat agent both
    call this, so private exclusion and telemetry are enforced in one place.
    Lessons are reached by `course/<relative path>` or by the absolute path search returns.
    Slug and title lookup stays wiki-only: a loose match over 749 lessons would turn a
    clean miss, or a unique wiki match, into a wrong or ambiguous answer.
    """
    # Private pages are indistinguishable from missing ones — a distinct "denied"
    # message would itself confirm the page exists.
    not_found = f"Page not found: {path_or_title!r}. Run search_wiki to find the right path."

    if _is_course_domain(path_or_title):
        return _read_lesson(path_or_title, not_found)

    candidate = Path(path_or_title)
    if candidate.exists():
        resolved = candidate.resolve()
        if resolved.is_relative_to(COURSES_DIR.resolve()):
            ref = f"{COURSE_DOMAIN}/{resolved.relative_to(COURSES_DIR.resolve()).as_posix()}"
            return _read_lesson(ref, not_found)
        if not resolved.is_relative_to(WIKI_DIR.resolve()):
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

    slug = slugify(path_or_title)
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
    """Read a specific wiki page or course lesson by file path or title.

    Args:
        path_or_title: A relative path like 'data/wiki/rag/rag-retrieval-strategies.md',
                       a page title like 'RAG Retrieval Strategies', or a lesson as
                       'course/<subject>/<module>/<lesson>.md'. Titles resolve to wiki pages only.

    Returns:
        Full page content, or an error message if not found.
    """
    return _read_page_text(path_or_title)


def _unknown_domain(domain: str) -> str:
    valid = ", ".join(_domains() + _course_domains())
    return f"Unknown domain: {domain!r}. Valid domains: {valid}"


def _frontmatter_of(path: Path) -> dict:
    """Frontmatter of a page, {} when the file is absent."""
    if not path.is_file():
        return {}
    return _parse_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))


def _list_course_domain(domain: str) -> str:
    """Courses for `course`, modules for `course/<subject>`, lessons for anything deeper."""
    root = _resolve_course_dir(domain)
    if root is None:
        return _unknown_domain(domain)
    depth = len(root.relative_to(COURSES_DIR).parts)
    label = (
        f"{COURSE_DOMAIN}/{root.relative_to(COURSES_DIR).as_posix()}" if depth else COURSE_DOMAIN
    )

    if depth < 2:
        meta_file = "_module.md" if depth else "_course.md"
        kind = "module" if depth else "course"
        lines = []
        for child in sorted(d for d in root.iterdir() if d.is_dir()):
            n_lessons = len(_course_pages(child))
            if not n_lessons:
                continue
            meta = _frontmatter_of(child / meta_file)
            lines.append(
                f"- **{meta.get('title', child.name)}** (`{label}/{child.name}`) · "
                f"{n_lessons} lesson(s)\n  {meta.get('summary', '')}"
            )
        _log_retrieval("list_domain", domain=domain, n_results=len(lines))
        if not lines:
            return f"No pages found in domain '{domain}'"
        return f"**{len(lines)} {kind}(s) in `{label}`**:\n\n" + "\n".join(lines)

    lessons = sorted(_course_pages(root))
    _log_retrieval("list_domain", domain=domain, n_results=len(lessons))
    if not lessons:
        return f"No pages found in domain '{domain}'"
    lines = [_course_line(p) for p in lessons]
    return f"**{len(lines)} lesson(s) in `{label}`**:\n\n" + "\n".join(lines)


def _course_line(page: Path) -> str:
    meta = _frontmatter_of(page)
    return (
        f"- **{meta.get('title', page.stem)}** (`{_course_ref(page)}`)\n  {meta.get('summary', '')}"
    )


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
    if _is_course_domain(domain):
        return _list_course_domain(domain)

    domain_dir = _resolve_domain_dir(domain)
    if domain_dir is None:
        return _unknown_domain(domain)

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
    """List wiki pages and course lessons, optionally filtered by tag or directory.

    Args:
        tag:       Domain tag to filter (e.g. 'adk', 'langgraph', 'rag')
        directory: Subdirectory to list — any domain directory under data/wiki/
                   (e.g. rag, langgraph, context, interview), or 'course' or
                   'course/<subject>' for lessons. Omitted: the wiki, then all lessons.

    Returns:
        List of pages with title, tags, summary, and backlink count.
    """
    lessons: list[Path] = []
    if directory:
        if ".." in directory or directory.startswith("/"):
            raise ValueError(f"Invalid directory: {directory!r}")
        search_dir = WIKI_DIR / directory
        if not search_dir.resolve().is_relative_to(WIKI_DIR.resolve()):
            raise ValueError(f"Directory escapes wiki root: {directory!r}")
    else:
        search_dir = WIKI_DIR
        lessons = _course_pages()
    pages = [
        p for p in search_dir.rglob("*.md") if not p.name.startswith("_") and not _is_private(p)
    ]
    if directory and _is_course_domain(directory):
        course_dir = _resolve_course_dir(directory)
        lessons = _course_pages(course_dir) if course_dir else []
        pages = []

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

    for lesson in sorted(lessons):
        meta = _frontmatter_of(lesson)
        if tag and tag not in meta.get("tags", []):
            continue
        results.append(_course_line(lesson))

    if not results:
        return (
            "No pages found"
            + (f" with tag '{tag}'" if tag else "")
            + (f" in '{directory}'" if directory else "")
        )

    _log_retrieval("list_pages", tag=tag, directory=directory, n_results=len(results))
    header = f"**{len(results)} page(s)**" + (f" tagged '{tag}'" if tag else "") + ":\n\n"
    return header + "\n".join(results)


# Courses are far bigger than wiki domains: a whole subject is megabytes of context. The
# largest AI Engineering module is under this limit.
COURSE_BRIEFING_MAX_CHARS = 1_000_000


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
    if _is_course_domain(domain):
        course_dir = _resolve_course_dir(domain)
        if course_dir is None:
            return _unknown_domain(domain)
        pages = sorted(_course_pages(course_dir))
        size = sum(p.stat().st_size for p in pages)
        if size > COURSE_BRIEFING_MAX_CHARS:
            return (
                f"Domain '{domain}' is too large to brief ({len(pages)} lessons, {size} bytes). "
                f"Use list_domain to pick a module, or search_wiki with this domain."
            )
    else:
        domain_dir = _resolve_domain_dir(domain)
        if domain_dir is None:
            return _unknown_domain(domain)
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
    import sys

    if "--rebuild" in sys.argv:
        with duckdb.connect(str(DB_PATH)) as con:
            build_index(con, force=True)
        sys.exit(0)

    log.info(
        "starting_mcp_server",
        wiki_dir=str(WIKI_DIR),
        courses_dir=str(COURSES_DIR),
        hybrid_search=HAS_EMBEDDINGS,
    )
    mcp.run()
