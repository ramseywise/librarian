"""Offline grounding eval (assistant trust G3): golden questions through the real agent loop,
scored on what the answer cites, not on what it says.

    uv run python -m evals.run_grounding_eval --dry-run     # what would run and what it would cost
    uv run python -m evals.run_grounding_eval --limit 3     # BILLABLE: the real model, 3 questions
    uv run python -m evals.run_grounding_eval               # BILLABLE: all of golden_grounding.json

Each question runs through `librarian.agent.loop.run_agent_stream` (the path the UI uses) against
the current index. There is no judge here: every metric is counted from the `grounding` event, so
a run costs the agent's calls only (plus the claim-support judge when `LIBRARIAN_CLAIM_JUDGE` is
on). The answer text is never written anywhere.

Metrics:
    all citations read   answers whose every citation is to a page read in that run / answers
                         that cited something
    ungrounded citations citations to a page not read / all citations, pooled over answers
    abstention           unanswerable questions answered without citing any page / unanswerable
    expected page cited  answerable questions citing an expected page / answerable (the check
                         that abstention is not bought by never citing)
    claim support        (claim, cited page) pairs with support found / pairs checked
                         (`grounding.support`, the G2 check: deterministic, plus the judge
                         when `LIBRARIAN_CLAIM_JUDGE` is on; n/a when the event carries none)

REPORT-ONLY: `THRESHOLDS` holds no floor until a baseline has been measured, and with no floor
set the run prints its numbers and exits 0. `golden_grounding.json` carries `"reviewed": false`
until a human has checked the questions.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from evals.run_chat_eval import CEILING, TYPICAL, _cost
from librarian.config import get_settings
from librarian.pricing import TokenUsage

if TYPE_CHECKING:
    import anthropic

EVALS_DIR = Path(__file__).parent
DEFAULT_DATASET = EVALS_DIR / "golden_grounding.json"
BASELINES = EVALS_DIR / "baselines"

# Floors (or, for `ungrounded_citations`, a ceiling) for the gate. None = not gated. They are
# set from a measured baseline and from nothing else; until one exists the eval only reports.
THRESHOLDS: dict[str, float | None] = {
    "all_citations_read": None,
    "ungrounded_citations": None,
    "abstention": None,
    "expected_page_cited": None,
    "claim_support": None,
}
# Metrics where lower is better: the threshold is a ceiling.
_LOWER_IS_BETTER = frozenset({"ungrounded_citations"})


@dataclass
class GroundingQuestion:
    id: str
    question: str
    expected_pages: list[str]

    @property
    def answerable(self) -> bool:
        return bool(self.expected_pages)


def load_golden(path: Path = DEFAULT_DATASET) -> tuple[list[GroundingQuestion], bool]:
    """(questions, reviewed). `reviewed` is False unless the file says otherwise."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    questions = [
        GroundingQuestion(q["id"], q["question"], list(q["expected_pages"]))
        for q in raw["questions"]
    ]
    return questions, bool(raw.get("reviewed", False))


@dataclass
class GroundingResult:
    id: str
    answerable: bool
    cited: list[str]
    pages_read: list[str]
    ungrounded: list[str]
    expected_cited: bool | None  # None for an unanswerable question
    support_checked: int | None  # (claim, page) pairs; None when the event carries no check
    support_found: int | None
    support_judged: bool
    cost: float | None


async def run_question(
    q: GroundingQuestion, *, client: anthropic.AsyncAnthropic, model: str
) -> GroundingResult:
    from librarian.agent import loop as agent

    usage = TokenUsage()

    def on_usage(u: TokenUsage) -> None:
        nonlocal usage
        usage = usage + u

    grounding: dict[str, Any] = {"pages_read": [], "cited": [], "ungrounded": []}
    async for event in agent.run_agent_stream(
        q.question, client=client, model=model, source="eval", on_usage=on_usage
    ):
        if event["type"] == "grounding":
            grounding = event
    cited = list(grounding["cited"])
    expected = {p.lower() for p in q.expected_pages}
    support = grounding.get("support")
    return GroundingResult(
        id=q.id,
        answerable=q.answerable,
        cited=cited,
        pages_read=list(grounding["pages_read"]),
        ungrounded=list(grounding["ungrounded"]),
        expected_cited=any(c.lower() in expected for c in cited) if q.answerable else None,
        support_checked=support["checked"] if support else None,
        support_found=support["supported"] if support else None,
        support_judged=bool(support and support.get("judge")),
        cost=_cost(model, usage),
    )


def _share(hits: int, total: int) -> float | None:
    return hits / total if total else None


@dataclass
class GroundingReport:
    results: list[GroundingResult]

    def summary(self) -> dict[str, Any]:
        r = self.results
        citing = [x for x in r if x.cited]
        answerable = [x for x in r if x.answerable]
        unanswerable = [x for x in r if not x.answerable]
        checked = [x for x in r if x.support_checked is not None]
        costs = [x.cost for x in r if x.cost is not None]
        return {
            "n": len(r),
            "n_answerable": len(answerable),
            "n_unanswerable": len(unanswerable),
            "n_citing": len(citing),
            "all_citations_read": _share(sum(not x.ungrounded for x in citing), len(citing)),
            "n_citations": sum(len(x.cited) for x in r),
            "ungrounded_citations": _share(
                sum(len(x.ungrounded) for x in r), sum(len(x.cited) for x in r)
            ),
            "abstention": _share(sum(not x.cited for x in unanswerable), len(unanswerable)),
            "expected_page_cited": _share(
                sum(bool(x.expected_cited) for x in answerable), len(answerable)
            ),
            "n_support_checked": sum(x.support_checked or 0 for x in checked),
            "n_judged": sum(x.support_judged for x in r),
            "claim_support": _share(
                sum(x.support_found or 0 for x in checked),
                sum(x.support_checked or 0 for x in checked),
            ),
            "cost_usd": sum(costs) if costs else None,
        }

    def __str__(self) -> str:
        s = self.summary()

        def f(v: float | None, fmt: str = "{:.3f}") -> str:
            return "n/a" if v is None else fmt.format(v)

        return "\n".join(
            [
                f"Questions           : {s['n']} ({s['n_answerable']} answerable, "
                f"{s['n_unanswerable']} unanswerable)",
                f"All citations read  : {f(s['all_citations_read'])}  (n={s['n_citing']} citing)",
                f"Ungrounded citations: {f(s['ungrounded_citations'])}  "
                f"(of {s['n_citations']} citations; lower is better)",
                f"Abstention          : {f(s['abstention'])}  (n={s['n_unanswerable']})",
                f"Expected page cited : {f(s['expected_page_cited'])}  (n={s['n_answerable']})",
                f"Claim support       : {f(s['claim_support'])}  "
                f"(of {s['n_support_checked']} claim-page pairs; "
                f"judge used on {s['n_judged']} answers)",
                f"Cost (agent)        : ${f(s['cost_usd'], '{:.4f}')}",
            ]
        )


async def run_grounding_eval(
    questions: list[GroundingQuestion], *, client: anthropic.AsyncAnthropic, model: str
) -> GroundingReport:
    """Sequential, like the other agent evals: readable telemetry and gentle on rate limits."""
    return GroundingReport([await run_question(q, client=client, model=model) for q in questions])


# -- dry run, gate, baseline ----------------------------------------------------------------


def estimate_cost(n: int, model: str) -> dict[str, float | None]:
    """From run_chat_eval's token budgets (not measured), with no judge call."""
    typical, ceiling = _cost(model, TYPICAL), _cost(model, CEILING)
    if typical is None or ceiling is None:
        return {"typical": None, "ceiling": None}
    return {"typical": n * typical, "ceiling": n * ceiling}


def dry_run_text(
    questions: list[GroundingQuestion], model: str, reviewed: bool, *, judge: bool = False
) -> str:
    est = estimate_cost(len(questions), model)
    lines = [
        f"DRY RUN: no client is created and nothing is billed. Would run {len(questions)} questions.",
        f"  agent model: {model}   (no rubric judge: metrics are counted from the grounding event)",
        f"  claim-support judge (LIBRARIAN_CLAIM_JUDGE): {'ON, one extra call per answer with a failing pair, not in the estimate' if judge else 'off'}",
        f"  golden set reviewed by a human: {reviewed}",
    ]
    lines += [
        f"  {q.id}: {q.question[:90]} [{', '.join(q.expected_pages) or 'unanswerable'}]"
        for q in questions
    ]
    if est["typical"] is None:
        lines.append("  cost estimate unavailable: the model is missing from librarian.pricing.")
    else:
        lines.append(
            f"  estimated cost, from token budgets: ~${est['typical']:.2f} typical, "
            f"${est['ceiling']:.2f} ceiling (8 turns at the 8192-token output cap, no caching)"
        )
    return "\n".join(lines)


def gate_failures(
    summary: dict[str, Any], thresholds: dict[str, float | None] | None = None
) -> list[str]:
    """One line per metric on the wrong side of its threshold. A metric with no threshold, or
    with no value this run, is never a failure."""
    out: list[str] = []
    for key, limit in (THRESHOLDS if thresholds is None else thresholds).items():
        value = summary.get(key)
        if limit is None or value is None:
            continue
        if key in _LOWER_IS_BETTER and value > limit:
            out.append(f"{key} is {value:.3f}, above the ceiling {limit:.3f}.")
        elif key not in _LOWER_IS_BETTER and value < limit:
            out.append(f"{key} is {value:.3f}, below the floor {limit:.3f}.")
    return out


def report_only(thresholds: dict[str, float | None] | None = None) -> bool:
    """True while no threshold is set: the run reports and cannot fail."""
    return all(v is None for v in (THRESHOLDS if thresholds is None else thresholds).values())


def save_baseline(report: GroundingReport, *, model: str, dataset: Path, reviewed: bool) -> Path:
    """Counts, cited page ids and costs. Never answer text."""
    BASELINES.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = BASELINES / f"grounding-{ts}.json"
    data = {
        "timestamp": ts,
        "mode": "grounding",
        "model": model,
        "dataset": dataset.name,
        "golden_set_hash": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "golden_reviewed": reviewed,
        "summary": report.summary(),
        "per_question": [asdict(r) for r in report.results],
    }
    path.write_text(json.dumps(data, indent=2))
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline grounding eval (BILLABLE unless --dry-run)."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=0, help="run only the first N questions")
    parser.add_argument("--model", default=None, help="agent model (default: the chat default)")
    parser.add_argument(
        "--dry-run", action="store_true", help="print the plan and cost estimate; no API calls"
    )
    args = parser.parse_args(argv)

    questions, reviewed = load_golden(args.dataset)
    if args.limit:
        questions = questions[: args.limit]

    from librarian.agent import loop as agent

    model = args.model or agent.default_model()
    if args.dry_run:
        print(dry_run_text(questions, model, reviewed, judge=get_settings().claim_judge))
        return 0

    import anthropic
    from dotenv import load_dotenv

    load_dotenv(EVALS_DIR.parent / ".env")
    client = anthropic.AsyncAnthropic()
    report = asyncio.run(run_grounding_eval(questions, client=client, model=model))
    print(report)
    path = save_baseline(report, model=model, dataset=args.dataset, reviewed=reviewed)
    print(f"\nBaseline saved -> {path}")
    if not reviewed:
        print("WARN: golden_grounding.json is not human-reviewed: read the numbers as indicative.")
    if report_only():
        print("REPORT-ONLY: no threshold is set (they come from a measured baseline).")
        return 0
    failures = gate_failures(report.summary())
    for line in failures:
        print(f"FAIL: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
