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
}

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
    """Either a continuous trend (`points`) or faceted panels (`panels`)."""

    metric: str
    faceted: bool
    points: list[Point] = field(default_factory=list)
    panels: list[Panel] = field(default_factory=list)
    regime_bands: list[tuple[str, str, str]] = field(default_factory=list)
    july_only: bool = False


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

    return Series(
        metric=metric,
        faceted=False,
        points=points,
        regime_bands=_regime_bands(points),
        july_only=july_only,
    )


def _frame(regime: str) -> str:
    return SAMPLING_FRAME.get(regime, SAMPLING_FRAME["unclassified"])


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

# Categorical slots 1-4 from the dataviz reference palette. Only the first four
# are used: they are the set that validates on the all-pairs list in both modes.
_PALETTE = {
    "light": ["#2a78d6", "#008300", "#e87ba4", "#eda100"],
    "dark": ["#3987e5", "#008300", "#d55181", "#c98500"],
}

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

# Friction: parsed since the JSONL era, stored from 2026-07-20. Backfilled to the
# July boundary by re-parsing retained transcripts -- same apparatus, wider
# projection, so these are NOT a new regime.
_TIER3 = [
    (
        "tool_error_rate",
        "Tool error rate",
        "Errors per 100 tool calls. Higher = more friction; check failure attribution.",
        "Normalised so long sessions are not penalised",
        "count",
    ),
    (
        "interruptions_p50",
        "User interruptions per session (p50)",
        "Fast follow-up turns — the agent went off-track and was corrected.",
        "Tool results excluded",
        "count",
    ),
]

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
    return (
        f'<section class="chart">{header}'
        f"{_svg_line(series.points, color, unit=unit)}"
        f'<p class="range">{html.escape(series.points[0].date)} - '
        f"{html.escape(series.points[-1].date)}</p>"
        f'<ul class="bands">{bands}</ul>'
        f"{_table_view(series.points)}</section>"
    )


def _subagent_totals(
    store: Path,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    """Sum the stored per-parent subagent breakdowns into (by_agent, by_model).

    Work sessions only, matching every other panel. Rows with a NULL column are
    parents that spawned no subagent — skipped, not counted as zero.
    """
    by_agent: dict[str, dict[str, float]] = {}
    by_model: dict[str, dict[str, float]] = {}
    for row in _work_sessions(read_all(store)):
        raw = row.get("subagent_costs")
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        for group, target in (("by_agent", by_agent), ("by_model", by_model)):
            for name, stats in (payload.get(group) or {}).items():
                slot = target.setdefault(name, {"cost": 0.0, "output_tokens": 0.0, "n": 0.0})
                slot["cost"] += stats.get("cost", 0.0)
                slot["output_tokens"] += stats.get("output_tokens", 0)
                slot["n"] += stats.get("n", 0)
    return by_agent, by_model


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


def _render_subagents(store: Path) -> str:
    """Subagent spend split by agent type and by model.

    Rendered as tables rather than a trend line: this is a categorical breakdown
    of a single window, and only 2.1.201+ transcripts carry an agent name, so a
    time series would show attribution coverage arriving rather than any change
    in how subagents are used.
    """
    by_agent, by_model = _subagent_totals(store)
    unattributed = by_agent.get(UNATTRIBUTED_AGENT, {}).get("cost", 0.0)
    grand = sum(s["cost"] for s in by_agent.values())
    caveat = ""
    if unattributed and grand:
        caveat = (
            f'<p class="saturated">⚠ {unattributed / grand * 100:.0f}% of subagent cost '
            f"predates CLI {SUBAGENT_ATTRIBUTION_CLI} and carries no agent name. "
            f"Per-agent shares below are shares of all subagent spend, so the named "
            f"rows understate each agent's true share of attributable work.</p>"
        )
    return (
        f'<section class="chart"><h3>Subagent attribution</h3>'
        f'<p class="note">Cost and tokens of subagent transcripts, charged to the '
        f"parent session that spawned them. Work sessions only.</p>"
        f"{caveat}"
        f'<div class="table-view">{_share_rows(by_agent, "agent")}</div>'
        f'<div class="table-view">{_share_rows(by_model, "model")}</div></section>'
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


def _render_experiments(experiments: list[Experiment] | None) -> str:
    if not experiments:
        return (
            '<section class="chart"><h3>Experiments</h3>'
            '<p class="note">No experiments tracked. Add hypothesis rows to the '
            "tooling ledger.</p></section>"
        )
    grouped = sorted(experiments, key=lambda e: (_STATUS_ORDER.get(e.status.split()[0], 9), e.name))
    rows = "".join(
        f"<tr><td>{html.escape(e.name)}</td><td>{html.escape(e.metric)}</td>"
        f'<td><span class="exp-badge {_STATUS_CLASS.get(e.status.split()[0], "exp-other")}">'
        f"{html.escape(e.status)}</span></td>"
        f"<td>{html.escape(e.date)}</td></tr>"
        for e in grouped
    )
    confirmed = sum(1 for e in experiments if e.status.split()[0] in ("confirmed", "verified"))
    failed = sum(1 for e in experiments if e.status.split()[0] == "failed")
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
) -> str:
    """Render the full dashboard to a self-contained HTML string."""

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
    tier3 = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_TIER3)
    )
    rates = "".join(
        _render_series(build_series(metric, store), _chart_var(i), title, note, prov, unit)
        for i, (metric, title, note, prov, unit) in enumerate(_RATES)
    )
    nav = (
        '<nav class="dash-nav">'
        '<a href="#cost">Cost &amp; Efficiency</a>'
        '<a href="#context">Context Health</a>'
        '<a href="#friction">Friction &amp; Quality</a>'
        '<a href="#progress">Experiments &amp; Progress</a>'
        "</nav>"
    )

    sec_cost = (
        f'<section id="cost"><h2>Cost &amp; Efficiency</h2>'
        f'<p class="sub">Am I spending well?</p>'
        f"{tier1}</section>"
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
        f"{tier3}{_render_subagents(store)}</section>"
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
        f"{nav}{sec_cost}{sec_context}{sec_friction}{sec_progress}"
        f"</div>"
    )


def write_dashboard(
    store: Path,
    out: Path,
    growth_md: Path | None = None,
    experiments: list[Experiment] | None = None,
) -> Path:
    """Render and write the dashboard, returning the output path."""
    funnel = funnel_counts(growth_md) if growth_md else None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(store, funnel, experiments), encoding="utf-8")
    log.info("dashboard.written", out=str(out), store=str(store))
    return out
