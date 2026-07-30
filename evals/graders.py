"""Answer-quality graders for the Librarian query/answer path.

Two graders:
- RetrievalGrader: hit_rate and mean_reciprocal_rank against expected source pages.
- AnswerGrader: token_overlap and semantic_similarity against expected answers.

Both are deterministic (no LLM calls) and safe to run in CI.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------


@dataclass
class GoldenEntry:
    """One entry from the golden dataset."""

    id: str
    category: str
    query: str
    expected_answer: str
    source_pages: list[str]
    difficulty: str


@dataclass
class RetrievalResult:
    """A single page returned by the retrieval pipeline."""

    page_path: str  # e.g. "wiki/rag/rag-retrieval-strategies.md"
    score: float = 0.0


@dataclass
class RetrievalGraderResult:
    """Per-entry retrieval grader output."""

    entry_id: str
    hit: bool  # at least one expected source page in retrieved results
    reciprocal_rank: float  # 1/rank of first expected page; 0 if not found
    retrieved_paths: list[str]
    expected_paths: list[str]


@dataclass
class AnswerGraderResult:
    """Per-entry answer grader output."""

    entry_id: str
    token_overlap: float  # Jaccard similarity of lowercased unigrams [0, 1]
    semantic_similarity: float  # cosine similarity of TF-IDF vectors [0, 1]
    candidate_answer: str
    expected_answer: str


@dataclass
class EvalReport:
    """Aggregate scores across all entries in a run."""

    hit_rate: float
    mean_reciprocal_rank: float
    mean_token_overlap: float
    mean_semantic_similarity: float
    retrieval_results: list[RetrievalGraderResult] = field(default_factory=list)
    answer_results: list[AnswerGraderResult] = field(default_factory=list)
    n_entries: int = 0

    def __str__(self) -> str:
        lines = [
            f"Entries evaluated : {self.n_entries}",
            f"Hit rate          : {self.hit_rate:.3f}  (floor >= 0.60)",
            f"Mean recip. rank  : {self.mean_reciprocal_rank:.3f}  (floor >= 0.40)",
            f"Token overlap     : {self.mean_token_overlap:.3f}",
            f"Semantic sim.     : {self.mean_semantic_similarity:.3f}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Retrieval grader
# ---------------------------------------------------------------------------


class RetrievalGrader:
    """Measures hit_rate and MRR against expected source pages.

    The retrieval pipeline returns a ranked list of RetrievalResult objects.
    The grader normalises paths for comparison so partial path matches work:
    "wiki/rag/rag-retrieval-strategies.md" matches if any retrieved path
    ends with that suffix.
    """

    def grade_entry(
        self,
        entry: GoldenEntry,
        retrieved: list[RetrievalResult],
    ) -> RetrievalGraderResult:
        retrieved_paths = [r.page_path for r in retrieved]
        rr = self._reciprocal_rank(entry.source_pages, retrieved_paths)
        return RetrievalGraderResult(
            entry_id=entry.id,
            hit=rr > 0,
            reciprocal_rank=rr,
            retrieved_paths=retrieved_paths,
            expected_paths=entry.source_pages,
        )

    def grade_batch(
        self,
        entries: list[GoldenEntry],
        retrieved_per_entry: list[list[RetrievalResult]],
    ) -> tuple[float, float, list[RetrievalGraderResult]]:
        """Grade a batch. Returns (hit_rate, mrr, per_entry_results)."""
        results = [
            self.grade_entry(e, r) for e, r in zip(entries, retrieved_per_entry, strict=True)
        ]
        hit_rate = sum(r.hit for r in results) / len(results) if results else 0.0
        mrr = sum(r.reciprocal_rank for r in results) / len(results) if results else 0.0
        return hit_rate, mrr, results

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(path: str) -> str:
        """Lower-case, strip leading slashes and whitespace."""
        return path.lower().strip().lstrip("/")

    def _matches(self, expected: str, retrieved_path: str) -> bool:
        """Return True if retrieved_path ends with expected (suffix match)."""
        norm_exp = self._normalise(expected)
        norm_ret = self._normalise(retrieved_path)
        return norm_ret == norm_exp or norm_ret.endswith("/" + norm_exp)

    def _rank_of_first_match(
        self, expected_pages: list[str], retrieved_paths: list[str]
    ) -> int | None:
        """Return 1-based rank of first retrieved path matching any expected page."""
        for rank, path in enumerate(retrieved_paths, start=1):
            if any(self._matches(exp, path) for exp in expected_pages):
                return rank
        return None

    def _reciprocal_rank(self, expected_pages: list[str], retrieved_paths: list[str]) -> float:
        rank = self._rank_of_first_match(expected_pages, retrieved_paths)
        return 1.0 / rank if rank is not None else 0.0


# ---------------------------------------------------------------------------
# Answer grader
# ---------------------------------------------------------------------------


def _tokenise(text: str) -> list[str]:
    """Lowercase alphabetic tokens — no external dependencies."""
    return re.findall(r"[a-z]+", text.lower())


def _token_overlap(a: str, b: str) -> float:
    """Jaccard similarity of unigram bags."""
    tokens_a = set(_tokenise(a))
    tokens_b = set(_tokenise(b))
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _tf(tokens: list[str]) -> dict[str, float]:
    """Term frequency (raw count normalised by doc length)."""
    freq: dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0.0) + 1.0
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}


def _tfidf_cosine(a: str, b: str) -> float:
    """Cosine similarity of TF-IDF vectors (IDF approximated over the two docs)."""
    tokens_a = _tokenise(a)
    tokens_b = _tokenise(b)
    vocab = set(tokens_a) | set(tokens_b)
    if not vocab:
        return 1.0

    # IDF: log(2 / (1 + df)) where df = number of docs containing the term
    idf: dict[str, float] = {}
    set_a, set_b = set(tokens_a), set(tokens_b)
    for term in vocab:
        df = (term in set_a) + (term in set_b)
        idf[term] = math.log(2.0 / (1.0 + df) + 1.0)  # smoothed

    tf_a = _tf(tokens_a)
    tf_b = _tf(tokens_b)

    vec_a = {t: tf_a.get(t, 0.0) * idf[t] for t in vocab}
    vec_b = {t: tf_b.get(t, 0.0) * idf[t] for t in vocab}

    dot = sum(vec_a[t] * vec_b[t] for t in vocab)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class AnswerGrader:
    """Scores candidate answers against expected answers.

    Metrics:
    - token_overlap: Jaccard similarity of unigram bags (0–1).
    - semantic_similarity: cosine similarity of TF-IDF vectors (0–1).

    Both are deterministic and require no external model. They serve as
    cheap regression gates; LLM-as-judge is the higher-quality complement.
    """

    def grade_entry(
        self,
        entry: GoldenEntry,
        candidate_answer: str,
    ) -> AnswerGraderResult:
        overlap = _token_overlap(entry.expected_answer, candidate_answer)
        sim = _tfidf_cosine(entry.expected_answer, candidate_answer)
        return AnswerGraderResult(
            entry_id=entry.id,
            token_overlap=overlap,
            semantic_similarity=sim,
            candidate_answer=candidate_answer,
            expected_answer=entry.expected_answer,
        )

    def grade_batch(
        self,
        entries: list[GoldenEntry],
        candidate_answers: list[str],
    ) -> tuple[float, float, list[AnswerGraderResult]]:
        """Grade a batch. Returns (mean_overlap, mean_sim, per_entry_results)."""
        results = [self.grade_entry(e, c) for e, c in zip(entries, candidate_answers, strict=True)]
        mean_overlap = sum(r.token_overlap for r in results) / len(results) if results else 0.0
        mean_sim = sum(r.semantic_similarity for r in results) / len(results) if results else 0.0
        return mean_overlap, mean_sim, results


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------


def load_golden_dataset(path: str | None = None) -> list[GoldenEntry]:
    """Load golden_dataset.json from the evals/ directory.

    Args:
        path: Optional explicit path. Defaults to golden_dataset.json
              in the same directory as this file.
    """
    import json
    from pathlib import Path

    if path is None:
        path = str(Path(__file__).parent / "golden_dataset.json")

    with open(path) as f:
        raw = json.load(f)

    return [
        GoldenEntry(
            id=item["id"],
            category=item["category"],
            query=item["query"],
            expected_answer=item["expected_answer"],
            source_pages=item["source_pages"],
            difficulty=item["difficulty"],
        )
        for item in raw
    ]
