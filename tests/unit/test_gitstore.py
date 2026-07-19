"""Repo-activity collection: churn filtering, bot detection, round-trip."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.cartographer.gitstore import (
    _NON_SOURCE,
    collect_commits,
    read_git_activity,
    read_prs,
    upsert_commits,
    upsert_prs,
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A tiny git repo with one source file and one vendored artifact."""
    r = tmp_path / "demo"
    r.mkdir()
    run = lambda *a: subprocess.run(a, cwd=r, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q")
    run("git", "config", "user.email", "t@example.com")
    run("git", "config", "user.name", "Tester")
    (r / "app.py").write_text("print(1)\nprint(2)\n")
    (r / "uv.lock").write_text("\n".join(f"line{i}" for i in range(500)))
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "feat: add app")
    return r


def test_churn_excludes_lockfiles(repo: Path) -> None:
    """A 500-line lockfile must not swamp a 2-line source change."""
    rows = collect_commits(repo, since="2000-01-01")
    assert len(rows) == 1
    assert rows[0]["insertions"] == 2, "lockfile lines leaked into churn"
    assert rows[0]["files_changed"] == 1


def test_commit_counted_even_when_churn_filtered(repo: Path) -> None:
    """Filtering churn must not drop the commit itself from the count."""
    rows = collect_commits(repo, since="2000-01-01")
    assert rows[0]["commits"] == 1


@pytest.mark.parametrize(
    "path",
    [
        "readings/book.pdf",
        "notebooks/explore.ipynb",
        "uv.lock",
        "app/package-lock.json",
        "wiki/.obsidian/plugins/x/main.js",
        "generative-ai/coursera-references/Course/file.py",
        "frontend/node_modules/lib/index.js",
    ],
)
def test_non_source_paths_filtered(path: str) -> None:
    assert _NON_SOURCE.search(path), f"{path} should be excluded from churn"


@pytest.mark.parametrize("path", ["src/app.py", "tools/cartographer/gitstore.py", "README.md"])
def test_source_paths_kept(path: str) -> None:
    assert not _NON_SOURCE.search(path), f"{path} should count as authored source"


def test_bot_commits_counted_separately(repo: Path) -> None:
    subprocess.run(
        [
            "git",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "Bump dep",
            "--author",
            "dependabot[bot] <b@x>",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    rows = collect_commits(repo, since="2000-01-01")
    total = sum(r["commits"] for r in rows)
    bots = sum(r["commits_bot"] for r in rows)
    assert total == 2
    assert bots == 1, "dependabot author not classified as bot"


def test_store_round_trip(tmp_path: Path) -> None:
    store = tmp_path / "facts.db"
    upsert_commits(
        [
            {
                "repo": "demo",
                "date": "2026-07-20",
                "commits": 3,
                "commits_bot": 1,
                "commits_claude_trailer": 0,
                "insertions": 40,
                "deletions": 5,
                "files_changed": 4,
            }
        ],
        store,
    )
    upsert_prs(
        [
            {
                "repo": "demo",
                "number": 7,
                "state": "MERGED",
                "created_date": "2026-07-18",
                "closed_date": "2026-07-19",
                "merged": 1,
                "additions": 10,
                "deletions": 2,
                "is_bot": 0,
            }
        ],
        store,
    )
    assert read_git_activity(store)[0]["commits"] == 3
    assert read_prs(store)[0]["merged"] == 1


def test_upsert_is_idempotent(tmp_path: Path) -> None:
    """Re-running collection replaces rows rather than double-counting."""
    store = tmp_path / "facts.db"
    row = {
        "repo": "demo",
        "date": "2026-07-20",
        "commits": 3,
        "commits_bot": 0,
        "commits_claude_trailer": 0,
        "insertions": 40,
        "deletions": 5,
        "files_changed": 4,
    }
    upsert_commits([row], store)
    upsert_commits([row], store)
    assert len(read_git_activity(store)) == 1


def test_missing_store_reads_empty(tmp_path: Path) -> None:
    assert read_git_activity(tmp_path / "nope.db") == []
