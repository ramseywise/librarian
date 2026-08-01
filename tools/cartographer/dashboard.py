"""Render the context-engineering dashboard from the fact table.

Reads `factstore` rows only — never rescans the corpus, so charts are recomputed
from stored history rather than an ever-shrinking JSONL window (local retention
is ~5 days).

Two metric classes render differently, and the distinction is load-bearing (Q0):

  * **Per-session properties** (cost, cache hit-rate, tokens) are comparable
    across instrumentation regimes -> one continuous trend line, regime bands
    shaded behind it.
  * **Population rates** (compaction %, sessions/week) are NOT comparable. In the
    Apr-Jun regime a session produced a note *only because it compacted*, so a
    rate line crossing that boundary plots the note-writing hook's behaviour, not
    Ramsey's. These render as separate per-regime panels, each labelled with its
    sampling frame.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from datetime import date as _date
from pathlib import Path
from typing import Any

import structlog

from tools.cartographer.factstore import (
    SUBAGENT_ATTRIBUTION_CLI,
    SUBAGENT_ATTRIBUTION_SINCE,
    UNATTRIBUTED_AGENT,
    read_all,
)
from tools.cartographer.gitstore import read_git_activity, read_prs

log = structlog.get_logger(__name__)

# Telemetry (per-request usage, max_context) begins with the JSONL era. Metrics
# derived from it must not render a single point before this date.
JULY_BOUNDARY = "2026-07-15"

# Date the friction columns entered the factstore. Data before this is backfilled
# from retained transcripts, not collected prospectively -- stated on the panel so
# the distinction stays visible.
FRICTION_STORED = "2026-07-20"

# Population-rate metrics: the sampling frame differs per regime, so these are
# faceted and never drawn as a continuous series.
RATE_METRICS = {"compaction_pct", "sessions_per_week"}

# July-forward only: the underlying columns are null in the note era.
JULY_ONLY_METRICS = {
    "max_context_p50",
    "max_context_p90",
    "pct_over_150k",
    "tool_error_rate",
    "interruptions_p50",
    "turns_per_session_p50",
    "single_turn_pct",
    "execution_skill_compliance_pct",
    "friction_labels_total",
    # Step 4: input tokens — telemetry era only (no pre-July per-request data)
    "input_tokens_p50",
    "input_tokens_sum",
    # Step 6: cost-by-context-bucket — needs max_context per session (July+)
    "cost_bucket_pct_over150k",
    # LIB-57: failure attribution + bash antipatterns — parsed since the JSONL
    # era only, same as tool_error_rate.
    "errors_code_total",
    "errors_env_total",
    "errors_tool_total",
    "errors_unknown_total",
    "bash_antipatterns_p50",
}

# Top N tools to trend individually; everything else is aggregated as "other".
# Determined empirically from the tool_counts column; extend as usage evolves.
_TOP_TOOLS_N = 5

# What each regime's corpus actually sampled. Rendered on every rate panel so a
# reader cannot mistake a logging artifact for a workflow change.
SAMPLING_FRAME = {
    "migrated-jsonl": "notes migrated from JSONL - compaction was never recorded, so 0% is structural",
    "note-hook": "notes written only when a session compacted - rate is not a workflow property",
    "telemetry-v1": "all sessions logged (JSONL)",
    "session-hygiene-v1": "all sessions logged (JSONL)",
    "unclassified": "sampling frame unknown - dates outside the regime table",
}

_CONTEXT_LIMIT = 150_000


@dataclass(frozen=True)
class Point:
    """One plotted observation. `n` carries the sample size behind it."""

    date: str
    value: float
    regime: str
    n: int = 1


@dataclass(frozen=True)
class Panel:
    """A single-regime facet. Never spans a boundary."""

    regime: str
    sampling_frame: str
    points: list[Point]


@dataclass(frozen=True)
class Series:
    """Either a continuous trend (`points`) or faceted panels (`panels`).

    `surface_points` carries per-surface breakdowns for continuous metrics,
    enabling the JS surface toggle. Keys are surface names (e.g. "claude-vscode")
    plus "unknown" for None-surface rows. Empty dict for rate/faceted metrics.
    """

    metric: str
    faceted: bool
    points: list[Point] = field(default_factory=list)
    panels: list[Panel] = field(default_factory=list)
    regime_bands: list[tuple[str, str, str]] = field(default_factory=list)
    july_only: bool = False
    surface_points: dict[str, list[Point]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------


def _work_sessions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Work-sessions only. Meta-sessions depress median size independently of any
    hygiene rule (research Disconfirming section 1) and are never pooled."""
    return [r for r in rows if not r.get("is_meta")]


def _iso_week(day: str) -> str:
    year, month, dom = (int(part) for part in day.split("-"))
    iso = _date(year, month, dom).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    ordered = sorted(values)
    idx = min(round((pct / 100) * (len(ordered) - 1)), len(ordered) - 1)
    return float(ordered[idx])


def _group(rows: list[dict[str, Any]], key: str = "date") -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(str(row[key]), []).append(row)
    return out


def _cache_hit_rate(bucket: list[dict[str, Any]]) -> float:
    read = sum(r.get("cache_read_tokens") or 0 for r in bucket)
    written = sum(r.get("cache_write_tokens") or 0 for r in bucket)
    fresh = sum(r.get("input_tokens") or 0 for r in bucket)
    denominator = read + written + fresh
    return round(100 * read / denominator, 2) if denominator else 0.0


def _metric_value(metric: str, bucket: list[dict[str, Any]]) -> float | None:
    """Compute `metric` over one date-bucket, or None when it does not apply."""
    if metric == "compaction_pct":
        return round(100 * sum(1 for r in bucket if r.get("compacted")) / len(bucket), 2)
    if metric == "cost_units_p50":
        return _percentile([float(r.get("cost_units") or 0) for r in bucket], 50)
    if metric == "cost_units_p90":
        return _percentile([float(r.get("cost_units") or 0) for r in bucket], 90)
    if metric == "cache_hit_rate":
        return _cache_hit_rate(bucket)
    if metric == "output_tokens_p50":
        return _percentile([float(r.get("output_tokens") or 0) for r in bucket], 50)
    if metric == "total_tokens_p50":
        return _percentile(
            [float((r.get("input_tokens") or 0) + (r.get("output_tokens") or 0)) for r in bucket],
            50,
        )
    if metric in {"max_context_p50", "max_context_p90"}:
        values = [float(r["max_context"]) for r in bucket if r.get("max_context")]
        if not values:
            return None
        return _percentile(values, 50 if metric.endswith("p50") else 90)
    if metric == "pct_over_150k":
        values = [r["max_context"] for r in bucket if r.get("max_context")]
        if not values:
            return None
        return round(100 * sum(1 for v in values if v >= _CONTEXT_LIMIT) / len(values), 2)
    if metric == "tool_error_rate":
        # Errors per 100 tool calls -- normalised, so a long session is not
        # counted as more friction than a short one doing the same work.
        scored = [r for r in bucket if r.get("tool_error_count") is not None]
        if not scored:
            return None
        calls = sum(_tool_call_total(r) for r in scored)
        if not calls:
            return None
        errors = sum(int(r.get("tool_error_count") or 0) for r in scored)
        return round(100 * errors / calls, 2)
    if metric == "turns_per_session_p50":
        values = [float(r["human_turns"]) for r in bucket if r.get("human_turns") is not None]
        if not values:
            return None
        return _percentile(values, 50)
    if metric == "single_turn_pct":
        values = [r["human_turns"] for r in bucket if r.get("human_turns") is not None]
        if not values:
            return None
        return round(100 * sum(1 for v in values if v <= 1) / len(values), 2)
    if metric == "interruptions_p50":
        values = [
            float(r["user_interruptions"])
            for r in bucket
            if r.get("user_interruptions") is not None
        ]
        if not values:
            return None
        return _percentile(values, 50)
    if metric == "execution_skill_compliance_pct":
        exec_rows = [r for r in bucket if r.get("session_intent") == "execution"]
        if not exec_rows:
            return None
        with_skills = sum(1 for r in exec_rows if len(json.loads(r.get("skill_costs") or "{}")) > 0)
        return round(100 * with_skills / len(exec_rows), 2)
    if metric == "friction_labels_total":
        return sum(int(r.get("friction_label_count") or 0) for r in bucket)
    # LIB-57: failure attribution + bash antipatterns, computed at parse time in
    # factstore._to_fact_from_jsonl (ported from the workflow-insights step-9
    # lookup table) since the parser discards raw error text after reducing it
    # to an error_kind count dict.
    if metric in {
        "errors_code_total",
        "errors_env_total",
        "errors_tool_total",
        "errors_unknown_total",
    }:
        column = metric.removesuffix("_total")
        return float(sum(int(r.get(column) or 0) for r in bucket))
    if metric == "bash_antipatterns_p50":
        values = [
            float(r["bash_antipatterns"]) for r in bucket if r.get("bash_antipatterns") is not None
        ]
        if not values:
            return None
        return _percentile(values, 50)
    # Step 4: input-token series
    if metric == "input_tokens_p50":
        values = [float(r.get("input_tokens") or 0) for r in bucket]
        if not values:
            return None
        return _percentile(values, 50)
    if metric == "input_tokens_sum":
        return float(sum(r.get("input_tokens") or 0 for r in bucket))
    # Step 6: cost share in >150k context bucket
    if metric == "cost_bucket_pct_over150k":
        scored = [r for r in bucket if r.get("max_context") is not None]
        if not scored:
            return None
        total_cost = sum(float(r.get("cost_units") or 0) for r in scored)
        if not total_cost:
            return None
        over_cost = sum(
            float(r.get("cost_units") or 0)
            for r in scored
            if (r.get("max_context") or 0) >= _CONTEXT_LIMIT
        )
        return round(100 * over_cost / total_cost, 2)
    raise ValueError(f"unknown metric: {metric}")


def _tool_call_total(row: dict[str, Any]) -> int:
    """Total tool invocations in a session, from the stored tool_counts JSON."""
    try:
        counts = json.loads(row.get("tool_counts") or "{}")
    except (TypeError, ValueError):
        return 0
    return sum(int(v) for v in counts.values()) if isinstance(counts, dict) else 0


def _regime_bands(points: list[Point]) -> list[tuple[str, str, str]]:
    """(regime, first_date, last_date) spans, for shading behind a trend line."""
    bands: list[tuple[str, str, str]] = []
    for point in points:
        if bands and bands[-1][0] == point.regime:
            regime, start, _ = bands[-1]
            bands[-1] = (regime, start, point.date)
        else:
            bands.append((point.regime, point.date, point.date))
    return bands


def build_series(metric: str, store: Path) -> Series:
    """Build `metric` from the fact table.

    Rate metrics come back faceted by regime; per-session properties come back as
    one continuous line with regime bands. July-only metrics drop every row
    before the telemetry boundary rather than imputing across it.
    """
    rows = _work_sessions(read_all(store))
    july_only = metric in JULY_ONLY_METRICS
    if july_only:
        rows = [r for r in rows if str(r["date"]) >= JULY_BOUNDARY]

    if metric == "sessions_per_week":
        buckets = _group(rows, "date")
        weekly: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for day, bucket in buckets.items():
            for row in bucket:
                weekly.setdefault((_iso_week(day), str(row["regime"])), []).append(row)
        by_regime: dict[str, list[Point]] = {}
        for (_week, regime), bucket in sorted(weekly.items()):
            start = min(str(r["date"]) for r in bucket)
            by_regime.setdefault(regime, []).append(
                Point(date=start, value=float(len(bucket)), regime=regime, n=len(bucket))
            )
        return Series(
            metric=metric,
            faceted=True,
            panels=[
                Panel(regime=regime, sampling_frame=_frame(regime), points=points)
                for regime, points in sorted(by_regime.items())
            ],
        )

    points: list[Point] = []
    for day, bucket in sorted(_group(rows).items()):
        # A date-bucket is single-regime by construction (regime is a date lookup).
        regime = str(bucket[0]["regime"])
        value = _metric_value(metric, bucket)
        if value is None:
            continue
        points.append(Point(date=day, value=value, regime=regime, n=len(bucket)))

    if metric in RATE_METRICS:
        by_regime = {}
        for point in points:
            by_regime.setdefault(point.regime, []).append(point)
        return Series(
            metric=metric,
            faceted=True,
            panels=[
                Panel(regime=regime, sampling_frame=_frame(regime), points=pts)
                for regime, pts in sorted(by_regime.items())
            ],
            july_only=july_only,
        )

    # Per-surface breakdown for the JS toggle. "unknown" buckets None-surface rows
    # (pre-July / pre-entrypoint transcripts). Only computed for continuous metrics.
    distinct_surfaces = sorted(
        {str(r.get("surface") or "unknown") for r in rows},
    )
    surface_points: dict[str, list[Point]] = {}
    for surf in distinct_surfaces:
        surf_rows = [r for r in rows if (r.get("surface") or "unknown") == surf]
        s_pts: list[Point] = []
        for day, bucket in sorted(_group(surf_rows).items()):
            regime = str(bucket[0]["regime"])
            value = _metric_value(metric, bucket)
            if value is None:
                continue
            s_pts.append(Point(date=day, value=value, regime=regime, n=len(bucket)))
        if s_pts:
            surface_points[surf] = s_pts

    return Series(
        metric=metric,
        faceted=False,
        points=points,
        regime_bands=_regime_bands(points),
        july_only=july_only,
        surface_points=surface_points,
    )


def _frame(regime: str) -> str:
    return SAMPLING_FRAME.get(regime, SAMPLING_FRAME["unclassified"])


def _distinct_surfaces(store: Path) -> list[str]:
    """Sorted list of distinct surface values in the fact table (work sessions only).

    "unknown" is included only if any row has a null/missing surface -- it is never
    fabricated when all rows carry a real surface value.
    """
    surfaces: set[str] = set()
    for row in _work_sessions(read_all(store)):
        surfaces.add(str(row.get("surface") or "unknown"))
    return sorted(surfaces)


def build_tool_trends(store: Path) -> tuple[list[str], dict[str, list[Point]]]:
    """Daily call-count trend for the top N tools plus an 'other' bucket.

    Returns (ordered_tool_names, {tool_name: [Point]}). July-forward only —
    tool_counts is null in the note era. The top-N selection is by total calls
    across the whole window, so the legend is stable over time.
    """
    rows = [r for r in _work_sessions(read_all(store)) if str(r.get("date") or "") >= JULY_BOUNDARY]
    # First pass: total calls per tool across the full window.
    total_by_tool: dict[str, int] = {}
    for row in rows:
        try:
            counts: dict[str, int] = json.loads(row.get("tool_counts") or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        for tool, n in counts.items():
            total_by_tool[tool] = total_by_tool.get(tool, 0) + int(n)
    top_tools = [t for t, _ in sorted(total_by_tool.items(), key=lambda kv: -kv[1])[:_TOP_TOOLS_N]]

    # Second pass: daily buckets per top tool + 'other'.
    daily: dict[str, dict[str, int]] = {}
    for row in rows:
        day = str(row.get("date") or "")
        try:
            counts = json.loads(row.get("tool_counts") or "{}")
        except (TypeError, json.JSONDecodeError):
            counts = {}
        bucket = daily.setdefault(day, dict.fromkeys(top_tools, 0))
        bucket.setdefault("other", 0)
        for tool, n in counts.items():
            if tool in top_tools:
                bucket[tool] += int(n)
            else:
                bucket["other"] += int(n)

    ordered = top_tools + (["other"] if any(d.get("other", 0) for d in daily.values()) else [])
    regime_rows = {str(r["date"]): str(r["regime"]) for r in rows}
    series: dict[str, list[Point]] = {}
    for tool in ordered:
        pts: list[Point] = []
        for day in sorted(daily):
            v = daily[day].get(tool, 0)
            pts.append(Point(date=day, value=float(v), regime=regime_rows.get(day, ""), n=1))
        if pts:
            series[tool] = pts
    return ordered, series


def _render_tool_trends(store: Path) -> str:
    """Daily tool-call trends for the top N tools plus 'other'.

    Step 6(b): shows which tools dominate invocation volume, how that shifts over
    time, and whether the Bash-over-dedicated-tool antipattern is structural.
    """
    ordered, series = build_tool_trends(store)
    if not series:
        return (
            '<section class="chart"><h3>Tool call trends (daily)</h3>'
            '<p class="note">No tool-count data yet. July-forward only.</p></section>'
        )
    colors = [
        "var(--chart-1)",
        "var(--chart-2)",
        "var(--chart-3)",
        "var(--chart-4)",
        "var(--muted)",
    ]
    charts = "".join(
        (
            f'<div style="margin-bottom:8px"><strong style="font-size:12px">'
            f"{html.escape(tool)}</strong>"
            f"{_svg_line(series[tool], colors[min(i, len(colors) - 1)], unit='count')}</div>"
        )
        for i, tool in enumerate(ordered)
        if tool in series
    )
    return (
        '<section class="chart"><h3>Tool call trends (daily)</h3>'
        '<p class="note">Daily call count for the top 5 tools by volume, '
        "plus an 'other' bucket. July-forward only. Bash volume is structural "
        "(28.7/session median from insights-log) — track for antipattern changes, "
        "not for absolute reduction.</p>"
        f"{charts}</section>"
    )


# ---------------------------------------------------------------------------
# Guacamayo promotion funnel (research F5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Funnel:
    """Promotion-funnel counts from the last logged synthesis event.

    `entries_in is None` means no synthesis has been logged - which is NOT zero.
    """

    last_synthesis: str | None = None
    entries_in: int | None = None
    to_sounding: int | None = None
    to_portfolio: int | None = None
    flagged_retro: int | None = None
    entries_since: int = 0


@dataclass(frozen=True)
class Experiment:
    """One tooling-ledger experiment row."""

    name: str
    metric: str
    status: str
    date: str


_SYNTHESIS = re.compile(r"\*\*Last Synthesis\*\*:\s*(\d{4}-\d{2}-\d{2})(.*)", re.IGNORECASE)
_SINCE = re.compile(r"\*\*Entries Since\*\*:\s*(\d+)", re.IGNORECASE)
_ENTRIES_IN = re.compile(r"(\d+)\s+entries", re.IGNORECASE)
_TO_SOUNDING = re.compile(r"(\d+)\s+woven into\s+sounding", re.IGNORECASE)
_TO_PORTFOLIO = re.compile(r"(\d+)\s+into\s+portfolio", re.IGNORECASE)
_FLAGGED = re.compile(r"(\d+)\s+process learnings flagged", re.IGNORECASE)


def funnel_counts(growth_md: Path) -> Funnel:
    """Read promotion-funnel counts from growth.md's logged synthesis header.

    Research F5: growth.md is a *draining* buffer - `/dream` clears it and resets
    "Entries Since" to 0. Polling the accumulator body therefore measures the
    drain, not the learning, and would render the funnel as flat zero. The counts
    that survive the clear live in the `**Last Synthesis**` header line, which
    records what the last `/dream` actually promoted.

    This is a read of an already-logged event, not a poll - the durable fix is
    for `/dream` to emit these counts at synthesis time (plan Step 10 note:
    out of scope here, needs its own plan).
    """
    if not growth_md.exists():
        log.warning("dashboard.funnel_missing", path=str(growth_md))
        return Funnel()

    text = growth_md.read_text(encoding="utf-8", errors="replace")
    since_match = _SINCE.search(text)
    entries_since = int(since_match.group(1)) if since_match else 0

    header = _SYNTHESIS.search(text)
    if not header:
        # No logged synthesis: unknown, never a fabricated zero.
        return Funnel(entries_since=entries_since)

    detail = header.group(2)

    def _first(pattern: re.Pattern[str]) -> int | None:
        match = pattern.search(detail)
        return int(match.group(1)) if match else None

    return Funnel(
        last_synthesis=header.group(1),
        entries_in=_first(_ENTRIES_IN),
        to_sounding=_first(_TO_SOUNDING),
        to_portfolio=_first(_TO_PORTFOLIO),
        flagged_retro=_first(_FLAGGED),
        entries_since=entries_since,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_TIER1 = [
    (
        "cost_units_p50",
        "Cost per session (p50)",
        "Lower is better. Each unit ≈ the cost of reading 1M input tokens.",
        "Work sessions only; meta-sessions excluded",
        "cost",
    ),
    (
        "cost_units_p90",
        "Cost per session (p90)",
        "Tail cost — the expensive sessions. Spikes = runaway context or long opus runs.",
        "",
        "cost",
    ),
    # Step 4: input-token series. Validates the 'context health is about input' intuition —
    # cache hit rate is a reuse proxy, not direct input-volume visibility.
    (
        "input_tokens_p50",
        "Input tokens per session (p50)",
        "Median input-token volume. High = large context carried in; rising = context growth.",
        "July-forward only; no pre-telemetry data",
        "tokens",
    ),
    (
        "input_tokens_sum",
        "Input tokens total (daily)",
        "Total input-token volume per day. Use alongside cache hit rate to read context cost.",
        "July-forward only",
        "tokens",
    ),
    (
        "cache_hit_rate",
        "Cache hit rate",
        "Higher is better. Below 90% means context churn is breaking prompt cache.",
        "",
        "pct",
    ),
    (
        "output_tokens_p50",
        "Output tokens per session (p50)",
        "Output volume per session. Output is 5× the cost of input.",
        "",
        "tokens",
    ),
]

_TIER2 = [
    (
        "max_context_p50",
        "Max context (p50)",
        "Median peak context. Staying below 150k avoids the 5× cost cliff.",
        "",
        "tokens",
    ),
    (
        "max_context_p90",
        "Max context (p90)",
        "The worst 10% of sessions. Shows how bad the outliers get.",
        "",
        "tokens",
    ),
    (
        "pct_over_150k",
        "% sessions over 150k context",
        "Share of sessions hitting the cost cliff. Was 66% in early July, target <30%.",
        "",
        "pct",
    ),
    # Step 6: cost-concentration in the >150k bucket — validates the '52% of spend' claim.
    (
        "cost_bucket_pct_over150k",
        "Cost share in >150k context sessions (%)",
        "Share of daily session cost in sessions that hit the 150k cliff. "
        "Validates or falsifies the '52% of spend' claim from insights-log.",
        "July-forward only; sessions without max_context excluded",
        "pct",
    ),
]

# Session shape: how work is divided into sessions. Read alongside "Sessions per
# week" -- volume alone cannot distinguish more work from the same work split
# across more cold starts, and those have opposite cost implications (each new
# session re-derives context that a continued one already holds).
_TIER_SHAPE = [
    (
        "turns_per_session_p50",
        "Human turns per session (p50)",
        "Turns before a session ends. Low = many cold starts paying context startup.",
        "",
        "count",
    ),
    (
        "single_turn_pct",
        "% single-turn sessions",
        "One-and-done sessions. Each pays full context load for one answer.",
        "",
        "pct",
    ),
]

# ---------------------------------------------------------------------------
# Friction tab — Step 9: prompt-eng / loop-eng / harness-eng regroup (F7)
#
# Research finding F4 confirmed: 3 of 5 original metrics measured productivity
# not friction. The regroup separates true friction (loop-eng) from capability
# signals (prompt-eng) and infrastructure health (harness-eng).
# ---------------------------------------------------------------------------

# Prompt-eng: does reasoning work? Skill compliance renamed from "friction" framing.
_FRICTION_PROMPT_ENG = [
    (
        "execution_skill_compliance_pct",
        "Skill compliance — execution sessions (%)",
        "Execution sessions invoking ≥1 skill. Low = unscaffolded work. "
        "Higher is better (productivity signal, not friction).",
        "Heuristic: intent classifier is v1",
        "pct",
    ),
]

# Loop-eng: does workflow repeat? The true-friction group.
_FRICTION_LOOP_ENG = [
    (
        "interruptions_p50",
        "User interruptions per session (p50)",
        "Fast follow-up turns (<5s) — agent went off-track and was corrected. "
        "Direct friction signal.",
        "Tool results excluded from turn count",
        "count",
    ),
    (
        "friction_labels_total",
        "Explicit friction labels (FRICTION:)",
        "Count of FRICTION: labels in user messages. User-reported friction only.",
        "User-authored signal",
        "count",
    ),
]

# Harness-eng: does infrastructure hold? Context + error signals.
_FRICTION_HARNESS_ENG = [
    (
        "tool_error_rate",
        "Tool error rate (per 100 calls)",
        "Errors per 100 tool calls. Structural noise level is ~28.7 Bash antipatterns/session "
        "(flat across interventions — endemic, not recoverable by config). "
        "Taxonomy split (code/env/tool/unknown) tracked in tool_errors column.",
        "Normalised so long sessions are not penalised",
        "count",
    ),
    # LIB-57: failure attribution, computed at parse time (errors_code/env/tool/
    # unknown columns) from the workflow-insights step-9 lookup table.
    (
        "errors_code_total",
        "Errors — code",
        "file_not_found, edit_failed, command_failed (retry unknown — parser "
        "carries no retry sequence, so transient/code fold together).",
        "Attribution applied at parse time; backfill requires re-parse",
        "count",
    ),
    (
        "errors_env_total",
        "Errors — env",
        "permission_denied, file_too_large, quota/rate-limit signals.",
        "Attribution applied at parse time; backfill requires re-parse",
        "count",
    ),
    (
        "errors_tool_total",
        "Errors — tool",
        "user_rejected (hook blocks) on any tool.",
        "Attribution applied at parse time; backfill requires re-parse",
        "count",
    ),
    (
        "errors_unknown_total",
        "Errors — unknown",
        "Unclassified error_kind values. A high rate flags a taxonomy gap, not noise to ignore.",
        "Attribution applied at parse time; backfill requires re-parse",
        "count",
    ),
    (
        "bash_antipatterns_p50",
        "Bash antipatterns per session (p50)",
        "Shell used where a dedicated tool (Read/Grep/Glob) exists — wastes "
        "context, slower than the native tool.",
        "",
        "count",
    ),
]

# Rework-cycle placeholder — loop-eng signal not yet captured (F5, Tier 3 deferred)
_REWORK_PLACEHOLDER = (
    '<section class="chart"><h3>Rework cycles</h3>'
    '<p class="note">Not yet captured. Detecting rework requires message-pair '
    "similarity analysis on session JSONL — deferred to Tier 3 (F5, LIB #65). "
    "Current proxy: user interruptions (see above).</p></section>"
)

# Population rates: within-regime diagnostics only. Rendered faceted, never as a
# cross-regime trend - the Apr-Jun corpus samples only compacted sessions.
_RATES = [
    (
        "compaction_pct",
        "Compaction rate",
        "How often sessions compact. Per-regime only — the pre-July logger makes these incomparable across regimes.",
        "Survivorship: see panel frames",
        "pct",
    ),
    (
        "sessions_per_week",
        "Sessions per week",
        "Session volume. More sessions could mean more work or the same work restarted.",
        "Sampling frame differs per regime",
        "count",
    ),
]


def _fmt_value(value: float, unit: str) -> str:
    if unit == "pct":
        return f"{value:.0f}%"
    if unit == "tokens" and abs(value) >= 1000:
        return f"{value / 1000:.0f}k"
    if unit == "cost" and abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if unit == "cost" and abs(value) >= 1000:
        return f"{value / 1000:.0f}k"
    return f"{value:g}"


_MONTH_ABBR = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def _svg_line(
    points: list[Point],
    color: str,
    width: int = 640,
    height: int = 160,
    unit: str = "count",
) -> str:
    """A minimal 2px trend line with y-axis labels and x-axis month ticks."""
    if not points:
        return '<p class="empty">no data</p>'
    pad_left = 48
    pad_bottom = 18
    plot_w = width - pad_left
    plot_h = height - pad_bottom
    values = [p.value for p in points]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    step = plot_w / max(len(points) - 1, 1)

    def _x(i: int) -> float:
        return pad_left + i * step

    def _y(v: float) -> float:
        return plot_h - ((v - lo) / span) * (plot_h - 20) - 10

    coords = " ".join(f"{_x(i):.1f},{_y(p.value):.1f}" for i, p in enumerate(points))
    dots = "".join(
        f'<circle cx="{_x(i):.1f}" cy="{_y(p.value):.1f}" r="4" '
        f'fill="{color}"><title>{html.escape(p.date)}: {p.value:g} (n={p.n})</title></circle>'
        for i, p in enumerate(points)
    )

    y_labels = (
        f'<text x="{pad_left - 4}" y="{_y(hi):.1f}" text-anchor="end" '
        f'dominant-baseline="middle" class="axis-label">{html.escape(_fmt_value(hi, unit))}</text>'
        f'<text x="{pad_left - 4}" y="{_y(lo):.1f}" text-anchor="end" '
        f'dominant-baseline="middle" class="axis-label">{html.escape(_fmt_value(lo, unit))}</text>'
    )

    x_labels = ""
    if len(points) > 14:
        seen_months: set[str] = set()
        for i, p in enumerate(points):
            month_str = p.date[:7]
            if month_str not in seen_months:
                seen_months.add(month_str)
                month_num = int(p.date[5:7])
                x_labels += (
                    f'<text x="{_x(i):.1f}" y="{height - 2}" text-anchor="middle" '
                    f'class="axis-label">{_MONTH_ABBR[month_num]}</text>'
                )
    else:
        x_labels = (
            f'<text x="{_x(0):.1f}" y="{height - 2}" text-anchor="start" '
            f'class="axis-label">{html.escape(points[0].date[5:])}</text>'
            f'<text x="{_x(len(points) - 1):.1f}" y="{height - 2}" text-anchor="end" '
            f'class="axis-label">{html.escape(points[-1].date[5:])}</text>'
        )

    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="none">'
        f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>{dots}{y_labels}{x_labels}</svg>'
    )


def _table_view(points: list[Point]) -> str:
    """The relief rule: three light-mode slots sit below 3:1 on the light surface,
    and the dark palette's worst adjacent CVD pair lands in the 6-8 floor band.
    Both are legal only with secondary encoding, so every chart ships a readable
    table alongside it - identity and value are never carried by hue alone.
    """
    rows = "".join(
        f"<tr><td>{html.escape(p.date)}</td><td>{p.value:g}</td>"
        f"<td>{html.escape(p.regime)}</td><td>{p.n}</td></tr>"
        for p in points
    )
    return (
        '<details class="table-view"><summary>Table view</summary>'
        "<table><thead><tr><th>date</th><th>value</th><th>regime</th><th>n</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></details>"
    )


def _span_days(points: list[Point]) -> int:
    """Calendar days covered by a panel's points."""
    first = _date.fromisoformat(points[0].date)
    last = _date.fromisoformat(points[-1].date)
    return (last - first).days


# Below this many points a line is unreadable — one or two points drew a ~2px
# sliver that looked like a rendering bug rather than a sparse regime.
_MIN_LINE_POINTS = 3


def _saturation_warning(panel: Panel) -> str:
    """Flag a rate panel pinned at either rail — that is the logger, not the workflow.

    Both rails are artifacts here, and both are structural (verified 2026-07-19):
    every `note-hook` day is exactly 100% because the hook only fired on
    compaction, and every `migrated-jsonl` day is exactly 0% because migrated
    notes never recorded compaction at all. Unflagged, the pair reads as a 0->100%
    improvement across the boundary when nothing about the work changed.
    """
    for rail, label in ((100.0, "100%"), (0.0, "0%")):
        pinned = [p for p in panel.points if p.value == rail]
        if len(pinned) >= _MIN_LINE_POINTS and len(pinned) >= len(panel.points) / 2:
            return (
                f'<p class="saturated">⚠ {len(pinned)} of {len(panel.points)} points sit at '
                f"{label} — at this rail the metric measures the logging trigger, "
                f"not behaviour.</p>"
            )
    return ""


def _panel_body(panel: Panel, color: str, span: int, widest: int, unit: str = "count") -> str:
    """A line when there is enough to plot, otherwise the values as text."""
    if len(panel.points) < _MIN_LINE_POINTS:
        values = ", ".join(f"{p.value:.0f}" for p in panel.points)
        label = "value" if len(panel.points) == 1 else "values"
        return (
            f'<p class="sparse"><strong>{html.escape(values)}</strong>'
            f'<span class="sparse-label"> ({len(panel.points)} {label} — '
            f"too few points to plot)</span></p>"
        )
    width = max(140, round(300 * span / widest))
    return _svg_line(panel.points, color, width=width, unit=unit)


def _render_series(
    series: Series,
    color: str,
    title: str,
    note: str,
    provenance: str = "",
    unit: str = "count",
) -> str:
    """Faceted panels for rate metrics; one banded line for properties."""
    prov = ""
    if provenance:
        prov = (
            f'<details class="provenance"><summary>Technical note</summary>'
            f"<p>{html.escape(provenance)}</p></details>"
        )
    header = f"<h3>{html.escape(title)}</h3><p class='note'>{html.escape(note)}</p>{prov}"

    if series.faceted:
        drawn = [p for p in series.panels if p.points]
        spans = {p.regime: max(_span_days(p.points), 1) for p in drawn}
        widest = max(spans.values(), default=1)
        panels = "".join(
            f'<div class="panel" style="flex:{spans[panel.regime]} 1 0">'
            f"<h4>{html.escape(panel.regime)}</h4>"
            f'<p class="frame">{html.escape(panel.sampling_frame)}</p>'
            f"{_saturation_warning(panel)}"
            f"{_panel_body(panel, color, spans[panel.regime], widest, unit)}"
            f'<p class="range">{html.escape(panel.points[0].date)} - '
            f"{html.escape(panel.points[-1].date)}</p></div>"
            for panel in drawn
        )
        return (
            f'<section class="chart faceted">{header}'
            f'<p class="rule">Population rate - separate panels per regime; '
            f"no line crosses a regime boundary.</p>"
            f'<div class="panels">{panels}</div>'
            f"{_table_view([p for panel in series.panels for p in panel.points])}</section>"
        )

    if not series.points:
        return f'<section class="chart">{header}<p class="empty">no data</p></section>'

    bands = "".join(
        f'<li><span class="swatch"></span>{html.escape(regime)}: '
        f"{html.escape(start)} - {html.escape(end)}</li>"
        for regime, start, end in series.regime_bands
    )

    # Pre-render one SVG per surface (including "all") as hidden divs.
    # The JS surface selector simply shows/hides these divs -- no SVG re-draw
    # in the browser, no framework, no build step. The "all" div is visible by
    # default; selecting a specific surface shows only its div.
    svg_all = _svg_line(series.points, color, unit=unit)
    surface_svgs = f'<div class="surf-view" data-surface="all">{svg_all}</div>'
    for surf, pts in series.surface_points.items():
        surf_svg = _svg_line(pts, color, unit=unit)
        surface_svgs += (
            f'<div class="surf-view" data-surface="{html.escape(surf)}" '
            f'style="display:none">{surf_svg}</div>'
        )

    return (
        f'<section class="chart" data-metric="{html.escape(series.metric)}">{header}'
        f"{surface_svgs}"
        f'<p class="range">{html.escape(series.points[0].date)} - '
        f"{html.escape(series.points[-1].date)}</p>"
        f'<ul class="bands">{bands}</ul>'
        f"{_table_view(series.points)}</section>"
    )


def _subagent_totals(
    store: Path,
    since: str | None = None,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]], dict[str, int]]:
    """Sum the stored per-parent subagent breakdowns into (by_agent, by_model, spawn_counts).

    Work sessions only, matching every other panel. Rows with a NULL column are
    parents that spawned no subagent -- skipped, not counted as zero.
    spawn_counts aggregates agent type counts from parent Agent tool calls.
    Pass `since` (YYYY-MM-DD) to restrict to sessions on/after that date -- used to
    measure unattributed share on a recent window, since pre-CLI-2.1.201 transcripts
    permanently lack attribution and would otherwise dominate an all-time cumulative
    view regardless of how many new named agents ship.
    """
    by_agent: dict[str, dict[str, float]] = {}
    by_model: dict[str, dict[str, float]] = {}
    spawn_counts: dict[str, int] = {}
    for row in _work_sessions(read_all(store)):
        if since and row.get("date", "") < since:
            continue
        raw = row.get("subagent_costs")
        if raw:
            try:
                payload = json.loads(raw)
            except (TypeError, json.JSONDecodeError):
                payload = {}
            for group, target in (("by_agent", by_agent), ("by_model", by_model)):
                for name, stats in (payload.get(group) or {}).items():
                    slot = target.setdefault(name, {"cost": 0.0, "output_tokens": 0.0, "n": 0.0})
                    slot["cost"] += stats.get("cost", 0.0)
                    slot["output_tokens"] += stats.get("output_tokens", 0)
                    slot["n"] += stats.get("n", 0)
        raw_spawns = row.get("agent_spawns")
        if raw_spawns:
            try:
                spawns = json.loads(raw_spawns)
            except (TypeError, json.JSONDecodeError):
                spawns = []
            for spawn in spawns:
                agent_type = spawn.get("type", "general-purpose")
                spawn_counts[agent_type] = spawn_counts.get(agent_type, 0) + 1
    return by_agent, by_model, spawn_counts


def _share_rows(totals: dict[str, dict[str, float]], label: str) -> str:
    """A cost-ranked breakdown table. Share is of subagent spend, not session spend."""
    if not totals:
        return '<p class="empty">no data</p>'
    grand = sum(s["cost"] for s in totals.values()) or 1.0
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{stats['cost']:,.0f}</td>"
        f"<td>{stats['cost'] / grand * 100:.0f}%</td>"
        f"<td>{stats['output_tokens']:,.0f}</td><td>{stats['n']:.0f}</td></tr>"
        for name, stats in sorted(totals.items(), key=lambda kv: -kv[1]["cost"])
    )
    return (
        f"<table><thead><tr><th>{html.escape(label)}</th><th>cost units</th>"
        f"<th>share</th><th>output tokens</th><th>transcripts</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _spawn_table(spawn_counts: dict[str, int]) -> str:
    """Spawned agents by type — from parent Agent tool calls."""
    if not spawn_counts:
        return ""
    total = sum(spawn_counts.values()) or 1
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td><td>{count / total * 100:.0f}%</td></tr>"
        for name, count in sorted(spawn_counts.items(), key=lambda kv: -kv[1])
    )
    return (
        f"<h4>Spawned agents by type</h4>"
        f'<p class="note">From parent sessions\' Agent tool calls.</p>'
        f"<table><thead><tr><th>agent type</th><th>spawns</th>"
        f"<th>share</th></tr></thead><tbody>{rows}</tbody></table>"
    )


def _render_subagents(store: Path) -> str:
    """Subagent spend split by agent type and by model.

    Rendered as tables rather than a trend line: this is a categorical breakdown
    of a single window, and only 2.1.201+ transcripts carry an agent name, so a
    time series would show attribution coverage arriving rather than any change
    in how subagents are used.
    """
    by_agent, by_model, spawn_counts = _subagent_totals(store)
    unattributed = by_agent.get(UNATTRIBUTED_AGENT, {}).get("cost", 0.0)
    grand = sum(s["cost"] for s in by_agent.values())
    # Recent-window figure: CLI 2.1.201 rollout date is the natural cut -- anything
    # before it structurally cannot carry attribution.
    recent_by_agent, _, _ = _subagent_totals(store, since=SUBAGENT_ATTRIBUTION_SINCE)
    recent_unattributed = recent_by_agent.get(UNATTRIBUTED_AGENT, {}).get("cost", 0.0)
    recent_grand = sum(s["cost"] for s in recent_by_agent.values())
    caveat = ""
    if unattributed and grand:
        caveat = (
            f'<p class="saturated">&#9888; {unattributed / grand * 100:.0f}% of subagent cost '
            f"predates CLI {SUBAGENT_ATTRIBUTION_CLI} and carries no agent name. "
            f"Per-agent shares below are shares of all subagent spend, so the named "
            f"rows understate each agent's true share of attributable work.</p>"
        )
        if recent_grand:
            caveat += (
                f'<p class="note">Since {SUBAGENT_ATTRIBUTION_SINCE}: '
                f"{recent_unattributed / recent_grand * 100:.0f}% unattributed "
                f"(recent-window figure -- the acceptance metric for GUA-45).</p>"
            )
    total_spawns = sum(spawn_counts.values())
    attributed_n = sum(s["n"] for s in by_agent.values())
    coverage_caveat = ""
    if total_spawns and attributed_n and total_spawns > attributed_n * 1.5:
        coverage_caveat = (
            f'<p class="saturated">⚠ {total_spawns} agents spawned but only '
            f"{attributed_n:.0f} cost-attributed — coverage gap.</p>"
        )
    return (
        f'<section class="chart"><h3>Subagent attribution</h3>'
        f'<p class="note">Cost and tokens of subagent transcripts, charged to the '
        f"parent session that spawned them. Work sessions only.</p>"
        f"{caveat}{coverage_caveat}"
        f'<div class="table-view">{_spawn_table(spawn_counts)}</div>'
        f'<div class="table-view">{_share_rows(by_agent, "agent")}</div>'
        f'<div class="table-view">{_share_rows(by_model, "model")}</div></section>'
    )


def build_skill_economics(store: Path) -> dict[str, dict[str, float]]:
    """Aggregate per-skill invocation count and cost from stored skill_costs JSON.

    Returns {skill_name: {"cost": float, "n": int}} sorted by cost descending.
    Work sessions only (meta-sessions excluded). July-forward only — skill_costs
    is null in the note era.
    """
    totals: dict[str, dict[str, float]] = {}
    for row in _work_sessions(read_all(store)):
        raw = row.get("skill_costs")
        if not raw:
            continue
        try:
            costs: dict[str, float] = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        for skill, cost in costs.items():
            entry = totals.setdefault(skill, {"cost": 0.0, "n": 0})
            entry["cost"] += float(cost)
            entry["n"] += 1
    return dict(sorted(totals.items(), key=lambda kv: -kv[1]["cost"]))


def _render_skill_economics(store: Path) -> str:
    """Per-skill invocation count and cost table.

    Parallel to the existing model/agent-type breakdown tables. Marker-owned
    region in the aggregate dashboard; not patched into context-dashboard.html
    (that is the review-card pattern, not needed here).
    """
    totals = build_skill_economics(store)
    if not totals:
        return (
            '<section class="chart"><h3>Skill economics</h3>'
            '<p class="note">No skill cost data yet. Skill invocations are attributed '
            "from JSONL era sessions (July+).</p></section>"
        )
    grand = sum(e["cost"] for e in totals.values()) or 1.0
    rows = "".join(
        f"<tr><td>{html.escape(skill)}</td>"
        f"<td>{stats['cost']:,.0f}</td>"
        f"<td>{stats['cost'] / grand * 100:.0f}%</td>"
        f"<td>{int(stats['n'])}</td></tr>"
        for skill, stats in totals.items()
    )
    return (
        '<section class="chart"><h3>Skill economics</h3>'
        '<p class="note">Per-skill cost and session count. Cost attributed from JSONL '
        "assistant output between a slash invocation and the next human turn. "
        "Work sessions only; July-forward.</p>"
        '<div class="table-view"><table>'
        "<thead><tr><th>Skill</th><th>cost units</th><th>share</th><th>sessions</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></section>"
    )


def _render_funnel(funnel: Funnel | None) -> str:
    if funnel is None or funnel.entries_in is None:
        return (
            '<section class="chart"><h3>Promotion funnel</h3>'
            '<p class="note">No logged synthesis event. growth.md drains on /dream, so an '
            "empty buffer is not evidence of zero promotions - the counts must be emitted "
            "at synthesis time.</p></section>"
        )
    stages = [
        ("entries in", funnel.entries_in),
        ("to sounding", funnel.to_sounding),
        ("to portfolio", funnel.to_portfolio),
        ("flagged for retro", funnel.flagged_retro),
    ]
    tiles = "".join(
        f'<div class="tile"><span class="value">{v if v is not None else "-"}</span>'
        f'<span class="label">{html.escape(label)}</span></div>'
        for label, v in stages
    )
    return (
        f'<section class="chart"><h3>Promotion funnel</h3>'
        f'<p class="note">Last synthesis {html.escape(funnel.last_synthesis or "unknown")} - '
        f"counts read from the logged event, not the drained buffer "
        f"(buffer now holds {funnel.entries_since}).</p>"
        f'<div class="tiles">{tiles}</div></section>'
    )


_STATUS_ORDER = {
    "confirmed": 0,
    "verified": 0,
    "failed": 1,
    "trending": 2,
    "hypothesis": 3,
    "inconclusive": 4,
}
_STATUS_CLASS = {"confirmed": "exp-confirmed", "verified": "exp-confirmed", "failed": "exp-failed"}

# ---------------------------------------------------------------------------
# Ledger parsing (Step 7)
# ---------------------------------------------------------------------------

_LEDGER_ROW = re.compile(
    r"^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
)
_LEDGER_LOG_ROW = re.compile(
    r"^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
)
_HEADER_CELL = re.compile(r"^-+$")


def parse_ledger(ledger_path: Path, log_path: Path | None = None) -> list[Experiment]:
    """Parse tooling-ledger.md (and optionally tooling-ledger-log.md) into Experiment rows.

    Active ledger schema: | Date | Change | Area | Metric | Status |
    Log ledger schema:    | Date | Change | Area | Verdict | Evidence |
    Both are 5-column tables. Rows with rollup/batch markers in the date cell are
    skipped (not parseable as individual experiments). Malformed rows degrade to
    'skipped N rows' logged at WARNING — never crash the dashboard build.

    Returns the list deduplicated by (date, name) — the log may contain superseded
    entries that are re-archived from the active ledger.
    """
    experiments: list[Experiment] = []
    skipped = 0

    def _parse_5col_table(text: str, is_log: bool) -> None:
        nonlocal skipped
        for line in text.splitlines():
            m = _LEDGER_ROW.match(line)
            if not m:
                continue
            cells = [m.group(i).strip() for i in range(1, 6)]
            date_cell, change_cell, _area_cell, metric_cell, status_cell = cells
            # Skip header and separator rows
            if _HEADER_CELL.match(date_cell) or date_cell.lower() in ("date", "---"):
                continue
            if _HEADER_CELL.match(status_cell) or status_cell.lower() in (
                "status",
                "verdict",
                "---",
            ):
                continue
            # Skip rollup/batch rows (not individual experiments)
            if any(kw in date_cell.lower() for kw in ("rollup", "batch", "2026-07 (rollup)")):
                skipped += 1
                continue
            if not change_cell or not status_cell:
                skipped += 1
                continue
            # For the log: same positional layout (date|change|area|verdict|evidence)
            # — verdict is in status_cell position, so no conditional needed.
            effective_status = status_cell
            # Strip backticks from metric
            effective_metric = metric_cell.strip("`") or "—"
            experiments.append(
                Experiment(
                    name=change_cell,
                    metric=effective_metric,
                    status=effective_status,
                    date=date_cell,
                )
            )

    if not ledger_path.exists():
        log.warning("dashboard.ledger_missing", path=str(ledger_path))
        return []

    try:
        _parse_5col_table(ledger_path.read_text(encoding="utf-8", errors="replace"), is_log=False)
    except Exception as exc:
        log.warning("dashboard.ledger_parse_error", path=str(ledger_path), error=str(exc))

    if log_path and log_path.exists():
        try:
            _parse_5col_table(log_path.read_text(encoding="utf-8", errors="replace"), is_log=True)
        except Exception as exc:
            log.warning("dashboard.ledger_log_parse_error", path=str(log_path), error=str(exc))

    if skipped:
        log.warning("dashboard.ledger_rows_skipped", skipped=skipped)

    # Dedup by (date, name) keeping last occurrence (log entries supersede earlier active rows).
    seen: dict[tuple[str, str], int] = {}
    for i, exp in enumerate(experiments):
        seen[(exp.date, exp.name)] = i
    return [experiments[i] for i in sorted(seen.values())]


def _status_key(status: str) -> str:
    parts = status.split()
    return parts[0] if parts else ""


def parse_findings(path: Path) -> list[dict]:
    """Read review-findings JSONL, parse each line, return list of finding dicts.

    Malformed lines are skipped with a warning so a single bad write never
    breaks the dashboard render.
    """
    findings: list[dict] = []
    if not path.exists():
        return findings
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            findings.append(json.loads(line))
        except json.JSONDecodeError:
            log.warning("dashboard.findings_parse_error", line=i, path=str(path))
    return findings


def _render_review_findings(findings: list[dict] | None) -> str:
    """Render the Code Review Findings subtab section.

    Four panels: severity distribution over time, findings by source, top
    recurring categories, and per-repo finding density. Renders an empty-state
    placeholder when no findings exist yet.
    """
    if not findings:
        return (
            '<section class="chart"><h3>Code Review Findings</h3>'
            '<p class="note">No review findings yet. Run <code>/code-review</code> '
            "or <code>/workflow-review</code> to populate.</p>"
            "<p>Each run appends structured findings (akira-scan + SANYI) to "
            "<code>guacamayo/.claude/docs/review-findings.jsonl</code>. "
            "Cartographer reads this file on every <code>--facts</code> run.</p>"
            "</section>"
        )

    # Severity distribution table
    impact_order = {"blocker": 0, "important": 1, "question": 2, "suggestion": 3, "nit": 4}
    impact_counts: dict[str, int] = {}
    for f in findings:
        impact = f.get("merge_impact", "unknown")
        impact_counts[impact] = impact_counts.get(impact, 0) + 1
    impact_rows = "".join(
        f"<tr><td>{html.escape(impact)}</td><td>{count}</td></tr>"
        for impact, count in sorted(
            impact_counts.items(), key=lambda kv: impact_order.get(kv[0], 9)
        )
    )
    severity_table = (
        "<h4>By severity</h4>"
        '<div class="table-view"><table>'
        "<thead><tr><th>Severity</th><th>Count</th></tr></thead>"
        f"<tbody>{impact_rows}</tbody></table></div>"
    )

    # Source breakdown (akira-scan vs SANYI vs other)
    source_counts: dict[str, int] = {}
    for f in findings:
        src = f.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    source_rows = "".join(
        f"<tr><td>{html.escape(src)}</td><td>{count}</td></tr>"
        for src, count in sorted(source_counts.items(), key=lambda kv: -kv[1])
    )
    source_table = (
        "<h4>By source</h4>"
        '<div class="table-view"><table>'
        "<thead><tr><th>Source</th><th>Count</th></tr></thead>"
        f"<tbody>{source_rows}</tbody></table></div>"
    )

    # Top recurring categories
    category_counts: dict[str, int] = {}
    for f in findings:
        cat = f.get("category")
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    category_html = ""
    if category_counts:
        cat_rows = "".join(
            f"<tr><td>{html.escape(cat)}</td><td>{count}</td></tr>"
            for cat, count in sorted(category_counts.items(), key=lambda kv: -kv[1])[:10]
        )
        category_html = (
            "<h4>Top categories</h4>"
            '<div class="table-view"><table>'
            "<thead><tr><th>Category</th><th>Count</th></tr></thead>"
            f"<tbody>{cat_rows}</tbody></table></div>"
        )

    # Per-repo finding density
    repo_counts: dict[str, int] = {}
    for f in findings:
        repo = f.get("repo", "unknown")
        repo_counts[repo] = repo_counts.get(repo, 0) + 1
    repo_rows = "".join(
        f"<tr><td>{html.escape(repo)}</td><td>{count}</td></tr>"
        for repo, count in sorted(repo_counts.items(), key=lambda kv: -kv[1])
    )
    repo_table = (
        "<h4>By repo</h4>"
        '<div class="table-view"><table>'
        "<thead><tr><th>Repo</th><th>Findings</th></tr></thead>"
        f"<tbody>{repo_rows}</tbody></table></div>"
    )

    total = len(findings)
    blockers = sum(1 for f in findings if f.get("merge_impact") == "blocker")
    return (
        f'<section class="chart"><h3>Code Review Findings</h3>'
        f'<p class="note">{total} findings total, {blockers} blockers. '
        f"Source: akira-scan + SANYI, persisted per review run.</p>"
        f"{severity_table}{source_table}{category_html}{repo_table}"
        f"</section>"
    )


# ---------------------------------------------------------------------------
# Marker-owned region helpers (canonical guacamayo dashboard patching)
#
# Every auto-refreshed card in context-dashboard.html is bounded by a pair of
# HTML comments:
#   <!-- REGION-NAME:START (regenerated by cartographer --facts; do not hand-edit) -->
#   ... rendered content ...
#   <!-- REGION-NAME:END -->
#
# _patch_marker_region is the shared swap logic.  Each card has its own pair of
# marker constants and a thin patch_* wrapper so callers stay readable.
# ---------------------------------------------------------------------------


def _patch_marker_region(dashboard: Path, start_marker: str, end_marker: str, content: str) -> bool:
    """Replace the content between start/end markers with `content`, in place.

    Returns False (without writing) when the file or either marker is absent.
    The start comment itself is preserved verbatim; only the region body changes.
    """
    if not dashboard.exists():
        log.warning("dashboard.patch_missing_file", path=str(dashboard), marker=start_marker)
        return False
    text = dashboard.read_text(encoding="utf-8")
    start = text.find(start_marker)
    open_end = text.find("-->", start) if start != -1 else -1
    end = text.find(end_marker, open_end + 3) if open_end != -1 else -1
    if end == -1:
        log.warning(
            "dashboard.patch_missing_markers",
            path=str(dashboard),
            start=start_marker,
            end=end_marker,
        )
        return False
    patched = text[: open_end + 3] + "\n    " + content + "\n    " + text[end:]
    dashboard.write_text(patched, encoding="utf-8")
    return True


REVIEW_CARD_START = "<!-- REVIEW-FINDINGS:START"
REVIEW_CARD_END = "<!-- REVIEW-FINDINGS:END -->"

# ---------------------------------------------------------------------------
# Additional marker-owned regions (Step 4-9 cards)
# ---------------------------------------------------------------------------

INPUT_TOKENS_CARD_START = "<!-- INPUT-TOKENS:START"
INPUT_TOKENS_CARD_END = "<!-- INPUT-TOKENS:END -->"

SKILL_ECONOMICS_CARD_START = "<!-- SKILL-ECONOMICS:START"
SKILL_ECONOMICS_CARD_END = "<!-- SKILL-ECONOMICS:END -->"

TOOL_TRENDS_CARD_START = "<!-- TOOL-TRENDS:START"
TOOL_TRENDS_CARD_END = "<!-- TOOL-TRENDS:END -->"

FRICTION_REGROUP_CARD_START = "<!-- FRICTION-REGROUP:START"
FRICTION_REGROUP_CARD_END = "<!-- FRICTION-REGROUP:END -->"

EXPERIMENTS_CARD_START = "<!-- EXPERIMENTS-LIFECYCLE:START"
EXPERIMENTS_CARD_END = "<!-- EXPERIMENTS-LIFECYCLE:END -->"

HOOK_ACTIVITY_CARD_START = "<!-- HOOK-ACTIVITY:START"
HOOK_ACTIVITY_CARD_END = "<!-- HOOK-ACTIVITY:END -->"

_SEVERITY_ORDER = {"blocker": 0, "important": 1, "question": 2, "suggestion": 3, "nit": 4}
_SEVERITY_COLOR = {"blocker": "var(--bad)", "important": "var(--warn)", "nit": "var(--text-3)"}
_REVIEW_ROW_CAP = 20


def _sev_style(sev: str) -> str:
    color = _SEVERITY_COLOR.get(sev)
    return f' style="color:{color}"' if color else ""


def _review_row(f: dict) -> str:
    where = f"{f.get('repo', '?')} {f.get('issue', '')}".strip()
    title = html.escape(f.get("title", "?"))
    file, line = f.get("file", ""), f.get("line", 0)
    if file and file != "n/a":
        loc = html.escape(file.rsplit("/", 1)[-1] + (f":{line}" if line else ""))
        title += f' <span style="color:var(--text-3)">({loc})</span>'
    sev = f.get("severity", "unknown")
    return (
        f"<tr><td>{html.escape(where)}</td><td>{title}</td>"
        f"<td>{html.escape(f.get('category', ''))}</td>"
        f"<td{_sev_style(sev)}>{html.escape(sev)}</td></tr>"
    )


def render_review_card(findings: list[dict]) -> str:
    """Render the review-findings card for the canonical guacamayo dashboard.

    Targets context-dashboard.html's hand-maintained idiom (card / card-note /
    stat-row / repo-table), unlike ``_render_review_findings`` which renders this
    repo's aggregate-dashboard chart idiom. Keyed to the review-findings.jsonl
    schema: date, repo, issue, file, line, category, severity, title.

    Step 8: findings are grouped by repo, time-descending within each repo.
    Severity is a sort key within each repo group (not the primary grouping).
    The `source` field is consumed when present (F8 full-schema rows) and
    degraded gracefully for older rows without it.
    """
    if not findings:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Review findings</div>\n'
            '      <p class="card-note">No review findings yet. Run <code>/code-review</code> '
            "or <code>/workflow-review</code> to populate.</p>\n"
            "    </div>"
        )

    sev_counts: dict[str, int] = {}
    for f in findings:
        sev = f.get("severity", "unknown")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
    stats = "".join(
        f'<div class="stat"><span class="value"{_sev_style(sev)}>{count}</span>'
        f'<span class="label">{html.escape(sev)}</span></div>'
        for sev, count in sorted(sev_counts.items(), key=lambda kv: _SEVERITY_ORDER.get(kv[0], 9))
    )

    # Step 8: group by repo, sort repos by most-recent finding date descending,
    # then within each repo sort by (severity, date descending).
    by_repo: dict[str, list[dict]] = {}
    for f in findings:
        by_repo.setdefault(f.get("repo", "unknown"), []).append(f)
    repo_order = sorted(
        by_repo,
        key=lambda r: max((f.get("date", "") for f in by_repo[r]), default=""),
        reverse=True,
    )

    rows_rendered = 0
    repo_sections = []
    for repo in repo_order:
        repo_findings = sorted(
            by_repo[repo],
            key=lambda f: (
                _SEVERITY_ORDER.get(f.get("severity", ""), 9),
                -(f.get("date") or "").__len__(),
            ),
        )
        # Sort time-descending within same severity
        repo_findings = sorted(
            by_repo[repo],
            key=lambda f: (_SEVERITY_ORDER.get(f.get("severity", ""), 9), f.get("date", "")),
        )
        repo_rows = ""
        for f in repo_findings:
            if rows_rendered >= _REVIEW_ROW_CAP:
                break
            repo_rows += _review_row(f)
            rows_rendered += 1
        if repo_rows:
            source_tag = ""
            # Consume `source` field (F8) when present on any finding in this repo
            sources = {f.get("source") for f in repo_findings if f.get("source")}
            if sources:
                source_tag = (
                    f' <span style="font-size:10px;color:var(--text-3)">'
                    f"[{html.escape(', '.join(sorted(sources)))}]</span>"
                )
            repo_sections.append(
                f'<tr><td colspan="4" style="padding-top:10px;font-weight:600;'
                f'font-size:12px;color:var(--text-secondary)">'
                f"{html.escape(repo)}{source_tag}</td></tr>"
                f"{repo_rows}"
            )

    dates = sorted(f.get("date", "") for f in findings if f.get("date"))
    latest = dates[-1] if dates else "?"
    targets = {(f.get("repo", "?"), f.get("issue", "?")) for f in findings}
    note = (
        f"{len(findings)} findings across {len(targets)} review targets, "
        f"{len(by_repo)} repos. Latest run: {html.escape(latest)}."
    )

    cap_note = ""
    if len(findings) > _REVIEW_ROW_CAP:
        cap_note = (
            '\n      <p style="font-size:11px;color:var(--text-3);margin-top:8px;font-style:italic">'
            f"Showing {_REVIEW_ROW_CAP} of {len(findings)} by severity; "
            "full list in review-findings.jsonl.</p>"
        )

    return (
        '<div class="card">\n'
        '      <div class="card-title">Review findings</div>\n'
        f'      <p class="card-note">{note}</p>\n'
        f'      <div class="stat-row" style="margin-bottom:16px">{stats}</div>\n'
        '      <div class="overflow-x">\n'
        '      <table class="repo-table">\n'
        "        <thead><tr><th>Repo / issue</th><th>Finding</th><th>Category</th><th>Severity</th></tr></thead>\n"
        f"        <tbody>{''.join(repo_sections)}</tbody>\n"
        "      </table>\n"
        f"      </div>{cap_note}\n"
        "    </div>"
    )


def patch_review_findings(dashboard: Path, findings: list[dict]) -> bool:
    """Regenerate the review card between REVIEW-FINDINGS markers, in place.

    The canonical dashboard is hand-maintained; only the marked region is
    cartographer-owned. Returns False without writing when the file or either
    marker is missing, so a moved marker never silently truncates the page.
    """
    if not dashboard.exists():
        log.warning("dashboard.review_patch_missing_file", path=str(dashboard))
        return False
    text = dashboard.read_text(encoding="utf-8")
    start = text.find(REVIEW_CARD_START)
    open_end = text.find("-->", start) if start != -1 else -1
    end = text.find(REVIEW_CARD_END, open_end + 3) if open_end != -1 else -1
    if end == -1:
        log.warning("dashboard.review_patch_missing_markers", path=str(dashboard))
        return False
    patched = text[: open_end + 3] + "\n    " + render_review_card(findings) + "\n    " + text[end:]
    dashboard.write_text(patched, encoding="utf-8")
    return True


def render_input_tokens_card(store: Path) -> str:
    """Render the input-tokens card for the canonical guacamayo dashboard.

    Two metrics: p50 per-session and daily total. Shows how much context is
    being carried in and how that tracks with cost. July-forward only.
    """
    series_p50 = build_series("input_tokens_p50", store)
    series_sum = build_series("input_tokens_sum", store)
    if not series_p50.points and not series_sum.points:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Input tokens</div>\n'
            '      <p class="card-note">No data yet. July-forward only.</p>\n'
            "    </div>"
        )
    latest_p50 = series_p50.points[-1].value if series_p50.points else 0
    latest_sum = series_sum.points[-1].value if series_sum.points else 0
    svg_p50 = _svg_line(series_p50.points, "var(--s1)", unit="tokens") if series_p50.points else ""
    svg_sum = _svg_line(series_sum.points, "var(--s2)", unit="tokens") if series_sum.points else ""
    return (
        '<div class="card">\n'
        '      <div class="card-title">Input tokens</div>\n'
        '      <p class="card-note">How much context is carried into each session. '
        "p50 = median per session; daily total tracks with daily cost. "
        '<span class="direction good">&darr; Lower input volume = cheaper sessions.</span></p>\n'
        '      <div class="card-row">\n'
        '        <div class="card">\n'
        '          <div class="card-title">Input tokens per session (p50)</div>\n'
        '          <div class="stat-row">'
        f'<div class="stat"><span class="value">{_fmt_value(latest_p50, "tokens")}</span>'
        '<span class="label">p50 today</span></div></div>\n'
        f"          {svg_p50}\n"
        "        </div>\n"
        '        <div class="card">\n'
        '          <div class="card-title">Input tokens total (daily)</div>\n'
        '          <div class="stat-row">'
        f'<div class="stat"><span class="value">{_fmt_value(latest_sum, "tokens")}</span>'
        '<span class="label">today</span></div></div>\n'
        f"          {svg_sum}\n"
        "        </div>\n"
        "      </div>\n"
        "    </div>"
    )


def patch_input_tokens_card(dashboard: Path, store: Path) -> bool:
    """Regenerate the input-tokens card between INPUT-TOKENS markers, in place."""
    return _patch_marker_region(
        dashboard, INPUT_TOKENS_CARD_START, INPUT_TOKENS_CARD_END, render_input_tokens_card(store)
    )


def render_skill_economics_card(store: Path) -> str:
    """Render the skill economics card for the canonical guacamayo dashboard."""
    totals = build_skill_economics(store)
    if not totals:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Skill economics</div>\n'
            '      <p class="card-note">No skill cost data yet. Skill invocations are '
            "attributed from JSONL era sessions (July+).</p>\n"
            "    </div>"
        )
    grand = sum(e["cost"] for e in totals.values()) or 1.0
    rows = "".join(
        f"<tr><td>{html.escape(skill)}</td>"
        f"<td>{stats['cost'] / 1_000_000:,.1f}M</td>"
        f"<td>{stats['cost'] / grand * 100:.0f}%</td>"
        f"<td>{int(stats['n'])}</td></tr>"
        for skill, stats in totals.items()
    )
    return (
        '<div class="card">\n'
        '      <div class="card-title">Skill economics</div>\n'
        '      <p class="card-note">Cost and session count per skill. Cost attributed from '
        "JSONL output between a slash invocation and the next human turn. "
        "Work sessions only; July-forward.</p>\n"
        '      <div class="overflow-x">\n'
        '      <table class="repo-table">\n'
        "        <thead><tr><th>Skill</th><th>Cost</th><th>Share</th><th>Sessions</th></tr></thead>\n"
        f"        <tbody>{rows}</tbody>\n"
        "      </table>\n"
        "      </div>\n"
        "    </div>"
    )


def patch_skill_economics_card(dashboard: Path, store: Path) -> bool:
    """Regenerate the skill economics card between SKILL-ECONOMICS markers, in place."""
    return _patch_marker_region(
        dashboard,
        SKILL_ECONOMICS_CARD_START,
        SKILL_ECONOMICS_CARD_END,
        render_skill_economics_card(store),
    )


def render_tool_trends_card(store: Path) -> str:
    """Render the tool-trends card for the canonical guacamayo dashboard."""
    ordered, series = build_tool_trends(store)
    if not series:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Tool call trends</div>\n'
            '      <p class="card-note">No tool-count data yet. July-forward only.</p>\n'
            "    </div>"
        )
    colors = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)", "var(--text-3)"]
    charts = "".join(
        f'<div style="margin-bottom:8px">'
        f'<div style="font-size:12px;font-weight:600;color:var(--text-2);margin-bottom:4px">'
        f"{html.escape(tool)}</div>"
        f"{_svg_line(series[tool], colors[min(i, len(colors) - 1)], unit='count', height=80)}</div>"
        for i, tool in enumerate(ordered)
        if tool in series
    )
    return (
        '<div class="card">\n'
        '      <div class="card-title">Tool call trends (daily)</div>\n'
        '      <p class="card-note">Daily call count for the top 5 tools by volume, '
        "plus an 'other' bucket. July-forward only. Bash volume is structural "
        "(28.7/session median) &mdash; track for antipattern changes, not absolute reduction.</p>\n"
        f"      {charts}\n"
        "    </div>"
    )


def patch_tool_trends_card(dashboard: Path, store: Path) -> bool:
    """Regenerate the tool-trends card between TOOL-TRENDS markers, in place."""
    return _patch_marker_region(
        dashboard, TOOL_TRENDS_CARD_START, TOOL_TRENDS_CARD_END, render_tool_trends_card(store)
    )


def render_friction_regroup_card(store: Path) -> str:
    """Render the friction three-group regroup card for the canonical guacamayo dashboard.

    Step 9: prompt-eng / loop-eng / harness-eng grouping. Each metric becomes a
    compact inline stat with sparkline, so all three groups fit without scrolling.
    """

    def _inline_metric(metric: str, title: str, unit: str, label_hint: str) -> str:
        series = build_series(metric, store)
        if not series.points:
            return (
                f'<div style="margin-bottom:8px">'
                f'<span style="font-size:12px;font-weight:600">{html.escape(title)}</span> '
                f'<span style="color:var(--text-3);font-size:11px">no data</span></div>'
            )
        latest = series.points[-1]
        svg = _svg_line(series.points, "var(--s1)", height=60, unit=unit)
        return (
            f'<div style="margin-bottom:12px">'
            f'<div style="font-size:12px;font-weight:600;margin-bottom:2px">{html.escape(title)}</div>'
            f'<span style="font-size:18px;font-weight:600">{html.escape(_fmt_value(latest.value, unit))}</span>'
            f'<span style="color:var(--text-3);font-size:11px;margin-left:6px">{html.escape(label_hint)}</span>'
            f"{svg}</div>"
        )

    def _hint(note: str, limit: int = 40) -> str:
        if len(note) <= limit:
            return note
        cut = note[:limit].rsplit(" ", 1)[0].rstrip()
        return f"{cut}…" if cut else f"{note[:limit]}…"

    prompt_eng = "".join(
        _inline_metric(metric, title, unit, _hint(note))
        for metric, title, note, _prov, unit in _FRICTION_PROMPT_ENG
    )
    loop_eng = "".join(
        _inline_metric(metric, title, unit, _hint(note))
        for metric, title, note, _prov, unit in _FRICTION_LOOP_ENG
    )
    harness_eng = "".join(
        _inline_metric(metric, title, unit, _hint(note))
        for metric, title, note, _prov, unit in _FRICTION_HARNESS_ENG
    )
    return (
        '<div class="card">\n'
        '      <div class="card-title">Friction &amp; Quality (regrouped)</div>\n'
        '      <p class="card-note">Metrics regrouped by engineering layer: '
        "<strong>Prompt-eng</strong> (capability signals, higher = better), "
        "<strong>Loop-eng</strong> (true friction, lower = better), "
        "<strong>Harness-eng</strong> (infrastructure health).</p>\n"
        '      <div class="card-row">\n'
        '        <div class="card" style="flex:1">\n'
        '          <div class="card-title">Prompt-eng</div>\n'
        '          <p class="card-note" style="color:var(--good)">Does reasoning work? '
        "Higher is better.</p>\n"
        f"          {prompt_eng}\n"
        "        </div>\n"
        '        <div class="card" style="flex:1">\n'
        '          <div class="card-title">Loop-eng</div>\n'
        '          <p class="card-note" style="color:var(--bad)">Does workflow repeat? '
        "Lower is better.</p>\n"
        f"          {loop_eng}\n"
        f'          <p style="font-size:11px;color:var(--text-3)">Rework cycles: '
        f"Not yet captured (message-pair analysis, Tier 3).</p>\n"
        "        </div>\n"
        '        <div class="card" style="flex:1">\n'
        '          <div class="card-title">Harness-eng</div>\n'
        '          <p class="card-note">Does infrastructure hold?</p>\n'
        f"          {harness_eng}\n"
        "        </div>\n"
        "      </div>\n"
        "    </div>"
    )


def patch_friction_regroup_card(dashboard: Path, store: Path) -> bool:
    """Regenerate the friction regroup card between FRICTION-REGROUP markers, in place."""
    return _patch_marker_region(
        dashboard,
        FRICTION_REGROUP_CARD_START,
        FRICTION_REGROUP_CARD_END,
        render_friction_regroup_card(store),
    )


def render_experiments_card(
    experiments: list[Experiment] | None,
    ledger_path: Path | None = None,
    ledger_log_path: Path | None = None,
) -> str:
    """Render the experiments lifecycle card for the canonical guacamayo dashboard.

    Reads from ledger when provided (Step 7). Falls back to the passed experiments
    list for backward compatibility. Renders verdict counts + top-10 table matching
    the hand-maintained card idiom.
    """
    if ledger_path is not None and experiments is None:
        experiments = parse_ledger(ledger_path, ledger_log_path)
    if not experiments:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Experiment verdicts</div>\n'
            '      <p class="card-note">No experiments tracked. Add hypothesis rows to the '
            "tooling ledger.</p>\n"
            "    </div>"
        )
    confirmed = sum(1 for e in experiments if _status_key(e.status) in ("confirmed", "verified"))
    failed = sum(1 for e in experiments if _status_key(e.status) == "failed")
    pending = len(experiments) - confirmed - failed

    _BADGE = {
        "confirmed": ("confirmed", "var(--good)"),
        "verified": ("confirmed", "var(--good)"),
        "failed": ("failed", "var(--bad)"),
    }

    def _badge(status: str) -> str:
        key = _status_key(status)
        label, color = _BADGE.get(key, (status[:10], "var(--text-3)"))
        return f'<span class="badge" style="color:{color}">{html.escape(label)}</span>'

    top = sorted(
        experiments,
        key=lambda e: (_STATUS_ORDER.get(_status_key(e.status), 9), e.date),
    )[:10]
    rows = "".join(
        f"<tr>"
        f'<td title="{html.escape(e.name)}">{html.escape(e.name[:50])}</td>'
        f'<td style="font-family:\'DM Mono\',monospace;font-size:11px" title="{html.escape(e.metric)}">{html.escape(e.metric[:30])}</td>'
        f"<td>{_badge(e.status)}</td>"
        f"<td>{html.escape(e.date)}</td>"
        f"</tr>"
        for e in top
    )
    cap = ""
    if len(experiments) > 10:
        cap = (
            f'\n      <p style="font-size:11px;color:var(--text-3);margin-top:8px;font-style:italic">'
            f"Showing top 10 of {len(experiments)}. Full list in tooling-ledger.md.</p>"
        )
    return (
        '<div class="card">\n'
        '      <div class="card-title">Experiment verdicts</div>\n'
        f'      <p class="card-note">{confirmed} confirmed, {failed} failed, {pending} pending. '
        f"Most experiments are &lt;5 days old &mdash; too early to call.</p>\n"
        '      <div class="stat-row" style="margin-bottom:16px">\n'
        f'        <div class="stat"><span class="value" style="color:var(--good)">{confirmed}</span>'
        '<span class="label">confirmed</span></div>\n'
        f'        <div class="stat"><span class="value" style="color:var(--bad)">{failed}</span>'
        '<span class="label">failed</span></div>\n'
        f'        <div class="stat"><span class="value" style="color:var(--text-3)">{pending}</span>'
        '<span class="label">pending</span></div>\n'
        "      </div>\n"
        '      <div class="overflow-x">\n'
        '      <table class="exp-table">\n'
        "        <thead><tr><th>Change</th><th>Metric</th><th>Status</th><th>Date</th></tr></thead>\n"
        f"        <tbody>{rows}</tbody>\n"
        f"      </table>\n"
        f"      </div>{cap}\n"
        "    </div>"
    )


def patch_experiments_card(
    dashboard: Path,
    experiments: list[Experiment] | None = None,
    ledger_path: Path | None = None,
    ledger_log_path: Path | None = None,
) -> bool:
    """Regenerate the experiments card between EXPERIMENTS-LIFECYCLE markers, in place."""
    content = render_experiments_card(experiments, ledger_path, ledger_log_path)
    return _patch_marker_region(dashboard, EXPERIMENTS_CARD_START, EXPERIMENTS_CARD_END, content)


# ---------------------------------------------------------------------------
# Hook activity (guard-hook fires from ~/.claude/hooks/lib.sh logging)
# ---------------------------------------------------------------------------
#
# Two logs, written by two different lib.sh helpers:
#   .hook-log.jsonl      -- log_event, carries exit_code (2 = block, 0 = warn)
#   .hook-pass-log.jsonl -- log_pass, no exit_code, silent OKs, capped by tail
#
# Both are written by shell `printf` with only `tr '"\\' '..'` sanitising the
# context field, so a logged multi-line command embeds real newlines and splits
# one record across several physical lines.  `strict=False` does NOT rescue those
# (it relaxes control chars *within* a string, not a string cut in half by
# splitlines), so the reader below also stitches continuation fragments back
# together before parsing.  strict=False is still passed for the raw-control-char
# case the sanitiser likewise misses (e.g. a literal tab in a command).

# Every hook that sources lib.sh -- used to report which guards have never fired.
KNOWN_HOOKS = (
    "branch_guard",
    "ci_drift_warn",
    "destructive_cmd_guard",
    "docs_drift_warn",
    "docs_hygiene",
    "function_complexity_warning",
    "issue_label_sync",
    "memory_duplication_guard",
    "memory_route_guard",
    "pip_guard",
    "review-verdict-gate",
    "risky_git_guard",
    "secrets_scan",
    "task_complete_check",
)

# Hooks wired to call log_pass; pass counts for anything else are absent, not zero.
PASS_LOGGING_HOOKS = ("risky_git_guard", "branch_guard")


def parse_hook_log(path: Path) -> list[dict]:
    """Read a hook JSONL log, tolerating records broken across physical lines.

    Records are emitted by shell printf, so an unescaped newline inside the
    `context` field splits one JSON object over several lines. Lines are
    re-joined until they parse (or the record is abandoned), and parsing uses
    strict=False so raw control characters inside strings are accepted.

    Malformed records are skipped with a warning -- one bad write never breaks
    the dashboard render. Returns [] when the file is absent.
    """
    events: list[dict] = []
    if not path.exists():
        return events
    buf = ""
    buf_start = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not buf:
            if not raw.strip():
                continue
            buf, buf_start = raw, i
        else:
            # Continuation of a record whose context field contained a newline.
            buf += "\n" + raw
        try:
            obj = json.loads(buf, strict=False)
        except json.JSONDecodeError:
            # A truncating `tail` can orphan a fragment with no opening brace;
            # give up on it rather than swallowing every following line.
            if not buf.lstrip().startswith("{"):
                log.warning("dashboard.hook_log_parse_error", line=buf_start, path=str(path))
                buf = ""
            continue
        if isinstance(obj, dict):
            events.append(obj)
        buf = ""
    if buf:
        log.warning("dashboard.hook_log_truncated_record", line=buf_start, path=str(path))
    return events


@dataclass
class HookActivity:
    """Per-hook block/warn/pass counts plus the roll-ups the card header needs."""

    rows: list[dict] = field(default_factory=list)
    blocks: int = 0
    warns: int = 0
    passes: int = 0
    seen: int = 0
    known: int = len(KNOWN_HOOKS)
    silent: list[str] = field(default_factory=list)
    since: str = ""


def build_hook_activity(event_log: Path, pass_log: Path) -> HookActivity:
    """Aggregate block/warn/pass counts per hook from the two lib.sh logs.

    Blocks are exit_code 2, warns are exit 0 with a message. Passes come from the
    separate pass log, which only a couple of hooks write and which lib.sh caps --
    so pass counts are floor values, and hooks that never call log_pass get None
    (rendered as an em dash) rather than a misleading 0.
    """
    stats: dict[str, dict[str, int]] = {}
    timestamps: list[str] = []

    for ev in parse_hook_log(event_log):
        hook = ev.get("hook")
        if not hook:
            continue
        entry = stats.setdefault(hook, {"blocks": 0, "warns": 0, "passes": 0})
        if ev.get("exit_code") == 2:
            entry["blocks"] += 1
        else:
            entry["warns"] += 1
        if ts := ev.get("ts"):
            timestamps.append(ts)

    for ev in parse_hook_log(pass_log):
        hook = ev.get("hook")
        if not hook:
            continue
        stats.setdefault(hook, {"blocks": 0, "warns": 0, "passes": 0})["passes"] += 1
        if ts := ev.get("ts"):
            timestamps.append(ts)

    rows = [
        {
            "hook": hook,
            "blocks": s["blocks"],
            "warns": s["warns"],
            # None (not 0) for hooks that never call log_pass -- absence of data.
            "passes": s["passes"] if hook in PASS_LOGGING_HOOKS else None,
        }
        for hook, s in stats.items()
    ]
    rows.sort(key=lambda r: (-r["blocks"], -r["warns"], r["hook"]))

    return HookActivity(
        rows=rows,
        blocks=sum(r["blocks"] for r in rows),
        warns=sum(r["warns"] for r in rows),
        passes=sum(s["passes"] for s in stats.values()),
        seen=len(rows),
        silent=sorted(h for h in KNOWN_HOOKS if h not in stats),
        since=min(timestamps, default="")[:10],
    )


def render_hook_activity_card(event_log: Path, pass_log: Path) -> str:
    """Render the hook-activity card for the canonical guacamayo dashboard."""
    act = build_hook_activity(event_log, pass_log)
    if not act.rows:
        return (
            '<div class="card">\n'
            '      <div class="card-title">Hook activity</div>\n'
            '      <p class="card-note">No hook fires logged yet. Guard hooks log to '
            "<code>~/.claude/.hook-log.jsonl</code> via <code>lib.sh</code>.</p>\n"
            "    </div>"
        )

    def _cell(value: int | None, color: str) -> str:
        if value is None:
            return "<td>&mdash;</td>"
        style = f' style="color:{color}"' if value else ""
        return f"<td{style}>{value}</td>"

    rows = "".join(
        f"<tr><td>{html.escape(r['hook'])}</td>"
        f"{_cell(r['blocks'], 'var(--bad)')}"
        f"{_cell(r['warns'], 'var(--warn)')}"
        f"{_cell(r['passes'], 'var(--good)')}</tr>"
        for r in act.rows
    )
    since = f" (since {act.since})" if act.since else ""
    silent = ""
    if act.silent:
        silent = (
            '\n      <p style="font-size:11px;color:var(--text-3);margin-top:8px;'
            'font-style:italic">Silent since logging began: '
            f"{html.escape(', '.join(act.silent))}. Pass-logging (log_pass) is only wired into "
            f"{html.escape(' + '.join(PASS_LOGGING_HOOKS))}, and the pass log is capped &mdash; "
            "pass counts are floor values, not totals.</p>"
        )
    return (
        '<div class="card">\n'
        f'      <div class="card-title">Hook activity{html.escape(since)}</div>\n'
        '      <p class="card-note">Guard-hook fires from <code>lib.sh</code> logging. '
        "<strong>Blocks</strong> = exit 2 (action denied), <strong>warns</strong> = exit 0 "
        "with a message, <strong>passes</strong> = silent OK (logged by opted-in hooks only).</p>\n"
        '      <div class="stat-row">\n'
        f'        <div class="stat"><span class="value" style="color:var(--bad)">{act.blocks}</span>'
        '<span class="label">blocks</span></div>\n'
        f'        <div class="stat"><span class="value" style="color:var(--warn)">{act.warns}</span>'
        '<span class="label">warns</span></div>\n'
        f'        <div class="stat"><span class="value" style="color:var(--good)">{act.passes}</span>'
        '<span class="label">passes logged</span></div>\n'
        f'        <div class="stat"><span class="value">{act.seen} / {act.known}</span>'
        '<span class="label">hooks seen firing</span></div>\n'
        "      </div>\n"
        '      <div class="overflow-x">\n'
        '      <table class="repo-table">\n'
        "        <thead><tr><th>Hook</th><th>Blocks</th><th>Warns</th><th>Passes</th></tr></thead>\n"
        f"        <tbody>{rows}</tbody>\n"
        "      </table>\n"
        f"      </div>{silent}\n"
        "    </div>"
    )


def patch_hook_activity_card(dashboard: Path, event_log: Path, pass_log: Path) -> bool:
    """Regenerate the hook-activity card between HOOK-ACTIVITY markers, in place."""
    return _patch_marker_region(
        dashboard,
        HOOK_ACTIVITY_CARD_START,
        HOOK_ACTIVITY_CARD_END,
        render_hook_activity_card(event_log, pass_log),
    )


def _render_experiments(experiments: list[Experiment] | None) -> str:
    if not experiments:
        return (
            '<section class="chart"><h3>Experiments</h3>'
            '<p class="note">No experiments tracked. Add hypothesis rows to the '
            "tooling ledger.</p></section>"
        )
    grouped = sorted(
        experiments, key=lambda e: (_STATUS_ORDER.get(_status_key(e.status), 9), e.name)
    )
    rows = "".join(
        f"<tr><td>{html.escape(e.name)}</td><td>{html.escape(e.metric)}</td>"
        f'<td><span class="exp-badge {_STATUS_CLASS.get(_status_key(e.status), "exp-other")}">'
        f"{html.escape(e.status)}</span></td>"
        f"<td>{html.escape(e.date)}</td></tr>"
        for e in grouped
    )
    confirmed = sum(1 for e in experiments if _status_key(e.status) in ("confirmed", "verified"))
    failed = sum(1 for e in experiments if _status_key(e.status) == "failed")
    pending = len(experiments) - confirmed - failed
    return (
        f'<section class="chart"><h3>Experiments</h3>'
        f'<p class="note">{confirmed} confirmed, {failed} failed, {pending} pending.</p>'
        f'<div class="table-view"><table>'
        f"<thead><tr><th>Change</th><th>Metric</th><th>Status</th><th>Date</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div></section>"
    )


_CSS = """
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;
--text-secondary:#52514e;--muted:#898781;--baseline:#c3c2b7;--border:rgba(11,11,11,.10);
--warn:#9a5b00;
--chart-1:#2a78d6;--chart-2:#008300;--chart-3:#e87ba4;--chart-4:#eda100;
font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--page);
color:var(--text-primary);padding:24px;}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{
color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#fff;
--text-secondary:#c3c2b7;--muted:#898781;--baseline:#383835;--border:rgba(255,255,255,.10);
--warn:#f0a94c;
--chart-1:#3987e5;--chart-2:#008300;--chart-3:#d55181;--chart-4:#c98500;}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;
--text-primary:#fff;--text-secondary:#c3c2b7;--baseline:#383835;--border:rgba(255,255,255,.10);
--warn:#f0a94c;
--chart-1:#3987e5;--chart-2:#008300;--chart-3:#d55181;--chart-4:#c98500;}
.dash-nav{position:sticky;top:0;z-index:10;background:var(--page);display:flex;gap:8px;
padding:8px 0 12px;border-bottom:1px solid var(--border);margin-bottom:16px;flex-wrap:wrap;}
.dash-nav a{font-size:13px;padding:4px 12px;border-radius:16px;text-decoration:none;
color:var(--text-secondary);background:var(--surface-1);border:1px solid var(--border);
transition:background .15s,color .15s;}
.dash-nav a:hover{color:var(--text-primary);background:var(--baseline);}
.viz-root section{scroll-margin-top:48px;}
.viz-root section>h2{font-size:17px;margin:24px 0 4px;border-left:3px solid var(--baseline);padding-left:12px;}
.viz-root h1{font-size:20px;margin:0 0 4px;}
.viz-root .sub{color:var(--text-secondary);margin:0 0 24px;font-size:13px;}
.chart{background:var(--surface-1);border:1px solid var(--border);border-radius:8px;
padding:16px;margin-bottom:16px;overflow-x:auto;}
.chart h3{font-size:15px;margin:0 0 2px;}
.chart h4{font-size:13px;margin:0 0 2px;}
.note,.frame,.range,.rule{color:var(--text-secondary);font-size:12px;margin:0 0 8px;}
.frame{color:var(--muted);font-style:italic;}
.rule{border-left:2px solid var(--baseline);padding-left:8px;}
.panels{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;}
/* flex-grow is set inline, proportional to each regime's span in days, so panel
   width reflects duration. min-width keeps a short regime legible. */
.panel{min-width:140px;}
.saturated{color:var(--warn);font-size:12px;margin:0 0 6px;font-weight:600;}
.sparse{margin:12px 0;font-size:20px;}
.sparse-label{font-size:12px;color:var(--text-secondary);font-weight:400;}
svg{width:100%;height:160px;display:block;}
.axis-label{font-size:10px;fill:var(--text-secondary);font-family:system-ui,sans-serif;}
.bands{list-style:none;padding:0;margin:8px 0 0;font-size:12px;color:var(--text-secondary);
display:flex;gap:16px;flex-wrap:wrap;}
.tiles{display:flex;gap:24px;flex-wrap:wrap;}
.tile{display:flex;flex-direction:column;}
.tile .value{font-size:32px;font-weight:600;}
.tile .label{font-size:12px;color:var(--text-secondary);}
.boundary{border-left:3px solid var(--baseline);padding-left:12px;margin:24px 0 12px;}
.empty{color:var(--muted);font-size:12px;}
.exp-badge{font-size:11px;padding:2px 8px;border-radius:10px;font-weight:600;}
.exp-confirmed{background:rgba(0,131,0,.15);color:#008300;}
.exp-failed{background:rgba(220,50,50,.12);color:#c03030;}
.exp-other{background:var(--border);color:var(--text-secondary);}
.provenance{font-size:11px;color:var(--muted);margin:0 0 6px;}
.provenance summary{cursor:pointer;}
.provenance p{margin:4px 0 0;}
.table-view{margin-top:12px;font-size:12px;color:var(--text-secondary);}
.table-view summary{cursor:pointer;color:var(--text-secondary);}
.table-view table{border-collapse:collapse;margin-top:8px;font-variant-numeric:tabular-nums;}
.table-view th,.table-view td{text-align:left;padding:2px 12px 2px 0;
border-bottom:1px solid var(--border);}
.surf-filter{display:flex;align-items:center;gap:8px;margin-left:auto;}
.surf-filter label{font-size:12px;color:var(--text-secondary);}
.surf-filter select{font-size:12px;padding:3px 8px;border-radius:12px;
border:1px solid var(--border);background:var(--surface-1);color:var(--text-primary);
cursor:pointer;}
"""


# Provenance ledger: signal -> (source, earliest honest date, status). Rendered so
# a reader can tell "flat line" from "never recorded", and so the next person to
# add a metric knows what is already collected before instrumenting again.
_COVERAGE = [
    ("Cost, tokens, cache", "JSONL usage + migrated notes", "2026-04-10", "complete"),
    ("Compaction flag", "note hook, then JSONL", "2026-04-10", "regime-bound - see rates"),
    ("Max context", "JSONL per-request", JULY_BOUNDARY, "no pre-July data, not imputed"),
    ("Skill + model attribution", "JSONL tool_use blocks", JULY_BOUNDARY, "no pre-July data"),
    ("Tool errors, interruptions", "JSONL tool_result is_error", JULY_BOUNDARY, "backfilled"),
    (
        "Human turns per session",
        "JSONL user records, tool_results excluded",
        JULY_BOUNDARY,
        "backfilled",
    ),
    ("Plan-doc outcome", "not collected", "-", "blocked - no ABANDONED label exists; see note"),
    (
        "Commits + churn",
        "git log across ~/workspace",
        "2026-04-03",
        "repo activity, not per-session",
    ),
    ("PRs opened/merged", "gh pr list", "2026-04-03", "repo activity; 94% dependabot"),
    ("Issues resolved", "not collected", "-", "no data - 0 GitHub issues, 0 LIN- refs in commits"),
    (
        "Subagent attribution",
        "JSONL subagent transcripts",
        JULY_BOUNDARY,
        f"per-model complete; agent names only from CLI {SUBAGENT_ATTRIBUTION_CLI}",
    ),
    (
        "Context fixed overhead",
        "manual JSONL sample, first-turn cache write",
        "2026-07-28",
        "one-time - GUA-44, see research doc; ~15-23k tokens/session, not tracked live",
    ),
    (
        "Failure attribution (code/env/tool/unknown)",
        "JSONL tool_errors, classified at parse time (LIB-57)",
        JULY_BOUNDARY,
        "backfill requires re-parse - raw error text discarded after error_kind reduction",
    ),
    (
        "Bash antipatterns",
        "JSONL Bash tool_use commands",
        JULY_BOUNDARY,
        "backfilled",
    ),
]

# Signals deliberately not collected, with the reason. Kept visible so the same
# proposal is not re-litigated from scratch each time.
_NOT_COLLECTED = (
    "Plan-doc Status transitions (EXECUTED vs ABANDONED) would be the natural "
    "outcome metric, and it is not built for two reasons measured 2026-07-20. "
    "First, .claude/docs/ is git-ignored by policy, so a doc has current state but "
    "no history - nothing recovers the past, only forward snapshots would work. "
    "Second, and decisive: across 61 plan docs, 37 carry a Status line and ZERO "
    "say ABANDONED (EXECUTED 26, COMPLETE 5, SUPERSEDED 2, IN PROGRESS 1). An "
    "abandoned plan is silently dropped, never marked - so the ratio would read "
    "~100% success by construction and measure labelling discipline, not outcomes. "
    "The vocabulary is also unnormalised (EXECUTED vs COMPLETE vs RESEARCH "
    "COMPLETE) and only 29 of 61 filenames are date-prefixed, so a time series "
    "would cover under half the corpus. Fixing the metric means fixing the "
    "convention first, not adding a panel."
)


def weekly_cost_by_repo(store: Path) -> tuple[dict[str, dict[str, float]], float, float]:
    """Weekly cost_units per repo, July-forward only.

    Cost is split across the repos a session actually worked in, weighted by how
    many records ran under each `cwd` (`session_repos`). A session that spent 90%
    of its records in one repo contributes 90% of its cost there -- 22% of
    sessions touch more than one repo, so assigning the whole session to a single
    winner would misattribute real spend.

    July-forward only (JULY_ONLY_METRICS): `session_repos` is derived from JSONL
    `cwd` records, which the note era never captured. A pre-July point would plot
    the absence of transcripts, not a quiet week.

    Returns (weekly, attributed_cost, total_cost). The two totals are what the
    panel needs to state its own coverage rather than implying it is complete.
    """
    weekly: dict[str, dict[str, float]] = {}
    attributed = 0.0
    total = 0.0
    for row in _work_sessions(read_all(store)):
        day = str(row.get("date") or "")
        if day < JULY_BOUNDARY:
            continue
        cost = float(row.get("cost_units") or 0.0)
        total += cost
        try:
            repos: dict[str, int] = json.loads(row.get("session_repos") or "{}")
        except (json.JSONDecodeError, TypeError):
            repos = {}
        if not repos:
            continue
        attributed += cost
        records = sum(repos.values())
        week = _iso_week(day)
        for repo, count in repos.items():
            bucket = weekly.setdefault(repo, {})
            bucket[week] = bucket.get(week, 0.0) + cost * count / records
    return weekly, attributed, total


def weekly_commits_by_repo(store: Path) -> dict[str, dict[str, float]]:
    """Weekly human (non-bot) commits per repo, July-forward only.

    Same window as `weekly_cost_by_repo` so the two panels sit on one x-axis.
    Bot commits are excluded, not pooled -- see gitstore.ATTRIBUTION.
    """
    weekly: dict[str, dict[str, float]] = {}
    for row in read_git_activity(store):
        day = str(row.get("date") or "")
        if day < JULY_BOUNDARY:
            continue
        human = int(row.get("commits") or 0) - int(row.get("commits_bot") or 0)
        if human <= 0:
            continue
        bucket = weekly.setdefault(str(row["repo"]), {})
        week = _iso_week(day)
        bucket[week] = bucket.get(week, 0.0) + human
    return weekly


def _render_repo_economics(store: Path) -> str:
    """Cost and commits per repo, side by side -- deliberately NOT divided.

    The ratio these two panels invite is exactly the number this dashboard must
    not print. Ramsey commits, always (gitstore.ATTRIBUTION): there is no
    commit -> session join, so cost-per-commit would read as "Claude cost X per
    commit" when the commits are Ramsey's and the trailer is absent from 400 of
    406 of them. Rendering both series unjoined lets a reader see effort next to
    outcome without the panel asserting a causal link the data cannot support.
    """
    cost_weekly, attributed, total = weekly_cost_by_repo(store)
    commit_weekly = weekly_commits_by_repo(store)
    if not cost_weekly and not commit_weekly:
        return ""

    repos = sorted(
        set(cost_weekly) | set(commit_weekly),
        key=lambda r: -sum(cost_weekly.get(r, {}).values()),
    )
    unattributed = total - attributed
    share = (unattributed / total * 100) if total else 0.0

    rows = []
    for repo in repos:
        cost = sum(cost_weekly.get(repo, {}).values())
        commits = int(sum(commit_weekly.get(repo, {}).values()))
        rows.append(
            f"<tr><td>{html.escape(repo)}</td>"
            f"<td>{cost / 1_000_000:,.1f}M</td><td>{commits}</td></tr>"
        )
    table = (
        f'<div class="table-view"><table>'
        f"<tr><th>Repo</th><th>Session cost (July+)</th><th>Human commits</th></tr>"
        f"{''.join(rows)}</table></div>"
    )
    return (
        f'<div class="boundary"><h2>Repo effort and outcome</h2>'
        f'<p class="sub">Session cost and landed commits per repo, side by side and '
        f"<strong>deliberately not divided</strong>. There is no commit -&gt; session "
        f"join: Ramsey commits, always, so a cost-per-commit ratio would read as "
        f"Claude-authored output when the commits are his. Read these as two "
        f"independent series over the same weeks.</p></div>"
        f'<div class="chart"><h3>Since {html.escape(JULY_BOUNDARY)}</h3>{table}'
        f'<p class="frame">Cost is split across the repos a session worked in, '
        f"weighted by records under each cwd; 22% of sessions touch more than one. "
        f"{unattributed / 1_000_000:,.1f}M cost units ({share:.0f}%) ran entirely at "
        f"the workspace root and name no repo - excluded here rather than assigned to "
        f"one. A repo with cost and zero commits means spend without landed work, not "
        f"a missing join.</p></div>"
    )


def _render_repo_activity(store: Path) -> str:
    """Repo-activity tiles: commits, churn, PR flow.

    Deliberately tiles and not a trend line. These are NOT per-session metrics and
    do not join to a session, so plotting them beside cost/context would invite the
    inference the caveat exists to block (see gitstore.ATTRIBUTION).
    """
    activity = read_git_activity(store)
    prs = read_prs(store)
    if not activity and not prs:
        return ""

    commits = sum(r["commits"] for r in activity)
    bot = sum(r["commits_bot"] for r in activity)
    trailer = sum(r["commits_claude_trailer"] for r in activity)
    human = commits - bot
    insertions = sum(r["insertions"] for r in activity)
    deletions = sum(r["deletions"] for r in activity)
    repos = len({r["repo"] for r in activity})
    human_prs = [p for p in prs if not p["is_bot"]]
    merged = sum(p["merged"] for p in human_prs)

    tiles = [
        (f"{human:,}", "human commits"),
        (f"{bot:,}", "bot commits"),
        (f"+{insertions:,}", "lines added (source only)"),
        (f"-{deletions:,}", "lines removed"),
        (f"{len(human_prs)}", "human PRs"),
        (f"{merged}", "PRs merged"),
        (f"{repos}", "active repos"),
    ]
    tile_html = "".join(
        f'<div class="tile"><span class="value">{html.escape(v)}</span>'
        f'<span class="label">{html.escape(label)}</span></div>'
        for v, label in tiles
    )
    return (
        f'<div class="boundary"><h2>Repo activity</h2>'
        f'<p class="sub">What landed in the repos. NOT a Claude-productivity metric '
        f"and not joinable to a session - Ramsey commits, always, so only "
        f"{trailer} of {commits:,} commits carry a Co-Authored-By trailer and its "
        f"absence means nothing. Read these as workspace throughput.</p></div>"
        f'<div class="chart"><h3>Totals since 2026-04-01</h3>'
        f'<div class="tiles">{tile_html}</div>'
        f'<p class="frame">Churn counts source files only - PDFs, notebooks, '
        f"lockfiles, vendored course material and bundled plugin JS are excluded. "
        f"Unfiltered, those were 50% of all insertions and one 70k-line PDF was the "
        f"single largest contributor.</p></div>"
    )


def _render_coverage() -> str:
    """The provenance ledger -- what is measured, since when, and what never was."""
    rows = "".join(
        f"<tr><td>{html.escape(signal)}</td><td>{html.escape(source)}</td>"
        f"<td>{html.escape(since)}</td><td>{html.escape(status)}</td></tr>"
        for signal, source, since, status in _COVERAGE
    )
    return (
        f'<div class="boundary"><h2>Signal coverage</h2>'
        f'<p class="sub">Where each number comes from and the earliest date it is '
        f"honest. A metric absent here is not being measured.</p></div>"
        f'<div class="chart"><div class="table-view"><table>'
        f"<tr><th>Signal</th><th>Source</th><th>Since</th><th>Status</th></tr>"
        f"{rows}</table></div>"
        f'<p class="frame">{html.escape(_NOT_COLLECTED)}</p></div>'
    )


def render_dashboard(
    store: Path,
    funnel: Funnel | None = None,
    experiments: list[Experiment] | None = None,
    review_findings: list[dict] | None = None,
    ledger_path: Path | None = None,
    ledger_log_path: Path | None = None,
) -> str:
    """Render the full dashboard to a self-contained HTML string.

    `ledger_path` and `ledger_log_path` are optional; when provided, the
    experiments section reads live from the tooling ledger (Step 7). When not
    provided, `experiments` is used directly (backward-compatible).
    """
    if ledger_path is not None and experiments is None:
        experiments = parse_ledger(ledger_path, ledger_log_path)

    def _chart_var(i: int) -> str:
        return f"var(--chart-{(i % 4) + 1})"

    tier1 = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_TIER1)
    )
    tier2 = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_TIER2)
    )
    shape = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_TIER_SHAPE)
    )
    # Step 9: friction tab regroup — three groups instead of flat _TIER3 list.
    friction_prompt = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_FRICTION_PROMPT_ENG)
    )
    friction_loop = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_FRICTION_LOOP_ENG)
    )
    friction_harness = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_FRICTION_HARNESS_ENG)
    )
    tier3 = (
        f'<div class="boundary"><h2 style="font-size:14px;margin:0 0 4px">Prompt-eng</h2>'
        f'<p class="sub" style="margin:0 0 12px">Does reasoning work? '
        f"Capability signals — higher is better.</p></div>"
        f"{friction_prompt}"
        f'<div class="boundary"><h2 style="font-size:14px;margin:0 0 4px">Loop-eng</h2>'
        f'<p class="sub" style="margin:0 0 12px">Does workflow repeat? '
        f"True friction signals — lower is better.</p></div>"
        f"{friction_loop}{_REWORK_PLACEHOLDER}"
        f'<div class="boundary"><h2 style="font-size:14px;margin:0 0 4px">Harness-eng</h2>'
        f'<p class="sub" style="margin:0 0 12px">Does infrastructure hold? '
        f"Error and context signals.</p></div>"
        f"{friction_harness}"
    )
    rates = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_RATES)
    )
    # Build surface selector: "All" + one option per distinct observed surface.
    surfaces = _distinct_surfaces(store)
    surf_options = '<option value="all">All surfaces</option>' + "".join(
        f'<option value="{html.escape(s)}">{html.escape(s)}</option>' for s in surfaces
    )
    surf_selector = (
        f'<div class="surf-filter">'
        f'<label for="surf-sel">Surface:</label>'
        f'<select id="surf-sel">{surf_options}</select>'
        f"</div>"
    )

    nav = (
        '<nav class="dash-nav">'
        '<a href="#cost">Cost &amp; Efficiency</a>'
        '<a href="#context">Context Health</a>'
        '<a href="#friction">Friction &amp; Quality</a>'
        '<a href="#review">Code Review</a>'
        '<a href="#progress">Experiments &amp; Progress</a>'
        f"{surf_selector}"
        "</nav>"
    )

    surf_js = (
        "<script>(function(){"
        'var sel=document.getElementById("surf-sel");'
        "if(!sel)return;"
        "function apply(v){"
        'document.querySelectorAll(".chart[data-metric]").forEach(function(chart){'
        'var views=chart.querySelectorAll(".surf-view");'
        "var found=false;"
        "views.forEach(function(d){"
        'var match=(d.dataset.surface===v)||(v==="all"&&d.dataset.surface==="all");'
        'd.style.display=match?"":"none";'
        "if(match)found=true;"
        "});"
        "if(!found){var a=chart.querySelector('.surf-view[data-surface=\"all\"]');"
        'if(a)a.style.display="";}'
        "});"
        "}"
        'sel.addEventListener("change",function(){apply(sel.value);});'
        'apply("all");'
        "})();</script>"
    )

    sec_cost = (
        f'<section id="cost"><h2>Cost &amp; Efficiency</h2>'
        f'<p class="sub">Am I spending well?</p>'
        f"{tier1}{_render_tool_trends(store)}</section>"
    )

    sec_context = (
        f'<section id="context"><h2>Context Health</h2>'
        f'<p class="sub">Is context under control? Telemetry begins {JULY_BOUNDARY} '
        f"— these metrics have no pre-boundary data.</p>"
        f"{tier2}{rates}{shape}</section>"
    )

    sec_friction = (
        f'<section id="friction"><h2>Friction &amp; Quality</h2>'
        f'<p class="sub">Where does work break? Stored from {FRICTION_STORED}, '
        f"backfilled to {JULY_BOUNDARY}.</p>"
        f"{tier3}{_render_subagents(store)}{_render_skill_economics(store)}</section>"
    )

    sec_review = (
        f'<section id="review"><h2>Code Review Findings</h2>'
        f'<p class="sub">Structured findings from akira-scan and SANYI, '
        f"persisted per review run.</p>"
        f"{_render_review_findings(review_findings)}</section>"
    )

    sec_progress = (
        f'<section id="progress"><h2>Experiments &amp; Progress</h2>'
        f'<p class="sub">Are my changes working?</p>'
        f"{_render_experiments(experiments)}"
        f"{_render_funnel(funnel)}"
        f"{_render_repo_activity(store)}"
        f"{_render_repo_economics(store)}"
        f"{_render_coverage()}</section>"
    )

    return (
        f"<style>{_CSS}</style>"
        f'<div class="viz-root"><h1>Context engineering dashboard</h1>'
        f'<p class="sub">Work sessions only, faceted by instrumentation regime. '
        f"Rates are never pooled across regimes.</p>"
        f"{nav}{sec_cost}{sec_context}{sec_friction}{sec_review}{sec_progress}"
        f"{surf_js}</div>"
    )


def write_dashboard(
    store: Path,
    out: Path,
    growth_md: Path | None = None,
    experiments: list[Experiment] | None = None,
    review_findings: list[dict] | None = None,
    ledger_path: Path | None = None,
    ledger_log_path: Path | None = None,
) -> Path:
    """Render and write the dashboard, returning the output path."""
    funnel = funnel_counts(growth_md) if growth_md else None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_dashboard(store, funnel, experiments, review_findings, ledger_path, ledger_log_path),
        encoding="utf-8",
    )
    log.info("dashboard.written", out=str(out), store=str(store))
    return out


# ---------------------------------------------------------------------------
# Region injection — context-dashboard.html marker pairs
# ---------------------------------------------------------------------------

# Marker pattern: <!-- NAME:START ... --> ... <!-- NAME:END -->
_MARKER_END_TMPL = "<!-- {name}:END -->"


def inject_regions(html_path: Path, regions: dict[str, str]) -> Path:
    """Replace content between START/END marker pairs in *html_path*.

    Only the bytes between each matched pair are replaced; everything else —
    including the marker comments themselves — is left untouched.  The result
    is built entirely in memory and written once, so a mid-run failure leaves
    the original file intact.

    Args:
        html_path: Target HTML file (read + written in place).
        regions: Mapping of region-name → replacement HTML.  Names not present
            in the file are skipped with a warning; names present in the file
            but absent from *regions* are left untouched.

    Returns:
        The path that was written.

    Raises:
        FileNotFoundError: If *html_path* does not exist.
    """
    # Guard: never write to the deprecated path. Checked before any read so the
    # refusal is unconditional rather than dependent on the file being readable.
    if html_path.name == "dashboard.html" and ".sounding" in str(html_path):
        raise ValueError(
            f"Refusing to write to deprecated path {html_path}. "
            "The shared artifact is context-dashboard.html."
        )

    if not html_path.exists():
        raise FileNotFoundError(f"context-dashboard not found: {html_path}")

    result = html_path.read_text(encoding="utf-8")
    for name, replacement in regions.items():
        start_tag = f"<!-- {name}:START"
        end_tag = _MARKER_END_TMPL.format(name=name)

        start_idx = result.find(start_tag)
        if start_idx == -1:
            log.warning("inject_regions.missing_start", region=name, path=str(html_path))
            continue

        # Find the end of the START comment (the closing ">")
        start_comment_end = result.index("-->", start_idx) + len("-->")

        end_idx = result.find(end_tag, start_comment_end)
        if end_idx == -1:
            # Fail soft: a half-marked region is skipped, not fatal. Raising here
            # would let one malformed pair block every other region's refresh.
            log.warning("inject_regions.missing_end", region=name, path=str(html_path))
            continue

        # Replace only the content BETWEEN the two markers.
        # Preserve a single newline on each side so markers stay on their own lines.
        before = result[:start_comment_end]
        after = result[end_idx:]
        result = before + "\n" + replacement + "\n" + after

    html_path.write_text(result, encoding="utf-8")
    log.info("inject_regions.written", path=str(html_path), regions=list(regions))
    return html_path


def render_review_findings_region(findings: list[dict] | None) -> str:
    """Return the injectable HTML for the REVIEW-FINDINGS marker region."""
    return _render_review_findings(findings)


def render_experiments_region(experiments: list[Experiment] | None) -> str:
    """Return the injectable HTML for the EXPERIMENTS-LIFECYCLE marker region."""
    return _render_experiments(experiments)
