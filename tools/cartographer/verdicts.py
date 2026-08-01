"""Deterministic experiment-verdict computation (LIB-58).

Moves verdict *measurement* out of the LLM step in /workflow-insights step 10.
The LLM's job becomes interpretation of already-computed verdicts, not deriving
them from prose. This module owns the arithmetic; `factstore.append_verdicts`
owns persistence; `dashboard.py` owns rendering the trajectory.

Ledger metric grammar (verified against `tooling-ledger.md`, 2026-08-01, 31
rows, 100% typed coverage):

    <type>:<signal>[-<more-words>] <comparator> <threshold>[%] [<qualifier>...]

Four types, one comparator vocabulary each:
    absence:<signal>      -- zero occurrences of <signal> confirms; "for N ..."
                              is a repeat-window qualifier, not a threshold.
    presence:<signal>      -- >=1 occurrence of <signal> confirms.
    count-drop:<signal>    -- <signal> compared against a numeric threshold via
                              "above"/"below" (falling metrics use "below").
    ratio:<signal>         -- <signal> compared against a percentage (or N/M)
                              threshold via "above"/"below".

A row may carry more than one metric clause (joined by " + "); each clause is
scored independently and the row verdict is the worst of the two (failed >
inconclusive > trending > confirmed, i.e. pessimistic combination) -- see
`_combine`.

Signal → factstore measurement is a closed registry (`_SIGNAL_METRICS`), not a
generic string search: most ledger signals name process/textual events (e.g.
"flat-sibling-issues-without-parent-link", "worktree-commit-blocks") that the
session fact table cannot observe at all. Naively pattern-matching the slug
against session text would either always return 0 (a false "confirmed" for an
absence claim) or require unbounded heuristics. Only signals with a real
factstore column are registered; everything else scores `inconclusive` with
evidence saying so -- never a fabricated confirm/fail.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Verdict vocabulary (matches the workflow-insights SKILL.md step 10 vocabulary
# so downstream prose stays consistent with the historical insights-log.md).
# ---------------------------------------------------------------------------

VERDICT_CONFIRMED = "confirmed"
VERDICT_TRENDING = "trending"
VERDICT_INCONCLUSIVE = "inconclusive"
VERDICT_FAILED = "failed"

_VERDICT_SEVERITY = {
    VERDICT_CONFIRMED: 0,
    VERDICT_TRENDING: 1,
    VERDICT_INCONCLUSIVE: 2,
    VERDICT_FAILED: 3,
}


@dataclass(frozen=True)
class Verdict:
    """One scored metric clause."""

    verdict: str
    evidence: str


def _combine(verdicts: list[Verdict]) -> Verdict:
    """Pessimistic combination across clauses in a multi-metric row.

    A row claiming two things is only as good as its worst-scored claim --
    `failed` on either clause means the hypothesis as a whole is not holding,
    `inconclusive` on either means the row cannot yet be called `confirmed`.
    """
    worst = max(verdicts, key=lambda v: _VERDICT_SEVERITY[v.verdict])
    if len(verdicts) == 1:
        return worst
    evidence = "; ".join(v.evidence for v in verdicts)
    return Verdict(worst.verdict, evidence)


# ---------------------------------------------------------------------------
# Metric-clause parsing
# ---------------------------------------------------------------------------

_METRIC_CLAUSE = re.compile(
    r"(?P<type>absence|presence|count-drop|ratio):(?P<signal>[^\s]+)"
    r"(?P<rest>.*?)(?=\s+\+\s+(?:absence|presence|count-drop|ratio):|$)",
    re.IGNORECASE | re.DOTALL,
)
_THRESHOLD = re.compile(
    r"\b(?P<comparator>above|below)\s+(?P<value>\d+(?:\.\d+)?)\s*(?P<pct>%)?"
    r"(?:\s*/\s*(?P<denom>\d+))?"
)


@dataclass(frozen=True)
class MetricClause:
    """One parsed `<type>:<signal> <comparator> <threshold>` clause."""

    metric_type: str  # absence | presence | count-drop | ratio
    signal: str
    comparator: str | None  # "above" | "below" | None (absence/presence have none)
    threshold: float | None
    is_percent: bool
    raw: str


def parse_metric(metric: str) -> list[MetricClause]:
    """Split a ledger Metric cell into its typed clauses.

    Handles multi-clause rows joined by " + " (row 23, 28, 29 in the ledger).
    Unparseable text (empty, "—", or missing a type prefix) returns [].
    """
    if not metric or metric.strip() in {"—", "-"}:
        return []
    clauses: list[MetricClause] = []
    for m in _METRIC_CLAUSE.finditer(metric):
        metric_type = m.group("type").lower()
        signal = m.group("signal").strip()
        rest = m.group("rest") or ""
        thr = _THRESHOLD.search(rest)
        comparator = thr.group("comparator").lower() if thr else None
        value = float(thr.group("value")) if thr else None
        is_percent = bool(thr and thr.group("pct"))
        if thr and thr.group("denom"):
            # "12/18" form -- normalise to a percentage threshold.
            value = round(100 * value / float(thr.group("denom")), 2)
            is_percent = True
        clauses.append(
            MetricClause(
                metric_type=metric_type,
                signal=signal,
                comparator=comparator,
                threshold=value,
                is_percent=is_percent,
                raw=(m.group(0)).strip(),
            )
        )
    return clauses


# ---------------------------------------------------------------------------
# Signal registry: ledger signal-slug -> factstore measurement
# ---------------------------------------------------------------------------
#
# Each entry computes a scalar from `sessions` fact rows (already filtered to
# work-sessions by the caller where that distinction matters -- see
# dashboard._work_sessions). Returns None when the corpus has no data for the
# signal (distinct from a genuine zero), so callers can tell "confirmed by
# absence" apart from "no data to judge absence".


def _bash_antipatterns_p50(rows: list[dict[str, Any]]) -> float | None:
    values = [float(r["bash_antipatterns"]) for r in rows if r.get("bash_antipatterns") is not None]
    if not values:
        return None
    ordered = sorted(values)
    idx = len(ordered) // 2
    return float(ordered[idx])


def _bash_antipatterns_total(rows: list[dict[str, Any]]) -> float | None:
    values = [r.get("bash_antipatterns") for r in rows if r.get("bash_antipatterns") is not None]
    if not values:
        return None
    return float(sum(values))


def _output_tokens_p90(rows: list[dict[str, Any]]) -> float | None:
    values = [float(r.get("output_tokens") or 0) for r in rows]
    if not values:
        return None
    ordered = sorted(values)
    idx = min(round(0.9 * (len(ordered) - 1)), len(ordered) - 1)
    return float(ordered[idx])


def _execution_skill_compliance_pct(rows: list[dict[str, Any]]) -> float | None:
    exec_rows = [r for r in rows if r.get("session_intent") == "execution"]
    if not exec_rows:
        return None
    with_skills = sum(1 for r in exec_rows if len(json.loads(r.get("skill_costs") or "{}")) > 0)
    return round(100 * with_skills / len(exec_rows), 2)


def _cost_over_150k_share_pct(rows: list[dict[str, Any]]) -> float | None:
    scored = [r for r in rows if r.get("max_context") is not None]
    if not scored:
        return None
    total_cost = sum(float(r.get("cost_units") or 0) for r in scored)
    if not total_cost:
        return None
    over_cost = sum(
        float(r.get("cost_units") or 0) for r in scored if (r.get("max_context") or 0) >= 150_000
    )
    return round(100 * over_cost / total_cost, 2)


def _fable_share_of_cost_pct(rows: list[dict[str, Any]]) -> float | None:
    """Share of total cost spent on fable across sessions with a `models` breakdown."""
    total = 0.0
    fable = 0.0
    scored = False
    for r in rows:
        try:
            models: dict[str, Any] = json.loads(r.get("models") or "{}")
        except (TypeError, ValueError):
            continue
        if not models:
            continue
        scored = True
        for model, cost in models.items():
            c = float(cost) if isinstance(cost, int | float) else 0.0
            total += c
            if "fable" in model.lower():
                fable += c
    if not scored or not total:
        return None
    return round(100 * fable / total, 2)


# Registry keyed by a normalised (lowercased, non-alnum-stripped) signal slug so
# the ledger's free-text hyphenation does not need to match a Python identifier
# exactly. Values are (measurement_fn, description) -- description feeds the
# inconclusive evidence string for unregistered signals via KeyError avoidance.
_SIGNAL_METRICS: dict[str, Any] = {
    "bash-antipatterns": _bash_antipatterns_p50,
    "p90-output-tokens": _output_tokens_p90,
    "execution-sessions-with-skills": _execution_skill_compliance_pct,
    "top-session-cost-concentration": _cost_over_150k_share_pct,
    "fable-tokens-in-non-verdict-skills": _fable_share_of_cost_pct,
}


def _normalize_signal(signal: str) -> str:
    return signal.strip().lower()


# ---------------------------------------------------------------------------
# Per-metric-type verdict rules
# ---------------------------------------------------------------------------


def _score_absence(clause: MetricClause, rows: list[dict[str, Any]]) -> Verdict:
    """absence:<signal> — confirmed iff the registered count is exactly 0.

    Ledger semantics: "absence" always means an event-count signal (e.g.
    bash-antipatterns as a stand-in for "no antipattern occurrences"), never a
    percentage. A registered signal returning a positive count is `failed`
    (the thing we hoped to eliminate is still happening); an unregistered
    signal is `inconclusive` — factstore has no observation channel for most
    absence signals (they describe git/GitHub/hook-log events, not session
    facts), so silence is not evidence.
    """
    key = _normalize_signal(clause.signal)
    fn = _SIGNAL_METRICS.get(key)
    if fn is None:
        return Verdict(
            VERDICT_INCONCLUSIVE,
            f"no factstore signal registered for '{clause.signal}' — cannot measure absence",
        )
    value = fn(rows)
    if value is None:
        return Verdict(
            VERDICT_INCONCLUSIVE, f"no data for '{clause.signal}' in the scored session window"
        )
    if value == 0:
        return Verdict(VERDICT_CONFIRMED, f"{clause.signal}=0 across scored sessions")
    return Verdict(VERDICT_FAILED, f"{clause.signal}={value} (expected 0)")


def _score_presence(clause: MetricClause, rows: list[dict[str, Any]]) -> Verdict:
    """presence:<signal> — confirmed iff the registered count/value is >0.

    Mirror of absence: a registered signal with any positive occurrence
    confirms; zero occurrences with real data available is `failed` (the
    capability never showed up); no registered signal is `inconclusive`.
    """
    key = _normalize_signal(clause.signal)
    fn = _SIGNAL_METRICS.get(key)
    if fn is None:
        return Verdict(
            VERDICT_INCONCLUSIVE,
            f"no factstore signal registered for '{clause.signal}' — cannot measure presence",
        )
    value = fn(rows)
    if value is None:
        return Verdict(
            VERDICT_INCONCLUSIVE, f"no data for '{clause.signal}' in the scored session window"
        )
    if value > 0:
        return Verdict(VERDICT_CONFIRMED, f"{clause.signal}={value} observed")
    return Verdict(VERDICT_FAILED, f"{clause.signal}=0 (expected at least one occurrence)")


def _score_count_drop(clause: MetricClause, rows: list[dict[str, Any]]) -> Verdict:
    """count-drop:<signal> <above|below> <N> — a raw-count threshold.

    A single run cannot distinguish "stagnant" from "not yet improved enough"
    for an unbounded count — that distinction needs history across runs, which
    is exactly what the append-only verdict table (and its trajectory render in
    dashboard.py) is for. So a single observation scores only two ways:
    threshold met -> `confirmed`; threshold not met -> `trending` (never
    `failed` from one data point). Declaring a young hypothesis dead belongs to
    /retro once the trajectory shows no movement across runs, not to a single
    insights run.
    """
    key = _normalize_signal(clause.signal)
    fn = _SIGNAL_METRICS.get(key)
    if fn is None:
        return Verdict(
            VERDICT_INCONCLUSIVE,
            f"no factstore signal registered for '{clause.signal}' — cannot measure count-drop",
        )
    value = fn(rows)
    if value is None:
        return Verdict(
            VERDICT_INCONCLUSIVE, f"no data for '{clause.signal}' in the scored session window"
        )
    if clause.threshold is None or clause.comparator is None:
        return Verdict(VERDICT_INCONCLUSIVE, f"{clause.signal}={value}, no parseable threshold")
    met = value < clause.threshold if clause.comparator == "below" else value > clause.threshold
    if met:
        return Verdict(
            VERDICT_CONFIRMED, f"{clause.signal}={value} {clause.comparator} {clause.threshold}"
        )
    return Verdict(
        VERDICT_TRENDING,
        f"{clause.signal}={value}, threshold {clause.comparator} {clause.threshold} not yet met",
    )


def _score_ratio(clause: MetricClause, rows: list[dict[str, Any]]) -> Verdict:
    """ratio:<signal> <above|below> <N%> — a percentage/fraction threshold.

    Same confirmed/trending split as count-drop for a not-yet-met threshold;
    a ratio further from its threshold than a fixed "close" band (10 points)
    reads as `failed` rather than `trending` — ratios (unlike raw counts) are
    bounded 0-100, so "half the distance to target" is a meaningful, comparable
    notion of "still plausibly moving" across different signals in a way a
    count-drop's unbounded raw value is not.
    """
    key = _normalize_signal(clause.signal)
    fn = _SIGNAL_METRICS.get(key)
    if fn is None:
        return Verdict(
            VERDICT_INCONCLUSIVE,
            f"no factstore signal registered for '{clause.signal}' — cannot measure ratio",
        )
    value = fn(rows)
    if value is None:
        return Verdict(
            VERDICT_INCONCLUSIVE, f"no data for '{clause.signal}' in the scored session window"
        )
    if clause.threshold is None or clause.comparator is None:
        return Verdict(VERDICT_INCONCLUSIVE, f"{clause.signal}={value}, no parseable threshold")
    met = value < clause.threshold if clause.comparator == "below" else value > clause.threshold
    if met:
        return Verdict(
            VERDICT_CONFIRMED, f"{clause.signal}={value}% {clause.comparator} {clause.threshold}%"
        )
    gap = abs(value - clause.threshold)
    _CLOSE_BAND = 10.0
    if gap <= _CLOSE_BAND:
        return Verdict(
            VERDICT_TRENDING,
            f"{clause.signal}={value}%, within {gap:.1f}pt of {clause.comparator} "
            f"{clause.threshold}% threshold",
        )
    return Verdict(
        VERDICT_FAILED,
        f"{clause.signal}={value}%, {gap:.1f}pt from {clause.comparator} {clause.threshold}% threshold",
    )


_SCORERS = {
    "absence": _score_absence,
    "presence": _score_presence,
    "count-drop": _score_count_drop,
    "ratio": _score_ratio,
}


def score_clause(clause: MetricClause, rows: list[dict[str, Any]]) -> Verdict:
    """Score one parsed metric clause against factstore rows."""
    scorer = _SCORERS[clause.metric_type]
    return scorer(clause, rows)


def score_metric(metric: str, rows: list[dict[str, Any]]) -> Verdict:
    """Score a raw ledger Metric cell (one or more clauses) into one Verdict.

    Empty/unparseable metrics (legacy `—` rows) return `inconclusive` — the
    ledger's own convention for "not yet a checkable metric" (see SKILL.md step
    10: "check legacy hypothesis rows ... if their status text contains a
    checkable signal" — this module does not attempt that prose heuristic;
    it only scores typed metrics, which is 100% ledger coverage as of 2026-08-01).
    """
    clauses = parse_metric(metric)
    if not clauses:
        return Verdict(VERDICT_INCONCLUSIVE, "no typed metric to score")
    scored = [score_clause(c, rows) for c in clauses]
    return _combine(scored)
