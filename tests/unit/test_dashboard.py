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
    LEDGER_METRIC_MAPPING,
    RATE_METRICS,
    SAMPLING_FRAME,
    Experiment,
    Panel,
    Point,
    _annotations_for_metric,
    _metric_value,
    _panel_body,
    _render_annotations,
    _saturation_warning,
    _svg_line,
    build_hook_activity,
    build_series,
    funnel_counts,
    parse_hook_log,
    render_dashboard,
    render_hook_activity_card,
    warn_unmapped_experiments,
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


# --- LIB-58: verdict trajectories --------------------------------------------


def test_verdict_trajectories_empty_state_when_no_verdict_store(two_regime_store: Path) -> None:
    """Omitting verdict_store entirely (the default) renders the empty state,
    so callers that never scored verdicts see no broken/missing section."""
    html = render_dashboard(two_regime_store, funnel=None)
    assert "No scored verdicts yet" in html


def test_verdict_trajectories_render_ordered_sequence(two_regime_store: Path) -> None:
    from tools.cartographer.factstore import append_verdicts

    append_verdicts(
        [
            {
                "experiment": "bash-antipattern-nudge",
                "date": "2026-07-18",
                "metric": "absence:bash-antipatterns",
                "verdict": "trending",
                "evidence": "bash-antipatterns=1 (expected 0)",
            }
        ],
        two_regime_store,
        run_at="2026-07-19T00:00:00Z",
    )
    append_verdicts(
        [
            {
                "experiment": "bash-antipattern-nudge",
                "date": "2026-07-18",
                "metric": "absence:bash-antipatterns",
                "verdict": "confirmed",
                "evidence": "bash-antipatterns=0 across scored sessions",
            }
        ],
        two_regime_store,
        run_at="2026-07-20T00:00:00Z",
    )

    html = render_dashboard(two_regime_store, funnel=None, verdict_store=two_regime_store)

    assert "Verdict trajectories" in html
    assert "bash-antipattern-nudge" in html
    pos_trending = html.index("trending")
    pos_confirmed = html.index("confirmed", pos_trending)
    assert pos_trending < pos_confirmed, "sequence should render oldest run first"


def test_render_verdict_trajectories_region_matches_dashboard_section() -> None:
    from tools.cartographer.dashboard import render_verdict_trajectories_region

    rows = [
        {
            "experiment": "exp-a",
            "date": "2026-07-18",
            "metric": "presence:foo",
            "verdict": "confirmed",
            "evidence": "foo observed",
            "run_at": "2026-07-20T00:00:00Z",
        }
    ]
    region_html = render_verdict_trajectories_region(rows)
    assert "exp-a" in region_html
    assert "Verdict trajectories" in region_html


def test_render_verdict_trajectories_region_empty_state() -> None:
    from tools.cartographer.dashboard import render_verdict_trajectories_region

    assert "No scored verdicts yet" in render_verdict_trajectories_region(None)


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
    assert "Skill compliance" in html


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


# ---------------------------------------------------------------------------
# Review-card patching (canonical guacamayo dashboard, GUA-21)
# ---------------------------------------------------------------------------

_FINDING = {
    "date": "2026-07-29",
    "review_type": "workflow-review",
    "repo": "atlas",
    "issue": "ATL-37",
    "file": "src/graph.py",
    "line": 155,
    "category": "resource-leak",
    "severity": "important",
    "title": "knowledge_tool_node leaks AtlasGraph on exception path",
}

_MARKED_PAGE = (
    '<section id="review">\n'
    "    <!-- REVIEW-FINDINGS:START (regenerated by cartographer --facts; do not hand-edit) -->\n"
    '    <div class="card">stale content</div>\n'
    "    <!-- REVIEW-FINDINGS:END -->\n"
    "</section>\n"
)


def test_render_review_card_counts_and_rows() -> None:
    from tools.cartographer.dashboard import render_review_card

    findings = [
        _FINDING,
        {**_FINDING, "severity": "nit", "file": "n/a", "line": 0, "title": "empty branches"},
    ]
    card = render_review_card(findings)
    assert '<span class="value" style="color:var(--warn)">1</span>' in card
    assert '<span class="label">important</span>' in card
    assert '<span class="label">nit</span>' in card
    assert "atlas ATL-37" in card
    assert "graph.py:155" in card  # file:line shown for located findings
    assert "n/a" not in card  # location suppressed for file="n/a"


def test_render_review_card_empty_state() -> None:
    from tools.cartographer.dashboard import render_review_card

    card = render_review_card([])
    assert "No review findings yet" in card


def test_render_review_card_orders_by_severity() -> None:
    from tools.cartographer.dashboard import render_review_card

    findings = [
        {**_FINDING, "severity": "nit", "title": "a nit"},
        {**_FINDING, "severity": "blocker", "title": "a blocker"},
    ]
    card = render_review_card(findings)
    assert card.index("a blocker") < card.index("a nit")


def test_patch_review_findings_replaces_marked_region(tmp_path: Path) -> None:
    from tools.cartographer.dashboard import patch_review_findings

    page = tmp_path / "context-dashboard.html"
    page.write_text(_MARKED_PAGE, encoding="utf-8")
    assert patch_review_findings(page, [_FINDING]) is True
    patched = page.read_text(encoding="utf-8")
    assert "stale content" not in patched
    assert "knowledge_tool_node" in patched
    # Markers and surrounding hand-maintained HTML survive the patch
    assert "REVIEW-FINDINGS:START" in patched
    assert "REVIEW-FINDINGS:END" in patched
    assert patched.startswith('<section id="review">')
    assert patched.rstrip().endswith("</section>")


def test_patch_review_findings_is_idempotent(tmp_path: Path) -> None:
    from tools.cartographer.dashboard import patch_review_findings

    page = tmp_path / "context-dashboard.html"
    page.write_text(_MARKED_PAGE, encoding="utf-8")
    patch_review_findings(page, [_FINDING])
    once = page.read_text(encoding="utf-8")
    patch_review_findings(page, [_FINDING])
    assert page.read_text(encoding="utf-8") == once


def test_patch_review_findings_missing_markers_leaves_file_untouched(tmp_path: Path) -> None:
    from tools.cartographer.dashboard import patch_review_findings

    page = tmp_path / "context-dashboard.html"
    original = "<section>no markers here</section>\n"
    page.write_text(original, encoding="utf-8")
    assert patch_review_findings(page, [_FINDING]) is False
    assert page.read_text(encoding="utf-8") == original


def test_patch_review_findings_missing_file(tmp_path: Path) -> None:
    from tools.cartographer.dashboard import patch_review_findings

    assert patch_review_findings(tmp_path / "absent.html", [_FINDING]) is False


# ---------------------------------------------------------------------------
# Step 4: input-token series
# ---------------------------------------------------------------------------


def test_input_tokens_p50_series_populated(tmp_path: Path) -> None:
    """input_tokens_p50 series is July-only and correctly computes median."""
    from tools.cartographer.dashboard import build_series

    store = tmp_path / "facts.db"
    upsert(
        [
            _row("j1", "2026-07-18", "session-hygiene-v1", input_tokens=1000),
            _row("j2", "2026-07-18", "session-hygiene-v1", input_tokens=3000),
            # pre-July row must be excluded
            _row("n1", "2026-06-01", "note-hook", input_tokens=999),
        ],
        store,
    )
    s = build_series("input_tokens_p50", store)
    assert s.july_only is True
    assert len(s.points) == 1
    # median of [1000, 3000] at p50 = 1000 (lower-side percentile)
    assert s.points[0].value in (1000.0, 2000.0, 3000.0)  # depends on percentile impl
    assert s.points[0].n == 2


# ---------------------------------------------------------------------------
# Step 5: per-skill economics card
# ---------------------------------------------------------------------------


def test_build_skill_economics_aggregates_correctly(tmp_path: Path) -> None:
    """build_skill_economics sums cost and counts sessions per skill."""
    import json

    from tools.cartographer.dashboard import build_skill_economics

    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "j1",
                "2026-07-18",
                "session-hygiene-v1",
                skill_costs=json.dumps({"wake": 500.0, "grow": 200.0}),
            ),
            _row(
                "j2",
                "2026-07-18",
                "session-hygiene-v1",
                skill_costs=json.dumps({"wake": 300.0, "dream": 100.0}),
            ),
            # meta row excluded
            _row(
                "m1",
                "2026-07-18",
                "session-hygiene-v1",
                skill_costs=json.dumps({"wake": 999.0}),
                is_meta=True,
            ),
        ],
        store,
    )
    totals = build_skill_economics(store)
    assert "wake" in totals
    assert totals["wake"]["cost"] == pytest.approx(800.0)
    assert totals["wake"]["n"] == 2
    assert "grow" in totals
    assert totals["grow"]["cost"] == pytest.approx(200.0)
    assert totals["grow"]["n"] == 1
    # meta row excluded
    assert totals["wake"]["cost"] == pytest.approx(800.0)


# ---------------------------------------------------------------------------
# Step 6: cost-by-context-bucket
# ---------------------------------------------------------------------------


def test_cost_bucket_pct_over150k_metric(tmp_path: Path) -> None:
    """cost_bucket_pct_over150k returns share of cost in >150k sessions."""
    from tools.cartographer.dashboard import build_series

    store = tmp_path / "facts.db"
    upsert(
        [
            _row("j1", "2026-07-18", "session-hygiene-v1", max_context=200_000, cost_units=80.0),
            _row("j2", "2026-07-18", "session-hygiene-v1", max_context=50_000, cost_units=20.0),
        ],
        store,
    )
    s = build_series("cost_bucket_pct_over150k", store)
    assert s.july_only is True
    assert len(s.points) == 1
    # 80 / (80+20) = 80%
    assert s.points[0].value == pytest.approx(80.0)


# ---------------------------------------------------------------------------
# Step 7: experiments lifecycle card / ledger parsing
# ---------------------------------------------------------------------------


def test_parse_ledger_active_rows(tmp_path: Path) -> None:
    """parse_ledger reads active tooling-ledger.md rows into Experiment objects."""
    from tools.cartographer.dashboard import parse_ledger

    ledger = tmp_path / "tooling-ledger.md"
    ledger.write_text(
        "# Tooling Ledger\n\n"
        "| Date | Change | Area | Metric | Status |\n"
        "|---|---|---|---|---|\n"
        "| 2026-07-20 | hook-experiment | workflow | `presence:foo` | hypothesis — due 08-03 |\n"
        "| 2026-07-24 | model-test | cost | `ratio:x above 80%` | verified |\n",
        encoding="utf-8",
    )
    exps = parse_ledger(ledger)
    assert len(exps) == 2
    assert exps[0].name == "hook-experiment"
    assert exps[0].metric == "presence:foo"
    assert exps[1].status == "verified"


def test_parse_ledger_malformed_row_skipped(tmp_path: Path) -> None:
    """A row without a change cell is skipped; parse never crashes."""
    from tools.cartographer.dashboard import parse_ledger

    ledger = tmp_path / "tooling-ledger.md"
    ledger.write_text(
        "| Date | Change | Area | Metric | Status |\n"
        "|---|---|---|---|---|\n"
        "|  |  | workflow | — | — |\n"  # empty cells → skipped
        "| 2026-07-20 | good-row | workflow | `presence:bar` | hypothesis |\n",
        encoding="utf-8",
    )
    exps = parse_ledger(ledger)
    assert len(exps) == 1
    assert exps[0].name == "good-row"


def test_parse_ledger_with_log(tmp_path: Path) -> None:
    """parse_ledger reads archived rows from the log file too."""
    from tools.cartographer.dashboard import parse_ledger

    ledger = tmp_path / "tooling-ledger.md"
    ledger.write_text(
        "| Date | Change | Area | Metric | Status |\n"
        "|---|---|---|---|---|\n"
        "| 2026-07-28 | active-exp | workflow | `presence:x` | hypothesis |\n",
        encoding="utf-8",
    )
    log_path = tmp_path / "tooling-ledger-log.md"
    log_path.write_text(
        "| Date | Change | Area | Verdict | Evidence |\n"
        "|---|---|---|---|---|\n"
        "| 2026-07-20 | old-exp | friction | failed | no signal |\n",
        encoding="utf-8",
    )
    exps = parse_ledger(ledger, log_path)
    names = {e.name for e in exps}
    assert "active-exp" in names
    assert "old-exp" in names


# ---------------------------------------------------------------------------
# Step 8: review tab repo grouping
# ---------------------------------------------------------------------------


def test_render_review_card_groups_by_repo(tmp_path: Path) -> None:
    """render_review_card groups findings by repo, most-recent repo first."""
    from tools.cartographer.dashboard import render_review_card

    findings = [
        {**_FINDING, "repo": "atlas", "date": "2026-07-20", "title": "atlas finding"},
        {**_FINDING, "repo": "librarian", "date": "2026-07-29", "title": "lib finding"},
        {**_FINDING, "repo": "atlas", "date": "2026-07-21", "title": "atlas finding 2"},
    ]
    card = render_review_card(findings)
    # librarian has most-recent finding — must appear before atlas
    assert card.index("librarian") < card.index("atlas")
    # both repos should appear as group headers
    assert "librarian" in card
    assert "atlas" in card


def test_render_review_card_source_field_consumed(tmp_path: Path) -> None:
    """When findings carry a source field, it appears in the repo group header."""
    from tools.cartographer.dashboard import render_review_card

    findings = [
        {**_FINDING, "source": "akira-scan", "title": "akira finding"},
    ]
    card = render_review_card(findings)
    assert "akira-scan" in card


def test_render_review_card_missing_source_tolerated(tmp_path: Path) -> None:
    """Old rows without source field still render without error."""
    from tools.cartographer.dashboard import render_review_card

    findings = [{**_FINDING}]  # _FINDING has no 'source'
    card = render_review_card(findings)
    assert "knowledge_tool_node" in card


# ---------------------------------------------------------------------------
# Step 9: friction tab regroup headers
# ---------------------------------------------------------------------------


def test_friction_tab_regroup_headers_present(tmp_path: Path) -> None:
    """render_dashboard includes the three friction group labels."""
    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "j1",
                "2026-07-18",
                "session-hygiene-v1",
                human_turns=5,
                user_interruptions=1,
                skill_costs='{"wake":100}',
                session_intent="execution",
                tool_counts='{"Bash":10}',
                tool_error_count=1,
                friction_label_count=0,
            ),
        ],
        store,
    )
    page = render_dashboard(store, funnel=None)
    assert "Prompt-eng" in page
    assert "Loop-eng" in page
    assert "Harness-eng" in page
    assert "Not yet captured" in page  # rework placeholder


# --- Hook activity card -------------------------------------------------------


def _hook_logs(tmp_path: Path, events: str, passes: str) -> tuple[Path, Path]:
    event_log = tmp_path / ".hook-log.jsonl"
    pass_log = tmp_path / ".hook-pass-log.jsonl"
    event_log.write_text(events, encoding="utf-8")
    pass_log.write_text(passes, encoding="utf-8")
    return event_log, pass_log


def test_hook_log_record_split_across_lines_is_stitched(tmp_path: Path) -> None:
    """lib.sh printf logs an unescaped newline inside `context`, splitting one
    JSON object across physical lines. Both halves belong to one record."""
    log = tmp_path / ".hook-log.jsonl"
    log.write_text(
        '{"ts":"2026-07-28T14:47:23Z","hook":"docs_hygiene","exit_code":0,'
        '"repo":"guacamayo","context":"pass: cd /tmp &&\nmake ship"}\n',
        encoding="utf-8",
    )

    events = parse_hook_log(log)

    assert len(events) == 1
    assert events[0]["hook"] == "docs_hygiene"


def test_hook_log_orphan_fragment_does_not_swallow_later_records(tmp_path: Path) -> None:
    """A `tail` cap can leave a headless fragment; it must be dropped, not
    prepended to every following line."""
    log = tmp_path / ".hook-log.jsonl"
    log.write_text(
        'make ship"}\n'
        '{"ts":"2026-07-28T15:00:00Z","hook":"branch_guard","exit_code":2,'
        '"repo":"librarian","context":"blocked"}\n',
        encoding="utf-8",
    )

    events = parse_hook_log(log)

    assert [e["hook"] for e in events] == ["branch_guard"]


def test_hook_activity_counts_blocks_and_warns_by_exit_code(tmp_path: Path) -> None:
    """exit 2 is a block; exit 0 with a message is a warn."""
    event_log, pass_log = _hook_logs(
        tmp_path,
        '{"ts":"2026-07-28T14:00:00Z","hook":"risky_git_guard","exit_code":2,"repo":"g","context":"x"}\n'
        '{"ts":"2026-07-28T14:01:00Z","hook":"risky_git_guard","exit_code":2,"repo":"g","context":"x"}\n'
        '{"ts":"2026-07-28T14:02:00Z","hook":"docs_hygiene","exit_code":0,"repo":"g","context":"x"}\n',
        '{"ts":"2026-07-28T14:03:00Z","hook":"risky_git_guard","repo":"g","context":"pass: x"}\n',
    )

    act = build_hook_activity(event_log, pass_log)

    assert (act.blocks, act.warns, act.passes) == (2, 1, 1)
    assert act.rows[0] == {"hook": "risky_git_guard", "blocks": 2, "warns": 0, "passes": 1}


def test_hook_without_pass_logging_reports_none_not_zero(tmp_path: Path) -> None:
    """Only a couple of hooks call log_pass. For the rest a pass count is
    absent data, and a rendered 0 would read as 'never passed'."""
    event_log, pass_log = _hook_logs(
        tmp_path,
        '{"ts":"2026-07-28T14:02:00Z","hook":"docs_hygiene","exit_code":0,"repo":"g","context":"x"}\n',
        "",
    )

    act = build_hook_activity(event_log, pass_log)

    assert act.rows[0]["passes"] is None
    assert "&mdash;" in render_hook_activity_card(event_log, pass_log)


def test_hook_activity_reports_hooks_that_never_fired(tmp_path: Path) -> None:
    """A guard that never fires is the interesting case -- name it explicitly."""
    event_log, pass_log = _hook_logs(
        tmp_path,
        '{"ts":"2026-07-28T14:02:00Z","hook":"docs_hygiene","exit_code":0,"repo":"g","context":"x"}\n',
        "",
    )

    act = build_hook_activity(event_log, pass_log)

    assert "secrets_scan" in act.silent
    assert "docs_hygiene" not in act.silent
    assert act.seen == 1


def test_hook_activity_empty_logs_render_placeholder(tmp_path: Path) -> None:
    """Missing logs render an empty state, never a broken card."""
    card = render_hook_activity_card(tmp_path / "absent.jsonl", tmp_path / "absent2.jsonl")

    assert "No hook fires logged yet" in card


# ---------------------------------------------------------------------------
# LIB-59: regime-band annotations — bind ledger experiments to friction charts
# ---------------------------------------------------------------------------


def test_ledger_metric_mapping_resolves_the_one_experiment() -> None:
    """The single verified MVP mapping: execution-sessions-with-skills -> the
    execution_skill_compliance_pct chart. No other signal is mapped."""
    assert LEDGER_METRIC_MAPPING == {
        "execution-sessions-with-skills": "execution_skill_compliance_pct"
    }

    exp = Experiment(
        name="Session intent classifier + compliance metric",
        metric="ratio:execution-sessions-with-skills above 80%",
        status="hypothesis — inconclusive (no compliance signals, 227 sessions) — due 08-10",
        date="2026-07-24",
    )
    mapped = _annotations_for_metric("execution_skill_compliance_pct", [exp])
    assert mapped == [exp]
    assert _annotations_for_metric("output_tokens_p50", [exp]) == []


def test_unmapped_ledger_rows_skip_silently() -> None:
    """Experiments with no LEDGER_METRIC_MAPPING entry never appear as an
    annotation for any metric -- they are dropped, not raised as an error."""
    absence_exp = Experiment(
        name="autocompact defect sweep",
        metric="absence:autocompact-defect-reports",
        status="hypothesis",
        date="2026-07-20",
    )
    presence_exp = Experiment(
        name="bash taxonomy rollout",
        metric="presence:bash-stratified-taxonomy",
        status="hypothesis",
        date="2026-07-21",
    )
    for metric in ("execution_skill_compliance_pct", "output_tokens_p50", "cost_units_p50"):
        assert _annotations_for_metric(metric, [absence_exp, presence_exp]) == []


def test_warn_unmapped_experiments_fires_for_new_signal() -> None:
    """A parsed experiment with no mapping entry surfaces as a WARNING, not a
    silent drop -- so a newly added ledger experiment is noticed, not lost."""
    import structlog

    mapped_exp = Experiment(
        name="mapped",
        metric="ratio:execution-sessions-with-skills above 80%",
        status="hypothesis",
        date="2026-07-24",
    )
    unmapped_exp = Experiment(
        name="new-experiment",
        metric="count-drop:some-brand-new-signal above 5",
        status="hypothesis",
        date="2026-07-30",
    )

    with structlog.testing.capture_logs() as cap:
        unmapped = warn_unmapped_experiments([mapped_exp, unmapped_exp])

    assert unmapped == ["some-brand-new-signal"]
    assert any(
        entry.get("event") == "dashboard.ledger_signal_unmapped"
        and entry.get("signal") == "some-brand-new-signal"
        for entry in cap
    )


def test_annotation_renders_on_execution_skill_compliance_series() -> None:
    """A mapped experiment inside a series' date range draws a vertical
    annotation line, with a hover title carrying name + metric + status."""
    points = [
        Point(date="2026-07-20", value=40.0, regime="session-hygiene-v1"),
        Point(date="2026-07-24", value=55.0, regime="session-hygiene-v1"),
        Point(date="2026-07-28", value=60.0, regime="session-hygiene-v1"),
    ]
    exp = Experiment(
        name="Session intent classifier + compliance metric",
        metric="ratio:execution-sessions-with-skills above 80%",
        status="hypothesis — inconclusive (no compliance signals, 227 sessions) — due 08-10",
        date="2026-07-24",
    )
    svg = _svg_line(points, "var(--chart-1)", experiments=[exp])

    assert "<line" in svg
    assert 'class="annotation-line"' in svg
    assert "Session intent classifier + compliance metric" in svg
    assert "ratio:execution-sessions-with-skills above 80%" in svg
    assert "inconclusive" in svg


def test_annotation_outside_series_date_range_does_not_render() -> None:
    """An experiment dated before/after the plotted series draws nothing --
    there is no x-coordinate on this chart for a date it never covers."""
    points = [
        Point(date="2026-07-20", value=40.0, regime="session-hygiene-v1"),
        Point(date="2026-07-28", value=60.0, regime="session-hygiene-v1"),
    ]
    too_early = Experiment(
        name="too-early",
        metric="ratio:execution-sessions-with-skills above 80%",
        status="hypothesis",
        date="2026-06-01",
    )
    too_late = Experiment(
        name="too-late",
        metric="ratio:execution-sessions-with-skills above 80%",
        status="hypothesis",
        date="2026-08-15",
    )
    svg = _render_annotations(points, [too_early, too_late], lambda i: float(i), plot_h=142.0)

    assert svg == ""


def test_render_dashboard_annotation_at_2026_07_24(tmp_path: Path) -> None:
    """End-to-end: the mapped ledger experiment shows up as an annotation on
    the execution_skill_compliance_pct chart in the full rendered page."""
    store = tmp_path / "facts.db"
    upsert(
        [
            _row(
                "e1",
                "2026-07-20",
                "session-hygiene-v1",
                session_intent="execution",
                skill_costs="{}",
            ),
            _row(
                "e2",
                "2026-07-24",
                "session-hygiene-v1",
                session_intent="execution",
                skill_costs='{"execute": 100}',
            ),
            _row(
                "e3",
                "2026-07-28",
                "session-hygiene-v1",
                session_intent="execution",
                skill_costs='{"execute": 100}',
            ),
        ],
        store,
    )
    experiments = [
        Experiment(
            name="Session intent classifier + compliance metric",
            metric="ratio:execution-sessions-with-skills above 80%",
            status="hypothesis — inconclusive (no compliance signals, 227 sessions) — due 08-10",
            date="2026-07-24",
        )
    ]
    html = render_dashboard(store, funnel=None, experiments=experiments)

    assert 'data-metric="execution_skill_compliance_pct"' in html
    assert 'class="annotation-line"' in html
    assert "Session intent classifier + compliance metric" in html
