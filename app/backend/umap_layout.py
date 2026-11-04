from __future__ import annotations

import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np

from shared.embeddings import compute_embeddings, current_page_ids
from shared.log_config import get_logger

log = get_logger(__name__)

CANVAS_W = 2000
CANVAS_H = 1500
CACHE_DB = Path(__file__).parent.parent.parent / ".embeddings_cache.duckdb"
# Row holding the most recent fit, whatever its page set.
LATEST_KEY = "latest"
# Reuse the latest fit while it still covers this share of the pages. The client places
# the rest (placeMissingNodes), so a new page costs no refit and moves no existing node.
MIN_COVERAGE = 0.9


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
    except Exception as e:  # reads as a miss; say so, since a miss costs a refit
        log.warning("umap.cache.read_failed", error=str(e))
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
    except Exception as e:
        log.warning("umap.cache.write_failed", error=str(e))


def compute_umap_positions(n_neighbors: int = 10, min_dist: float = 0.3) -> dict[str, dict]:
    """Compute UMAP layout with DuckDB caching.

    The layout is keyed by the set of page IDs. Unchanged wiki states serve cached
    coordinates instantly. After pages are added or removed the latest fit keeps being
    served until it covers less than MIN_COVERAGE of them; only then is UMAP re-run.
    """
    page_ids = current_page_ids()
    n = len(page_ids)

    if n < 4:
        return {pid: {"x": float(i * 220), "y": 0.0} for i, pid in enumerate(page_ids)}

    cache_key = _layout_cache_key(page_ids)
    cached = _load_cached_layout(cache_key)
    latest = _load_cached_layout(LATEST_KEY)
    if cached is not None:
        if latest is None:  # a cache written before LATEST_KEY existed
            _save_layout(LATEST_KEY, cached)
        return cached
    if latest is not None:
        covered = {pid: latest[pid] for pid in page_ids if pid in latest}
        if len(covered) >= MIN_COVERAGE * n:
            return covered

    # Imported here: umap pulls in numba, seconds of startup that only a refit needs.
    from umap import UMAP

    page_ids, vecs = compute_embeddings()
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
    _save_layout(LATEST_KEY, layout)
    return layout
