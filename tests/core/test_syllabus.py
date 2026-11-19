"""docs/syllabus.md's readers: unit sections from a start-here readme, quoted text, paragraphs."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.courses import syllabus
from librarian.courses.glossary import GlossaryTerm
from librarian.courses.labs import Lab
from librarian.courses.loader import Catalog, LessonRec, WikiRef

START_HERE = """---
title: Course
---
# Course

## Course outcomes

1. One outcome.

## Units

### [01 First](../01-first/readme.md)

**Objectives:** do [the thing](https://example.com).

### [04 Borrowed](../../other/09-borrowed/readme.md)

**Objectives:** borrowed.

### Related notes elsewhere

Not a unit.

## Primary texts
"""


def test_units_keyed_by_module_path_including_other_courses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    front = tmp_path / "course" / syllabus.FRONT
    front.mkdir(parents=True)
    (front / "readme.md").write_text(START_HERE)
    monkeypatch.setattr(syllabus, "COURSES_DIR", tmp_path)
    units = syllabus._units(tmp_path / "course")
    assert units == {
        "course/01-first": "**Objectives:** do the thing.",
        "other/09-borrowed": "**Objectives:** borrowed.",
    }


def test_sections_stop_at_same_or_higher_heading() -> None:
    lines = ["## A", "a1", "### A.1", "a2", "## B", "b1", "# Top", "t"]
    assert syllabus._sections(lines, 2) == {"A": ["a1", "### A.1", "a2"], "B": ["b1"]}


def test_first_paragraph_skips_quotes_and_tables() -> None:
    lines = ["", "> aside", "| a | b |", "First line", "continues [here](x.md).", "", "Second."]
    assert syllabus._first_paragraph(lines) == "First line continues here."


def _rec(lid: str, concepts: list[str], tier: str = "", semantic: int = 0) -> LessonRec:
    course, module, *_ = lid.split("/")
    return LessonRec(
        id=lid, course=course, module=module, title=lid.rsplit("/", 1)[-1], summary="",
        order=0, section="", kind="reading", source="", body="", concepts=concepts,
        semantic=semantic, tier=tier,
    )  # fmt: skip


def _lab(lid: str, notes: tuple[str, ...]) -> Lab:
    course, module, *_ = lid.split("/")
    return Lab(
        id=lid, course=course, module=module, path="practice/x", title=lid.rsplit("/", 1)[-1],
        purpose="", pattern="", language="python", runs_offline=True, verified_by="",
        licence="", notes=notes, files=(),
    )  # fmt: skip


@pytest.fixture
def writer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> syllabus._Writer:
    monkeypatch.setattr(syllabus, "COURSES_DIR", tmp_path / "courses")
    monkeypatch.setattr(syllabus, "WIKI_DIR", tmp_path / "wiki")
    lessons = {
        r.id: r
        for r in (
            _rec("c/01-a/notes/intro", ["rag", "near"], tier="foundations", semantic=1),
            _rec("c/01-a/notes/more", ["rag"]),
            _rec("c/02-b/notes/use", ["rag", "evals"], tier="practitioner"),
            _rec("c/03-c/notes/again", ["rag"], tier="practitioner"),
        )
    }
    wiki = {
        p: WikiRef(id=p, title=p.upper(), summary="", domain="rag")
        for p in ("rag", "evals", "near", "idle")
    }
    modules = [
        {
            "id": m,
            "title": m.upper(),
            "lessons": [{"id": lid} for lid in lessons if f"/{m}/" in lid],
        }
        for m in ("01-a", "02-b", "03-c")
    ]
    cat = Catalog(
        courses=[{"id": "c", "modules": modules}], lessons=lessons, wiki=wiki, by_concept={}
    )
    w = syllabus._Writer(cat, tmp_path / "docs" / "syllabus.md")
    for module in modules:
        syllabus._module(w, cat.courses[0], module, "")
    return w


def test_module_prints_tiers_and_keeps_embedding_links_apart(writer: syllabus._Writer) -> None:
    text = "\n".join(writer.lines)
    assert "**Tier:** 1 foundations · 1 not yet tiered" in text
    assert "*(foundations)*" in text
    assert "  - Nearby (embedding only): NEAR" in text
    assert writer.where["rag"] == [
        "c/01-a/notes/intro", "c/01-a/notes/more", "c/02-b/notes/use", "c/03-c/notes/again",
    ]  # fmt: skip
    assert "near" not in writer.where


def test_competency_map_introduces_develops_and_demonstrates(
    writer: syllabus._Writer, monkeypatch: pytest.MonkeyPatch
) -> None:
    terms = [
        GlossaryTerm.model_validate({"id": t, "label": t.title(), "def": "d", "page": p})
        for t, p in (
            ("retrieval", "rag"),
            ("evaluation", "evals"),
            ("idle", "idle"),
            ("gone", "private-page"),
        )
    ]
    monkeypatch.setattr(syllabus.glossary, "load_terms", lambda: terms)
    lab = _lab("c/02-b/practice/eval-lab", ("c/02-b/notes/use",))
    monkeypatch.setattr(syllabus.labs, "all_labs", lambda: {lab.id: lab})
    writer.lines.clear()
    syllabus._competencies(writer)
    text = "\n".join(writer.lines)
    assert "2 of 3 terms are taught; 0 of those have no lab." in text
    assert "  - Introduced: [intro](../courses/c/01-a/notes/intro.md) (01-A, foundations)" in text
    assert "  - Developed in: 02-B (1) · 03-C (1)" in text
    assert "  - Demonstrated by: [eval-lab](../courses/c/02-b/practice/eval-lab)" in text
    assert "**Terms no note links:** Idle (IDLE)" in text
    assert "| RAG | 3 | 4 | 2 practitioner · 1 foundations · 1 untiered |" in text
    assert "| EVALS |" not in text
