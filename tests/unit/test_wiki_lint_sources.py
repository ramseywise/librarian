"""Evidence for Buyi "Wiki provenance is traceable" + the Jianyi 5-field schema.

Cures the BY-4 debt record: wiki-lint.sh checked title/tags/summary/updated but
not sources:, and nothing validated that source paths resolve. The hook runs
from the repo root, so source paths are checked relative to cwd.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "wiki-lint.sh"

PAGE = """---
title: Test Page
tags: [rag, concept]
summary: A page used by the wiki-lint evidence tests
updated: 2026-07-20
{sources}
---

# Test Page

Body referencing nothing.
"""


def run_hook(page: Path) -> tuple[int, str]:
    """Run wiki-lint.sh from the repo root against a wiki-relative page path."""
    proc = subprocess.run(
        ["bash", str(HOOK)],
        cwd=REPO,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "CLAUDE_TOOL_INPUT_FILE_PATH": str(page)},
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stderr


@pytest.fixture()
def page(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A scratch page under the real wiki/ — the hook only lints wiki/* paths."""
    scratch = REPO / "wiki" / "_lint_test_scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    target = scratch / "provenance-fixture.md"
    yield target
    target.unlink(missing_ok=True)
    scratch.rmdir()


def test_missing_sources_field_is_flagged(page: Path) -> None:
    page.write_text(PAGE.format(sources="").replace("\n\n---", "\n---"))
    code, err = run_hook(page.relative_to(REPO))
    assert code == 0, "hook is advisory — must never block the write"
    assert "missing frontmatter field 'sources:'" in err


def test_unresolvable_source_path_is_flagged(page: Path) -> None:
    page.write_text(PAGE.format(sources="sources:\n  - raw/notion/does-not-exist-9f3a.md"))
    _, err = run_hook(page.relative_to(REPO))
    assert "unresolvable source 'raw/notion/does-not-exist-9f3a.md'" in err


def test_resolvable_source_path_passes(page: Path) -> None:
    # CLAUDE.md is a real repo file — stands in for a real raw/ source
    page.write_text(PAGE.format(sources="sources:\n  - CLAUDE.md"))
    _, err = run_hook(page.relative_to(REPO))
    assert "unresolvable source" not in err
    assert "missing frontmatter field 'sources:'" not in err


def test_url_source_is_accepted(page: Path) -> None:
    page.write_text(PAGE.format(sources="sources:\n  - https://example.com/article"))
    _, err = run_hook(page.relative_to(REPO))
    assert "unresolvable source" not in err


def test_hook_exits_zero_even_when_flagging(page: Path) -> None:
    """Regression: `grep -oP` is unsupported by BSD grep, and under `set -e` its
    failure aborted the hook (exit 2) before the orphan check ever ran."""
    page.write_text(PAGE.format(sources="sources:\n  - CLAUDE.md"))
    code, _ = run_hook(page.relative_to(REPO))
    assert code == 0


def test_wikilink_and_orphan_checks_still_run(page: Path) -> None:
    """The orphan check sits after the wikilink loop — if either aborts, no
    ORPHAN line is emitted for a page nothing links to."""
    page.write_text(PAGE.format(sources="sources:\n  - CLAUDE.md"))
    _, err = run_hook(page.relative_to(REPO))
    assert "ORPHAN" in err


def test_empty_inline_sources_list_is_flagged(page: Path) -> None:
    page.write_text(PAGE.format(sources="sources: []"))
    _, err = run_hook(page.relative_to(REPO))
    assert "'sources:' is empty" in err
