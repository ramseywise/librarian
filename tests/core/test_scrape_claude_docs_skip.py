"""scrape_claude_docs leaves out the projects in SKIP_PROJECTS, spell's unlicensed docs among them."""

from __future__ import annotations

from pathlib import Path

from librarian.ingest.scrape_claude_docs import SKIP_PROJECTS, scrape_projects


def _project(workspace: Path, name: str) -> None:
    for rel in (".claude/skills/x/SKILL.md", "docs/guide.md"):
        path = workspace / name / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name} {rel}\n")


def test_spell_and_librarian_are_skipped(tmp_path: Path) -> None:
    assert {"librarian", "spell"} <= SKIP_PROJECTS
    workspace, out = tmp_path / "workspace", tmp_path / "out"
    for name in ("spell", "librarian", "kiez"):
        _project(workspace, name)
    written = scrape_projects(workspace, out, dry_run=False)
    assert written == 2
    assert {p.name for p in out.iterdir()} == {"kiez"}
