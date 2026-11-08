"""Offline chat-answer eval (phase 4b item 5): golden questions through the real agent loop.

    uv run python -m evals.run_chat_eval --dry-run          # what would run and what it would cost
    uv run python -m evals.run_chat_eval --limit 5          # BILLABLE: the real model, 5 questions
    uv run python -m evals.run_chat_eval                    # BILLABLE: all of evals/golden_chat.json

Each question runs through `librarian.agent.loop.run_agent_stream` (the path the UI uses) against
the current index. The answer text is held in memory for the judge and never written anywhere: the
baseline keeps scores, cited page ids and costs only. An LLM judge scores each rubric line 0 to 1.
The judge is the oracle, so this is a WARN-only gate: it prints warning lines and exits 0.

Metrics:
    grounding           share of answers with no citation to a page the run did not read
    citation precision  cited pages that are expected / pages cited, over answerable questions that
                        cited something
    cited recall        expected pages cited / expected, over answerable questions
    rubric score        mean of the judge's per-line scores, 0 to 1
    no-answer clean     share of no-answer questions where the answer cites no page

`golden_chat.json` carries `"reviewed": false` until a human has checked the questions.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from evals.graders import AgentGrader, AgentRun, GoldenEntry
from librarian.pricing import TokenUsage, cost_usd

if TYPE_CHECKING:
    import anthropic

EVALS_DIR = Path(__file__).parent
DEFAULT_DATASET = EVALS_DIR / "golden_chat.json"
BASELINES = EVALS_DIR / "baselines"
JUDGE_MODEL = os.getenv("EVAL_CHAT_JUDGE_MODEL", "claude-sonnet-5-5")

# Dry-run estimate, from token budgets (not measured). Typical: 5 model turns of ~9k uncached input
# (system, tool specs, growing tool results) and ~400 output. Ceiling: librarian.agent.loop's 8
# turns of ~25k input and its 8192 max_tokens. Judge: ~1.5k in, ~400 out. No cache discount.
TYPICAL = TokenUsage(input=5 * 9_000, output=5 * 400)
CEILING = TokenUsage(input=8 * 25_000, output=8 * 8_192)
JUDGE_USAGE = TokenUsage(input=1_500, output=400)

# A fall of more than this against the latest saved baseline is a warning.
WARN_DROP = 0.10


@dataclass
class ChatQuestion:
    id: str
    question: str
    expected_pages: list[str]
    rubric: list[str]

    @property
    def answerable(self) -> bool:
        return bool(self.expected_pages)


def load_chat_golden(path: Path = DEFAULT_DATASET) -> tuple[list[ChatQuestion], bool]:
    """(questions, reviewed). `reviewed` is False unless the file says otherwise."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    questions = [
        ChatQuestion(q["id"], q["question"], list(q["expected_pages"]), list(q["rubric"]))
        for q in raw["questions"]
    ]
    return questions, bool(raw.get("reviewed", False))


# -- judge --------------------------------------------------------------------------------

_JUDGE_SYSTEM = """You grade an answer from a knowledge-base assistant against rubric lines.

For each numbered rubric line give a score from 0 to 1: 1 when the answer satisfies the line,
0.5 when it does so in part, 0 when it does not or contradicts it. Judge the content only; ignore
inline citation markers like [page:some-id] and formatting.

Reply with only a JSON object: {"scores": [<one number per line, in order>], "rationale": "<one sentence>"}"""

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_rubric_reply(text: str, n_lines: int) -> tuple[list[float] | None, str]:
    """(scores, rationale); (None, raw) when the reply is not a verdict for exactly `n_lines` lines.

    An unparseable reply is left out of the mean rather than scored 0: it is a judge problem.
    """
    m = _JSON_OBJ_RE.search(text)
    if not m:
        return None, text.strip()
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None, text.strip()
    scores = obj.get("scores")
    ok = (
        isinstance(scores, list)
        and len(scores) == n_lines
        and all(
            isinstance(s, int | float) and not isinstance(s, bool) and 0 <= s <= 1 for s in scores
        )
    )
    if not ok:
        return None, text.strip()
    return [float(s) for s in scores], str(obj.get("rationale", ""))


@dataclass
class RubricJudgment:
    scores: list[float] | None
    rationale: str
    usage: TokenUsage = field(default_factory=TokenUsage)

    @property
    def score(self) -> float | None:
        return sum(self.scores) / len(self.scores) if self.scores else None


def _usage_of(resp: object) -> TokenUsage:
    u = getattr(resp, "usage", None)

    def n(name: str) -> int:
        v = getattr(u, name, 0)
        return v if isinstance(v, int) and not isinstance(v, bool) else 0

    return TokenUsage(input=n("input_tokens"), output=n("output_tokens"))


async def judge_answer(
    client: anthropic.AsyncAnthropic, model: str, q: ChatQuestion, answer: str
) -> RubricJudgment:
    """One judge call per question (BILLABLE with a real client)."""
    lines = "\n".join(f"{i}. {line}" for i, line in enumerate(q.rubric, 1))
    prompt = f"Question:\n{q.question}\n\nRubric lines:\n{lines}\n\nAnswer:\n{answer}"
    resp = await client.messages.create(
        model=model,
        max_tokens=1024,
        system=_JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    scores, rationale = parse_rubric_reply(text, len(q.rubric))
    return RubricJudgment(scores, rationale, _usage_of(resp))


# -- run and grade ------------------------------------------------------------------------


@dataclass
class ChatResult:
    id: str
    answerable: bool
    cited: list[str]
    pages_read: list[str]
    ungrounded: list[str]
    grounded: bool
    citation_precision: float | None  # None when nothing was cited or no page is expected
    cited_recall: float | None  # None for no-answer questions
    rubric_score: float | None
    judge_rationale: str
    agent_cost: float | None
    judge_cost: float | None


async def run_question(
    q: ChatQuestion,
    *,
    client: anthropic.AsyncAnthropic,
    model: str,
    judge_model: str,
) -> ChatResult:
    from librarian.agent import loop as agent

    usage = TokenUsage()

    def on_usage(u: TokenUsage) -> None:
        nonlocal usage
        usage = usage + u

    tokens: list[str] = []
    grounding: dict[str, Any] = {"pages_read": [], "cited": [], "ungrounded": []}
    async for event in agent.run_agent_stream(
        q.question, client=client, model=model, source="eval", on_usage=on_usage
    ):
        if event["type"] == "token":
            tokens.append(event["content"])
        elif event["type"] == "grounding":
            grounding = event
    answer = "".join(tokens)  # in memory only: judged below, never stored

    run = AgentRun(
        answer=answer,
        pages_read=list(grounding["pages_read"]),
        cited=list(grounding["cited"]),
        ungrounded=list(grounding["ungrounded"]),
    )
    # AgentGrader supplies grounding and recall; it speaks GoldenEntry, so adapt the question.
    entry = GoldenEntry(
        id=q.id,
        category="chat",
        query=q.question,
        expected_answer="",
        source_pages=q.expected_pages,
        difficulty="",
    )
    graded = AgentGrader().grade_entry(entry, run)
    expected = {p.lower() for p in q.expected_pages}
    cited = [c.lower() for c in run.cited]
    precision = sum(c in expected for c in cited) / len(cited) if cited and q.answerable else None
    judgment = await judge_answer(client, judge_model, q, answer)
    return ChatResult(
        id=q.id,
        answerable=q.answerable,
        cited=run.cited,
        pages_read=run.pages_read,
        ungrounded=run.ungrounded,
        grounded=graded.grounded,
        citation_precision=precision,
        cited_recall=graded.cited_recall if q.answerable else None,
        rubric_score=judgment.score,
        judge_rationale=judgment.rationale,
        agent_cost=_cost(model, usage),
        judge_cost=_cost(judge_model, judgment.usage),
    )


def _cost(model: str, usage: TokenUsage) -> float | None:
    try:
        return cost_usd(model, usage)
    except KeyError:
        return None


def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


@dataclass
class ChatReport:
    results: list[ChatResult]

    def summary(self) -> dict[str, Any]:
        r = self.results
        answerable = [x for x in r if x.answerable]
        no_answer = [x for x in r if not x.answerable]
        precision = [x.citation_precision for x in r if x.citation_precision is not None]
        costs = [c for x in r for c in (x.agent_cost, x.judge_cost) if c is not None]
        return {
            "n": len(r),
            "n_answerable": len(answerable),
            "n_no_answer": len(no_answer),
            "grounding": _mean([float(x.grounded) for x in r]),
            "citation_precision": _mean(precision),
            "n_precision": len(precision),
            "cited_recall": _mean(
                [x.cited_recall for x in answerable if x.cited_recall is not None]
            ),
            "rubric_score": _mean([x.rubric_score for x in r if x.rubric_score is not None]),
            "n_judged": sum(x.rubric_score is not None for x in r),
            "no_answer_clean": _mean([float(not x.cited) for x in no_answer]),
            "cost_usd": sum(costs) if costs else None,
        }

    def __str__(self) -> str:
        s = self.summary()

        def f(v: float | None, fmt: str = "{:.3f}") -> str:
            return "n/a" if v is None else fmt.format(v)

        return "\n".join(
            [
                f"Questions         : {s['n']} ({s['n_answerable']} answerable, {s['n_no_answer']} no-answer)",
                f"Grounding         : {f(s['grounding'])}",
                f"Citation precision: {f(s['citation_precision'])}  (n={s['n_precision']})",
                f"Cited recall      : {f(s['cited_recall'])}",
                f"Rubric score      : {f(s['rubric_score'])}  ({s['n_judged']}/{s['n']} judged)",
                f"No-answer clean   : {f(s['no_answer_clean'])}",
                f"Cost (agent+judge): ${f(s['cost_usd'], '{:.4f}')}",
            ]
        )


async def run_chat_eval(
    questions: list[ChatQuestion],
    *,
    client: anthropic.AsyncAnthropic,
    model: str,
    judge_model: str,
) -> ChatReport:
    """Sequential, like the other agent evals: readable telemetry and gentle on rate limits."""
    results = [
        await run_question(q, client=client, model=model, judge_model=judge_model)
        for q in questions
    ]
    return ChatReport(results)


# -- dry run, warnings, baseline ------------------------------------------------------------


def estimate_cost(n: int, model: str, judge_model: str) -> dict[str, float | None]:
    typical = _cost(model, TYPICAL)
    ceiling = _cost(model, CEILING)
    judge = _cost(judge_model, JUDGE_USAGE)
    if typical is None or ceiling is None or judge is None:
        return {"typical": None, "ceiling": None}
    return {"typical": n * (typical + judge), "ceiling": n * (ceiling + judge)}


def dry_run_text(
    questions: list[ChatQuestion], model: str, judge_model: str, reviewed: bool
) -> str:
    est = estimate_cost(len(questions), model, judge_model)
    lines = [
        f"DRY RUN: no client is created and nothing is billed. Would run {len(questions)} questions.",
        f"  agent model: {model}   judge model: {judge_model}",
        f"  golden set reviewed by a human: {reviewed}",
    ]
    lines += [
        f"  {q.id}: {q.question[:90]} [{'no answer' if not q.answerable else ', '.join(q.expected_pages)}]"
        for q in questions
    ]
    if est["typical"] is None:
        lines.append("  cost estimate unavailable: a model is missing from librarian.pricing.")
    else:
        lines.append(
            f"  estimated cost, from token budgets: ~${est['typical']:.2f} typical, "
            f"${est['ceiling']:.2f} ceiling (8 turns at the 8192-token output cap, no caching)"
        )
    return "\n".join(lines)


def latest_baseline(directory: Path = BASELINES) -> dict[str, Any] | None:
    files = sorted(directory.glob("chat-*.json"))
    return json.loads(files[-1].read_text()) if files else None


def warnings(summary: dict[str, Any], baseline: dict[str, Any] | None, reviewed: bool) -> list[str]:
    out: list[str] = []
    if not reviewed:
        out.append("golden_chat.json is not human-reviewed: read the scores as indicative.")
    if baseline is None:
        out.append("no earlier chat baseline to compare with.")
        return out
    prev = baseline["summary"]
    for key in ("grounding", "citation_precision", "cited_recall", "rubric_score"):
        now, was = summary.get(key), prev.get(key)
        if now is not None and was is not None and was - now > WARN_DROP:
            out.append(f"{key} fell from {was:.3f} to {now:.3f} (more than {WARN_DROP:.2f}).")
    return out


def save_baseline(
    report: ChatReport, *, model: str, judge_model: str, dataset: Path, reviewed: bool
) -> Path:
    """Scores, cited page ids and costs. Never answer text."""
    BASELINES.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = BASELINES / f"chat-{ts}.json"
    data = {
        "timestamp": ts,
        "mode": "chat",
        "model": model,
        "judge_model": judge_model,
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
        description="Offline chat-answer eval (BILLABLE unless --dry-run)."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=0, help="run only the first N questions")
    parser.add_argument("--model", default=None, help="agent model (default: the chat default)")
    parser.add_argument("--judge-model", default=JUDGE_MODEL)
    parser.add_argument(
        "--dry-run", action="store_true", help="print the plan and cost estimate; no API calls"
    )
    args = parser.parse_args(argv)

    questions, reviewed = load_chat_golden(args.dataset)
    if args.limit:
        questions = questions[: args.limit]

    from librarian.agent import loop as agent

    model = args.model or agent.default_model()
    if args.dry_run:
        print(dry_run_text(questions, model, args.judge_model, reviewed))
        return 0

    import anthropic
    from dotenv import load_dotenv

    load_dotenv(EVALS_DIR.parent / ".env")
    client = anthropic.AsyncAnthropic()
    report = asyncio.run(
        run_chat_eval(questions, client=client, model=model, judge_model=args.judge_model)
    )
    print(report)
    previous = latest_baseline()
    path = save_baseline(
        report, model=model, judge_model=args.judge_model, dataset=args.dataset, reviewed=reviewed
    )
    for w in warnings(report.summary(), previous, reviewed):
        print(f"WARN: {w}")
    print(f"\nBaseline saved -> {path}")
    return 0  # WARN-only: the judge is the oracle, so this never blocks


if __name__ == "__main__":
    sys.exit(main())
