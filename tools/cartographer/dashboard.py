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
import re
from dataclasses import dataclass, field
from datetime import date as _date
from pathlib import Path
from typing import Any

import structlog

from tools.cartographer.factstore import read_all

log = structlog.get_logger(__name__)

# Telemetry (per-request usage, max_context) begins with the JSONL era. Metrics
# derived from it must not render a single point before this date.
JULY_BOUNDARY = "2026-07-15"

# Population-rate metrics: the sampling frame differs per regime, so these are
# faceted and never drawn as a continuous series.
RATE_METRICS = {"compaction_pct", "sessions_per_week"}

# July-forward only: the underlying columns are null in the note era.
JULY_ONLY_METRICS = {"max_context_p50", "max_context_p90", "pct_over_150k"}

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
    raise ValueError(f"unknown metric: {metric}")


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
    ("cost_units_p50", "Cost per session (p50)", "headline - cost units, work sessions only"),
    ("cost_units_p90", "Cost per session (p90)", "tail sessions"),
    ("cache_hit_rate", "Cache hit rate", "% of input tokens served from cache"),
    ("output_tokens_p50", "Output tokens per session (p50)", "volume produced"),
]

_TIER2 = [
    ("max_context_p50", "Max context (p50)", "peak context per session"),
    ("max_context_p90", "Max context (p90)", "tail context pressure"),
    ("pct_over_150k", "% sessions over 150k context", "the 66% baseline"),
]

# Population rates: within-regime diagnostics only. Rendered faceted, never as a
# cross-regime trend - the Apr-Jun corpus samples only compacted sessions.
_RATES = [
    (
        "compaction_pct",
        "Compaction rate",
        "diagnostic only - NOT a cross-regime trend (survivorship: see panel frames)",
    ),
    ("sessions_per_week", "Sessions per week", "volume by regime; sampling frame differs"),
]


def _svg_line(points: list[Point], color: str, width: int = 640, height: int = 160) -> str:
    """A minimal 2px trend line. Recessive baseline, no gridline clutter."""
    if not points:
        return '<p class="empty">no data</p>'
    values = [p.value for p in points]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    step = width / max(len(points) - 1, 1)
    coords = " ".join(
        f"{i * step:.1f},{height - ((p.value - lo) / span) * (height - 20) - 10:.1f}"
        for i, p in enumerate(points)
    )
    dots = "".join(
        f'<circle cx="{i * step:.1f}" '
        f'cy="{height - ((p.value - lo) / span) * (height - 20) - 10:.1f}" r="4" '
        f'fill="{color}"><title>{html.escape(p.date)}: {p.value:g} (n={p.n})</title></circle>'
        for i, p in enumerate(points)
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="none">'
        f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>{dots}</svg>'
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


def _panel_body(panel: Panel, color: str, span: int, widest: int) -> str:
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
    return _svg_line(panel.points, color, width=width)


def _render_series(series: Series, color: str, title: str, note: str) -> str:
    """Faceted panels for rate metrics; one banded line for properties."""
    header = f"<h3>{html.escape(title)}</h3><p class='note'>{html.escape(note)}</p>"

    if series.faceted:
        drawn = [p for p in series.panels if p.points]
        # Width tracks each regime's span in days, so a 3-day regime does not get
        # the same axis width as an 8-week one — equal-width panels made the July
        # regimes look comparable in duration to pre-hygiene, which they are not.
        spans = {p.regime: max(_span_days(p.points), 1) for p in drawn}
        widest = max(spans.values(), default=1)
        panels = "".join(
            f'<div class="panel" style="flex:{spans[panel.regime]} 1 0">'
            f"<h4>{html.escape(panel.regime)}</h4>"
            f'<p class="frame">{html.escape(panel.sampling_frame)}</p>'
            f"{_saturation_warning(panel)}"
            f"{_panel_body(panel, color, spans[panel.regime], widest)}"
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
        f"{_svg_line(series.points, color)}"
        f'<p class="range">{html.escape(series.points[0].date)} - '
        f"{html.escape(series.points[-1].date)}</p>"
        f'<ul class="bands">{bands}</ul>'
        f"{_table_view(series.points)}</section>"
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


_CSS = """
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;
--text-secondary:#52514e;--muted:#898781;--baseline:#c3c2b7;--border:rgba(11,11,11,.10);
--warn:#9a5b00;
font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--page);
color:var(--text-primary);padding:24px;}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{
color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#fff;
--text-secondary:#c3c2b7;--muted:#898781;--baseline:#383835;--border:rgba(255,255,255,.10);
--warn:#f0a94c;}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;
--text-primary:#fff;--text-secondary:#c3c2b7;--baseline:#383835;--border:rgba(255,255,255,.10);
--warn:#f0a94c;}
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
.bands{list-style:none;padding:0;margin:8px 0 0;font-size:12px;color:var(--text-secondary);
display:flex;gap:16px;flex-wrap:wrap;}
.tiles{display:flex;gap:24px;flex-wrap:wrap;}
.tile{display:flex;flex-direction:column;}
.tile .value{font-size:32px;font-weight:600;}
.tile .label{font-size:12px;color:var(--text-secondary);}
.boundary{border-left:3px solid var(--baseline);padding-left:12px;margin:24px 0 12px;}
.empty{color:var(--muted);font-size:12px;}
.table-view{margin-top:12px;font-size:12px;color:var(--text-secondary);}
.table-view summary{cursor:pointer;color:var(--text-secondary);}
.table-view table{border-collapse:collapse;margin-top:8px;font-variant-numeric:tabular-nums;}
.table-view th,.table-view td{text-align:left;padding:2px 12px 2px 0;
border-bottom:1px solid var(--border);}
"""


def render_dashboard(store: Path, funnel: Funnel | None = None) -> str:
    """Render the full dashboard to a self-contained HTML string."""
    tier1 = "".join(
        _render_series(build_series(metric, store), _PALETTE["light"][i % 4], title, note)
        for i, (metric, title, note) in enumerate(_TIER1)
    )
    tier2 = "".join(
        _render_series(build_series(metric, store), _PALETTE["light"][i % 4], title, note)
        for i, (metric, title, note) in enumerate(_TIER2)
    )
    rates = "".join(
        _render_series(build_series(metric, store), _PALETTE["light"][i % 4], title, note)
        for i, (metric, title, note) in enumerate(_RATES)
    )
    return (
        f"<style>{_CSS}</style>"
        f'<div class="viz-root"><h1>Context engineering dashboard</h1>'
        f'<p class="sub">Work sessions only, faceted by instrumentation regime. '
        f"Rates are never pooled across regimes.</p>"
        f"{tier1}"
        f'<div class="boundary"><h2>July-forward telemetry</h2>'
        f'<p class="sub">telemetry begins {JULY_BOUNDARY} - these metrics have no '
        f"pre-boundary data and are not imputed backwards.</p></div>"
        f"{tier2}"
        f'<div class="boundary"><h2>Population rates - per-regime only</h2>'
        f'<p class="sub">These measure the logger as much as the workflow: in the '
        f"pre-hygiene regime a note existed only when a session compacted. Faceted "
        f"per regime, never joined into one line.</p></div>"
        f"{rates}"
        f"{_render_funnel(funnel)}"
        f"</div>"
    )


def write_dashboard(store: Path, out: Path, growth_md: Path | None = None) -> Path:
    """Render and write the dashboard, returning the output path."""
    funnel = funnel_counts(growth_md) if growth_md else None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(store, funnel), encoding="utf-8")
    log.info("dashboard.written", out=str(out), store=str(store))
    return out
