"""Codemap indexer — orchestrates repo walk → content-hash check → parse → upsert.

Reads the repo list (``default_repos_file()``: your gitignored repos.local.txt, else the
tracked repos.txt), for each configured repo walks source files
matching a registered language (see librarian.tools.codemap.parser.LANGUAGES), skips files
whose hash equals ``files.content_hash`` in the DB (the DB is the only change-tracking state, so
a deleted or rebuilt DB is always repopulated), parses changed files with
librarian.tools.codemap.parser, and upserts symbols/files/edges into .code_index.duckdb,
one transaction per file. Removed files are pruned from the DB along with edges into them.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import duckdb
import structlog

from librarian.config import discover_root
from librarian.tools.codemap import db, manifest, parser, symbol_embeddings

log = structlog.get_logger()

CODEMAP_DIR = Path(__file__).parent
SHARED_REPOS_FILE = CODEMAP_DIR / "repos.txt"
LOCAL_REPOS_FILE = CODEMAP_DIR / "repos.local.txt"


def default_repos_file() -> Path:
    """`$CODEMAP_REPOS_FILE`, else the gitignored `repos.local.txt`, else the tracked `repos.txt`."""
    env = os.environ.get("CODEMAP_REPOS_FILE")
    if env:
        return Path(env).expanduser()
    return LOCAL_REPOS_FILE if LOCAL_REPOS_FILE.is_file() else SHARED_REPOS_FILE


def _repo_path(raw: str) -> Path:
    """`~` is the user's home; a relative path is relative to the librarian checkout."""
    path = Path(raw).expanduser()
    return path if path.is_absolute() else (discover_root() / path).resolve()


_EXCLUDE_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build"}


@dataclass
class RepoConfig:
    repo_id: str
    root_path: Path


def load_repos(repos_file: Path | None = None) -> list[RepoConfig]:
    repos_file = repos_file or default_repos_file()
    if not repos_file.exists():
        return []
    repos: list[RepoConfig] = []
    for line in repos_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        root_path = _repo_path(parts[0])
        repo_id = parts[1] if len(parts) > 1 else root_path.name
        repos.append(RepoConfig(repo_id=repo_id, root_path=root_path))
    return repos


def _iter_source_files(root: Path) -> Iterator[Path]:
    """Yield indexable files under root, never descending into excluded directories.

    Exclusion is tested on directory names below ``root`` only, so a repo that itself
    lives under a directory called ``build`` is still indexed.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _EXCLUDE_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix in parser.LANGUAGES:
                yield path


def _insert_many(con: duckdb.DuckDBPyConnection, sql: str, rows: list[list]) -> None:
    if rows:  # DuckDB's executemany rejects an empty parameter list
        con.executemany(sql, rows)


def index_repo(con: duckdb.DuckDBPyConnection, repo: RepoConfig, dry_run: bool = False) -> dict:
    """Index one repo. Returns counts: parsed, skipped, removed, errors."""
    if not repo.root_path.is_dir():
        log.warning("codemap.repo_not_found", repo_id=repo.repo_id, path=str(repo.root_path))
        return {"parsed": 0, "skipped": 0, "removed": 0, "errors": 1}

    counts = {"parsed": 0, "skipped": 0, "removed": 0, "errors": 0}
    seen_file_ids: set[str] = set()
    first_language: str | None = None
    known_hashes: dict[str, str] = dict(
        con.execute(
            "SELECT file_id, content_hash FROM files WHERE repo_id = ?", [repo.repo_id]
        ).fetchall()
    )

    for path in _iter_source_files(repo.root_path):
        rel_path = str(path.relative_to(repo.root_path))
        file_id = f"{repo.repo_id}:{rel_path}"
        seen_file_ids.add(file_id)
        lang_name = parser.LANGUAGES[path.suffix].name
        first_language = first_language or lang_name

        content_hash = manifest.file_hash(path)
        if known_hashes.get(file_id) == content_hash:
            counts["skipped"] += 1
            continue

        if dry_run:
            counts["parsed"] += 1
            continue

        try:
            result = parser.parse_file(str(path))
        except Exception as e:
            log.warning("codemap.parse_failed", file_id=file_id, error=str(e))
            counts["errors"] += 1
            continue

        loc = path.read_text(errors="replace").count("\n") + 1
        con.begin()
        try:
            _reset_inbound_call_edges(con, file_id)
            con.execute("DELETE FROM symbols WHERE file_id = ?", [file_id])
            con.execute("DELETE FROM edges WHERE src_file_id = ?", [file_id])
            con.execute(
                """
                INSERT OR REPLACE INTO files
                (file_id, repo_id, rel_path, language, content_hash, loc, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    file_id,
                    repo.repo_id,
                    rel_path,
                    lang_name,
                    content_hash,
                    loc,
                    date.today().isoformat(),
                ],
            )
            _insert_many(
                con,
                """
                INSERT OR REPLACE INTO symbols
                (symbol_id, file_id, repo_id, name, kind, signature, docstring,
                 parent_scope, start_line, end_line, start_byte, end_byte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    [
                        f"{file_id}:{sym.start_byte}",
                        file_id,
                        repo.repo_id,
                        sym.name,
                        sym.kind,
                        sym.signature,
                        sym.docstring,
                        sym.parent_scope,
                        sym.start_line,
                        sym.end_line,
                        sym.start_byte,
                        sym.end_byte,
                    ]
                    for sym in result.symbols
                ],
            )
            _insert_many(
                con,
                """
                INSERT INTO edges (src_file_id, dst_file_id, dst_symbol, edge_type, weight)
                VALUES (?, NULL, ?, 'import', 1)
                """,
                [[file_id, imp.target] for imp in result.imports],
            )
            _insert_many(
                con,
                """
                INSERT INTO edges
                (src_file_id, dst_file_id, dst_symbol, dst_symbol_id, src_symbol_id,
                 edge_type, weight)
                VALUES (?, NULL, ?, NULL, ?, 'call', 1)
                """,
                [
                    [
                        file_id,
                        call.callee_name,
                        f"{file_id}:{call.caller_symbol_start_byte}"
                        if call.caller_symbol_start_byte is not None
                        else None,
                    ]
                    for call in result.calls
                ],
            )
            con.commit()
        except Exception as e:
            con.rollback()
            log.warning("codemap.write_failed", file_id=file_id, error=str(e))
            counts["errors"] += 1
            continue

        counts["parsed"] += 1

    if not dry_run:
        counts["removed"] = _prune_removed_files(con, repo.repo_id, seen_file_ids)

        con.execute(
            "INSERT OR REPLACE INTO repos VALUES (?, ?, ?, ?)",
            [repo.repo_id, str(repo.root_path), first_language, date.today().isoformat()],
        )

    return counts


def _reset_inbound_call_edges(con: duckdb.DuckDBPyConnection, file_id: str) -> None:
    """Make call edges that resolved into ``file_id`` pending again.

    Symbol ids are ``file:start_byte``, so replacing a file's symbols invalidates every
    ``dst_symbol_id`` that pointed into it, and ambiguous names may have fanned out to
    several rows. Each affected (caller, callee name) group is collapsed back to one
    unresolved row so ``_resolve_call_edges`` can resolve it afresh. Import edges that
    pointed at the file are un-resolved too (a removed file must not dangle).
    """
    groups = con.execute(
        """
        SELECT DISTINCT src_file_id, src_symbol_id, dst_symbol FROM edges
        WHERE edge_type = 'call' AND dst_file_id = ? AND src_file_id <> ?
        """,
        [file_id, file_id],
    ).fetchall()
    for src_file_id, src_symbol_id, dst_symbol in groups:
        con.execute(
            """
            DELETE FROM edges WHERE edge_type = 'call' AND src_file_id = ?
              AND src_symbol_id IS NOT DISTINCT FROM ? AND dst_symbol = ?
            """,
            [src_file_id, src_symbol_id, dst_symbol],
        )
        con.execute(
            """
            INSERT INTO edges
            (src_file_id, dst_file_id, dst_symbol, dst_symbol_id, src_symbol_id,
             edge_type, weight)
            VALUES (?, NULL, ?, NULL, ?, 'call', 1)
            """,
            [src_file_id, dst_symbol, src_symbol_id],
        )
    con.execute(
        "UPDATE edges SET dst_file_id = NULL WHERE edge_type = 'import' AND dst_file_id = ?",
        [file_id],
    )


def _prune_removed_files(
    con: duckdb.DuckDBPyConnection, repo_id: str, seen_file_ids: set[str]
) -> int:
    """Delete files that left the repo, with their symbols and edges in both directions."""
    existing = con.execute("SELECT file_id FROM files WHERE repo_id = ?", [repo_id]).fetchall()
    removed = 0
    for (file_id,) in existing:
        if file_id in seen_file_ids:
            continue
        con.begin()
        try:
            _reset_inbound_call_edges(con, file_id)
            con.execute("DELETE FROM files WHERE file_id = ?", [file_id])
            con.execute("DELETE FROM symbols WHERE file_id = ?", [file_id])
            con.execute("DELETE FROM edges WHERE src_file_id = ?", [file_id])
            con.commit()
        except Exception:
            con.rollback()
            raise
        removed += 1
    return removed


def _resolve_import_edges(con: duckdb.DuckDBPyConnection) -> None:
    """Second pass: resolve dst_symbol import strings to dst_file_id where possible."""
    files = con.execute("SELECT file_id, repo_id, rel_path FROM files").fetchall()
    by_module: dict[tuple[str, str], str] = {}
    for file_id, repo_id, rel_path in files:
        module = rel_path[:-3].replace("/", ".") if rel_path.endswith(".py") else rel_path
        if module.endswith(".__init__"):
            module = module[: -len(".__init__")]
        by_module[(repo_id, module)] = file_id

    edges = con.execute(
        "SELECT rowid, src_file_id, dst_symbol FROM edges WHERE dst_file_id IS NULL"
    ).fetchall()
    for rowid, src_file_id, dst_symbol in edges:
        repo_id = src_file_id.split(":", 1)[0]
        target_file_id = by_module.get((repo_id, dst_symbol))
        if target_file_id and target_file_id != src_file_id:
            con.execute("UPDATE edges SET dst_file_id = ? WHERE rowid = ?", [target_file_id, rowid])


def _resolve_call_edges(con: duckdb.DuckDBPyConnection) -> None:
    """Second pass: resolve call-edge callee names to symbol_id(s) within the
    same repo. One edge is written per matching symbol — ambiguous names
    (e.g. multiple classes each defining __init__) fan out to multiple edges
    rather than being dropped, since silently losing a real call relationship
    is worse than mild over-linking."""
    by_name: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for symbol_id, file_id, repo_id, name in con.execute(
        "SELECT symbol_id, file_id, repo_id, name FROM symbols"
    ).fetchall():
        by_name.setdefault((repo_id, name), []).append((symbol_id, file_id))

    pending = con.execute(
        "SELECT rowid, src_file_id, src_symbol_id, dst_symbol "
        "FROM edges WHERE edge_type = 'call' AND dst_symbol_id IS NULL"
    ).fetchall()
    for rowid, src_file_id, src_symbol_id, callee_name in pending:
        repo_id = src_file_id.split(":", 1)[0]
        matches = by_name.get((repo_id, callee_name), [])
        if not matches:
            continue

        target_symbol_id, target_file_id = matches[0]
        con.execute(
            "UPDATE edges SET dst_symbol_id = ?, dst_file_id = ? WHERE rowid = ?",
            [target_symbol_id, target_file_id, rowid],
        )
        for extra_symbol_id, extra_file_id in matches[1:]:
            con.execute(
                """
                INSERT INTO edges
                (src_file_id, dst_file_id, dst_symbol, dst_symbol_id, src_symbol_id,
                 edge_type, weight)
                VALUES (?, ?, ?, ?, ?, 'call', 1)
                """,
                [src_file_id, extra_file_id, callee_name, extra_symbol_id, src_symbol_id],
            )


def run(
    repos_file: Path | None = None,
    only_repo: str | None = None,
    dry_run: bool = False,
) -> dict:
    repos_file = repos_file or default_repos_file()
    repos = load_repos(repos_file)
    if only_repo:
        repos = [r for r in repos if r.repo_id == only_repo]

    if not repos:
        log.warning("codemap.no_repos_configured", repos_file=str(repos_file))
        return {}

    con = db.get_con(read_only=False)
    totals: dict[str, dict] = {}
    try:
        for repo in repos:
            log.info("codemap.indexing_repo", repo_id=repo.repo_id, path=str(repo.root_path))
            totals[repo.repo_id] = index_repo(con, repo, dry_run=dry_run)

        if not dry_run:
            _resolve_import_edges(con)
            _resolve_call_edges(con)
            if symbol_embeddings.HAS_EMBEDDINGS:
                n = symbol_embeddings.sync_embeddings(con)
                log.info("codemap.embeddings_synced", count=n)
            db.touch_built_at(con)
    finally:
        con.close()

    return totals
