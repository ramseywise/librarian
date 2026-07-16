"""Codemap Query API — read-only HTTP layer over .code_index.duckdb.

Owns the DuckDB connection so indexing (writer, run centrally) and
querying (readers, e.g. MCP tool clients) are separate processes — no
consumer needs to open the DB file directly.

Run: uv run uvicorn tools.codemap.api:app --port 8100
     (or: make codemap-api)

For non-localhost hosting, set CODEMAP_API_HOST/CODEMAP_API_PORT and run:
     uv run python -m tools.codemap.api
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from tools.codemap import db, symbol_embeddings  # noqa: E402

app = FastAPI(title="Codemap Query API")


def _con() -> duckdb.DuckDBPyConnection:
    return db.get_con(read_only=True)


@app.get("/api/repos")
def list_repos() -> list[dict]:
    con = _con()
    try:
        rows = con.execute(
            "SELECT repo_id, root_path, language, last_indexed_at FROM repos ORDER BY repo_id"
        ).fetchall()
    finally:
        con.close()
    return [
        {"repo_id": r[0], "root_path": r[1], "language": r[2], "last_indexed_at": r[3]}
        for r in rows
    ]


@app.get("/api/symbols/find")
def find_symbol(name: str, repo: str = "", limit: int = 20) -> list[dict]:
    con = _con()
    try:
        sql = """
            SELECT symbol_id, name, kind, signature, docstring, file_id, repo_id,
                   start_line, end_line
            FROM symbols
            WHERE lower(name) LIKE '%' || lower(?) || '%'
        """
        params: list = [name]
        if repo:
            sql += " AND repo_id = ?"
            params.append(repo)
        sql += """
            ORDER BY
                CASE WHEN lower(name) = lower(?) THEN 0 ELSE 1 END,
                length(name)
            LIMIT ?
        """
        params += [name, limit]
        rows = con.execute(sql, params).fetchall()
    finally:
        con.close()
    return [
        {
            "symbol_id": r[0],
            "name": r[1],
            "kind": r[2],
            "signature": r[3],
            "docstring": r[4],
            "file_id": r[5],
            "repo_id": r[6],
            "start_line": r[7],
            "end_line": r[8],
        }
        for r in rows
    ]


@app.get("/api/files/{repo}/{rel_path:path}/symbols")
def get_file_symbols(repo: str, rel_path: str) -> list[dict]:
    file_id = f"{repo}:{rel_path}"
    con = _con()
    try:
        rows = con.execute(
            """
            SELECT name, kind, signature, docstring, parent_scope, start_line, end_line
            FROM symbols WHERE file_id = ? ORDER BY start_line
            """,
            [file_id],
        ).fetchall()
    finally:
        con.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No symbols found for {file_id!r}")
    return [
        {
            "name": r[0],
            "kind": r[1],
            "signature": r[2],
            "docstring": r[3],
            "parent_scope": r[4],
            "start_line": r[5],
            "end_line": r[6],
        }
        for r in rows
    ]


@app.get("/api/references")
def find_references(symbol_or_path: str, repo: str = "") -> list[dict]:
    """Files that import the file matching symbol_or_path (as a rel_path),
    or files defining a symbol matching symbol_or_path (as a name)."""
    con = _con()
    try:
        file_sql = "SELECT file_id FROM files WHERE rel_path = ?"
        file_params: list = [symbol_or_path]
        if repo:
            file_sql += " AND repo_id = ?"
            file_params.append(repo)
        target_files = con.execute(file_sql, file_params).fetchall()

        if not target_files:
            sym_sql = "SELECT DISTINCT file_id FROM symbols WHERE name = ?"
            sym_params: list = [symbol_or_path]
            if repo:
                sym_sql += " AND repo_id = ?"
                sym_params.append(repo)
            target_files = con.execute(sym_sql, sym_params).fetchall()

        if not target_files:
            return []

        target_ids = [r[0] for r in target_files]
        placeholders = ", ".join("?" for _ in target_ids)
        rows = con.execute(
            f"""
            SELECT e.src_file_id, f.rel_path, f.repo_id, e.weight
            FROM edges e
            JOIN files f ON f.file_id = e.src_file_id
            WHERE e.dst_file_id IN ({placeholders})
            ORDER BY e.weight DESC
            """,
            target_ids,
        ).fetchall()
    finally:
        con.close()
    return [{"src_file_id": r[0], "rel_path": r[1], "repo_id": r[2], "weight": r[3]} for r in rows]


@app.get("/api/callers")
def find_callers(symbol_name: str, repo: str = "") -> list[dict]:
    """Symbols that call a given symbol name, ranked by weight (fan-out for
    ambiguous names — see codemap-code-index.md on the one-edge-per-match policy)."""
    con = _con()
    try:
        sql = """
            SELECT caller.name, caller.kind, f.rel_path, f.repo_id, e.weight
            FROM edges e
            JOIN files f ON f.file_id = e.src_file_id
            LEFT JOIN symbols caller ON caller.symbol_id = e.src_symbol_id
            WHERE e.edge_type = 'call' AND e.dst_symbol = ?
        """
        params: list = [symbol_name]
        if repo:
            sql += " AND f.repo_id = ?"
            params.append(repo)
        sql += " ORDER BY e.weight DESC"
        rows = con.execute(sql, params).fetchall()
    finally:
        con.close()
    return [
        {
            "caller_name": r[0],
            "caller_kind": r[1],
            "rel_path": r[2],
            "repo_id": r[3],
            "weight": r[4],
        }
        for r in rows
    ]


@app.get("/api/symbols/semantic_search")
def semantic_search_symbols(query: str, repo: str = "", limit: int = 10) -> list[dict]:
    if not symbol_embeddings.HAS_EMBEDDINGS:
        raise HTTPException(
            status_code=501,
            detail=(
                "Semantic search unavailable — sentence-transformers not installed "
                "(install with: uv sync --extra api --extra codemap)"
            ),
        )
    con = _con()
    try:
        return symbol_embeddings.semantic_search(con, query, repo_id=repo or None, limit=limit)
    finally:
        con.close()


@app.get("/api/repo_map")
def repo_map(repo: str, limit: int = 50) -> list[dict]:
    """Files ranked by inbound reference weight, each with its top symbols."""
    con = _con()
    try:
        rows = con.execute(
            """
            SELECT f.file_id, f.rel_path, COALESCE(SUM(e.weight), 0) AS inbound
            FROM files f
            LEFT JOIN edges e ON e.dst_file_id = f.file_id
            WHERE f.repo_id = ?
            GROUP BY f.file_id, f.rel_path
            ORDER BY inbound DESC, f.rel_path
            LIMIT ?
            """,
            [repo, limit],
        ).fetchall()

        result = []
        for file_id, rel_path, inbound in rows:
            symbols = con.execute(
                "SELECT name, kind FROM symbols WHERE file_id = ? ORDER BY start_line LIMIT 8",
                [file_id],
            ).fetchall()
            result.append(
                {
                    "rel_path": rel_path,
                    "inbound_weight": inbound,
                    "symbols": [{"name": s[0], "kind": s[1]} for s in symbols],
                }
            )
    finally:
        con.close()
    return result


def _run() -> None:
    import uvicorn

    host = os.environ.get("CODEMAP_API_HOST", "127.0.0.1")
    port = int(os.environ.get("CODEMAP_API_PORT", "8100"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    _run()
