"""Unit tests for evals/graders.py — retrieval and answer quality graders.

All tests are deterministic; no LLM calls, no live servers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from evals.graders import (
    AnswerGrader,
    GoldenEntry,
    RetrievalGrader,
    RetrievalResult,
    _tfidf_cosine,
    _token_overlap,
    load_golden_dataset,
)

GOLDEN_PATH = Path(__file__).parents[2] / "evals" / "golden_dataset.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_entry(
    *,
    id: str = "test-001",
    category: str = "retrieval",
    query: str = "What is RRF?",
    expected_answer: str = "RRF combines ranked lists by position.",
    source_pages: list[str] | None = None,
    difficulty: str = "easy",
) -> GoldenEntry:
    return GoldenEntry(
        id=id,
        category=category,
        query=query,
        expected_answer=expected_answer,
        source_pages=source_pages or ["wiki/rag/reciprocal-rank-fusion.md"],
        difficulty=difficulty,
    )


# ---------------------------------------------------------------------------
# Golden dataset schema tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_golden_dataset_loads() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    assert len(entries) == 50, f"expected 50 entries, got {len(entries)}"


@pytest.mark.unit
def test_golden_dataset_required_fields() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    for e in entries:
        assert e.id, f"missing id in {e}"
        assert e.query, f"missing query in entry {e.id}"
        assert e.expected_answer, f"missing expected_answer in entry {e.id}"
        assert e.source_pages, f"missing source_pages in entry {e.id}"
        assert e.category, f"missing category in entry {e.id}"
        assert e.difficulty in {"easy", "medium", "hard"}, (
            f"invalid difficulty '{e.difficulty}' in entry {e.id}"
        )


@pytest.mark.unit
def test_golden_dataset_ids_unique() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    ids = [e.id for e in entries]
    assert len(ids) == len(set(ids)), "duplicate IDs in golden dataset"


@pytest.mark.unit
def test_golden_dataset_source_pages_reference_wiki() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    for e in entries:
        for page in e.source_pages:
            assert page.startswith("wiki/"), (
                f"source_page '{page}' in entry {e.id} must start with 'wiki/'"
            )


@pytest.mark.unit
def test_golden_dataset_category_distribution() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    from collections import Counter

    cats = Counter(e.category for e in entries)
    # Sanity: all entries have a recognisable category
    valid = {"retrieval", "memory", "architecture", "patterns", "eval", "infra", "meta"}
    for cat in cats:
        assert cat in valid, f"unknown category '{cat}'"
    # At least 3 distinct categories
    assert len(cats) >= 3, f"expected >= 3 categories, got {cats}"


@pytest.mark.unit
def test_golden_dataset_difficulty_distribution() -> None:
    entries = load_golden_dataset(str(GOLDEN_PATH))
    from collections import Counter

    diff = Counter(e.difficulty for e in entries)
    assert "easy" in diff
    assert "medium" in diff
    assert "hard" in diff


@pytest.mark.unit
def test_golden_dataset_source_pages_exist_in_wiki() -> None:
    """Each source_page path must exist under wiki/ in the repo.

    This is the domain-truth gate: Q&A pairs must be grounded in real pages.
    """
    repo_root = Path(__file__).parents[2]
    entries = load_golden_dataset(str(GOLDEN_PATH))
    missing: list[str] = []
    for e in entries:
        for page in e.source_pages:
            full = repo_root / page
            if not full.exists():
                missing.append(f"{e.id}: {page}")

    assert not missing, "Golden dataset references non-existent wiki pages:\n  " + "\n  ".join(
        missing
    )


# ---------------------------------------------------------------------------
# RetrievalGrader tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_retrieval_grader_hit_exact_match() -> None:
    grader = RetrievalGrader()
    entry = _make_entry(source_pages=["wiki/rag/reciprocal-rank-fusion.md"])
    retrieved = [RetrievalResult("wiki/rag/reciprocal-rank-fusion.md", score=0.9)]
    result = grader.grade_entry(entry, retrieved)
    assert result.hit is True
    assert result.reciprocal_rank == pytest.approx(1.0)


@pytest.mark.unit
def test_retrieval_grader_hit_suffix_match() -> None:
    grader = RetrievalGrader()
    entry = _make_entry(source_pages=["wiki/rag/reciprocal-rank-fusion.md"])
    # Retrieved path has a leading slash — should still match
    retrieved = [RetrievalResult("/wiki/rag/reciprocal-rank-fusion.md", score=0.9)]
    result = grader.grade_entry(entry, retrieved)
    assert result.hit is True


@pytest.mark.unit
def test_retrieval_grader_miss() -> None:
    grader = RetrievalGrader()
    entry = _make_entry(source_pages=["wiki/rag/reciprocal-rank-fusion.md"])
    retrieved = [RetrievalResult("wiki/rag/rag-reranking.md", score=0.8)]
    result = grader.grade_entry(entry, retrieved)
    assert result.hit is False
    assert result.reciprocal_rank == pytest.approx(0.0)


@pytest.mark.unit
def test_retrieval_grader_mrr_rank_2() -> None:
    grader = RetrievalGrader()
    entry = _make_entry(source_pages=["wiki/rag/reciprocal-rank-fusion.md"])
    retrieved = [
        RetrievalResult("wiki/rag/rag-reranking.md", score=0.9),
        RetrievalResult("wiki/rag/reciprocal-rank-fusion.md", score=0.8),
        RetrievalResult("wiki/rag/crag-retry-logic.md", score=0.7),
    ]
    result = grader.grade_entry(entry, retrieved)
    assert result.hit is True
    assert result.reciprocal_rank == pytest.approx(1 / 2)


@pytest.mark.unit
def test_retrieval_grader_multi_expected_pages() -> None:
    grader = RetrievalGrader()
    entry = _make_entry(
        source_pages=[
            "wiki/rag/reciprocal-rank-fusion.md",
            "wiki/rag/rag-retrieval-strategies.md",
        ]
    )
    # Only the second expected page appears, at rank 3
    retrieved = [
        RetrievalResult("wiki/rag/rag-reranking.md", score=0.9),
        RetrievalResult("wiki/rag/crag-retry-logic.md", score=0.8),
        RetrievalResult("wiki/rag/rag-retrieval-strategies.md", score=0.7),
    ]
    result = grader.grade_entry(entry, retrieved)
    assert result.hit is True
    assert result.reciprocal_rank == pytest.approx(1 / 3)


@pytest.mark.unit
def test_retrieval_grader_empty_retrieved() -> None:
    grader = RetrievalGrader()
    entry = _make_entry()
    result = grader.grade_entry(entry, [])
    assert result.hit is False
    assert result.reciprocal_rank == pytest.approx(0.0)


@pytest.mark.unit
def test_retrieval_grader_batch_hit_rate_and_mrr() -> None:
    grader = RetrievalGrader()
    entries = [
        _make_entry(id="e1", source_pages=["wiki/rag/a.md"]),
        _make_entry(id="e2", source_pages=["wiki/rag/b.md"]),
        _make_entry(id="e3", source_pages=["wiki/rag/c.md"]),
    ]
    retrieved = [
        [RetrievalResult("wiki/rag/a.md")],  # rank-1 hit
        [RetrievalResult("wiki/rag/x.md"), RetrievalResult("wiki/rag/b.md")],  # rank-2
        [RetrievalResult("wiki/rag/x.md")],  # miss
    ]
    hit_rate, mrr, results = grader.grade_batch(entries, retrieved)
    assert hit_rate == pytest.approx(2 / 3)
    assert mrr == pytest.approx((1.0 + 0.5 + 0.0) / 3)
    assert len(results) == 3


# ---------------------------------------------------------------------------
# AnswerGrader — token_overlap tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_token_overlap_identical() -> None:
    assert _token_overlap("the quick brown fox", "the quick brown fox") == pytest.approx(1.0)


@pytest.mark.unit
def test_token_overlap_disjoint() -> None:
    assert _token_overlap("apple banana", "dog cat") == pytest.approx(0.0)


@pytest.mark.unit
def test_token_overlap_partial() -> None:
    # "a b c" vs "a b d" — shared: {a, b}, union: {a, b, c, d} → 0.5
    score = _token_overlap("a b c", "a b d")
    assert score == pytest.approx(0.5)


@pytest.mark.unit
def test_token_overlap_case_insensitive() -> None:
    assert _token_overlap("RRF Fusion", "rrf fusion") == pytest.approx(1.0)


@pytest.mark.unit
def test_token_overlap_both_empty() -> None:
    assert _token_overlap("", "") == pytest.approx(1.0)


@pytest.mark.unit
def test_token_overlap_one_empty() -> None:
    assert _token_overlap("something", "") == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# AnswerGrader — semantic_similarity tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tfidf_cosine_identical() -> None:
    score = _tfidf_cosine("rrf combines ranked lists", "rrf combines ranked lists")
    assert score == pytest.approx(1.0, abs=1e-6)


@pytest.mark.unit
def test_tfidf_cosine_disjoint() -> None:
    score = _tfidf_cosine("apple banana cherry", "dog elephant fox")
    assert score == pytest.approx(0.0, abs=1e-6)


@pytest.mark.unit
def test_tfidf_cosine_similar_higher_than_disjoint() -> None:
    similar = _tfidf_cosine(
        "RRF combines ranked lists by position",
        "RRF merges ranked lists using rank positions",
    )
    unrelated = _tfidf_cosine(
        "RRF combines ranked lists by position",
        "deep neural networks learn representations",
    )
    assert similar > unrelated


@pytest.mark.unit
def test_tfidf_cosine_both_empty() -> None:
    assert _tfidf_cosine("", "") == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# AnswerGrader — grade_entry and grade_batch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_answer_grader_perfect_score() -> None:
    grader = AnswerGrader()
    entry = _make_entry(expected_answer="RRF combines ranked lists by position.")
    result = grader.grade_entry(entry, "RRF combines ranked lists by position.")
    assert result.token_overlap == pytest.approx(1.0)
    assert result.semantic_similarity == pytest.approx(1.0, abs=1e-6)
    assert result.entry_id == entry.id


@pytest.mark.unit
def test_answer_grader_empty_candidate() -> None:
    grader = AnswerGrader()
    entry = _make_entry(expected_answer="Some answer with content.")
    result = grader.grade_entry(entry, "")
    assert result.token_overlap == pytest.approx(0.0)
    assert result.semantic_similarity == pytest.approx(0.0)


@pytest.mark.unit
def test_answer_grader_partial_overlap() -> None:
    grader = AnswerGrader()
    entry = _make_entry(expected_answer="RRF uses rank position not raw scores.")
    result = grader.grade_entry(entry, "RRF uses rank position for fusion.")
    # Some shared terms → scores > 0
    assert result.token_overlap > 0.0
    assert result.semantic_similarity > 0.0


@pytest.mark.unit
def test_answer_grader_batch_lengths_match() -> None:
    grader = AnswerGrader()
    entries = [_make_entry(id=f"e{i}") for i in range(5)]
    candidates = ["answer " * (i + 1) for i in range(5)]
    mean_overlap, mean_sim, results = grader.grade_batch(entries, candidates)
    assert len(results) == 5
    assert 0.0 <= mean_overlap <= 1.0
    assert 0.0 <= mean_sim <= 1.0


@pytest.mark.unit
def test_answer_grader_batch_mean_on_identical() -> None:
    grader = AnswerGrader()
    answer = "The cross-encoder reranker scores pairs using sigmoid normalisation."
    entries = [_make_entry(id=f"e{i}", expected_answer=answer) for i in range(4)]
    candidates = [answer] * 4
    mean_overlap, mean_sim, _ = grader.grade_batch(entries, candidates)
    assert mean_overlap == pytest.approx(1.0)
    assert mean_sim == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Oracle baseline: run_eval produces scores at or above floors
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_oracle_eval_passes_floors() -> None:
    from evals.run_eval import HIT_RATE_FLOOR, MRR_FLOOR, run

    report = run()
    assert report.hit_rate >= HIT_RATE_FLOOR, (
        f"hit_rate {report.hit_rate:.3f} below floor {HIT_RATE_FLOOR}"
    )
    assert report.mean_reciprocal_rank >= MRR_FLOOR, (
        f"MRR {report.mean_reciprocal_rank:.3f} below floor {MRR_FLOOR}"
    )
    assert report.n_entries == 50
