"""scrape_repos must not re-copy what scrape_claude_docs already puts in data/raw/claude-docs/.

Both scrapers used to take .claude/skills, .claude/docs, docs/ and .agents/ from every
repo, so each of those files landed in data/raw/ twice and was compiled twice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core import scrape_repos
from core.scrape_repos import CLAUDE_DOCS_GLOBS, EXTRACT_GLOBS, scrape_repo


def _make_repo(root: Path) -> Path:
    for rel in ("CLAUDE.md", ".claude/skills/x/SKILL.md", "docs/guide.md"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(f"# {rel}\n")
    return root


def test_glob_sets_are_disjoint() -> None:
    assert not set(EXTRACT_GLOBS) & set(CLAUDE_DOCS_GLOBS)


def test_top_level_repo_skips_claude_docs_globs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scrape_repos, "WORKSPACE_DIR", tmp_path)
    repo = _make_repo(tmp_path / "proj")
    scrape_repo(repo, tmp_path / "out")
    assert sorted(p.name for p in (tmp_path / "out" / "proj").iterdir()) == ["CLAUDE.md"]


def test_nested_repo_keeps_claude_docs_globs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scrape_repos, "WORKSPACE_DIR", tmp_path)
    repo = _make_repo(tmp_path / "group" / "proj")
    scrape_repo(repo, tmp_path / "out")
    assert len(list((tmp_path / "out" / "proj").iterdir())) == 3


def test_skipped_project_keeps_claude_docs_globs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scrape_repos, "WORKSPACE_DIR", tmp_path)
    repo = _make_repo(tmp_path / "librarian")
    scrape_repo(repo, tmp_path / "out")
    assert len(list((tmp_path / "out" / "librarian").iterdir())) == 3
