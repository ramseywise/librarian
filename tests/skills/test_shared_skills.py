"""Skills shared with learn-ai-engineering are rendered from `.claude/skills/_shared/` templates.

The in-repo copies must match their render. The sibling checkout is compared only when present, so CI
(which has none) checks this repo and skips the other with a message.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from librarian.tools import skillsync

ROOT = skillsync.ROOT


@pytest.mark.parametrize("skill", skillsync.SKILLS)
def test_own_copy_matches_template(skill: str) -> None:
    on_disk = (ROOT / ".claude" / "skills" / skill / "SKILL.md").read_text()
    assert on_disk == skillsync.expected("librarian", skill), (
        f"{skill} drifted from {skillsync.SHARED}/{skill}.md: edit the template, run `make skills-sync`"
    )


@pytest.mark.parametrize("skill", skillsync.SKILLS)
@pytest.mark.parametrize("repo", skillsync.REPOS)
def test_render_is_complete(skill: str, repo: str) -> None:
    text = skillsync.expected(repo, skill)
    assert not re.search(r"\{\{[#/A-Za-z_]*\}?\}", text)
    assert "Generated from" in text


def test_repo_specific_text_stays_in_its_repo() -> None:
    lib = skillsync.expected("librarian", "curriculum")
    lae = skillsync.expected("lae", "curriculum")
    assert "uv run librarian courses check curriculum" in lib
    assert "scripts/curriculum_map.py" not in lib
    assert "scripts/curriculum_map.py" in lae
    assert "librarian courses check" not in lae


def test_block_errors() -> None:
    bad = "---\nname: x\n---\n{{#lae}}\nbody\n"
    with pytest.raises(ValueError, match="never closed"):
        skillsync.render(bad, "lae", "x")
    with pytest.raises(ValueError, match="no value"):
        skillsync.render("---\nname: x\n---\n{{NOPE}}\n", "lae", "x")


def test_sibling_copy_matches_when_present(capsys: pytest.CaptureFixture[str]) -> None:
    sibling = skillsync.sibling_dir(None)
    if not (sibling / ".claude" / "skills").is_dir():
        pytest.skip(f"no learn-ai-engineering checkout at {sibling}; its copies were not compared")
    assert skillsync.check(sibling, quiet=True) == 0, capsys.readouterr().out


def test_check_skips_missing_sibling(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert skillsync.check(tmp_path / "absent", quiet=True) == 0
    assert "SKIP lae" in capsys.readouterr().out
