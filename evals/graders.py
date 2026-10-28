"""Answer-quality graders for the Librarian query/answer path.

Deterministic graders (no LLM calls, safe to run in CI):
- RetrievalGrader: hit_rate and mean_reciprocal_rank against expected source pages.
- AnswerGrader: token_overlap and semantic_similarity against expected answers.
- AgentGrader: expected source-page recall over the pages a chat-agent run read/cited,
  plus citation grounding.

Billable (opt-in only):
- LLMJudgeGrader: one model call per entry scoring the agent's answer against
  expected_answer. Never constructed unless run_eval.py is given --judge.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import anthropic

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

    page_path: str  # e.g. "data/wiki/rag/rag-retrieval-strategies.md"
    score: float = 0.0


@dataclass
class RetrievalGraderResult:
    """Per-entry retrieval grader output."""

    entry_id: str
    hit: bool  # at least one expected source page in retrieved results
    reciprocal_rank: float  # 1/rank of first expected page; 0 if not found
    expected_set_recall: float  # |expected pages retrieved| / |expected|
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
    mean_expected_set_recall: float
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
            f"Expected-set rec. : {self.mean_expected_set_recall:.3f}",
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
    "data/wiki/rag/rag-retrieval-strategies.md" matches if any retrieved path
    ends with that suffix.
    """

    def grade_entry(
        self,
        entry: GoldenEntry,
        retrieved: list[RetrievalResult],
    ) -> RetrievalGraderResult:
        retrieved_paths = [r.page_path for r in retrieved]
        rr = self._reciprocal_rank(entry.source_pages, retrieved_paths)
        matched = sum(
            any(self._matches(exp, p) for p in retrieved_paths) for exp in entry.source_pages
        )
        recall = matched / len(entry.source_pages) if entry.source_pages else 0.0
        return RetrievalGraderResult(
            entry_id=entry.id,
            hit=rr > 0,
            reciprocal_rank=rr,
            expected_set_recall=recall,
            retrieved_paths=retrieved_paths,
            expected_paths=entry.source_pages,
        )

    def grade_batch(
        self,
        entries: list[GoldenEntry],
        retrieved_per_entry: list[list[RetrievalResult]],
    ) -> tuple[float, float, float, list[RetrievalGraderResult]]:
        """Grade a batch. Returns (hit_rate, mrr, mean_recall, per_entry_results)."""
        results = [
            self.grade_entry(e, r) for e, r in zip(entries, retrieved_per_entry, strict=True)
        ]
        hit_rate = sum(r.hit for r in results) / len(results) if results else 0.0
        mrr = sum(r.reciprocal_rank for r in results) / len(results) if results else 0.0
        mean_recall = sum(r.expected_set_recall for r in results) / len(results) if results else 0.0
        return hit_rate, mrr, mean_recall, results

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
# Agent grader (deterministic)
# ---------------------------------------------------------------------------


@dataclass
class AgentRun:
    """What one chat-agent run produced, collected from its SSE events."""

    answer: str
    pages_read: list[str]
    cited: list[str]
    ungrounded: list[str]


@dataclass
class AgentGraderResult:
    """Per-entry agent grader output."""

    entry_id: str
    read_recall: float  # |expected pages read| / |expected|
    cited_recall: float  # |expected pages cited| / |expected|
    grounded: bool  # no citation to a page left unread in this run
    has_citation: bool
    expected_ids: list[str]
    pages_read: list[str]
    cited: list[str]
    ungrounded: list[str]


@dataclass
class AgentEvalReport:
    """Aggregate agent-mode scores. Report-only — see run_eval.run_agent_eval."""

    n_entries: int
    mean_read_recall: float
    mean_cited_recall: float
    grounded_rate: float
    citation_rate: float
    mean_judge_score: float | None = None  # 1–5; None when --judge was not given
    n_judged: int = 0
    results: list[AgentGraderResult] = field(default_factory=list)
    judge_results: list[JudgeResult] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Entries evaluated : {self.n_entries}",
            f"Read recall       : {self.mean_read_recall:.3f}",
            f"Cited recall      : {self.mean_cited_recall:.3f}",
            f"Grounded rate     : {self.grounded_rate:.3f}",
            f"Citation rate     : {self.citation_rate:.3f}",
        ]
        if self.mean_judge_score is not None:
            lines.append(
                f"Judge score (1-5) : {self.mean_judge_score:.2f}  "
                f"({self.n_judged}/{self.n_entries} parsed)"
            )
        lines.append("(agent mode is report-only — no floor until a baseline is measured)")
        return "\n".join(lines)


def _page_id(path: str) -> str:
    """Golden source_pages are repo-relative paths; the agent speaks in filename stems."""
    return Path(path).stem.lower()


class AgentGrader:
    """Grades a chat-agent run against an entry's expected source pages.

    read_recall asks "did the agent find and read the right pages"; cited_recall asks
    "did it attribute its answer to them". A run can read everything and cite nothing,
    which is exactly the gap prompt-only grounding left unmeasured.
    """

    def grade_entry(self, entry: GoldenEntry, run: AgentRun) -> AgentGraderResult:
        expected = list(dict.fromkeys(_page_id(p) for p in entry.source_pages))
        read = {p.lower() for p in run.pages_read}
        cited = {c.lower() for c in run.cited}

        def recall(found: set[str]) -> float:
            return sum(e in found for e in expected) / len(expected) if expected else 0.0

        return AgentGraderResult(
            entry_id=entry.id,
            read_recall=recall(read),
            cited_recall=recall(cited),
            grounded=not run.ungrounded,
            has_citation=bool(run.cited),
            expected_ids=expected,
            pages_read=run.pages_read,
            cited=run.cited,
            ungrounded=run.ungrounded,
        )

    def grade_batch(
        self, entries: list[GoldenEntry], runs: list[AgentRun]
    ) -> tuple[list[AgentGraderResult], dict[str, float]]:
        """Returns (per_entry_results, means keyed by metric name)."""
        results = [self.grade_entry(e, r) for e, r in zip(entries, runs, strict=True)]
        n = len(results) or 1
        means = {
            "read_recall": sum(r.read_recall for r in results) / n,
            "cited_recall": sum(r.cited_recall for r in results) / n,
            "grounded_rate": sum(r.grounded for r in results) / n,
            "citation_rate": sum(r.has_citation for r in results) / n,
        }
        return results, means


# ---------------------------------------------------------------------------
# LLM judge (billable — opt-in only)
# ---------------------------------------------------------------------------


@dataclass
class JudgeResult:
    """Per-entry judge output. score is None when the reply could not be parsed."""

    entry_id: str
    score: int | None
    rationale: str


_JUDGE_SYSTEM = """You grade answers from a knowledge-base assistant against a reference answer.

Score 1-5 for factual agreement with the reference:
5 — every key claim in the reference is present and nothing contradicts it
4 — most key claims present, nothing contradicts it
3 — some key claims present, or a minor contradiction
2 — few key claims present, or a material contradiction
1 — wrong, off-topic, or a refusal

Extra correct detail beyond the reference is not penalised. Ignore inline citation
markers like [page:some-id] and ignore formatting.

Reply with only a JSON object: {"score": <1-5>, "rationale": "<one sentence>"}"""

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_judge_reply(text: str) -> tuple[int | None, str]:
    """Extract (score, rationale); (None, raw) if the reply is not a valid verdict.

    Unparseable replies are excluded from the mean rather than scored 0 — a parse
    failure is a judge problem, not evidence about the answer.
    """
    m = _JSON_OBJ_RE.search(text)
    if not m:
        return None, text.strip()
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, text.strip()
    score = obj.get("score")
    if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
        return None, text.strip()
    return score, str(obj.get("rationale", ""))


class LLMJudgeGrader:
    """Scores an agent answer against expected_answer with one model call per entry.

    BILLABLE. The client is injected (an anthropic.AsyncAnthropic in real use, a fake
    in tests); nothing here reads the environment.
    """

    def __init__(
        self, client: anthropic.AsyncAnthropic, model: str, max_tokens: int = 2048
    ) -> None:
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    async def grade_entry(self, entry: GoldenEntry, answer: str) -> JudgeResult:
        prompt = (
            f"Question:\n{entry.query}\n\n"
            f"Reference answer:\n{entry.expected_answer}\n\n"
            f"Candidate answer:\n{answer}"
        )
        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=_JUDGE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        score, rationale = parse_judge_reply(text)
        return JudgeResult(entry_id=entry.id, score=score, rationale=rationale)


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------


def load_golden_dataset(path: str | None = None) -> list[GoldenEntry]:
    """Load golden_dataset.json from the evals/ directory.

    Args:
        path: Optional explicit path. Defaults to golden_dataset.json
              in the same directory as this file.
    """
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
