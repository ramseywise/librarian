"""UMAP layout reuse (app/backend/umap_layout.py): page changes don't move the map."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("duckdb")

from app.backend import umap_layout


class _FakeUMAP:
    fits = 0

    def __init__(self, **_: object) -> None:
        type(self).fits += 1

    def fit_transform(self, vecs: np.ndarray) -> np.ndarray:
        return np.arange(len(vecs) * 2, dtype=float).reshape(-1, 2)


@pytest.fixture
def pages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    ids = [f"p{i}" for i in range(20)]
    monkeypatch.setattr(umap_layout, "CACHE_DB", tmp_path / "layout.duckdb")
    monkeypatch.setattr(umap_layout, "current_page_ids", lambda: list(ids))
    monkeypatch.setattr(
        umap_layout, "compute_embeddings", lambda: (list(ids), np.zeros((len(ids), 3)))
    )
    monkeypatch.setitem(sys.modules, "umap", types.SimpleNamespace(UMAP=_FakeUMAP))
    _FakeUMAP.fits = 0
    return ids


def test_same_pages_serve_the_cache(pages: list[str]) -> None:
    first = umap_layout.compute_umap_positions()
    assert umap_layout.compute_umap_positions() == first
    assert _FakeUMAP.fits == 1


def test_a_new_page_neither_refits_nor_moves_nodes(pages: list[str]) -> None:
    first = umap_layout.compute_umap_positions()
    pages.append("brand-new")
    assert umap_layout.compute_umap_positions() == first  # client places the new page
    assert _FakeUMAP.fits == 1


def test_a_removed_page_is_dropped_without_a_refit(pages: list[str]) -> None:
    first = umap_layout.compute_umap_positions()
    gone = pages.pop()
    second = umap_layout.compute_umap_positions()
    assert gone not in second
    assert second == {k: v for k, v in first.items() if k != gone}
    assert _FakeUMAP.fits == 1


def test_refits_once_the_latest_covers_too_little(pages: list[str]) -> None:
    umap_layout.compute_umap_positions()
    pages.extend(f"new{i}" for i in range(5))  # 20 of 25 = 80% covered
    assert set(umap_layout.compute_umap_positions()) == set(pages)
    assert _FakeUMAP.fits == 2


def test_cache_hit_needs_neither_umap_nor_embeddings(
    pages: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    first = umap_layout.compute_umap_positions()

    def boom() -> None:
        raise AssertionError("a cache hit must not read embeddings")

    monkeypatch.setattr(umap_layout, "compute_embeddings", boom)
    monkeypatch.setitem(sys.modules, "umap", None)  # `import umap` now raises ImportError
    assert umap_layout.compute_umap_positions() == first


def test_cache_from_before_latest_key_still_avoids_a_refit(pages: list[str]) -> None:
    first = umap_layout.compute_umap_positions()
    con = __import__("duckdb").connect(str(umap_layout.CACHE_DB))
    con.execute("DELETE FROM umap_layout WHERE cache_key = ?", [umap_layout.LATEST_KEY])
    con.close()
    assert umap_layout.compute_umap_positions() == first  # exact hit, backfills latest
    pages.append("brand-new")
    assert umap_layout.compute_umap_positions() == first
    assert _FakeUMAP.fits == 1
