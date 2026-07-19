"""Codemap indexer — orchestrates repo walk → manifest check → parse → upsert.

Reads tools/codemap/repos.txt, for each configured repo walks source files
matching a registered language (see tools.codemap.parser.LANGUAGES), skips
unchanged files via manifest.check(), parses changed files with
tools.codemap.parser, and upserts symbols/files/edges into .code_index.duckdb.
Removed files are pruned from both the DB and the manifest.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import duckdb
import structlog

from tools.codemap import db, manifest, parser, symbol_embeddings

log = structlog.get_logger()

REPO_ROOT = Path(__file__).parent.parent.parent
DEFAULT_REPOS_FILE = REPO_ROOT / "tools" / "codemap" / "repos.txt"

_EXCLUDE_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build"}


@dataclass
class RepoConfig:
    repo_id: str
    root_path: Path


def load_repos(repos_file: Path = DEFAULT_REPOS_FILE) -> list[RepoConfig]:
    if not repos_file.exists():
        return []
    repos: list[RepoConfig] = []
    for line in repos_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        root_path = Path(parts[0]).expanduser()
        repo_id = parts[1] if len(parts) > 1 else root_path.name
        repos.append(RepoConfig(repo_id=repo_id, root_path=root_path))
    return repos


def _iter_source_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if path.suffix not in parser.LANGUAGES:
            continue
        if any(part in _EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def index_repo(con: duckdb.DuckDBPyConnection, repo: RepoConfig, dry_run: bool = False) -> dict:
    """Index one repo. Returns counts: parsed, skipped, removed, errors."""
    if not repo.root_path.is_dir():
        log.warning("codemap.repo_not_found", repo_id=repo.repo_id, path=str(repo.root_path))
        return {"parsed": 0, "skipped": 0, "removed": 0, "errors": 1}

    counts = {"parsed": 0, "skipped": 0, "removed": 0, "errors": 0}
    seen_file_ids: set[str] = set()
    first_language: str | None = None

    for path in _iter_source_files(repo.root_path):
        rel_path = str(path.relative_to(repo.root_path))
        file_id = f"{repo.repo_id}:{rel_path}"
        seen_file_ids.add(file_id)
        lang_name = parser.LANGUAGES[path.suffix].name
        first_language = first_language or lang_name

        needs_parse, _reason = manifest.check(file_id, path)
        if not needs_parse:
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

        con.execute("DELETE FROM symbols WHERE file_id = ?", [file_id])
        con.execute("DELETE FROM edges WHERE src_file_id = ?", [file_id])

        loc = path.read_text(errors="replace").count("\n") + 1
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
                manifest.file_hash(path),
                loc,
                date.today().isoformat(),
            ],
        )

        for sym in result.symbols:
            symbol_id = f"{file_id}:{sym.start_byte}"
            con.execute(
                """
                INSERT OR REPLACE INTO symbols
                (symbol_id, file_id, repo_id, name, kind, signature, docstring,
                 parent_scope, start_line, end_line, start_byte, end_byte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    symbol_id,
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
                ],
            )

        for imp in result.imports:
            con.execute(
                """
                INSERT INTO edges (src_file_id, dst_file_id, dst_symbol, edge_type, weight)
                VALUES (?, NULL, ?, 'import', 1)
                """,
                [file_id, imp.target],
            )

        for call in result.calls:
            src_symbol_id = (
                f"{file_id}:{call.caller_symbol_start_byte}"
                if call.caller_symbol_start_byte is not None
                else None
            )
            con.execute(
                """
                INSERT INTO edges
                (src_file_id, dst_file_id, dst_symbol, dst_symbol_id, src_symbol_id,
                 edge_type, weight)
                VALUES (?, NULL, ?, NULL, ?, 'call', 1)
                """,
                [file_id, call.callee_name, src_symbol_id],
            )

        manifest.mark(file_id, path)
        counts["parsed"] += 1

    if not dry_run:
        _prune_removed_files(con, repo.repo_id, seen_file_ids)
        counts["removed"] = _prune_stale_manifest_entries(repo.repo_id, seen_file_ids)

        con.execute(
            "INSERT OR REPLACE INTO repos VALUES (?, ?, ?, ?)",
            [repo.repo_id, str(repo.root_path), first_language, date.today().isoformat()],
        )

    return counts


def _prune_removed_files(
    con: duckdb.DuckDBPyConnection, repo_id: str, seen_file_ids: set[str]
) -> None:
    existing = con.execute("SELECT file_id FROM files WHERE repo_id = ?", [repo_id]).fetchall()
    for (file_id,) in existing:
        if file_id not in seen_file_ids:
            con.execute("DELETE FROM files WHERE file_id = ?", [file_id])
            con.execute("DELETE FROM symbols WHERE file_id = ?", [file_id])
            con.execute("DELETE FROM edges WHERE src_file_id = ?", [file_id])


def _prune_stale_manifest_entries(repo_id: str, seen_file_ids: set[str]) -> int:
    removed = 0
    for file_id in manifest.known_file_ids():
        if file_id.startswith(f"{repo_id}:") and file_id not in seen_file_ids:
            manifest.remove(file_id)
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
    repos_file: Path = DEFAULT_REPOS_FILE,
    only_repo: str | None = None,
    dry_run: bool = False,
) -> dict:
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
