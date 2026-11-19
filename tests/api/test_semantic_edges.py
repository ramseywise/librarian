"""Similar-page edges: a global cut, or each page's k nearest (the map's Similar chip)."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("sklearn")

from librarian.retrieval import embeddings

# a and b nearly the same; c between them and d; d far from all but c.
IDS = ["a", "b", "c", "d"]
VECS = np.array([[1, 0, 0], [0.99, 0.14, 0], [0.6, 0.8, 0], [0, 0.6, 0.8]], dtype=np.float32)


@pytest.fixture(autouse=True)
def _vectors(monkeypatch: pytest.MonkeyPatch) -> None:
    unit = VECS / np.linalg.norm(VECS, axis=1, keepdims=True)
    monkeypatch.setattr(embeddings, "compute_embeddings", lambda: (list(IDS), unit))


def pairs(edges: list[dict]) -> set[tuple[str, str]]:
    return {(e["source"], e["target"]) for e in edges}


def test_a_global_cut_leaves_the_far_page_with_no_neighbour() -> None:
    assert pairs(embeddings.semantic_edges(0.9)) == {("a", "b")}


def test_k_nearest_gives_every_page_a_neighbour_above_the_floor() -> None:
    got = pairs(embeddings.semantic_edges(0.3, k=1))
    assert {p for pair in got for p in pair} == set(IDS)
    assert ("c", "d") in got


def test_keep_drops_pages_before_choosing_so_they_take_no_slot() -> None:
    got = pairs(embeddings.semantic_edges(0.3, k=1, keep={"a", "c", "d"}))
    assert got == {("a", "c"), ("c", "d")}
