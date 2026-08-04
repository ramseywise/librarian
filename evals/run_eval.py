"""Eval runner: retrieval grader + answer grader over the golden dataset.

Usage:
    uv run python evals/run_eval.py           # oracle mode (default, gates floors)
    uv run python evals/run_eval.py --live    # live retrieval (report-only)

Two modes:

*Oracle* (default): simulates retrieval by returning the expected source pages
in rank-1 position and uses the expected answer as the candidate answer.  This
produces a 1.0 baseline that proves the grader mechanics are wired correctly,
and it gates on the regression floors (exit 1 below floor).

*Live* (`--live`): retrieval goes through the real search core
(`app.mcp_server.server._search_rows` — BM25 + hybrid rerank), so hit-rate and
MRR measure actual pipeline quality.  Answers stay oracle (live answer grading
needs the LLM — separate concern).  Live mode is report-only: floors are
printed for reference but never exit(1).  Retrieved paths are absolute; the
grader's suffix matching handles the repo-relative golden `source_pages`, so
no normalization is needed.

Exit codes:
    0 — all scores at or above floor thresholds (or --live mode)
    1 — one or more scores below floor (oracle mode only)
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Make the evals package importable when run as a script from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.graders import (
    AnswerGrader,
    EvalReport,
    GoldenEntry,
    RetrievalGrader,
    RetrievalResult,
    load_golden_dataset,
)

# ---------------------------------------------------------------------------
# Regression floors (from data/wiki/rag/rag-evaluation.md — never lower these)
# ---------------------------------------------------------------------------

HIT_RATE_FLOOR = 0.60
MRR_FLOOR = 0.40


# ---------------------------------------------------------------------------
# Oracle simulation helpers
# ---------------------------------------------------------------------------


def _oracle_retrieval(entry: GoldenEntry) -> list[RetrievalResult]:
    """Return expected source pages as rank-1 results (oracle baseline)."""
    return [RetrievalResult(page_path=p, score=1.0) for p in entry.source_pages]


def _oracle_answer(entry: GoldenEntry) -> str:
    """Return expected answer verbatim (oracle baseline)."""
    return entry.expected_answer


def _live_retrieval(entry: GoldenEntry) -> list[RetrievalResult]:
    """Retrieve through the real search core (BM25 + hybrid rerank)."""
    from app.mcp_server.server import _search_rows

    rows = _search_rows(entry.query, domain="", limit=10, tool="eval")
    return [RetrievalResult(page_path=row[0], score=float(row[6])) for row in rows]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run(
    dataset_path: str | None = None,
    *,
    verbose: bool = False,
    live: bool = False,
) -> EvalReport:
    entries = load_golden_dataset(dataset_path)

    retrieval_grader = RetrievalGrader()
    answer_grader = AnswerGrader()

    retrieve = _live_retrieval if live else _oracle_retrieval
    retrieved_lists = [retrieve(e) for e in entries]
    candidate_answers = [_oracle_answer(e) for e in entries]

    hit_rate, mrr, ret_results = retrieval_grader.grade_batch(entries, retrieved_lists)
    mean_overlap, mean_sim, ans_results = answer_grader.grade_batch(entries, candidate_answers)

    report = EvalReport(
        hit_rate=hit_rate,
        mean_reciprocal_rank=mrr,
        mean_token_overlap=mean_overlap,
        mean_semantic_similarity=mean_sim,
        retrieval_results=ret_results,
        answer_results=ans_results,
        n_entries=len(entries),
    )

    if verbose:
        _print_failures(ret_results, ans_results)

    return report


def _print_failures(
    ret_results: list,
    ans_results: list,
    *,
    overlap_warn: float = 0.5,
    sim_warn: float = 0.5,
) -> None:
    miss_ret = [r for r in ret_results if not r.hit]
    if miss_ret:
        print(f"\nRetrieval misses ({len(miss_ret)}):")
        for r in miss_ret:
            print(f"  {r.entry_id}: expected {r.expected_paths}")

    low_ans = [
        r for r in ans_results if r.token_overlap < overlap_warn or r.semantic_similarity < sim_warn
    ]
    if low_ans:
        print(f"\nLow-scoring answers ({len(low_ans)}):")
        for r in low_ans:
            print(f"  {r.entry_id}: overlap={r.token_overlap:.2f} sim={r.semantic_similarity:.2f}")


def _save_baseline(report: EvalReport, out_dir: Path, prefix: str = "baseline") -> Path:
    """Persist baseline scores as JSON for regression tracking."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_path = out_dir / f"{prefix}-{ts}.json"
    data = {
        "timestamp": ts,
        "mode": "live" if prefix.startswith("live") else "oracle",
        "n_entries": report.n_entries,
        "hit_rate": report.hit_rate,
        "mean_reciprocal_rank": report.mean_reciprocal_rank,
        "mean_token_overlap": report.mean_token_overlap,
        "mean_semantic_similarity": report.mean_semantic_similarity,
        "floors": {
            "hit_rate": HIT_RATE_FLOOR,
            "mrr": MRR_FLOOR,
        },
    }
    out_path.write_text(json.dumps(data, indent=2))
    return out_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run answer-quality graders over the golden dataset."
    )
    parser.add_argument("--dataset", default=None, help="Path to golden_dataset.json")
    parser.add_argument("--verbose", action="store_true", help="Print failures")
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save scores to evals/baselines/",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Retrieve via the live search core (report-only; floors do not gate)",
    )
    args = parser.parse_args()

    report = run(dataset_path=args.dataset, verbose=args.verbose, live=args.live)
    print(report)

    if args.save_baseline:
        baseline_dir = Path(__file__).parent / "baselines"
        prefix = "live-baseline" if args.live else "baseline"
        path = _save_baseline(report, baseline_dir, prefix=prefix)
        print(f"\nBaseline saved → {path}")

    # Gate on floors — oracle mode only; live mode reports without failing
    failures = []
    if report.hit_rate < HIT_RATE_FLOOR:
        failures.append(f"hit_rate {report.hit_rate:.3f} < floor {HIT_RATE_FLOOR}")
    if report.mean_reciprocal_rank < MRR_FLOOR:
        failures.append(f"MRR {report.mean_reciprocal_rank:.3f} < floor {MRR_FLOOR}")

    if failures:
        print("\nFLOOR VIOLATIONS:")
        for f in failures:
            print(f"  {f}")
        if not args.live:
            sys.exit(1)
        print("(live mode is report-only — floors gate oracle mode)")
    else:
        print("\nAll floors passed.")


if __name__ == "__main__":
    main()
