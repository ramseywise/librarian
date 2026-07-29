"""Dashboard rendering tests (Phase B, Steps 5-6).

The central invariant under test is Q0's scope limit: the Apr-Jun note corpus
only exists *where sessions compacted*, so population-rate metrics measure the
logger, not the workflow. They may never be drawn as one continuous series
across a regime boundary. Per-session property metrics (cost, cache rate,
tokens) are comparable and may.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer.dashboard import (
    JULY_BOUNDARY,
    RATE_METRICS,
    SAMPLING_FRAME,
    Experiment,
    Panel,
    Point,
    _metric_value,
    _panel_body,
    _saturation_warning,
    _svg_line,
    build_series,
    funnel_counts,
    render_dashboard,
)
from tools.cartographer.factstore import ERA_JSONL, ERA_NOTE, upsert


def _row(session_id: str, date: str, regime: str, **overrides: object) -> dict[str, Any]:
    """A fact row shaped exactly like factstore.FACT_COLUMNS requires."""
    row: dict[str, Any] = {
        "session_id": session_id,
        "date": date,
        "project": "/Users/x/repo",
        "era": ERA_NOTE if date < JULY_BOUNDARY else ERA_JSONL,
        "regime": regime,
        "source_path": f"/tmp/{session_id}",
        "input_tokens": 100,
        "output_tokens": 200,
        "cache_read_tokens": 300,
        "cache_write_tokens": 40,
        "cost_units": 1234.5,
        "compacted": True,
        "is_meta": False,
    }
    row.update(overrides)
    return row


@pytest.fixture
def two_regime_store(tmp_path: Path) -> Path:
    """A store straddling the regime break: note-hook notes + July JSONL."""
    store = tmp_path / "facts.db"
    rows = [
        _row("n1", "2026-05-01", "note-hook", compacted=True),
        _row("n2", "2026-05-02", "note-hook", compacted=True),
        _row("n3", "2026-06-10", "note-hook", compacted=False),
        _row("j1", "2026-07-16", "telemetry-v1", compacted=False, max_context=150_000),
        _row("j2", "2026-07-18", "session-hygiene-v1", compacted=False, max_context=90_000),
        _row("j3", "2026-07-18", "session-hygiene-v1", compacted=True, max_context=180_000),
    ]
    upsert(rows, store)
    return store


# --- Step 5: the enforced rule ---------------------------------------------


@pytest.mark.parametrize("metric", sorted(RATE_METRICS))
def test_rate_metrics_never_continuous(two_regime_store: Path, metric: str) -> None:
    """A population-rate metric must render as per-regime panels, never one line.

    This is the survivorship guard: note-hook notes exist only where a session
    compacted, so a compaction-% line crossing 2026-07-15 would plot the
    note-writing hook's behaviour as if it were Ramsey's.
    """
    series = build_series(metric, two_regime_store)

    assert series.faceted is True, f"{metric} must be faceted by regime"
    assert series.panels, f"{metric} produced no panels"

    # Every panel is confined to exactly one regime.
    for panel in series.panels:
        regimes = {point.regime for point in panel.points}
        assert regimes == {panel.regime}, (
            f"{metric} panel {panel.regime!r} mixes regimes: {regimes}"
        )

    # No panel spans a boundary, and each declares its sampling frame.
    assert len({p.regime for p in series.panels}) == len(series.panels)
    for panel in series.panels:
        assert panel.sampling_frame, f"{metric} panel {panel.regime!r} lacks a sampling frame"
        assert panel.sampling_frame == SAMPLING_FRAME[panel.regime]


def test_property_metrics_are_continuous(two_regime_store: Path) -> None:
    """The converse: per-session properties DO cross regimes, with bands behind."""
    series = build_series("cost_units_p50", two_regime_store)

    assert series.faceted is False
    assert series.regime_bands, "a continuous trend must shade its regime bands"
    regimes = {point.regime for point in series.points}
    assert len(regimes) > 1, "expected one line spanning multiple regimes"


def test_headline_is_cost_not_compaction() -> None:
    """Q3 as superseded: compaction rate is disqualified as the headline."""
    assert "compaction_pct" in RATE_METRICS
    assert "sessions_per_week" in RATE_METRICS
    assert "cost_units_p50" not in RATE_METRICS


def test_work_sessions_only_excludes_meta(tmp_path: Path) -> None:
    """Research Disconfirming section 1: meta-sessions are never pooled in."""
    store = tmp_path / "facts.db"
    upsert(
        [
            _row("w1", "2026-07-18", "session-hygiene-v1", is_meta=False),
            _row("m1", "2026-07-18", "session-hygiene-v1", is_meta=True),
        ],
        store,
    )
    series = build_series("cost_units_p50", store)
    assert all(point.n == 1 for point in series.points), "meta session leaked into the series"


# --- Step 6: the era boundary ----------------------------------------------


def test_era_boundary(two_regime_store: Path) -> None:
    """No July-only metric may render a pre-July data point."""
    for metric in ("max_context_p50", "max_context_p90", "pct_over_150k"):
        series = build_series(metric, two_regime_store)
        points = series.points or [p for panel in series.panels for p in panel.points]
        assert points, f"{metric} rendered nothing"
        for point in points:
            assert point.date >= JULY_BOUNDARY, (
                f"{metric} rendered {point.date}, before the telemetry boundary"
            )


def test_july_panel_declares_its_boundary(two_regime_store: Path) -> None:
    html = render_dashboard(two_regime_store, funnel=None)
    assert JULY_BOUNDARY in html
    assert "telemetry begins" in html.lower()


def test_rate_metrics_actually_reach_the_page(two_regime_store: Path) -> None:
    """The faceting rule is only worth anything if the rate charts render.

    Guards a real gap: the metrics were computed and unit-tested while being
    absent from the rendered page, so a reader never saw them.
    """
    html = render_dashboard(two_regime_store, funnel=None)
    assert "Compaction rate" in html
    assert "Sessions per week" in html
    # Each faceted chart states the no-crossing rule and its per-panel frame.
    assert html.count("no line crosses a regime boundary") == len(RATE_METRICS)
    assert "rate is not a workflow property" in html


def test_panel_width_tracks_regime_span(two_regime_store: Path) -> None:
    """Equal-width panels implied equal duration: a 3-day regime rendered as wide
    as an 8-week one. Width now carries the span, so flex-grow must differ."""
    html = render_dashboard(two_regime_store, funnel=None)
    grows = re.findall(r"flex:(\d+) 1 0", html)
    assert grows, "faceted panels should carry a proportional flex-grow"
    assert len(set(grows)) > 1, f"panels all same width despite differing spans: {grows}"


def test_sparse_panel_renders_values_not_a_sliver() -> None:
    """One or two points drew a ~2px line that read as a rendering bug."""
    panel = Panel(
        regime="telemetry-v1",
        sampling_frame="all sessions logged (JSONL)",
        points=[Point(date="2026-07-15", value=7.0, regime="telemetry-v1")],
    )
    body = _panel_body(panel, "#000", span=1, widest=60)
    assert "<svg" not in body
    assert "too few points to plot" in body
    assert "7" in body


def test_saturated_rate_panel_is_flagged() -> None:
    """note-hook compaction is 186/186 then 26/26 — exactly 100%. That is the
    note-writing hook's trigger, and unflagged it reads as an upward trend."""
    points = [
        Point(date=f"2026-05-{day:02d}", value=100.0, regime="note-hook") for day in range(1, 6)
    ]
    panel = Panel(regime="note-hook", sampling_frame="frame", points=points)
    assert "100%" in _saturation_warning(panel)
    assert "logging trigger" in _saturation_warning(panel)


def test_zero_rail_panel_is_flagged() -> None:
    """0% is as much a logging artifact as 100%: migrated-jsonl notes never
    recorded compaction, so the whole regime sits on the floor."""
    points = [
        Point(date=f"2026-04-{day:02d}", value=0.0, regime="migrated-jsonl")
        for day in range(10, 16)
    ]
    panel = Panel(regime="migrated-jsonl", sampling_frame="frame", points=points)
    assert "0%" in _saturation_warning(panel)
    assert "logging trigger" in _saturation_warning(panel)


def test_unsaturated_panel_is_not_flagged() -> None:
    points = [
        Point(date=f"2026-07-{day:02d}", value=float(v), regime="session-hygiene-v1")
        for day, v in zip(range(15, 20), [10, 20, 5, 0, 15], strict=True)
    ]
    panel = Panel(regime="session-hygiene-v1", sampling_frame="frame", points=points)
    assert _saturation_warning(panel) == ""


# --- Step 6: the growth.md drain problem -----------------------------------


def test_funnel_counts_read_the_logged_event_not_the_drained_buffer(tmp_path: Path) -> None:
    """Research F5: growth.md drains to zero on /dream.

    Polling the accumulator measures the drain, not the learning. The counts must
    come from the logged synthesis event in the header, which survives the clear.
    """
    growth = tmp_path / "growth.md"
    growth.write_text(
        "# Growth - Learning Accumulator\n\n"
        "**Last Synthesis**: 2026-07-18 afternoon (/dream - 9 entries: 3 woven into "
        "sounding.md, 1 into portfolio.md, 4 process learnings flagged for /retro, "
        "1 already captured in seeds from prior synthesis)\n"
        "**Entries Since**: 0\n\n"
        "---\n",
        encoding="utf-8",
    )

    funnel = funnel_counts(growth)

    # The buffer is empty, but the funnel is NOT zero.
    assert funnel.entries_since == 0
    assert funnel.entries_in == 9
    assert funnel.to_sounding == 3
    assert funnel.to_portfolio == 1
    assert funnel.flagged_retro == 4
    assert funnel.last_synthesis == "2026-07-18"


def test_funnel_counts_absent_header_is_none_not_zero(tmp_path: Path) -> None:
    """A missing synthesis line is unknown, never a fabricated zero."""
    growth = tmp_path / "growth.md"
    growth.write_text("# Growth\n\n**Entries Since**: 0\n", encoding="utf-8")

    funnel = funnel_counts(growth)

    assert funnel.entries_in is None
    assert funnel.entries_since == 0


# --- Step 1: dark-mode SVG contrast via CSS variables -------------------------


def test_dark_mode_uses_css_variables(two_regime_store: Path) -> None:
    """SVG strokes must use var(--chart-N), not hardcoded hex colours.
    The CSS must define --chart-N in both light and dark blocks."""
    html = render_dashboard(two_regime_store, funnel=None)
    assert "var(--chart-" in html, "SVG should use CSS variable references"
    for light_hex in ("#2a78d6", "#e87ba4", "#eda100"):
        assert f'stroke="{light_hex}"' not in html, (
            f"hardcoded light palette colour {light_hex} found in SVG stroke"
        )
    assert "--chart-1:#3987e5" in html, "dark-mode CSS must define --chart-1"
    assert "--chart-1:#2a78d6" in html, "light-mode CSS must define --chart-1"


# --- Step 3: topic sections with sticky nav -----------------------------------


def test_dashboard_has_four_sections(two_regime_store: Path) -> None:
    html = render_dashboard(two_regime_store, funnel=None)
    for section_id in ("cost", "context", "friction", "review", "progress"):
        assert f'id="{section_id}"' in html, f"missing section #{section_id}"


def test_dashboard_has_nav(two_regime_store: Path) -> None:
    html = render_dashboard(two_regime_store, funnel=None)
    assert "<nav" in html, "sticky nav element missing"
    for href in ("#cost", "#context", "#friction", "#review", "#progress"):
        assert f'href="{href}"' in html, f"nav link to {href} missing"


# --- Step 4: axis labels -----------------------------------------------------


def test_svg_has_axis_labels() -> None:
    """SVG charts should render y-axis min/max and x-axis date labels."""
    points = [
        Point(date=f"2026-07-{d:02d}", value=float(v), regime="session-hygiene-v1")
        for d, v in [(15, 10000), (16, 20000), (17, 15000), (18, 30000)]
    ]
    svg = _svg_line(points, "var(--chart-1)", unit="tokens")
    assert "<text" in svg, "axis labels should render as <text> elements"
    assert "30k" in svg, "y-axis max should show formatted value"
    assert "10k" in svg, "y-axis min should show formatted value"


# --- Step 5: experiment verdicts panel ----------------------------------------


def test_experiment_panel_renders(two_regime_store: Path) -> None:
    experiments = [
        Experiment(name="compact-wiki", metric="ratio:foo", status="confirmed", date="2026-07"),
        Experiment(name="bash-block", metric="count-drop:bar", status="failed", date="2026-07"),
        Experiment(name="wake-nudge", metric="presence:baz", status="hypothesis", date="2026-07"),
    ]
    html = render_dashboard(two_regime_store, funnel=None, experiments=experiments)
    assert "compact-wiki" in html
    assert "bash-block" in html
    assert "exp-confirmed" in html
    assert "exp-failed" in html


def test_experiment_grouping() -> None:
    """Confirmed sorts before failed before inconclusive."""
    from tools.cartographer.dashboard import _render_experiments

    experiments = [
        Experiment(name="z-last", metric="m", status="hypothesis", date="d"),
        Experiment(name="a-first", metric="m", status="confirmed", date="d"),
        Experiment(name="m-mid", metric="m", status="failed", date="d"),
    ]
    html = _render_experiments(experiments)
    pos_confirmed = html.index("a-first")
    pos_failed = html.index("m-mid")
    pos_hyp = html.index("z-last")
    assert pos_confirmed < pos_failed < pos_hyp


def test_experiment_empty_state(two_regime_store: Path) -> None:
    html = render_dashboard(two_regime_store, funnel=None, experiments=None)
    assert "No experiments tracked" in html


# --- Phase 4: execution skill compliance ------------------------------------


def test_execution_skill_compliance_renders(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "e1",
                "2026-07-18",
                "session-hygiene-v1",
                session_intent="execution",
                skill_costs='{"execute": 100}',
            ),
            _row(
                "e2",
                "2026-07-18",
                "session-hygiene-v1",
                session_intent="execution",
                skill_costs="{}",
            ),
            _row("s1", "2026-07-18", "session-hygiene-v1", session_intent="scoping"),
        ],
        store,
    )
    html = render_dashboard(store, funnel=None)
    assert "Execution sessions with skills" in html


def test_execution_skill_compliance_no_execution_sessions() -> None:
    bucket = [{"session_intent": "scoping", "skill_costs": "{}"}]
    assert _metric_value("execution_skill_compliance_pct", bucket) is None


def test_execution_skill_compliance_correct_pct() -> None:
    bucket = [
        {"session_intent": "execution", "skill_costs": '{"execute": 100}'},
        {"session_intent": "execution", "skill_costs": "{}"},
    ]
    assert _metric_value("execution_skill_compliance_pct", bucket) == 50.0


# --- Phase 5: friction labels total ------------------------------------------


def test_friction_labels_total_renders(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert(
        [
            _row("f1", "2026-07-18", "session-hygiene-v1", friction_label_count=2),
            _row("f2", "2026-07-18", "session-hygiene-v1", friction_label_count=1),
        ],
        store,
    )
    html = render_dashboard(store, funnel=None)
    assert "Explicit friction labels" in html


def test_friction_labels_total_zero() -> None:
    bucket = [{"friction_label_count": 0}, {"friction_label_count": None}]
    assert _metric_value("friction_labels_total", bucket) == 0


# --- Phase 6: subagent spawns table ------------------------------------------


def test_subagent_spawns_table_renders(tmp_path: Path) -> None:
    import json

    store = tmp_path / "facts.db"
    spawns = json.dumps(
        [
            {"type": "Explore", "description": "Find files", "model": None},
            {"type": "Explore", "description": "Search code", "model": None},
            {"type": "code-reviewer", "description": "Review", "model": "sonnet"},
        ]
    )
    upsert([_row("a1", "2026-07-18", "session-hygiene-v1", agent_spawns=spawns)], store)
    html = render_dashboard(store, funnel=None)
    assert "Spawned agents by type" in html
    assert "Explore" in html
    assert "code-reviewer" in html


def test_subagent_spawns_empty(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert([_row("a1", "2026-07-18", "session-hygiene-v1")], store)
    html = render_dashboard(store, funnel=None)
    assert "Spawned agents by type" not in html


# --- GUA-43: surface filter --------------------------------------------------


def _two_surface_store(tmp_path: Path) -> Path:
    """Store with two distinct surfaces for testing the JS toggle."""
    store = tmp_path / "facts.db"
    rows = [
        _row("j1", "2026-07-16", "telemetry-v1", surface="claude-vscode"),
        _row("j2", "2026-07-17", "telemetry-v1", surface="claude-vscode"),
        _row("j3", "2026-07-18", "session-hygiene-v1", surface="claude-cli"),
        _row("j4", "2026-07-18", "session-hygiene-v1"),  # surface=None -> "unknown"
    ]
    upsert(rows, store)
    return store


def test_build_series_surface_points_populated(tmp_path: Path) -> None:
    """build_series returns per-surface point breakdowns for continuous metrics."""
    store = _two_surface_store(tmp_path)
    series = build_series("cost_units_p50", store)
    assert not series.faceted
    assert "claude-vscode" in series.surface_points


def test_build_series_all_surfaces_in_all_points(tmp_path: Path) -> None:
    """The all-surfaces series is not limited to a single surface."""
    store = _two_surface_store(tmp_path)
    series = build_series("cost_units_p50", store)
    # Points should span all rows, not just one surface
    assert len(series.points) >= 2


def test_render_dashboard_has_surface_selector(tmp_path: Path) -> None:
    """render_dashboard includes a surface selector element in the nav."""
    store = _two_surface_store(tmp_path)
    page = render_dashboard(store, funnel=None)
    assert 'id="surf-sel"' in page
    assert "surf-filter" in page


def test_render_dashboard_has_js_toggle(tmp_path: Path) -> None:
    """render_dashboard includes the vanilla JS surface toggle script."""
    store = _two_surface_store(tmp_path)
    page = render_dashboard(store, funnel=None)
    assert "surf-view" in page
    assert "surf-sel" in page


def test_render_dashboard_surf_view_divs_present(tmp_path: Path) -> None:
    """Continuous chart sections embed per-surface .surf-view divs."""
    store = _two_surface_store(tmp_path)
    page = render_dashboard(store, funnel=None)
    # At least the "all" surf-view must be present
    assert 'data-surface="all"' in page


def test_distinct_surfaces_returns_observed_values(tmp_path: Path) -> None:
    """_distinct_surfaces returns the surfaces actually present in the store."""
    from tools.cartographer.dashboard import _distinct_surfaces

    store = _two_surface_store(tmp_path)
    surfaces = _distinct_surfaces(store)
    assert "claude-vscode" in surfaces
    assert isinstance(surfaces, list)
    assert surfaces == sorted(surfaces)
