"""core/import_courses.py — MDX/notebook conversion and the idempotent sync contract.

The sync contract is what lets coursework be edited in librarian while
learn-ai-engineering is still being consolidated: generated files carry an
`imported_hash`; an edited or hand-authored file is never overwritten or deleted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from core import import_courses as ic


def test_mdx_callouts_tabs_screenshots_and_promo_drop() -> None:
    src = """import { Callout, Tabs } from 'nextra/components'
import shot from '../img/shot.png'

# Title

<Callout type="warning">
Be careful.
</Callout>

<Callout type="info">
Use code PROMPTING20 for 20% off
</Callout>

<Tabs items={['Python', 'JS']}>
  <Tab>
    py code
  </Tab>
  <Tabs.Tab>
    js code
  </Tabs.Tab>
</Tabs>

<Screenshot src={shot} alt="A shot" />

<CoursePromo title="x">
  Buy now
</CoursePromo>

```jsx
<Callout>kept in code</Callout>
```
"""
    md, imports = ic.mdx_to_markdown(src)
    assert "import" not in md.split("```")[0]
    assert "> **Warning:**\n> Be careful." in md
    assert "PROMPTING20" not in md
    assert "**Python**\n\npy code" in md
    assert "**JS**\n\njs code" in md
    assert "![A shot](../img/shot.png)" in md
    assert "Buy now" not in md
    assert "<Callout>kept in code</Callout>" in md
    assert imports == {"shot": "../img/shot.png"}


def test_notebook_keeps_cells_drops_outputs() -> None:
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": ["# NB\n", "text"]},
            {"cell_type": "code", "source": ["print(1)"], "outputs": [{"text": "OUTPUT"}]},
        ],
        "metadata": {"language_info": {"name": "python"}},
    }
    md = ic.notebook_to_markdown(json.dumps(nb))
    assert "# NB" in md and "```python\nprint(1)\n```" in md
    assert "OUTPUT" not in md


def test_render_hash_ignores_its_own_line() -> None:
    text = ic.render({"title": "T"}, "body")
    assert ic._recorded_hash(text) == ic._hash(text)
    assert ic._hash(text.replace("body", "edited")) != ic._recorded_hash(text)


# ── sync contract ────────────────────────────────────────────────────────────


@pytest.fixture()
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    source = tmp_path / "lae"
    mod = source / "generative-ai" / "01-llm-fundamentals"
    (mod / "img").mkdir(parents=True)
    (mod / "img" / "fig.png").write_bytes(b"\x89PNG")
    (mod / "01-intro.md").write_text("# Intro\n\nSee ![fig](img/fig.png) and [next](02-next.md).\n")
    (mod / "02-next.md").write_text("# Next\n\nMore.\n")
    vendored = mod / "some-repo-main"
    vendored.mkdir()
    (vendored / "README.md").write_text("# Vendored\n")
    (source / "generative-ai" / "README.md").write_text("# Gen AI\n")

    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    return source, dest


def _sync(source: Path) -> dict[str, int]:
    return ic.apply(ic.build_plan(source, ["generative-ai"]), ["generative-ai"], dry_run=False)


def test_import_converts_links_assets_and_skips_vendored(tree: tuple[Path, Path]) -> None:
    source, dest = tree
    stats = _sync(source)
    lessons = sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*.md"))
    assert not any("vendored" in p.lower() or "some-repo" in p for p in lessons)
    intro = next(dest.rglob("*intro*.md")).read_text()
    assert "imported_hash:" in intro
    link = intro.split("[next](")[1].split(")")[0]
    assert (next(dest.rglob("*intro*.md")).parent / link).is_file()
    assert "!fig" not in intro.split("---")[1]  # image markup kept out of the summary
    assert any(dest.rglob("assets/**/fig.png"))
    assert stats["created"] == len(lessons) and stats["assets"] == 1

    module_meta = next(dest.rglob("*llm-fundamentals/_module.md")).read_text()
    assert "some-repo-main" in module_meta  # listed as a reference, not imported


def test_reimport_is_idempotent(tree: tuple[Path, Path]) -> None:
    source, _ = tree
    _sync(source)
    stats = _sync(source)
    assert stats["created"] == stats["updated"] == stats["removed"] == stats["assets"] == 0


def test_local_edits_and_hand_authored_files_survive(tree: tuple[Path, Path]) -> None:
    source, dest = tree
    _sync(source)
    intro = next(dest.rglob("*intro*.md"))
    intro.write_text(intro.read_text() + "\nMy own notes.\n")
    authored = intro.parent / "my-lesson.md"
    authored.write_text("---\ntitle: Mine\n---\n\nWritten in librarian.\n")

    (source / "generative-ai" / "01-llm-fundamentals" / "01-intro.md").write_text(
        "# Intro\n\nChanged upstream.\n"
    )
    stats = _sync(source)
    assert stats["kept_local_edit"] == 1
    assert "My own notes." in intro.read_text()

    # Source deletion removes untouched generated copies only.
    for p in (source / "generative-ai" / "01-llm-fundamentals").glob("0*.md"):
        p.unlink()
    stats = _sync(source)
    assert stats["removed"] == 1  # 02-next; the edited intro stays
    assert intro.exists() and authored.exists()
    assert not any(dest.rglob("*next*.md"))


def test_unchanged_generated_file_updates_with_source(tree: tuple[Path, Path]) -> None:
    source, dest = tree
    _sync(source)
    (source / "generative-ai" / "01-llm-fundamentals" / "02-next.md").write_text(
        "# Next\n\nRevised.\n"
    )
    stats = _sync(source)
    assert stats["updated"] >= 1
    assert "Revised." in next(dest.rglob("*next*.md")).read_text()


def test_commit_hook_whitespace_fix_is_not_a_local_edit(tree: tuple[Path, Path]) -> None:
    source, dest = tree
    (source / "generative-ai" / "01-llm-fundamentals" / "02-next.md").write_text(
        "# Next\n\nMore.   \n\n\n"
    )
    _sync(source)
    nxt = next(dest.rglob("*next*.md"))
    assert "More.\n" in nxt.read_text() and "   " not in nxt.read_text()

    # A file written before render() normalized whitespace, then fixed by the hook.
    legacy = nxt.read_text().replace("More.\n", "More.  \n")
    legacy = ic._HASH_LINE_RE.sub("", legacy)
    nxt.write_text(legacy.replace("---\n", f"---\nimported_hash: {ic._hash(legacy)}\n", 1))
    nxt.write_text(ic._normalize_ws(nxt.read_text()))  # what trailing-whitespace leaves
    stats = _sync(source)
    assert stats["kept_local_edit"] == 0
    assert ic._recorded_hash(nxt.read_text()) == ic._hash(nxt.read_text())


def test_programming_course_reads_sisyphus_drills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sisyphus = tmp_path / "sisyphus"
    sql = sisyphus / "drills" / "sql"
    sql.mkdir(parents=True)
    (sql / "README.md").write_text("# SQL drills\n")
    (sisyphus / "drills" / "coding").mkdir()
    (sisyphus / "drills" / "coding" / "drill-log.md").write_text("# Log\n")
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)

    plan = ic.build_plan(tmp_path / "lae", ["programming"], sisyphus)
    ic.apply(plan, ["programming"], dry_run=False)

    lessons = [p.relative_to(dest).as_posix() for p in dest.rglob("*.md")]
    assert not any("drill-log" in p for p in lessons)  # progress history, not a lesson
    readme = next(dest.rglob("programming/sql/*.md")).read_text()
    assert "source: sisyphus/drills/sql/README.md" in readme
    assert "source: sisyphus/drills" in (dest / "programming" / "_course.md").read_text()


def test_drill_frontmatter_becomes_drill_lesson(tree: tuple[Path, Path]) -> None:
    source, dest = tree
    (source / "generative-ai" / "01-llm-fundamentals" / "03-drill.md").write_text(
        "---\ntitle: Rank orders\ntrack: sql\ndifficulty: medium\ntimebox_min: 20\n"
        "concepts: [window-functions]\nsource: original\n---\n\n# Ignored H1\n\nDo it.\n"
    )
    _sync(source)
    text = next(dest.rglob("*drill*.md")).read_text()
    meta = yaml.safe_load(text.split("---\n")[1])
    assert meta["title"] == "Rank orders" and meta["kind"] == "drill"
    assert meta["track"] == "sql" and meta["timebox_min"] == 20
    assert meta["wiki"] == ["window-functions"]
    assert meta["source"].startswith("learn-ai-engineering/")  # the drill's own `source` is dropped
    assert "Do it." in text and "concepts:" not in text
    # Frontmatter without a track stays a plain reading with its frontmatter dropped.
    assert (
        yaml.safe_load(next(dest.rglob("*intro*.md")).read_text().split("---\n")[1])["kind"]
        == "reading"
    )
