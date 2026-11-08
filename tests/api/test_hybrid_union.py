"""The `hybrid-union` experiment's merge: BM25 rows first, cosine-only rows appended."""

from __future__ import annotations

import numpy as np

from librarian.retrieval import embeddings, ranking


def _row(path: str, vec: list[float] | None, score: float | None) -> tuple:
    blob = np.asarray(vec, dtype=np.float32).tobytes() if vec else None
    return (path, path, "", "", "", 0, blob, score)


def test_union_adds_cosine_only_rows_after_bm25_rows() -> None:
    bm25 = [_row("a", [0.0, 1.0], 2.0), _row("b", [0.0, 1.0], 1.0)]
    allrows = [
        bm25[0],
        _row("c", [1.0, 0.0], None),
        _row("d", [0.6, 0.8], None),
        _row("e", None, None),
        _row("f", [0.0, 1.0], None),
    ]
    assert embeddings.blob_to_floats(allrows[1][6]) == [1.0, 0.0]
    out = ranking.union_candidates(bm25, allrows, [1.0, 0.0], 2)
    assert [r[0] for r in out] == ["a", "b", "c", "d"]  # no dupes, no embedding-less row, top 2
    assert [r[7] for r in out] == [2.0, 1.0, 0.0, 0.0]


def test_union_leaves_score_null_for_fallback_rows() -> None:
    bm25 = [_row("a", [0.0, 1.0], None)]
    out = ranking.union_candidates(bm25, [_row("c", [1.0, 0.0], None)], [1.0, 0.0], 5)
    assert [r[7] for r in out] == [None, None]
