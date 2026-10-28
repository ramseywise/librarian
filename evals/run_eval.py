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
(`app.mcp_server.server._search_rows` — BM25 + RRF rerank), so hit-rate and
MRR measure actual pipeline quality.  Answers stay oracle (live answer grading
needs the LLM — separate concern).  Retrieved paths are absolute; the grader's
suffix matching handles the repo-relative golden `source_pages`, so no
normalization is needed.

Live arms with a committed baseline gate against their own floors
(`LIVE_ARM_FLOORS`): `sem` is the healthy pipeline, `nofts` is the degraded
substring-fallback path taken when the fts extension is unavailable.  Both are
gated so a ranking change cannot improve one arm at the other's expense.  The
`lex` and `graph` ablations remain report-only.

*Agent* (`--agent`, BILLABLE): runs each query through the real chat agent
(`app.backend.agent.run_agent_stream`, the path the UI uses) and grades the run with
`AgentGrader` — expected source-page recall over pages read and pages cited, plus
citation grounding. `--judge` adds `LLMJudgeGrader` (one more billable call per entry)
scoring the answer against `expected_answer`. `--limit N` caps the entries run.
Report-only: no floor until a baseline has been measured.

Exit codes:
    0 — all scores at or above the applicable floors
    1 — one or more scores below floor (oracle mode, or a gated live arm)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

# Make the evals package importable when run as a script from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from evals.graders import (
    AgentEvalReport,
    AgentGrader,
    AgentRun,
    AnswerGrader,
    EvalReport,
    GoldenEntry,
    JudgeResult,
    LLMJudgeGrader,
    RetrievalGrader,
    RetrievalResult,
    load_golden_dataset,
)

if TYPE_CHECKING:
    import anthropic

# ---------------------------------------------------------------------------
# Regression floors (from data/wiki/rag/rag-evaluation.md — never lower these)
# ---------------------------------------------------------------------------

HIT_RATE_FLOOR = 0.60
MRR_FLOOR = 0.40

# Per-arm live floors, derived from the committed baselines minus a tolerance for
# run-to-run noise (embedding nondeterminism, tie order). The `nofts` arm scores
# far below the oracle floors by construction — retrieval there is substring
# matching — so gating it against HIT_RATE_FLOOR/MRR_FLOOR would either fail
# permanently or force those floors down and stop protecting the healthy arm.
# Each arm is therefore gated against its own measured baseline.
LIVE_FLOOR_TOLERANCE = 0.05

LIVE_ARM_FLOORS: dict[str, dict[str, float]] = {
    # evals/baselines/live-baseline-2026-08-04T14-24-15Z.json — hit 1.0, MRR 0.905
    "sem": {"hit_rate": 0.95, "mrr": 0.85},
    # evals/baselines/live-nofts-baseline-2026-08-04T14-24-43Z.json — hit 0.58, MRR 0.295
    "nofts": {"hit_rate": 0.53, "mrr": 0.245},
}


# ---------------------------------------------------------------------------
# Oracle simulation helpers
# ---------------------------------------------------------------------------


def _oracle_retrieval(entry: GoldenEntry) -> list[RetrievalResult]:
    """Return expected source pages as rank-1 results (oracle baseline)."""
    return [RetrievalResult(page_path=p, score=1.0) for p in entry.source_pages]


def _oracle_answer(entry: GoldenEntry) -> str:
    """Return expected answer verbatim (oracle baseline)."""
    return entry.expected_answer


def _live_retrieval(entry: GoldenEntry, arm: str = "sem") -> list[RetrievalResult]:
    """Retrieve through the real search core (BM25 + RRF rerank)."""
    from app.mcp_server.server import _search_rows

    rows, _degraded = _search_rows(
        entry.query, domain="", limit=10, tool="eval", expand=(arm == "graph")
    )
    return [RetrievalResult(page_path=row[0], score=float(row[6])) for row in rows]


def _resolve_dataset_path(dataset_path: str | None) -> Path:
    """Mirror load_golden_dataset's default so provenance can hash the file."""
    return Path(dataset_path) if dataset_path else Path(__file__).parent / "golden_dataset.json"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run(
    dataset_path: str | None = None,
    *,
    verbose: bool = False,
    live: bool = False,
    arm: str = "sem",
) -> EvalReport:
    entries = load_golden_dataset(dataset_path)

    retrieval_grader = RetrievalGrader()
    answer_grader = AnswerGrader()

    restore_embeddings = None
    restore_fts = None
    if live and arm == "lex":
        # Lexical arm: drop the semantic + backlink blend so ranking is BM25-only.
        # The index must exist BEFORE the flag flips — build_index also consults
        # HAS_EMBEDDINGS, and a rebuild triggered mid-run would persist an
        # embedding-less index that later sem/graph arms silently rank against.
        from app.mcp_server import server

        server.get_con().close()
        restore_embeddings = server.HAS_EMBEDDINGS
        server.HAS_EMBEDDINGS = False
    elif live and arm == "nofts":
        # Degraded arm: force the tokenized-LIKE fallback so the floor gate covers
        # the path taken when the fts extension is unavailable. Same ordering
        # constraint as `lex` — build the index while fts still works, so the arm
        # measures degraded *retrieval*, not a degraded index.
        from app.mcp_server import server

        server.get_con().close()
        restore_fts = server._ensure_fts
        server._ensure_fts = lambda con: False

    try:
        if live:
            retrieved_lists = [_live_retrieval(e, arm=arm) for e in entries]
        else:
            retrieved_lists = [_oracle_retrieval(e) for e in entries]
    finally:
        from app.mcp_server import server

        if restore_embeddings is not None:
            server.HAS_EMBEDDINGS = restore_embeddings
        if restore_fts is not None:
            server._ensure_fts = restore_fts

    candidate_answers = [_oracle_answer(e) for e in entries]

    hit_rate, mrr, mean_recall, ret_results = retrieval_grader.grade_batch(entries, retrieved_lists)
    mean_overlap, mean_sim, ans_results = answer_grader.grade_batch(entries, candidate_answers)

    report = EvalReport(
        hit_rate=hit_rate,
        mean_reciprocal_rank=mrr,
        mean_expected_set_recall=mean_recall,
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


def _edge_count() -> int:
    """Row count of the materialized typed-edges table."""
    from app.mcp_server.server import get_con

    con = get_con()
    try:
        return con.execute("SELECT count(*) FROM edges").fetchone()[0]
    finally:
        con.close()


def _save_baseline(
    report: EvalReport,
    out_dir: Path,
    prefix: str = "baseline",
    *,
    arm: str | None = None,
    dataset_file: Path | None = None,
) -> Path:
    """Persist baseline scores + run provenance as JSON for regression tracking.

    Provenance pins what the numbers were measured against — a baseline whose
    golden set, embedding model, or edge count has since changed is not
    comparable, and without the hash that drift is invisible.
    """
    from app.mcp_server.server import EMB_MODEL_ID

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_path = out_dir / f"{prefix}-{ts}.json"
    live = prefix.startswith("live")
    dataset_file = dataset_file if dataset_file is not None else _resolve_dataset_path(None)
    data = {
        "timestamp": ts,
        "mode": "live" if live else "oracle",
        "arm": arm if live else None,
        "dataset": dataset_file.name,
        "golden_set_hash": hashlib.sha256(dataset_file.read_bytes()).hexdigest(),
        "embedding_model_id": EMB_MODEL_ID,
        "edge_count": _edge_count() if live else None,
        "n_entries": report.n_entries,
        "hit_rate": report.hit_rate,
        "mean_reciprocal_rank": report.mean_reciprocal_rank,
        "mean_expected_set_recall": report.mean_expected_set_recall,
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
# Agent mode (BILLABLE — every entry is a real agent run)
# ---------------------------------------------------------------------------

# Judge model: same default as the agent. Override with EVAL_JUDGE_MODEL to trade
# judge quality for cost once the judge has been calibrated against human grades.
JUDGE_MODEL = os.getenv("EVAL_JUDGE_MODEL", "claude-opus-5-5")


async def collect_agent_run(
    query: str, *, client: anthropic.AsyncAnthropic, model: str | None = None
) -> AgentRun:
    """Drive run_agent_stream to completion and collect what the grader needs.

    Consumes the same SSE events the UI does, so the eval measures the shipped path.
    Telemetry lines are tagged source="eval" so they can be filtered from chat traffic.
    """
    from app.backend import agent

    tokens: list[str] = []
    grounding: dict[str, list[str]] = {"pages_read": [], "cited": [], "ungrounded": []}
    async for event in agent.run_agent_stream(
        query, client=client, model=model or agent.MODEL, source="eval"
    ):
        if event["type"] == "token":
            tokens.append(event["content"])
        elif event["type"] == "grounding":
            grounding = event
    return AgentRun(
        answer="".join(tokens),
        pages_read=list(grounding["pages_read"]),
        cited=list(grounding["cited"]),
        ungrounded=list(grounding["ungrounded"]),
    )


async def run_agent_eval(
    entries: list[GoldenEntry],
    *,
    client: anthropic.AsyncAnthropic,
    model: str | None = None,
    judge: LLMJudgeGrader | None = None,
) -> AgentEvalReport:
    """Run and grade the chat agent over `entries`.

    Sequential on purpose: one entry at a time keeps rate-limit behaviour and per-run
    telemetry easy to read, and the golden sets are small.

    No gating threshold: agent-mode scores have never been measured, and a floor set
    before a baseline exists is a guess. Gate it the way the live arms were gated —
    measure, commit the baseline, then set floor = baseline - tolerance.
    """
    runs = [await collect_agent_run(e.query, client=client, model=model) for e in entries]
    results, means = AgentGrader().grade_batch(entries, runs)

    judge_results: list[JudgeResult] = []
    if judge is not None:
        judge_results = [
            await judge.grade_entry(e, r.answer) for e, r in zip(entries, runs, strict=True)
        ]
    scores = [j.score for j in judge_results if j.score is not None]

    return AgentEvalReport(
        n_entries=len(entries),
        mean_read_recall=means["read_recall"],
        mean_cited_recall=means["cited_recall"],
        grounded_rate=means["grounded_rate"],
        citation_rate=means["citation_rate"],
        mean_judge_score=sum(scores) / len(scores) if scores else None,
        n_judged=len(scores),
        results=results,
        judge_results=judge_results,
    )


def _print_agent_failures(report: AgentEvalReport) -> None:
    for r in report.results:
        if r.read_recall < 1.0 or not r.grounded:
            print(
                f"  {r.entry_id}: read_recall={r.read_recall:.2f} "
                f"cited_recall={r.cited_recall:.2f} expected={r.expected_ids} "
                f"read={r.pages_read} ungrounded={r.ungrounded}"
            )
    for j in report.judge_results:
        if j.score is None or j.score <= 2:
            print(f"  {j.entry_id}: judge={j.score} — {j.rationale}")


def _save_agent_baseline(
    report: AgentEvalReport, out_dir: Path, *, dataset_file: Path, model: str
) -> Path:
    """Persist agent-mode scores + provenance. Not consumed by any gate yet."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    prefix = "agent-multihop" if "multihop" in dataset_file.stem else "agent"
    out_path = out_dir / f"{prefix}-baseline-{ts}.json"
    data = {
        "timestamp": ts,
        "mode": "agent",
        "model": model,
        "judge_model": JUDGE_MODEL if report.judge_results else None,
        "dataset": dataset_file.name,
        "golden_set_hash": hashlib.sha256(dataset_file.read_bytes()).hexdigest(),
        "n_entries": report.n_entries,
        "mean_read_recall": report.mean_read_recall,
        "mean_cited_recall": report.mean_cited_recall,
        "grounded_rate": report.grounded_rate,
        "citation_rate": report.citation_rate,
        "mean_judge_score": report.mean_judge_score,
        "n_judged": report.n_judged,
        "per_entry": [asdict(r) for r in report.results],
        "judge": [asdict(j) for j in report.judge_results],
    }
    out_path.write_text(json.dumps(data, indent=2))
    return out_path


def _main_agent(args: argparse.Namespace) -> None:
    import anthropic
    from dotenv import load_dotenv

    from app.backend import agent

    load_dotenv(Path(__file__).parent.parent / ".env")
    entries = load_golden_dataset(args.dataset)
    if args.limit:
        entries = entries[: args.limit]

    client = anthropic.AsyncAnthropic()
    judge = LLMJudgeGrader(client, JUDGE_MODEL) if args.judge else None
    report = asyncio.run(run_agent_eval(entries, client=client, judge=judge))
    print(report)
    if args.verbose:
        _print_agent_failures(report)
    if args.save_baseline:
        path = _save_agent_baseline(
            report,
            Path(__file__).parent / "baselines",
            dataset_file=_resolve_dataset_path(args.dataset),
            model=agent.MODEL,
        )
        print(f"\nBaseline saved → {path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
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
    parser.add_argument(
        "--arm",
        choices=["lex", "sem", "graph", "nofts"],
        default="sem",
        help="Live-mode ablation arm: lex (BM25 only), sem (current pipeline), "
        "graph (sem + one-hop typed expansion), nofts (fts forced off — the "
        "degraded substring-fallback path)",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="BILLABLE: run each query through the chat agent and grade source-page "
        "recall + citation grounding (report-only)",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="BILLABLE: with --agent, also score answers with the LLM judge",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="With --agent, run only the first N entries"
    )
    args = parser.parse_args()

    if args.arm != "sem" and not args.live:
        parser.error("--arm applies to live mode only (add --live)")
    if (args.judge or args.limit) and not args.agent:
        parser.error("--judge and --limit apply to agent mode only (add --agent)")
    if args.agent:
        if args.live:
            parser.error("--agent and --live are separate modes")
        _main_agent(args)
        return

    report = run(dataset_path=args.dataset, verbose=args.verbose, live=args.live, arm=args.arm)
    print(report)

    if args.save_baseline:
        baseline_dir = Path(__file__).parent / "baselines"
        dataset_file = _resolve_dataset_path(args.dataset)
        if args.live:
            prefix = f"live-{args.arm}"
            if "multihop" in dataset_file.stem:
                prefix += "-multihop"
        else:
            prefix = "baseline"
        path = _save_baseline(
            report, baseline_dir, prefix=prefix, arm=args.arm, dataset_file=dataset_file
        )
        print(f"\nBaseline saved → {path}")

    # Gate on floors. Oracle mode uses the global floors. Live mode gates only
    # the arms with a committed baseline (sem, nofts) — `lex` and `graph` are
    # ablations with no regression contract, so they stay report-only.
    if args.live:
        floors = LIVE_ARM_FLOORS.get(args.arm)
        gating = floors is not None
    else:
        floors = {"hit_rate": HIT_RATE_FLOOR, "mrr": MRR_FLOOR}
        gating = True

    failures = []
    if floors is not None:
        if report.hit_rate < floors["hit_rate"]:
            failures.append(f"hit_rate {report.hit_rate:.3f} < floor {floors['hit_rate']}")
        if report.mean_reciprocal_rank < floors["mrr"]:
            failures.append(f"MRR {report.mean_reciprocal_rank:.3f} < floor {floors['mrr']}")

    if failures:
        print("\nFLOOR VIOLATIONS:")
        for f in failures:
            print(f"  {f}")
        if gating:
            sys.exit(1)
    elif floors is None:
        print(f"\n(arm '{args.arm}' has no regression floor — report-only)")
    else:
        print("\nAll floors passed.")


if __name__ == "__main__":
    main()
