from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import duckdb
import frontmatter
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"
CACHE_DB = Path(__file__).parent.parent.parent / ".embeddings_cache.duckdb"
MODEL_NAME = os.environ.get("LIBRARIAN_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def warmup() -> None:
    model = _get_model()
    model.encode(["warmup"], normalize_embeddings=True)


def _page_text(md_file: Path) -> str:
    post = frontmatter.load(md_file)
    title = post.get("title") or md_file.stem
    summary = post.get("summary") or ""
    return f"{title}. {summary}\n\n{post.content[:600]}"


def _content_hash(md_file: Path) -> str:
    return hashlib.sha256(md_file.read_bytes()).hexdigest()[:16]


def _open_cache() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(CACHE_DB))
    con.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            path         TEXT PRIMARY KEY,
            content_hash TEXT,
            vector       BLOB,
            model_name   TEXT DEFAULT ''
        )
    """)
    # Add model_name column if missing (migration from old schema)
    cols = {r[0] for r in con.execute("PRAGMA table_info('embeddings')").fetchall()}
    if "model_name" not in cols:
        con.execute("ALTER TABLE embeddings ADD COLUMN model_name TEXT DEFAULT ''")
    # Invalidate cache if model changed
    stale = con.execute(
        "SELECT COUNT(*) FROM embeddings WHERE model_name != ?", [MODEL_NAME]
    ).fetchone()[0]
    if stale > 0:
        con.execute("DELETE FROM embeddings WHERE model_name != ?", [MODEL_NAME])
    return con


def _vec_to_blob(vec: np.ndarray) -> bytes:
    flat = vec.tolist()
    return struct.pack(f"{len(flat)}f", *flat)


def _blob_to_vec(blob: bytes) -> np.ndarray:
    n = len(blob) // 4
    return np.array(struct.unpack(f"{n}f", blob), dtype=np.float32)


def compute_embeddings() -> tuple[list[str], np.ndarray]:
    """Compute (or load from cache) embeddings for all wiki pages.

    Pages whose content hasn't changed since last run are served from DuckDB
    without calling the model — only new/changed pages are re-encoded.
    """
    md_files = sorted(f for f in WIKI_DIR.rglob("*.md") if not f.name.startswith("_"))
    if not md_files:
        return [], np.array([])

    con = _open_cache()
    cached: dict[str, tuple[str, np.ndarray]] = {}
    for path, chash, blob in con.execute(
        "SELECT path, content_hash, vector FROM embeddings"
    ).fetchall():
        cached[path] = (chash, _blob_to_vec(blob))

    page_ids: list[str] = []
    vecs: list[np.ndarray] = []
    to_encode: list[tuple[str, str, str]] = []  # (path_str, page_id, text)

    for md_file in md_files:
        path_str = str(md_file)
        page_id = md_file.stem
        chash = _content_hash(md_file)

        if path_str in cached and cached[path_str][0] == chash:
            page_ids.append(page_id)
            vecs.append(cached[path_str][1])
        else:
            to_encode.append((path_str, page_id, _page_text(md_file), chash))

    if to_encode:
        model = _get_model()
        texts = [t[2] for t in to_encode]
        new_vecs = model.encode(texts, normalize_embeddings=True)
        rows = []
        for i, (path_str, page_id, _, chash) in enumerate(to_encode):
            vec = new_vecs[i]
            page_ids.append(page_id)
            vecs.append(vec)
            rows.append((path_str, chash, _vec_to_blob(vec), MODEL_NAME))
        con.executemany("INSERT OR REPLACE INTO embeddings VALUES (?, ?, ?, ?)", rows)

    # Prune stale cache entries (deleted pages)
    current_paths = {str(f) for f in md_files}
    stale = [(p,) for p in cached if p not in current_paths]
    if stale:
        con.executemany("DELETE FROM embeddings WHERE path = ?", stale)

    con.close()
    return page_ids, np.array(vecs, dtype=np.float32)


def semantic_edges(threshold: float = 0.65) -> list[dict]:
    page_ids, vecs = compute_embeddings()
    if len(page_ids) < 2:
        return []
    sim = cosine_similarity(vecs)
    edges = []
    for i in range(len(page_ids)):
        for j in range(i + 1, len(page_ids)):
            score = float(sim[i, j])
            if score >= threshold:
                a, b = page_ids[i], page_ids[j]
                edges.append(
                    {
                        "id": f"sem:{a}->{b}",
                        "source": a,
                        "target": b,
                        "data": {"edgeType": "semantic", "score": round(score, 3)},
                    }
                )
    return edges
