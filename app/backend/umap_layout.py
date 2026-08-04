from __future__ import annotations

import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
from umap import UMAP

from shared.embeddings import compute_embeddings

CANVAS_W = 2000
CANVAS_H = 1500
CACHE_DB = Path(__file__).parent.parent.parent / ".embeddings_cache.duckdb"


def _layout_cache_key(page_ids: list[str]) -> str:
    """Stable cache key from the ordered list of page IDs."""
    return hashlib.sha256(",".join(sorted(page_ids)).encode()).hexdigest()[:16]


def _load_cached_layout(cache_key: str) -> dict[str, dict] | None:
    try:
        con = duckdb.connect(str(CACHE_DB))
        con.execute("""
            CREATE TABLE IF NOT EXISTS umap_layout (
                cache_key TEXT PRIMARY KEY,
                layout    TEXT
            )
        """)
        row = con.execute(
            "SELECT layout FROM umap_layout WHERE cache_key = ?", [cache_key]
        ).fetchone()
        con.close()
        return json.loads(row[0]) if row else None
    except Exception:
        return None


def _save_layout(cache_key: str, layout: dict[str, dict]) -> None:
    try:
        con = duckdb.connect(str(CACHE_DB))
        con.execute("""
            CREATE TABLE IF NOT EXISTS umap_layout (
                cache_key TEXT PRIMARY KEY,
                layout    TEXT
            )
        """)
        con.execute(
            "INSERT OR REPLACE INTO umap_layout VALUES (?, ?)",
            [cache_key, json.dumps(layout)],
        )
        con.close()
    except Exception:
        pass


def compute_umap_positions(n_neighbors: int = 10, min_dist: float = 0.3) -> dict[str, dict]:
    """Compute UMAP layout with DuckDB caching.

    The layout is keyed by the set of page IDs. When pages are added or removed
    the cache is invalidated and UMAP is re-run. Unchanged wiki states serve
    cached coordinates instantly.
    """
    page_ids, vecs = compute_embeddings()
    n = len(page_ids)

    if n < 4:
        return {pid: {"x": float(i * 220), "y": 0.0} for i, pid in enumerate(page_ids)}

    cache_key = _layout_cache_key(page_ids)
    cached = _load_cached_layout(cache_key)
    if cached is not None:
        return cached

    reducer = UMAP(
        n_neighbors=min(n_neighbors, n - 1),
        min_dist=min_dist,
        n_components=2,
        random_state=42,
        low_memory=False,
    )
    coords: np.ndarray = reducer.fit_transform(vecs)

    x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
    y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
    x_range = x_max - x_min or 1.0
    y_range = y_max - y_min or 1.0

    layout = {
        pid: {
            "x": round(float((coords[i, 0] - x_min) / x_range * CANVAS_W - CANVAS_W / 2), 1),
            "y": round(float((coords[i, 1] - y_min) / y_range * CANVAS_H - CANVAS_H / 2), 1),
        }
        for i, pid in enumerate(page_ids)
    }

    _save_layout(cache_key, layout)
    return layout
