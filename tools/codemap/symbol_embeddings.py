"""Optional semantic search over symbols.

Mirrors app/backend/embeddings.py's content-hash-cached embedding pattern,
applied to symbol name+kind+signature+docstring text instead of wiki page
text, and app/mcp_server/server.py's HAS_EMBEDDINGS optional-import gate.
Gracefully absent if sentence-transformers isn't installed — activates
automatically when it is (e.g. via `uv sync --extra api --extra codemap`).

Stored in its own symbol_embeddings table, created lazily on first use —
not part of the core codemap schema/SCHEMA_VERSION, so installs that never
enable embeddings pay no schema cost at all.
"""

from __future__ import annotations

import hashlib
import struct

import duckdb

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _symbol_text(name: str, kind: str, signature: str, docstring: str) -> str:
    return f"{name} ({kind}). {signature}\n{docstring}"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _vec_to_blob(vec: np.ndarray) -> bytes:
    flat = vec.tolist()
    return struct.pack(f"{len(flat)}f", *flat)


def _blob_to_vec(blob: bytes) -> np.ndarray:
    n = len(blob) // 4
    return np.array(struct.unpack(f"{n}f", blob), dtype=np.float32)


def ensure_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS symbol_embeddings (
            symbol_id     TEXT PRIMARY KEY,
            content_hash  TEXT NOT NULL,
            vector        BLOB NOT NULL
        )
        """
    )


def sync_embeddings(con: duckdb.DuckDBPyConnection, repo_id: str | None = None) -> int:
    """Compute/refresh embeddings for symbols missing or stale in
    symbol_embeddings. Returns the count of symbols (re)embedded. No-op
    returning 0 if sentence-transformers is not installed."""
    if not HAS_EMBEDDINGS:
        return 0
    ensure_table(con)

    sql = "SELECT symbol_id, name, kind, signature, docstring FROM symbols"
    params: list = []
    if repo_id:
        sql += " WHERE repo_id = ?"
        params.append(repo_id)
    symbols = con.execute(sql, params).fetchall()

    cached = dict(con.execute("SELECT symbol_id, content_hash FROM symbol_embeddings").fetchall())

    to_encode: list[tuple[str, str, str]] = []
    for symbol_id, name, kind, signature, docstring in symbols:
        text = _symbol_text(name, kind, signature or "", docstring or "")
        chash = _content_hash(text)
        if cached.get(symbol_id) != chash:
            to_encode.append((symbol_id, chash, text))

    if not to_encode:
        return 0

    model = _get_model()
    vecs = model.encode([t[2] for t in to_encode], normalize_embeddings=True)
    rows = [
        (symbol_id, chash, _vec_to_blob(vecs[i]))
        for i, (symbol_id, chash, _) in enumerate(to_encode)
    ]
    con.executemany("INSERT OR REPLACE INTO symbol_embeddings VALUES (?, ?, ?)", rows)

    live_ids = {s[0] for s in symbols}
    stale = [(sid,) for sid in cached if sid not in live_ids]
    if stale:
        con.executemany("DELETE FROM symbol_embeddings WHERE symbol_id = ?", stale)

    return len(to_encode)


def semantic_search(
    con: duckdb.DuckDBPyConnection, query: str, repo_id: str | None = None, limit: int = 10
) -> list[dict]:
    """Cosine-similarity search over cached symbol embeddings. Empty list if
    sentence-transformers is absent or nothing is cached yet."""
    if not HAS_EMBEDDINGS:
        return []
    ensure_table(con)

    sql = (
        "SELECT s.symbol_id, s.name, s.kind, s.signature, s.docstring, s.file_id, "
        "s.repo_id, s.start_line, s.end_line, e.vector "
        "FROM symbols s JOIN symbol_embeddings e ON e.symbol_id = s.symbol_id"
    )
    params: list = []
    if repo_id:
        sql += " WHERE s.repo_id = ?"
        params.append(repo_id)
    rows = con.execute(sql, params).fetchall()
    if not rows:
        return []

    model = _get_model()
    q_vec = model.encode([query], normalize_embeddings=True)[0]

    scored = []
    for r in rows:
        vec = _blob_to_vec(r[9])
        score = float(np.dot(q_vec, vec))
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "symbol_id": r[0], "name": r[1], "kind": r[2], "signature": r[3],
            "docstring": r[4], "file_id": r[5], "repo_id": r[6],
            "start_line": r[7], "end_line": r[8], "score": round(score, 4),
        }
        for score, r in scored[:limit]
    ]
