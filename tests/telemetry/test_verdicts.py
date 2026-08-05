from __future__ import annotations

import json
from typing import Any

import pytest

from tools.cartographer.verdicts import (
    VERDICT_CONFIRMED,
    VERDICT_FAILED,
    VERDICT_INCONCLUSIVE,
    VERDICT_TRENDING,
    MetricClause,
    Verdict,
    parse_metric,
    score_clause,
    score_metric,
)


def _row(**overrides: object) -> dict[str, Any]:
    row: dict[str, Any] = {
        "session_id": "s1",
        "bash_antipatterns": None,
        "output_tokens": 100,
        "session_intent": "execution",
        "skill_costs": "{}",
        "max_context": None,
        "cost_units": 0.0,
        "models": "{}",
    }
    row.update(overrides)
    return row


# --- parse_metric -----------------------------------------------------------


def test_parse_metric_empty_returns_no_clauses() -> None:
    assert parse_metric("") == []
    assert parse_metric("—") == []
    assert parse_metric("-") == []


def test_parse_metric_single_clause_absence() -> None:
    clauses = parse_metric("absence:bash-antipatterns")
    assert len(clauses) == 1
    c = clauses[0]
    assert c.metric_type == "absence"
    assert c.signal == "bash-antipatterns"
    assert c.comparator is None
    assert c.threshold is None


def test_parse_metric_ratio_with_percent_threshold() -> None:
    clauses = parse_metric("ratio:execution-sessions-with-skills above 80%")
    assert len(clauses) == 1
    c = clauses[0]
    assert c.metric_type == "ratio"
    assert c.signal == "execution-sessions-with-skills"
    assert c.comparator == "above"
    assert c.threshold == 80.0
    assert c.is_percent is True


def test_parse_metric_fraction_threshold_normalized_to_percent() -> None:
    clauses = parse_metric("ratio:portfolio-avg-score above 12/18")
    assert len(clauses) == 1
    c = clauses[0]
    assert c.threshold == pytest.approx(66.67, abs=0.01)
    assert c.is_percent is True


def test_parse_metric_count_drop_below_threshold() -> None:
    clauses = parse_metric("count-drop:p90-output-tokens below 50000")
    assert len(clauses) == 1
    c = clauses[0]
    assert c.metric_type == "count-drop"
    assert c.comparator == "below"
    assert c.threshold == 50000.0


def test_parse_metric_multi_clause_joined_by_plus() -> None:
    clauses = parse_metric(
        "absence:bash-antipatterns + ratio:execution-sessions-with-skills above 80%"
    )
    assert len(clauses) == 2
    assert clauses[0].metric_type == "absence"
    assert clauses[1].metric_type == "ratio"
    assert clauses[1].threshold == 80.0


def test_parse_metric_unregistered_signal_still_parses() -> None:
    # Parsing is independent of the signal registry -- scoring is where
    # unregistered signals get an inconclusive verdict, not parsing.
    clauses = parse_metric("presence:worktree-commit-blocks")
    assert len(clauses) == 1
    assert clauses[0].signal == "worktree-commit-blocks"


# --- absence -----------------------------------------------------------------


def test_absence_confirmed_when_registered_signal_is_zero() -> None:
    rows = [_row(bash_antipatterns=0) for _ in range(5)]
    v = score_metric("absence:bash-antipatterns", rows)
    assert v.verdict == VERDICT_CONFIRMED


def test_absence_failed_when_registered_signal_is_positive() -> None:
    rows = [_row(bash_antipatterns=2) for _ in range(5)]
    v = score_metric("absence:bash-antipatterns", rows)
    assert v.verdict == VERDICT_FAILED


def test_absence_inconclusive_when_signal_unregistered() -> None:
    rows = [_row() for _ in range(5)]
    v = score_metric("absence:flat-sibling-issues-without-parent-link", rows)
    assert v.verdict == VERDICT_INCONCLUSIVE
    assert "no factstore signal registered" in v.evidence


def test_absence_inconclusive_when_no_data() -> None:
    rows = [_row(bash_antipatterns=None) for _ in range(5)]
    v = score_metric("absence:bash-antipatterns", rows)
    assert v.verdict == VERDICT_INCONCLUSIVE


def test_absence_inconclusive_on_empty_rows() -> None:
    v = score_metric("absence:bash-antipatterns", [])
    assert v.verdict == VERDICT_INCONCLUSIVE


# --- presence ------------------------------------------------------------


def test_presence_confirmed_when_registered_signal_positive() -> None:
    rows = [_row(output_tokens=1000) for _ in range(3)]
    v = score_metric("presence:p90-output-tokens", rows)
    assert v.verdict == VERDICT_CONFIRMED


def test_presence_failed_when_registered_signal_zero() -> None:
    rows = [_row(output_tokens=0) for _ in range(3)]
    v = score_metric("presence:p90-output-tokens", rows)
    assert v.verdict == VERDICT_FAILED


def test_presence_inconclusive_when_signal_unregistered() -> None:
    v = score_metric("presence:cross-repo-prefix-mismatch-branches", [_row()])
    assert v.verdict == VERDICT_INCONCLUSIVE


# --- count-drop ----------------------------------------------------------


def test_count_drop_confirmed_when_threshold_met() -> None:
    rows = [_row(output_tokens=1000) for _ in range(10)]
    v = score_metric("count-drop:p90-output-tokens below 50000", rows)
    assert v.verdict == VERDICT_CONFIRMED


def test_count_drop_trending_never_failed_when_threshold_not_met() -> None:
    rows = [_row(output_tokens=100_000) for _ in range(10)]
    v = score_metric("count-drop:p90-output-tokens below 50000", rows)
    assert v.verdict == VERDICT_TRENDING


def test_count_drop_inconclusive_when_no_threshold_parsed() -> None:
    rows = [_row(output_tokens=100) for _ in range(3)]
    v = score_metric("count-drop:p90-output-tokens", rows)
    assert v.verdict == VERDICT_INCONCLUSIVE


def test_count_drop_inconclusive_when_unregistered() -> None:
    v = score_metric("count-drop:some-unknown-signal below 10", [_row()])
    assert v.verdict == VERDICT_INCONCLUSIVE


# --- ratio -----------------------------------------------------------------


def _exec_rows(n_with_skills: int, n_without: int) -> list[dict[str, Any]]:
    rows = [
        _row(session_intent="execution", skill_costs=json.dumps({"code-review": 1.0}))
        for _ in range(n_with_skills)
    ]
    rows += [_row(session_intent="execution", skill_costs="{}") for _ in range(n_without)]
    return rows


def test_ratio_confirmed_when_above_threshold() -> None:
    rows = _exec_rows(n_with_skills=9, n_without=1)  # 90%
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_CONFIRMED


def test_ratio_trending_when_within_close_band() -> None:
    rows = _exec_rows(n_with_skills=7, n_without=3)  # 70%, 10pt below 80%
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_TRENDING


def test_ratio_failed_when_far_from_threshold() -> None:
    rows = _exec_rows(n_with_skills=1, n_without=9)  # 10%, 70pt below 80%
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_FAILED


def test_ratio_inconclusive_when_no_exec_sessions() -> None:
    rows = [_row(session_intent="planning") for _ in range(3)]
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_INCONCLUSIVE


def test_ratio_boundary_exact_threshold_is_not_yet_confirmed() -> None:
    """The comparator is strict (`>`/`<`), so landing exactly on the threshold
    does not confirm -- it's a 0pt gap, well within the trending band."""
    rows = _exec_rows(n_with_skills=8, n_without=2)  # exactly 80%
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_TRENDING


def test_ratio_boundary_just_above_threshold_confirms() -> None:
    rows = _exec_rows(n_with_skills=9, n_without=1)  # 90%, strictly above 80%
    v = score_metric("ratio:execution-sessions-with-skills above 80%", rows)
    assert v.verdict == VERDICT_CONFIRMED


# --- combination across multi-clause rows ---------------------------------


def test_multi_clause_pessimistic_combination_worst_wins() -> None:
    rows = [_row(bash_antipatterns=3, output_tokens=1000) for _ in range(5)]
    # absence fails (antipatterns present); count-drop confirms -> combined = failed
    v = score_metric("absence:bash-antipatterns + count-drop:p90-output-tokens below 50000", rows)
    assert v.verdict == VERDICT_FAILED
    assert "bash-antipatterns" in v.evidence
    assert "p90-output-tokens" in v.evidence


# --- score_metric top-level fallbacks -------------------------------------


def test_score_metric_unparseable_is_inconclusive() -> None:
    v = score_metric("—", [_row()])
    assert v.verdict == VERDICT_INCONCLUSIVE
    assert v.evidence == "no typed metric to score"


def test_score_clause_dispatches_by_metric_type() -> None:
    clause = MetricClause(
        metric_type="absence",
        signal="bash-antipatterns",
        comparator=None,
        threshold=None,
        is_percent=False,
        raw="absence:bash-antipatterns",
    )
    v = score_clause(clause, [_row(bash_antipatterns=0)])
    assert isinstance(v, Verdict)
    assert v.verdict == VERDICT_CONFIRMED
