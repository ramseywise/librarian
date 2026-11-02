"""core/import_courses.py — MDX/notebook conversion and the idempotent sync contract.

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


def test_drills_course_reads_sisyphus_drills(
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

    plan = ic.build_plan(tmp_path / "lae", ["drills"], sisyphus)
    ic.apply(plan, ["drills"], dry_run=False)

    lessons = [p.relative_to(dest).as_posix() for p in dest.rglob("*.md")]
    assert not any("drill-log" in p for p in lessons)  # progress history, not a lesson
    readme = (dest / "drills" / "sql" / "readme.md").read_text()  # not _module.md
    assert "source: sisyphus/drills/sql/README.md" in readme
    assert "source: sisyphus/drills" in (dest / "drills" / "_course.md").read_text()


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


# ── pillar layout and flashcards ─────────────────────────────────────────────

REAL_SOURCE = ic.DEFAULT_SOURCE
REAL_DECK = REAL_SOURCE / "ai-engineering" / "01-prompt-engineering" / "slides" / "deck.yaml"

DECK = """
deck: {title: Stats}
parts:
  - title: One
    slides:
      - layout: statement
        title: Skipped, it is a statement
        statement: Big sentence.
        takeaway: Statement takeaways are not cards.
        source: notes/01-estimation.md
      - layout: bullets
        title: Skipped, no takeaway
        source: notes/01-estimation.md
      - layout: bullets
        title: The title
        recall: "What does **MLE** do?"
        takeaway: >-
          Maximises the `likelihood`
          of the data.
        source: notes/01-estimation.md#mle
      - layout: bullets
        title: Falls back to the title
        takeaway: Attaches to the module.
      - layout: bullets
        title: Unknown note
        takeaway: Also attaches to the module.
        source: notes/99-gone.md
  - title: Closing
    agenda: false
    slides:
      - {layout: bullets, title: From the README, takeaway: Anchor stripped., source: "README.md#rules"}
"""


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
    (mod / "slides").mkdir()
    (mod / "slides" / "deck.yaml").write_text(DECK)
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


def test_deck_slides_become_flashcards(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    _sync_analytics(source)
    mod = dest / "data-analytics" / "02-statistics"
    meta = _front(mod / "_flashcards.md")
    assert meta["decks"] == ["learn-ai-engineering/data-analytics/02-statistics/slides/deck.yaml"]
    lesson = "data-analytics/02-statistics/notes/01-estimation"
    assert meta["cards"] == [
        {
            "front": "What does **MLE** do?",
            "back": "Maximises the `likelihood` of the data.",
            "lesson": lesson,
        },
        {"front": "Falls back to the title", "back": "Attaches to the module."},
        {"front": "Unknown note", "back": "Also attaches to the module."},
        {
            "front": "From the README",
            "back": "Anchor stripped.",
            "lesson": "data-analytics/02-statistics/readme",
        },
    ]


def test_flashcards_follow_the_sync_contract(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    deck = source / "data-analytics" / "02-statistics" / "slides" / "deck.yaml"
    cards = dest / "data-analytics" / "02-statistics" / "_flashcards.md"

    _sync_analytics(source)
    assert _sync_analytics(source)["updated"] == 0  # idempotent

    deck.write_text(DECK.replace("Attaches to the module.", "Changed answer."))
    assert _sync_analytics(source)["updated"] == 1
    assert "Changed answer." in cards.read_text()

    deck.unlink()
    assert _sync_analytics(source)["removed"] == 1
    assert not cards.exists()


def test_dry_run_writes_nothing(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    plan = ic.build_plan(source, ["data-analytics"])
    assert plan.flashcards == 4
    assert ic.apply(plan, ["data-analytics"], dry_run=True)["created"] > 0
    assert not dest.exists()


def test_half_written_deck_is_skipped_not_fatal(pillar: tuple[Path, Path]) -> None:
    source, dest = pillar
    (source / "data-analytics" / "02-statistics" / "slides" / "deck.yaml").write_text(
        "parts: [{slides: [unclosed\n"
    )
    _sync_analytics(source)
    assert not (dest / "data-analytics" / "02-statistics" / "_flashcards.md").exists()
    assert (dest / "data-analytics" / "02-statistics" / "readme.md").exists()


def test_nested_track_decks_attach_relative_to_their_own_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """programming/python/<module>/slides/deck.yaml: the track is the librarian module."""
    source = tmp_path / "lae"
    py = source / "programming" / "python" / "01-foundations"
    (py / "notes").mkdir(parents=True)
    (py / "slides").mkdir()
    (py / "notes" / "01-values.md").write_text("# Values\n")
    (py / "slides" / "deck.yaml").write_text(
        "parts: [{slides: [{layout: code, title: T, takeaway: A, source: notes/01-values.md}]}]\n"
    )
    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)
    meta = _front(dest / "programming" / "python" / "_flashcards.md")
    assert meta["cards"][0]["lesson"] == "programming/python/01-foundations/notes/01-values"


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


@pytest.mark.skipif(not REAL_DECK.exists(), reason="needs the learn-ai-engineering checkout")
def test_real_prompt_engineering_deck(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The deck-spec worked example, into a temp dir. The deck is still being edited, so the
    expected count is derived from the YAML rather than hard-coded."""
    monkeypatch.setattr(ic, "COURSES_DIR", tmp_path)
    plan = ic.build_plan(REAL_SOURCE, ["ai-engineering"])
    path = tmp_path / "ai-engineering" / "01-prompt-engineering" / "_flashcards.md"
    cards = _front_text(plan.files[path])["cards"]

    slides = [s for p in yaml.safe_load(REAL_DECK.read_text())["parts"] for s in p["slides"]]
    expected = [s for s in slides if s["layout"] != "statement" and s.get("takeaway")]
    assert expected and len(cards) == len(expected)
    assert {c["front"] for c in cards} == {
        " ".join(s.get("recall", s["title"]).split()) for s in expected
    }

    lesson_files = {str(p.relative_to(tmp_path).with_suffix("")) for p in plan.files}
    attached = [c for c in cards if "lesson" in c]
    assert attached and all(c["lesson"] in lesson_files for c in attached)
    # Every slide in this deck names a note or the README, so every card has a lesson.
    assert len(attached) == len(cards)


def _front_text(text: str) -> dict:
    return yaml.safe_load(text.split("---\n")[1])


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

    dest = tmp_path / "courses"
    monkeypatch.setattr(ic, "COURSES_DIR", dest)
    ic.apply(ic.build_plan(source, ["programming"]), ["programming"], dry_run=False)

    assert (
        "title: Probability and statistics"
        in (dest / "programming" / "02-probability-and-statistics" / "_module.md").read_text()
    )
    assert "03 — Real Title" in (dest / "programming" / "03-real" / "_module.md").read_text()
