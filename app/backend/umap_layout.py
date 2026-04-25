from __future__ import annotations

import numpy as np
from umap import UMAP

from .embeddings import compute_embeddings

CANVAS_W = 2000
CANVAS_H = 1500


def compute_umap_positions(n_neighbors: int = 10, min_dist: float = 0.3) -> dict[str, dict]:
    page_ids, vecs = compute_embeddings()
    n = len(page_ids)

    if n < 4:
        return {pid: {"x": float(i * 220), "y": 0.0} for i, pid in enumerate(page_ids)}

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

    return {
        pid: {
            "x": round(float((coords[i, 0] - x_min) / x_range * CANVAS_W - CANVAS_W / 2), 1),
            "y": round(float((coords[i, 1] - y_min) / y_range * CANVAS_H - CANVAS_H / 2), 1),
        }
        for i, pid in enumerate(page_ids)
    }
