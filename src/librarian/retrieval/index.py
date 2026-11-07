"""The DuckDB search index over data/wiki/ and data/courses/: build, refresh, open.

Tables: `pages` and `course_pages` (text, hash, backlinks, embedding), `edges` (typed
relationships, wiki only), `meta` (schema version, build time), plus an FTS index per page table.
Lessons live in their own table and FTS index because BM25 statistics, backlinks and typed edges
are corpus-wide: sharing a table would change wiki rankings.

Write ownership. DuckDB lets one process hold a read-write connection to a file at a time, and
the API (`librarian api`) and the MCP server (`librarian mcp`) both open this one. `open_index`
is the single entry point: it connects with a bounded retry on lock conflicts, so a second process
waits for the first one's (short) refresh or query instead of failing, then refreshes the index
if it is behind the files. Whoever finds the index stale writes it, one at a time; the other waits
and then finds it fresh. See src/librarian/README.md ("Index ownership").
"""

from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path

import duckdb

from librarian.log_config import get_logger
from librarian.retrieval import corpus, embeddings
from librarian.retrieval.graph_expansion import build_typed_edges
from librarian.wiki.common import (
    ANY_TYPED_LINK_RE,
    CANONICAL_LINK_TYPES,
    WIKILINK_RE,
    parse_frontmatter,
    slugify,
    text_aliases,
)

log = get_logger(__name__)

# 6→7: adds content_hash for incremental indexing (LIB-124). 7→8: adds course_pages.
SCHEMA_VERSION = "8"

# How long a connection waits for another process's lock. A refresh of a few pages takes well
# under a second and a full rebuild about twenty, so this outlasts both.
LOCK_TIMEOUT_S = 60.0

# Optional FTS — installed per connection; absence is non-fatal but logged
HAS_FTS = False


class IndexBusyError(RuntimeError):
    """Another process held the index lock for longer than LOCK_TIMEOUT_S."""


def ensure_fts(con: duckdb.DuckDBPyConnection) -> bool:
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


# ---------------------------------------------------------------------------
# Index freshness check
# ---------------------------------------------------------------------------


def needs_rebuild(con: duckdb.DuckDBPyConnection) -> bool:
    """Return True if the index is absent or schema-mismatched (full rebuild required).

    Stale pages after a valid schema are handled by stale_pages(), which uses
    content hashes for page-level change detection.
    """
    try:
        version = con.execute("SELECT val FROM meta WHERE key = 'schema_version'").fetchone()
        # Schema is valid when version matches — stale pages handled by stale_pages()
        return not version or version[0] != SCHEMA_VERSION
    except Exception:
        return True


def _content_hash(path: Path) -> str:
    """SHA-256 of page bytes, first 16 hex chars — same convention as embeddings.compute_embeddings."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _is_unindexed(path: Path) -> bool:
    """True for a page `read_pages` never indexes: a tombstone or unparseable frontmatter."""
    meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
    return not meta or "tombstone" in meta.get("tags", [])


def stale_pages(con: duckdb.DuckDBPyConnection) -> list[Path]:
    """Return paths of wiki pages and lessons whose content hash differs from the indexed hash.

    Returns an empty list when the index is fully fresh and no pages have been deleted.
    A tombstone with no index row is correct, not stale: read_pages never indexes one. One that
    still has a row was retired since the last build, so it stays stale until _update_pages prunes it.
    """
    try:
        indexed: dict[str, str] = {
            row[0]: row[1]
            for table in ("pages", "course_pages")
            for row in con.execute(f"SELECT path, content_hash FROM {table}").fetchall()
        }
    except Exception:
        return corpus.wiki_pages() + corpus.course_pages()

    return [
        p
        for p in corpus.wiki_pages() + corpus.course_pages()
        if indexed.get(str(p)) != _content_hash(p) and (str(p) in indexed or not _is_unindexed(p))
    ]


def has_deleted_pages(con: duckdb.DuckDBPyConnection) -> bool:
    """Return True if any page in the index no longer exists on disk."""
    try:
        indexed_paths = {
            r[0]
            for table in ("pages", "course_pages")
            for r in con.execute(f"SELECT path FROM {table}").fetchall()
        }
    except Exception:
        return False
    current_paths = {str(p) for p in corpus.wiki_pages() + corpus.course_pages()}
    return bool(indexed_paths - current_paths)


# ---------------------------------------------------------------------------
# Index build
# ---------------------------------------------------------------------------


def compute_backlinks(pages: list[tuple]) -> dict[str, int]:
    """Count inbound wikilinks for each page slug."""
    slug_to_path: dict[str, str] = {}
    for path, title, *_ in pages:
        slug = slugify(title)
        slug_to_path[slug] = path
        # also register by stem
        stem = Path(path).stem
        slug_to_path[stem] = path
    for row in pages:
        for alias in text_aliases(row[5]):
            slug_to_path.setdefault(slugify(alias), row[0])

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


def read_pages(paths: list[Path]) -> list[tuple]:
    """Parse frontmatter + text for the given pages.

    Returns tuples of (path_str, title, tags, summary, updated, content, content_hash).
    Tombstone pages and pages with unparseable frontmatter are excluded.
    """
    raw: list[tuple] = []
    for page in paths:
        text = page.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        if not meta:
            # Unparseable frontmatter (already warned): it may be a broken tombstone, so do not
            # index it as a live page.
            log.warning("page_skipped_bad_frontmatter", path=str(page))
            continue
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


def _embed_pages(raw: list[tuple]) -> dict[str, bytes]:
    """Vector blobs by path for `read_pages` tuples; {} when embeddings are unavailable or fail.

    Embeds `title. summary` plus the first 600 characters of the whole file text.
    """
    if not embeddings.HAS_EMBEDDINGS:
        return {}
    try:
        texts = [f"{r[1]}. {r[3]}\n\n{r[5][:600]}" for r in raw]
        vecs = embeddings.encode(texts)
        return {row[0]: embeddings.vec_to_blob(vecs[i].tolist()) for i, row in enumerate(raw)}
    except Exception as e:
        log.warning("embedding_failed", error=str(e))
        return {}


def _create_fts_index(con: duckdb.DuckDBPyConnection, table: str) -> bool:
    """(Re)build one table's FTS index. DuckDB FTS has no row-level update API; overwrite=1
    re-reads the indexed columns from the table (fast) but cannot be avoided."""
    try:
        con.execute(
            f"PRAGMA create_fts_index('{table}', 'path', 'title', 'summary', 'content', "
            "overwrite=1)"
        )
        return True
    except Exception as exc:
        extra = {} if table == "pages" else {"table": table}
        log.warning("fts_index_failed", error=str(exc), **extra)
        return False


def _full_rebuild(con: duckdb.DuckDBPyConnection) -> None:
    """Drop and recreate all index tables, then re-index every wiki page and lesson.

    Called when the schema version mismatches or the index is absent.
    After this runs, subsequent calls take the incremental path via stale_pages().
    """
    global HAS_FTS
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

    ensure_fts(con)

    # Collect all pages
    raw_pages = read_pages(sorted(corpus.wiki_pages()))

    # raw_pages tuples: (path, title, tags, summary, updated, content, content_hash)
    backlinks = compute_backlinks(raw_pages)

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
    vectors = _embed_pages(raw_pages)

    rows = [
        (path, title, tags, summary, updated, content, backlinks.get(path, 0), vectors.get(path), h)
        for path, title, tags, summary, updated, content, h in raw_pages
    ]

    con.executemany(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )

    if HAS_FTS and not _create_fts_index(con, "pages"):
        HAS_FTS = False

    n_lessons = _upsert_lessons(con, sorted(corpus.course_pages()))

    con.execute("INSERT INTO meta VALUES ('schema_version', ?)", [SCHEMA_VERSION])
    con.execute("INSERT INTO meta VALUES ('built_at', ?)", [str(time.time())])

    log.info(
        "index_built",
        page_count=len(rows),
        lesson_count=n_lessons,
        with_embeddings=bool(vectors),
        typed_edges=len(typed_edges),
        unrecognized_annotations=n_unrecognized,
    )


def _upsert_lessons(con: duckdb.DuckDBPyConnection, lessons: list[Path]) -> int:
    """Embed and write lessons to course_pages, prune removed ones, refresh their FTS index.

    Lessons carry no backlinks or edges: a wikilink from a lesson is not evidence about a
    wiki page, and a lesson's title or stem must not capture a wiki link's resolution.
    """
    raw = read_pages(lessons)
    vectors = _embed_pages(raw) if raw else {}
    if raw:
        con.executemany(
            "INSERT OR REPLACE INTO course_pages VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)",
            [
                (path, title, tags, summary, updated, content, vectors.get(path), chash)
                for path, title, tags, summary, updated, content, chash in raw
            ],
        )

    current = {str(p) for p in corpus.course_pages()}
    indexed = {r[0] for r in con.execute("SELECT path FROM course_pages").fetchall()}
    removed = indexed - current
    if removed:
        con.executemany("DELETE FROM course_pages WHERE path = ?", [(p,) for p in removed])
        log.info("course_index_pruned", removed_count=len(removed))

    if HAS_FTS:
        _create_fts_index(con, "course_pages")
    return len(indexed - removed)


def _update_pages(con: duckdb.DuckDBPyConnection, pages: list[Path]) -> None:
    """Re-index a subset of pages without touching the rest of the corpus.

    Called for incremental updates when the schema is valid but some pages have
    changed content. Also handles deleted pages (tombstones in DB but not on disk).
    Lessons and wiki pages are refreshed independently: a course change leaves every
    `pages` row, the wiki FTS index and the edges table as they were.
    """
    lessons = [p for p in pages if p.is_relative_to(corpus.COURSES_DIR)]
    pages = [p for p in pages if not p.is_relative_to(corpus.COURSES_DIR)]
    indexed_lessons = {r[0] for r in con.execute("SELECT path FROM course_pages").fetchall()}
    if lessons or indexed_lessons - {str(p) for p in corpus.course_pages()}:
        ensure_fts(con)
        _upsert_lessons(con, lessons)
        log.info("incremental_course_update", stale_count=len(lessons))

    indexed_wiki = {r[0] for r in con.execute("SELECT path FROM pages").fetchall()}
    if not pages and not indexed_wiki - {str(p) for p in corpus.wiki_pages()}:
        con.execute("UPDATE meta SET val = ? WHERE key = 'built_at'", [str(time.time())])
        return

    # All changed pages may be tombstones (no raw pages): skip re-embed, still prune deleted.
    raw_pages = read_pages(pages)

    # Recompute backlinks over full corpus — a page's backlink count depends on
    # all other pages' content. This is one dict comprehension, not re-embedding.
    all_raw = read_pages(corpus.wiki_pages())
    backlinks = compute_backlinks(all_raw)

    # Embed only the changed pages
    vectors = _embed_pages(raw_pages) if raw_pages else {}

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
                vectors.get(path),
                h,
            )
            for path, title, tags, summary, updated, content, h in raw_pages
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

    # Prune deleted and newly tombstoned pages: in DB but no longer indexable. Before the FTS
    # rebuild, which would otherwise keep their text searchable.
    removed = indexed_paths - {row[0] for row in all_raw}
    if removed:
        con.executemany("DELETE FROM pages WHERE path = ?", [(p,) for p in removed])
        for p in removed:
            con.execute("DELETE FROM edges WHERE source_path = ? OR target_path = ?", [p, p])
        log.info("index_pruned", removed_count=len(removed))

    # Rebuild the FTS index (see _create_fts_index). HAS_FTS is per process: a fresh one has
    # not loaded the extension yet, so load it here rather than trust the global.
    if ensure_fts(con):
        _create_fts_index(con, "pages")

    con.execute("UPDATE meta SET val = ? WHERE key = 'built_at'", [str(time.time())])
    log.info("incremental_index_update", stale_count=len(pages))


def build_index(con: duckdb.DuckDBPyConnection, force: bool = False) -> None:
    """Build or incrementally update the DuckDB index over data/wiki/ and data/courses/.

    force=True drops and re-embeds the whole corpus (admin path: `make index-rebuild`).
    """
    if force or needs_rebuild(con):
        _full_rebuild(con)
        return

    stale = stale_pages(con)
    if not stale and not has_deleted_pages(con):
        return  # index is fresh — nothing to do

    _update_pages(con, stale)


# ---------------------------------------------------------------------------
# Opening
# ---------------------------------------------------------------------------


def connect() -> duckdb.DuckDBPyConnection:
    """Open the index file read-write, waiting for another process's lock instead of failing.

    DuckDB allows one read-write process per file, so with the API and the MCP server both
    running, an open that lands inside the other's refresh or query raises `IOException: Could
    not set lock`. The holder is short-lived (it closes after each call), so back off and retry
    until LOCK_TIMEOUT_S; any other error, or a timeout, is raised.
    """
    deadline = time.monotonic() + LOCK_TIMEOUT_S
    delay = 0.02
    warned = False
    while True:
        try:
            return duckdb.connect(str(corpus.DB_PATH))
        except duckdb.IOException as exc:
            if "lock" not in str(exc).lower():
                raise
            if time.monotonic() >= deadline:
                raise IndexBusyError(
                    f"{corpus.DB_PATH} is locked by another process (waited {LOCK_TIMEOUT_S:.0f}s)"
                ) from exc
            if not warned:
                log.info("index_locked_waiting", path=str(corpus.DB_PATH))
                warned = True
            time.sleep(delay + random.uniform(0, delay))
            delay = min(delay * 2, 0.5)


def open_index() -> duckdb.DuckDBPyConnection:
    """A connection to an up-to-date index, refreshed from disk first. The caller closes it."""
    con = connect()
    build_index(con)
    return con


def rebuild_index() -> None:
    """Drop and re-embed the whole index (`librarian mcp --rebuild`, `make index-rebuild`)."""
    con = connect()
    try:
        build_index(con, force=True)
    finally:
        con.close()
