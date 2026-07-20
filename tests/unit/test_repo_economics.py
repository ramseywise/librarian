"""Repo-level cost attribution: the session -> repo join and its two snags.

The join these tests guard replaced a broken one. `sessions.project` holds the
*launch* directory, which is the bare workspace root for 86% of July sessions, so
`basename(project) == repo` matched 20% of spend and left major repos with cost
but no commits (and vice versa). Attribution now comes from `session_repos`,
derived from every `cwd` in the transcript.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer.dashboard import (
    JULY_BOUNDARY,
    weekly_commits_by_repo,
    weekly_cost_by_repo,
)
from tools.cartographer.factstore import ALL_COLUMNS, upsert
from tools.cartographer.gitstore import upsert_commits
from tools.cartographer.parser import _session_repos


def _session(
    session_id: str, date: str, cost: float, repos: dict[str, int], **kw: object
) -> dict[str, Any]:
    row = {
        "session_id": session_id,
        "date": date,
        "project": kw.get("project", "/Users/wiseer/workspace"),
        "era": kw.get("era", "jsonl"),
        "regime": "telemetry-v1",
        "source_path": "test",
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "cost_units": cost,
        "compacted": False,
        "is_meta": kw.get("is_meta", False),
        "session_repos": json.dumps(repos),
    }
    return {col: row.get(col) for col in ALL_COLUMNS}


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "facts.db"


# --- parser: resolving repos from cwd ---------------------------------------


def test_session_repos_counts_every_cwd_not_just_the_first() -> None:
    """The launch dir is the workspace root; the repo shows up in later records."""
    records = [
        {"cwd": "/Users/wiseer/workspace"},
        {"cwd": "/Users/wiseer/workspace/librarian"},
        {"cwd": "/Users/wiseer/workspace/librarian/app"},
    ]
    assert _session_repos(records) == {"librarian": 2}


def test_session_repos_returns_full_distribution_for_multi_repo_sessions() -> None:
    """22% of sessions touch >1 repo -- the caller needs the split, not a winner."""
    records = [{"cwd": "/Users/wiseer/workspace/librarian"}] * 3 + [
        {"cwd": "/Users/wiseer/workspace/atlas"}
    ]
    assert _session_repos(records) == {"librarian": 3, "atlas": 1}


def test_session_repos_empty_when_session_never_leaves_root() -> None:
    """SNAG 2: workspace-root-only sessions are real, and name no repo."""
    assert _session_repos([{"cwd": "/Users/wiseer/workspace"}] * 5) == {}


def test_session_repos_ignores_paths_outside_the_workspace() -> None:
    records = [{"cwd": "/Users/wiseer/.claude/skills"}, {"cwd": "/tmp"}, {}]
    assert _session_repos(records) == {}


# --- SNAG 1: note-era rows must not enter the join --------------------------


def test_note_era_rows_are_excluded_by_the_july_boundary(store: Path) -> None:
    """Dirty project values ("Workspace", "null") predate JULY_BOUNDARY.

    They are excluded by date, not by name-cleaning, so a new dirty value cannot
    leak in later.
    """
    upsert(
        [
            _session("note1", "2026-05-01", 900.0, {}, project="Workspace", era="note"),
            _session("note2", "2026-06-01", 900.0, {}, project="null", era="note"),
            _session("jul", "2026-07-16", 100.0, {"librarian": 1}),
        ],
        store,
    )
    weekly, attributed, total = weekly_cost_by_repo(store)

    assert set(weekly) == {"librarian"}
    # Note-era cost is outside the window entirely -- not merely unattributed.
    assert total == pytest.approx(100.0)
    assert attributed == pytest.approx(100.0)


def test_no_bucket_predates_the_july_boundary(store: Path) -> None:
    upsert([_session("s", "2026-07-01", 50.0, {"librarian": 1})], store)
    weekly, _, total = weekly_cost_by_repo(store)
    assert weekly == {}
    assert total == 0.0


# --- SNAG 2: workspace-root sessions are dropped, and counted ---------------


def test_root_only_sessions_are_excluded_but_reported_in_the_total(store: Path) -> None:
    """The panel states its own coverage: attributed < total is the signal."""
    upsert(
        [
            _session("root", "2026-07-16", 800.0, {}),
            _session("repo", "2026-07-16", 200.0, {"librarian": 1}),
        ],
        store,
    )
    weekly, attributed, total = weekly_cost_by_repo(store)

    assert sum(weekly["librarian"].values()) == pytest.approx(200.0)
    assert attributed == pytest.approx(200.0)
    assert total == pytest.approx(1000.0)
    # 80% unattributed must remain visible rather than silently vanishing.
    assert total - attributed == pytest.approx(800.0)


def test_root_cost_is_never_assigned_to_a_repo(store: Path) -> None:
    """Bucketing root sessions into any repo would be fabrication."""
    upsert([_session("root", "2026-07-16", 500.0, {})], store)
    weekly, attributed, _ = weekly_cost_by_repo(store)
    assert weekly == {}
    assert attributed == 0.0


# --- cost splitting ---------------------------------------------------------


def test_multi_repo_cost_splits_proportionally_to_records(store: Path) -> None:
    upsert([_session("s", "2026-07-16", 100.0, {"librarian": 3, "atlas": 1})], store)
    weekly, attributed, _ = weekly_cost_by_repo(store)

    assert sum(weekly["librarian"].values()) == pytest.approx(75.0)
    assert sum(weekly["atlas"].values()) == pytest.approx(25.0)
    # Splitting conserves total spend -- no double-counting across repos.
    assert attributed == pytest.approx(100.0)


def test_meta_sessions_are_excluded(store: Path) -> None:
    upsert([_session("m", "2026-07-16", 400.0, {"librarian": 1}, is_meta=True)], store)
    weekly, _, total = weekly_cost_by_repo(store)
    assert weekly == {}
    assert total == 0.0


def test_cost_buckets_by_iso_week(store: Path) -> None:
    upsert(
        [
            _session("a", "2026-07-16", 10.0, {"librarian": 1}),
            _session("b", "2026-07-17", 10.0, {"librarian": 1}),
            _session("c", "2026-07-27", 10.0, {"librarian": 1}),
        ],
        store,
    )
    weekly, _, _ = weekly_cost_by_repo(store)
    assert len(weekly["librarian"]) == 2


# --- commits side -----------------------------------------------------------


def _git_row(repo: str, date: str, commits: int, bot: int = 0) -> dict[str, Any]:
    return {
        "repo": repo,
        "date": date,
        "commits": commits,
        "commits_bot": bot,
        "commits_claude_trailer": 0,
        "insertions": 0,
        "deletions": 0,
        "files_changed": 0,
    }


def test_commits_exclude_bots_and_predate_boundary(store: Path) -> None:
    sqlite3.connect(store).close()
    upsert_commits(
        [
            _git_row("librarian", "2026-07-16", 10, bot=4),
            _git_row("librarian", "2026-07-01", 99),
        ],
        store,
    )
    weekly = weekly_commits_by_repo(store)
    assert sum(weekly["librarian"].values()) == 6


def test_repo_with_cost_and_no_commits_is_a_finding_not_a_join_failure(store: Path) -> None:
    """dssg really did burn spend with nothing landed -- the panel must show it."""
    upsert([_session("s", "2026-07-16", 300.0, {"dssg": 1})], store)
    upsert_commits([_git_row("librarian", "2026-07-16", 5)], store)

    cost, _, _ = weekly_cost_by_repo(store)
    commits = weekly_commits_by_repo(store)

    assert sum(cost["dssg"].values()) == pytest.approx(300.0)
    assert "dssg" not in commits


def test_both_series_share_the_july_boundary(store: Path) -> None:
    """The two panels sit on one x-axis; a mismatched window would misalign them."""
    assert JULY_BOUNDARY == "2026-07-15"
