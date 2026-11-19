"""docs/syllabus.md's readers: unit sections from a start-here readme, quoted text, paragraphs."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.courses import syllabus

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
