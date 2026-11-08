"""librarian.courses.importer — MDX/notebook conversion and the idempotent sync contract.

The sync contract is what lets coursework be edited in librarian while
learn-ai-engineering is still being consolidated: generated files carry an
`imported_hash`; an edited or hand-authored file is never overwritten or deleted.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from librarian.courses import importer as ic


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


def test_summary_keeps_underscores_in_code_and_identifiers() -> None:
    body = "Given `orders(order_id, user_id)`, rank each _user's_ **largest** orders by snake_case amount."
    assert ic._summary_from(body) == (
        "Given orders(order_id, user_id), rank each user's largest orders by snake_case amount."
    )


def test_credential_redaction_spares_plain_key_kwargs() -> None:
    src = (
        "API_KEY = 'sk-live-123'\nhub.Module(key='sentence')\npassword=\"hunter22\"\n"
        "Tokenizer(oov_token = \"<oov>\", pad_token='[PAD]')\n"
    )
    out = ic._CREDENTIAL_RE.sub(r'\1"<redacted>"', src)
    assert "sk-live-123" not in out and "hunter22" not in out
    assert "key='sentence'" in out and '"<oov>"' in out and "'[PAD]'" in out


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


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def practice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """A checkout laid out like learn-ai-engineering: practice/ is allowlisted, and the root
    .gitignore keeps the private files under programming/drills/ out."""
    source = tmp_path / "lae"
    drills = source / "programming" / "drills"
    (drills / "sql").mkdir(parents=True)
    (drills / "sql" / "README.md").write_text("# SQL drills\n")
    (drills / "sql" / "01-rank.md").write_text("# Rank\n\n![shot](img/open.png)\n")
    (drills / "sql" / "img").mkdir()
    (drills / "sql" / "img" / "open.png").write_bytes(b"\x89PNG")
    (drills / "sql" / "private.md").write_text("# Private\n")
    (drills / "coding").mkdir()
    (drills / "coding" / "drill-log.md").write_text("# Log\n")
    (drills / "coding" / "held.md").write_text("# Uncleared\n\n![fig](figure.png)\n")
    (drills / "coding" / "figure.png").write_bytes(b"\x89PNG")
    (drills / "secret-module").mkdir()
    (drills / "secret-module" / "README.md").write_text("# Secret\n")
    leetcode = drills / "python" / "leetcode"
    leetcode.mkdir(parents=True)
    (drills / "python" / "README.md").write_text("# Python\n")
    (leetcode / "two-sum.md").write_text("# Two sum\n")
    (source / "practice" / "interviewing").mkdir(parents=True)
    (source / "practice" / "interviewing" / "README.md").write_text("# Interviewing\n")
    (source / "practice" / "interviewing" / "private.md").write_text("# Private interview\n")
    (source / "practice" / ".gitignore").write_text(
        "*\n!*/\n!/.gitignore\n!/interviewing/README.md\n"
    )
    (source / ".gitignore").write_text(
        "/programming/drills/sql/private.md\n"
        "/programming/drills/coding/\n"
        "/programming/drills/secret-module/\n"
        "/programming/drills/python/leetcode/\n"
    )
    _git(source.parent, "init", "-q", str(source))
    _git(leetcode, "init", "-q")  # git reports this as one directory entry
    _git(source, "add", ".gitignore", "practice/", "programming/")
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    return source, dest


def test_drills_are_a_module_of_programming(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    assert "drills" not in ic.SUBJECTS
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)

    lessons = [p.relative_to(dest).as_posix() for p in dest.rglob("*.md")]
    assert not any("drill-log" in p for p in lessons)  # progress history, not a lesson
    readme = (dest / "programming" / "drills" / "sql" / "readme.md").read_text()
    assert "source: learn-ai-engineering/programming/drills/sql/README.md" in readme
    assert (
        "source: learn-ai-engineering/programming/drills"
        in (dest / "programming" / "drills" / "_module.md").read_text()
    )


def test_drill_under_programming_keeps_kind_drill(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    (source / "programming" / "drills" / "sql" / "02-window.md").write_text(
        "---\ntitle: Window\ntrack: sql\ntopic: window\ndifficulty: easy\ntimebox_min: 5\n"
        "concepts: [window-functions]\nsource: original\n---\n\n## Prompt\n\nDo it.\n"
    )
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    meta = _front(dest / "programming" / "drills" / "sql" / "02-window.md")
    assert meta["kind"] == "drill" and meta["track"] == "sql"
    assert meta["wiki"] == ["window-functions"]


def test_tracked_drill_log_is_still_not_a_lesson(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    log = source / "programming" / "drills" / "sql" / "drill-log.md"
    log.write_text("# Log\n")
    _git(source, "add", "programming/drills/sql/drill-log.md")
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    assert not list(dest.rglob("drill-log*"))


def test_retired_course_files_are_removed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    (dest / "drills").mkdir(parents=True)
    generated = ic.render({"title": "Old"})
    (dest / "drills" / "_course.md").write_text(generated)
    (dest / "drills" / "edited.md").write_text("# Mine\n")
    plan = ic.Plan(source=tmp_path)
    stats = ic.apply(plan, list(ic.RETIRED_SUBJECTS), dry_run=False)
    assert stats["removed"] == 1
    assert not (dest / "drills" / "_course.md").exists()
    assert (dest / "drills" / "edited.md").exists()  # never delete what was edited here


def test_private_files_do_not_import(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    subjects = ["programming", "interviewing"]
    ic.apply(ic.build_plan(source, subjects), subjects, dry_run=False)

    files = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    assert "programming/drills/sql/01-rank.md" in files
    assert "programming/drills/assets/sql/img/open.png" in files  # tracked image comes along
    assert "interviewing/00-start-here/readme.md" in files
    for private in ("private", "held", "drill-log", "two-sum", "figure", "secret"):
        assert not any(private in f for f in files), private


def test_ignored_nested_repo_is_not_even_a_reference(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    ignored = ic._git_ignored(source, source / "programming")
    assert ignored is not None and "programming/drills/python/leetcode/" in ignored  # dir entry
    assert ic._matches_ignored("programming/drills/python/leetcode/two-sum.md", ignored)

    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    module = dest / "programming" / "drills" / "_module.md"
    assert "references" not in _front(module)
    assert "leetcode" not in module.read_text()


def test_ignored_image_is_not_copied(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    gitignore = source / ".gitignore"
    gitignore.write_text(
        gitignore.read_text().replace(
            "/programming/drills/coding/\n",
            "/programming/drills/coding/figure.png\n/programming/drills/coding/drill-log.md\n",
        )
    )
    _git(source, "add", ".gitignore", "programming/")
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    assert (dest / "programming" / "drills" / "coding" / "held.md").exists()
    assert not list(dest.rglob("figure.png"))


@pytest.mark.parametrize(
    ("subject", "rel"),
    [("interviewing", "practice/interviewing"), ("programming", "programming/drills")],
)
def test_subjects_with_private_files_fail_closed_without_git(
    tmp_path: Path, subject: str, rel: str
) -> None:
    (tmp_path / rel).mkdir(parents=True)
    (tmp_path / rel / "private.md").write_text("# Private\n")
    with pytest.raises(RuntimeError, match="not a git checkout"):
        ic.build_plan(tmp_path, [subject])


def test_links_rewrite_across_courses(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    chapter = source / "data-engineering" / "01-storage"
    chapter.mkdir(parents=True)
    (chapter / "README.md").write_text("# Storage\n")
    guide = source / "practice" / "interviewing" / "README.md"
    guide.write_text("# Interviewing\n\n[Storage](../../data-engineering/01-storage/README.md)\n")
    _git(source, "add", "practice/")
    ic.apply(ic.build_plan(source, ["interviewing"]), ["interviewing"], dry_run=False)
    body = (dest / "interviewing" / "00-start-here" / "readme.md").read_text()
    assert "(../../data-engineering/01-storage/readme.md)" in body
    assert not (dest / "data-engineering").exists()  # linked to, not imported


def test_root_readme_links_to_non_lessons_gain_a_level(practice: tuple[Path, Path]) -> None:
    source, dest = practice
    deck = source / "programming" / "python" / "slides"
    deck.mkdir(parents=True)
    (deck / "deck.pptx").write_bytes(b"PK")
    (source / "programming" / "README.md").write_text(
        "# Programming\n\n[Deck](python/slides/deck.pptx) [Drills](drills/sql/README.md)\n"
    )
    (source / "programming" / "python" / "notes.md").write_text(
        "# Notes\n\n[Deck](slides/deck.pptx)\n"
    )
    _git(source, "add", "programming/")
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    readme = (dest / "programming" / "00-start-here" / "readme.md").read_text()
    assert "(../python/slides/deck.pptx)" in readme
    assert "(../drills/sql/readme.md)" in readme
    # a lesson whose folder keeps its layout keeps the link as written
    assert "(slides/deck.pptx)" in (dest / "programming" / "python" / "notes.md").read_text()


def test_links_follow_renamed_folders_and_point_unmirrored_files_at_github(
    practice: tuple[Path, Path],
) -> None:
    source, dest = practice
    week = source / "programming" / "drills" / "sql" / "Week_1"
    week.mkdir()
    (week / "case (study).md").write_text("# Case\n")
    (week / "data.csv").write_text("a,b\n")
    examples = source / "programming" / "drills" / "sql" / "examples"
    examples.mkdir()
    (examples / "1.select.py").write_text("print(1)\n")
    (source / "DECKS.md").write_text("# Decks\n")
    (source / "programming" / "python" / "notes.md").write_text(
        "# Notes\n\n[Week](../drills/sql/Week_1/) [CSV](../drills/sql/Week_1/data.csv) "
        "[Case](../drills/sql/Week_1/case%20%28study%29.md) [Decks](../../DECKS.md) "
        "[Examples](../drills/sql/examples/)\n"
    )
    _git(source, "add", "DECKS.md", "programming/")
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    notes = (dest / "programming" / "python" / "notes.md").read_text()
    assert "(../drills/sql/week-1)" in notes
    assert "(../drills/sql/week-1/data.csv)" in notes
    assert "(../drills/sql/week-1/case-study.md)" in notes
    assert f"({ic.SIBLING_URL}/blob/main/DECKS.md)" in notes
    # a folder with no lesson in it has no copy here
    assert f"({ic.SIBLING_URL}/tree/main/programming/drills/sql/examples)" in notes


def test_vendored_paths_are_not_fooled_by_practice_dirs(tmp_path: Path) -> None:
    practice_dir = tmp_path / "practice"
    for name in ("drills", "interviewing"):
        (practice_dir / name).mkdir(parents=True)
        assert not ic._is_vendored(practice_dir / name)
    (practice_dir / "datatalks-de").mkdir()
    assert ic._is_vendored(practice_dir / "datatalks-de")  # the rule still fires
    nested = practice_dir / "drills" / "python" / "leetcode"
    nested.mkdir(parents=True)
    (nested / ".git").mkdir()
    assert ic._is_vendored(nested)  # no longer exempt


def test_vendored_urls_read_third_party(tmp_path: Path) -> None:
    (tmp_path / "THIRD_PARTY.md").write_text(
        "| Path | Upstream |\n|---|---|\n"
        "| `a/practice/kept/` | https://github.com/x/kept | MIT | what |\n"
        "| `a/old-main` (gitignored, never tracked) | https://github.com/x/old | gone | what |\n"
    )
    assert ic._vendored_urls(tmp_path) == {
        "a/practice/kept": "https://github.com/x/kept",
        "a/old-main": "https://github.com/x/old",
    }


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


# ── pillar layout ─────────────────────────────────────────────


def _front(path: Path) -> dict:
    return yaml.safe_load(path.read_text().split("---\n")[1])


@pytest.fixture()
def pillar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    source = tmp_path / "lae"
    subject = source / "data-analytics"
    mod = subject / "02-statistics"
    for rel, text in {
        "README.md": "# Statistics\n\nA pillar about estimating things from noisy data, well.\n",
        "references.md": "# 02-statistics references\n\nStatus: being written.\n",
        "notes/01-estimation.md": "---\norigin: synthesis\n---\n# Estimation\n\nBody.\n",
        "practice/lab/01-lab.md": "# Lab\n",
        "practice/datatalks-de/README.md": "# Zoomcamp\n",
        "practice/datatalks-de/week1/homework.md": "# Homework\n",
    }.items():
        (mod / rel).parent.mkdir(parents=True, exist_ok=True)
        (mod / rel).write_text(text)
    (mod / "practice" / "datatalks-de" / "syllabus.pdf").write_bytes(b"%PDF")
    (subject / "README.md").write_text("# Data Analytics\n")
    (subject / "references.md").write_text("# Data analytics references\n")
    (subject / "sources" / "book").mkdir(parents=True)
    (subject / "sources" / "paper-2024.pdf").write_bytes(b"%PDF")
    (subject / "sources" / "book" / "ch01-intro.pdf").write_bytes(b"%PDF")

    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    return source, dest


def _sync_analytics(source: Path) -> dict[str, int]:
    return ic.apply(ic.build_plan(source, ["data-analytics"]), ["data-analytics"], dry_run=False)


def test_importer_does_not_write_or_remove_flashcards(pillar: tuple[Path, Path]) -> None:
    """Flashcards are built by tools/slides/flashcards.py; the importer leaves them alone."""
    source, dest = pillar
    _sync_analytics(source)
    mod = dest / "data-analytics" / "02-statistics"
    assert not (mod / "_flashcards.md").exists()
    assert (
        ic.build_plan(source, ["data-analytics"]).files.keys().isdisjoint({mod / "_flashcards.md"})
    )

    # Even one that still carries the old imported_hash survives a sync that does not plan it.
    cards = mod / "_flashcards.md"
    cards.write_text(ic.render({"decks": [], "cards": [{"front": "Q", "back": "A"}]}))
    assert "imported_hash" in cards.read_text()
    stats = _sync_analytics(source)
    assert cards.exists() and stats["removed"] == 0
    (source / "data-analytics" / "02-statistics" / "notes" / "01-estimation.md").unlink()
    assert _sync_analytics(source)["removed"] == 1  # the lesson goes, the cards stay
    assert cards.exists()


def test_pillar_layout_modules_sections_and_references(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    modules = {m.name: m for m in ic.discover(source, "data-analytics")}
    assert list(modules) == ["00-start-here", "02-statistics", "sources"]

    mod = modules["02-statistics"]
    assert [lesson.src.name for lesson in mod.lessons] == [
        "README.md",
        "01-estimation.md",
        "01-lab.md",
        "references.md",  # last, after the notes and practice it backs
    ]
    assert {r["source"] for r in modules["sources"].readings} == {
        "data-analytics/sources/paper-2024.pdf",
        "data-analytics/sources/book/ch01-intro.pdf",
    }
    assert not modules["sources"].lessons

    _sync_analytics(source)
    root = dest / "data-analytics" / "02-statistics"
    assert _front(root / "notes" / "01-estimation.md")["section"] == "Notes"
    assert _front(root / "practice" / "lab" / "01-lab.md")["section"] == "Practice / Lab"
    refs = _front(root / "references.md")
    assert refs["title"] == "References" and refs["section"] == "References"
    assert "section" not in _front(root / "readme.md")
    assert _front(root / "_module.md")["title"] == "Statistics"
    assert "origin" not in (root / "notes" / "01-estimation.md").read_text()  # source frontmatter


def test_course_folder_in_practice_is_a_reference_not_lessons(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    _sync_analytics(source)
    root = dest / "data-analytics" / "02-statistics"
    assert not (root / "practice" / "datatalks-de").exists()
    meta = _front(root / "_module.md")
    assert [r["title"] for r in meta["references"]] == ["datatalks-de"]
    assert "readings" not in meta  # its PDFs stay out too


def test_gitignored_files_do_not_import(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    data = source / "data-analytics" / "02-statistics" / "practice" / "lab" / "datasets"
    data.mkdir()
    (data / "README.md").write_text("# Dataset readme\n")
    (data / "codebook.pdf").write_bytes(b"%PDF")
    (source / ".gitignore").write_text("datasets/\n")
    subprocess.run(["git", "init", "-q", str(source)], check=True)

    _sync_analytics(source)
    root = dest / "data-analytics" / "02-statistics"
    assert not (root / "practice" / "lab" / "datasets").exists()
    assert "readings" not in _front(root / "_module.md")
    assert (root / "practice" / "lab" / "01-lab.md").exists()  # untracked but not ignored


def test_placeholder_readme_heading_does_not_become_the_module_title(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "src"
    placeholder = source / "programming" / "02-probability-and-statistics"
    placeholder.mkdir(parents=True)
    (placeholder / "README.md").write_text("# 02-probability-and-statistics\n\nBeing written.\n")
    written = source / "programming" / "03-real"
    written.mkdir()
    (written / "README.md").write_text("# 03 — Real Title\n\nBody.\n")

    _git(source, "init")  # programming fails closed outside a checkout
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)

    assert (
        "title: Probability and statistics"
        in (dest / "programming" / "02-probability-and-statistics" / "_module.md").read_text()
    )
    assert "03 — Real Title" in (dest / "programming" / "03-real" / "_module.md").read_text()


# ── mirroring: home figures, decks, manifests, adoption ─────────────────────


def test_subject_home_figure_goes_to_the_private_mirror(pillar: tuple[Path, Path]) -> None:
    """A book figure in `<home>/sources/images/` lands in `assets/sources/`, which is private."""
    source, dest = pillar
    home = source / "data-analytics"
    (home / "sources" / "images").mkdir(parents=True)
    (home / "sources" / "images" / "book-fig1.png").write_bytes(b"\x89PNG")
    note = home / "02-statistics" / "notes" / "01-estimation.md"
    note.write_text(note.read_text() + "\n![fig](../../sources/images/book-fig1.png)\n")
    _sync_analytics(source)
    public = dest / "data-analytics" / "02-statistics" / "assets" / "sources" / "images"
    assert not (public / "book-fig1.png").exists()
    assert (dest / "private" / public.relative_to(dest) / "book-fig1.png").is_file()
    lesson = next((dest / "data-analytics" / "02-statistics").rglob("*estimation.md")).read_text()
    assert "../assets/sources/images/book-fig1.png" in lesson


def test_deck_is_mirrored_with_its_figure_paths(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    mod = source / "data-analytics" / "02-statistics"
    (mod / "notes" / "figs").mkdir()
    (mod / "notes" / "figs" / "curve.png").write_bytes(b"\x89PNG")
    (mod / "slides").mkdir()
    (mod / "slides" / "deck.yaml").write_text("slides:\n  - image: ../notes/figs/curve.png\n")
    _sync_analytics(source)
    deck = dest / "data-analytics" / "02-statistics" / "slides" / "deck.yaml"
    text = deck.read_text()
    assert text.startswith("# imported_hash: ")
    image = yaml.safe_load(text)["slides"][0]["image"]
    assert (deck.parent / image).is_file()
    assert _sync_analytics(source)["updated"] == 0


def test_manifest_paths_follow_the_mirror_names(tmp_path: Path) -> None:
    pillar_dest = tmp_path / "02-statistics"
    (pillar_dest / "practice").mkdir(parents=True)
    (pillar_dest / "practice" / "readme.md").write_text("# Labs\n")
    (pillar_dest / "practice" / "intro-lab.md").write_text("# Lab\n")
    (pillar_dest / "practice" / "run.py").write_text("")
    text = (
        "examples:\n"
        '  - path: "practice/README.md"\n    purpose: "x"\n'
        '  - path: "practice/Intro_Lab.ipynb"\n    purpose: "y"\n'
        '  - path: "practice/datatalks-de"\n    purpose: "z"\n'
        '  - path: "practice/run.py"\n    purpose: "w"\n'
    )
    out = ic._rewrite_manifest(text, pillar_dest)
    assert '"practice/readme.md"' in out and '"practice/intro-lab.md"' in out
    assert '"practice/run.py"' in out
    assert "datatalks-de" not in out and 'purpose: "z"' not in out


def test_private_readings_overlay_is_owned_without_a_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ic, "COURSES_DIR", tmp_path)
    readings = "---\nreadings:\n- title: A\n  source: x/sources/a.pdf\n---\n"
    private = tmp_path / "private" / "data-analytics" / "02-statistics" / "_module.md"
    public = tmp_path / "data-analytics" / "02-statistics" / "_module.md"
    assert ic._owned(private, readings, set())
    assert not ic._owned(private, readings, set(), removing=True)
    assert not ic._owned(public, readings, set())
    assert not ic._owned(private, readings + "Hand notes.\n", set())


def test_adopted_files_must_be_ours(tmp_path: Path) -> None:
    lesson, deck = tmp_path / "01-x.md", tmp_path / "deck.yaml"
    adopted = {lesson, deck}
    assert ic._owned(lesson, "---\nsource: learn-ai-engineering/x.md\n---\n", adopted)
    assert not ic._owned(lesson, "---\ntitle: mine\n---\n", adopted)
    assert not ic._owned(tmp_path / "other.md", "source: learn-ai-engineering/x", adopted)
    assert ic._owned(deck, "slides: []\n", adopted)
    assert not ic._owned(deck, "slides: []\n", adopted, removing=True)
