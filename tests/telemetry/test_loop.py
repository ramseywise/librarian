"""The loop tab must agree with the hook about what a valid Status is.

`loop.py` re-implements the plan-doc `Status:` parser that
`~/.claude/hooks/plan_status_validate.sh` enforces on Write/Edit. Two parsers over one
format drift silently: the tab would report drift the hook does not enforce, or hide
drift it does. The first test class pins the shapes the hook accepts and rejects.

The rest pin the drift rules themselves — both directions, so a detector that fires on
everything (or nothing) cannot go green. See ramseywise/librarian#91.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.cartographer import loop


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


# --- status parsing: must match plan_status_validate.sh -------------------------------


def test_plain_status_parses(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Status: COMPLETE\n"), "repo")
    assert doc.status == "COMPLETE"
    assert doc.suffix == ""
    assert doc.conforming


def test_bare_status_key_with_no_value_is_non_conforming(tmp_path: Path) -> None:
    """`Status:` with nothing after it is rejected by the hook, unlike a missing line."""
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Status:\n"), "repo")
    assert doc.has_status
    assert not doc.conforming


def test_bold_key_form_parses(tmp_path: Path) -> None:
    """`**Status**:` occurs in the corpus and the hook accepts it."""
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "  **Status**:  READY\n"), "repo")
    assert doc.status == "READY"
    assert doc.conforming


def test_trailing_prose_is_non_conforming(tmp_path: Path) -> None:
    """The live failure shape: a token followed by an explanation."""
    doc = loop.parse_plan_doc(
        _write(tmp_path, "a.md", "Status: IN PROGRESS -> EXECUTED when steps land\n"), "repo"
    )
    assert doc.status == "IN"
    assert not doc.conforming


def test_unknown_token_is_non_conforming(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Status: DONE\n"), "repo")
    assert not doc.conforming


def test_missing_status_line_is_not_flagged(tmp_path: Path) -> None:
    """The hook exits 0 on a doc with no Status: line — the tab must not be stricter."""
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "# Plan\n\nSome text.\n"), "repo")
    assert doc.status == ""
    assert doc.conforming


def test_first_status_line_wins(tmp_path: Path) -> None:
    """Section-level `Status:` lines deeper in a doc are not the doc's status.

    ai-project-template's mirror-redesign plan carries `Status: EXECUTED` on line 3 and
    `Status: IN PROGRESS -> ...` on line 882. The hook reads the first and passes it; a
    parser reading the last would report a doc the hook accepts as broken.
    """
    doc = loop.parse_plan_doc(
        _write(tmp_path, "a.md", "Status: READY\n\nStatus: COMPLETE\n"), "repo"
    )
    assert doc.status == "READY"


# --- companion fields: the hook's other two rules ---------------------------------------


def test_executed_without_review_is_non_conforming(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Status: EXECUTED\n"), "repo")
    assert not doc.conforming
    assert "Review" in doc.problem


def test_executed_with_review_is_conforming(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(
        _write(tmp_path, "a.md", "Status: EXECUTED\nReview: passed\n"), "repo"
    )
    assert doc.conforming


def test_superseded_without_superseded_by_is_non_conforming(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Status: SUPERSEDED\n"), "repo")
    assert not doc.conforming
    assert "Superseded-by" in doc.problem


def test_superseded_with_superseded_by_is_conforming(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(
        _write(tmp_path, "a.md", "Status: SUPERSEDED\n**Superseded-by**: other.md\n"), "repo"
    )
    assert doc.conforming


def test_other_states_need_no_companion_field(tmp_path: Path) -> None:
    """Only EXECUTED and SUPERSEDED carry a companion requirement."""
    for state in ("RESEARCH", "PLANNED", "READY", "IN_PROGRESS", "COMPLETE"):
        doc = loop.parse_plan_doc(_write(tmp_path, "a.md", f"Status: {state}\n"), "repo")
        assert doc.conforming, state


# --- differential: the parser and the hook must agree doc-for-doc ------------------------


def test_agrees_with_the_hook_on_every_shape(tmp_path: Path) -> None:
    """Run the real hook's validator against the same docs and compare verdicts.

    Two parsers over one format drift silently. This executes
    `~/.claude/hooks/plan_status_validate.sh` directly, so a change to either side that
    is not mirrored fails here rather than showing up as phantom drift on the dashboard.
    Skipped when the hook is not installed (CI, a fresh clone).
    """
    hook = Path.home() / ".claude" / "hooks" / "plan_status_validate.sh"
    if not hook.exists():
        pytest.skip(f"hook not installed at {hook}")

    bodies = [
        "Status: EXECUTED\nReview: passed\n",
        "Status: EXECUTED\n",
        "Status: SUPERSEDED\n",
        "Status: SUPERSEDED\nSuperseded-by: x.md\n",
        "  **Status**:  READY\n",
        "Status: IN PROGRESS -> EXECUTED when steps land\n",
        "Status: DONE\n",
        "# Plan\n\nNo status here.\n",
        "Status: READY\n\nStatus: COMPLETE\n",
        "Status:\n",
    ]

    # The hook only fires on paths matching /.claude/docs/plans/*.md.
    plans = tmp_path / ".claude" / "docs" / "plans"
    plans.mkdir(parents=True)

    for i, body in enumerate(bodies):
        path = plans / f"case{i}.md"
        path.write_text(body, encoding="utf-8")
        proc = subprocess.run(
            [str(hook)],
            input=json.dumps({"tool_input": {"file_path": str(path)}}),
            capture_output=True,
            text=True,
            check=False,
        )
        hook_accepts = proc.returncode == 0
        assert loop.parse_plan_doc(path, "repo").conforming is hook_accepts, (
            f"disagreement on {body!r}: hook exit={proc.returncode}, "
            f"parser conforming={loop.parse_plan_doc(path, 'repo').conforming}"
        )


# --- issue extraction ------------------------------------------------------------------


def test_issue_field_wins_over_filename(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "LIB-99-x.md", "Issue: #42\n"), "repo")
    assert doc.issue == 42


def test_qualified_issue_ref_parses(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "a.md", "Issue: ramseywise/librarian#42\n"), "repo")
    assert doc.issue == 42


def test_filename_fallback(tmp_path: Path) -> None:
    doc = loop.parse_plan_doc(_write(tmp_path, "LIB-91-loop-tab.md", "# Plan\n"), "repo")
    assert doc.issue == 91


def test_undatable_doc_has_no_issue(tmp_path: Path) -> None:
    """Most docs do not join. That must read as no-issue, not as issue 0."""
    doc = loop.parse_plan_doc(_write(tmp_path, "2026-08-02-notes.md", "# Plan\n"), "repo")
    assert doc.issue is None


# --- collection scope -------------------------------------------------------------------


def test_collect_scans_only_claude_docs_plans(tmp_path: Path) -> None:
    """Ingested snapshots elsewhere in a repo must not be counted twice."""
    live = tmp_path / "myrepo" / ".claude" / "docs" / "plans"
    live.mkdir(parents=True)
    (live / "p.md").write_text("Status: READY\n", encoding="utf-8")

    ingested = tmp_path / "librarian" / "data" / "raw" / "claude-docs" / "plans"
    ingested.mkdir(parents=True)
    (ingested / "p.md").write_text("Status: PLANNED\n", encoding="utf-8")

    docs = loop.collect_plan_docs(tmp_path)
    assert [d.status for d in docs] == ["READY"]


def test_collect_missing_workspace_is_empty(tmp_path: Path) -> None:
    assert loop.collect_plan_docs(tmp_path / "nope") == []


# --- counts ------------------------------------------------------------------------------


def test_status_counts_include_zeros() -> None:
    counts = loop.status_counts([])
    assert set(counts) == set(loop.CANONICAL_STATUSES)
    assert all(v == 0 for v in counts.values())


def test_label_counts_exclude_closed_issues() -> None:
    issues = [
        {"state": "OPEN", "labels": "ready,bug"},
        {"state": "CLOSED", "labels": "ready"},
    ]
    assert loop.label_counts(issues)["ready"] == 1


def test_label_counts_multi_label_issue_counts_once_per_label() -> None:
    issues = [{"state": "OPEN", "labels": "ready,in-progress"}]
    counts = loop.label_counts(issues)
    assert counts["ready"] == 1
    assert counts["in-progress"] == 1


# --- drift: both directions ---------------------------------------------------------------


def _doc(status: str, issue: int | None = 1, repo: str = "r") -> loop.PlanDoc:
    return loop.PlanDoc(
        path=f"{repo}/p.md", repo=repo, status=status, suffix="", issue=issue, has_status=True
    )


def _issue(state: str, labels: str = "", number: int = 1, repo: str = "r") -> dict:
    return {"repo": repo, "number": number, "state": state, "labels": labels}


def test_terminal_plan_with_open_issue_is_drift() -> None:
    drifts = loop.detect_drift([_doc("EXECUTED")], [_issue("OPEN", "in-review")])
    assert len(drifts) == 1
    assert "still open" in drifts[0].reason


def test_terminal_plan_with_closed_issue_is_clean() -> None:
    assert loop.detect_drift([_doc("EXECUTED")], [_issue("CLOSED", "in-review")]) == []


def test_non_terminal_plan_with_closed_issue_is_drift() -> None:
    """The corpus's dominant shape: the issue got closed, the plan doc did not move."""
    drifts = loop.detect_drift([_doc("PLANNED")], [_issue("CLOSED", "ready")])
    assert len(drifts) == 1
    assert "still PLANNED" in drifts[0].reason


def test_non_terminal_plan_with_open_issue_is_clean() -> None:
    assert loop.detect_drift([_doc("PLANNED")], [_issue("OPEN", "backlog")]) == []


def test_statusless_doc_with_closed_issue_is_not_drift() -> None:
    """No Status: line means nothing to disagree with — the hook allows it."""
    assert loop.detect_drift([_doc("")], [_issue("CLOSED")]) == []


def test_in_progress_plan_with_wrong_label_is_drift() -> None:
    drifts = loop.detect_drift([_doc("IN_PROGRESS")], [_issue("OPEN", "backlog")])
    assert len(drifts) == 1
    assert drifts[0].label == "backlog"


def test_in_progress_plan_with_in_progress_label_is_clean() -> None:
    assert loop.detect_drift([_doc("IN_PROGRESS")], [_issue("OPEN", "in-progress")]) == []


def test_in_progress_plan_with_in_review_label_is_clean() -> None:
    assert loop.detect_drift([_doc("IN_PROGRESS")], [_issue("OPEN", "in-review")]) == []


def test_unjoinable_doc_is_not_drift() -> None:
    """No issue reference means unreported, never a disagreement."""
    assert loop.detect_drift([_doc("EXECUTED", issue=None)], [_issue("OPEN")]) == []


def test_issue_in_another_repo_does_not_join() -> None:
    """Issue numbers collide across repos; the join key is (repo, number)."""
    docs = [_doc("EXECUTED", issue=1, repo="alpha")]
    assert loop.detect_drift(docs, [_issue("OPEN", number=1, repo="beta")]) == []


def test_non_conforming_selects_only_bad_docs() -> None:
    good = _doc("READY")
    bad = loop.PlanDoc(
        path="r/b.md", repo="r", status="IN", suffix="PROGRESS", issue=None, has_status=True
    )
    assert loop.non_conforming([good, bad]) == [bad]
