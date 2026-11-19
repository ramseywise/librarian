"""The depth classifier's prompt and cleaning, and the scorer (`librarian courses review depth-*`)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from librarian.courses import depth
from librarian.courses.review import depth_classify as dc
from librarian.courses.review import depth_score as ds

NOTE = """---
title: A note
depth: deep
---

# A note

## Using it

```python
## not a heading
```

### A subsection

## Why it works

## Pitfalls

### A pitfall heading

## Next
"""
HEADINGS = [
    (2, "Using it"),
    (3, "A subsection"),
    (2, "Why it works"),
    (2, "Pitfalls"),
    (3, "A pitfall heading"),
    (2, "Next"),
]


def test_headings_skip_the_title_and_code_and_template_sections_do_not_count() -> None:
    assert ds.headings_of(NOTE) == HEADINGS
    assert depth.content_mask(HEADINGS) == [True, True, True, False, False, False]


def test_the_model_sees_the_note_without_its_frontmatter() -> None:
    prompt = dc.note_prompt("ds/notes/01-a.md", NOTE)
    assert "depth: deep" not in prompt
    assert "Path: ds/notes/01-a.md" in prompt
    assert "### A subsection" in prompt


def test_a_listing_of_every_section_becomes_the_stored_form() -> None:
    cleaned, dropped = dc.clean(
        {
            "sections": {
                "Using it": "core",
                "A subsection": "intro",
                "Why it works": "deep",
                "Not there": "deep",
                "Next": "core",  # a template heading carries no depth
                "Pitfalls": "hard",
            },
            "mixed": [{"heading": "Using it", "passage": "The proof of", "depth": "deep"}],
        },
        HEADINGS,
    )
    assert cleaned == {
        "depth": "core",
        "depth_sections": {"A subsection": "intro", "Why it works": "deep"},
        "mixed": [{"heading": "Using it", "passage": "The proof of", "depth": "deep"}],
    }
    assert len(dropped) == 3
    assert dc.clean({"sections": ["Why it works"]}, HEADINGS) == (
        {},
        ["sections is a list, not a mapping"],
    )
    assert dc.clean({"sections": {"Next": "core"}}, HEADINGS)[0] == {}


def test_the_default_is_core_unless_no_section_is_and_a_gap_takes_the_depth_around_it() -> None:
    # no core section: the default is the commonest depth, so only the odd section is listed
    all_deep, _ = dc.clean(
        {"sections": {"Using it": "deep", "A subsection": "deep", "Why it works": "intro"}},
        HEADINGS,
    )
    assert all_deep["depth"] == "deep"
    assert all_deep["depth_sections"] == {"Why it works": "intro"}
    # a subsection the model left out sits at its parent's depth, and the row says so
    gap, dropped = dc.clean({"sections": {"Using it": "intro", "Why it works": "core"}}, HEADINGS)
    assert gap["depth_sections"] == {"Using it": "intro"}
    assert depth.section_depths(gap["depth"], gap["depth_sections"], HEADINGS)[:3] == [
        "intro",
        "intro",
        "core",
    ]
    assert dropped == ["'A subsection': no depth given"]


def test_a_reply_is_read_through_a_fence_or_not_at_all() -> None:
    assert dc.parse('```json\n{"depth": "core"}\n```') == {"depth": "core"}
    assert dc.parse("I cannot say.") is None
    assert dc.parse("{not json}") is None


def _client(reply: str) -> SimpleNamespace:
    def create(**_: object) -> SimpleNamespace:
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=reply)],
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        )

    return SimpleNamespace(messages=SimpleNamespace(create=create))


def test_classify_gives_a_cleaned_row_or_an_error_row() -> None:
    listing = {"Using it": "core", "A subsection": "core", "Why it works": "deep"}
    reply = json.dumps({"sections": listing, "mixed": []})
    row = dc.classify(_client(reply), "m", "system", "ds/notes/01-a.md", NOTE)
    assert row["depth"] == "core"
    assert row["depth_sections"] == {"Why it works": "deep"}
    assert row["dropped"] == []
    bad = dc.classify(_client("no"), "m", "system", "ds/notes/01-a.md", NOTE)
    assert bad["error"] == "reply is not JSON"
    assert "depth" not in bad


def test_private_notes_are_refused_before_any_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    note = tmp_path / "private" / "ds" / "notes" / "01-a.md"
    note.parent.mkdir(parents=True)
    note.write_text(NOTE)
    monkeypatch.setenv("COURSES_DIR", str(tmp_path))
    from librarian.config import get_settings

    get_settings.cache_clear()
    try:
        assert dc.main(["private/ds/notes/01-a.md", "--out", str(tmp_path / "run.jsonl")]) == 2
    finally:
        get_settings.cache_clear()
    assert "private or missing" in capsys.readouterr().err
    assert not (tmp_path / "run.jsonl").exists()


def _gold(path: str, depth: str, sections: dict[str, str]) -> dict[str, Any]:
    return {"path": path, "depth": depth, "depth_sections": sections}


def test_sections_are_scored_by_their_effective_depth(tmp_path: Path) -> None:
    for name in ("a.md", "b.md", "c.md", "d.md"):
        (tmp_path / name).write_text(NOTE)
    gold = [
        _gold("a.md", "core", {"Why it works": "deep"}),
        _gold("b.md", "core", {}),
        _gold("c.md", "deep", {"Using it": "core"}),
        _gold("d.md", "core", {}),
    ]
    predictions = {
        # the same sections written with another default: still wholly right
        "a.md": {
            "path": "a.md",
            "depth": "deep",
            "depth_sections": {"Using it": "core"},
        },
        # one section too deep; an entry under Pitfalls is not counted
        "b.md": {
            "path": "b.md",
            "depth": "core",
            "depth_sections": {"A subsection": "deep", "A pitfall heading": "deep"},
        },
        "c.md": {"path": "c.md", "depth": "core", "depth_sections": {}},
    }
    report = ds.score(gold, predictions, tmp_path)
    assert report["scored"] == 3
    assert report["missing"] == ["d.md"]
    assert "note" not in report and "marks" not in report
    # nine content headings: b's subsection and c's "Why it works" are wrong
    assert report["section"]["n"] == 9
    assert report["section"]["accuracy"] == pytest.approx(7 / 9)
    assert report["section"]["confusion"] == {
        "core->core": 6,
        "core->deep": 1,
        "deep->core": 1,
        "deep->deep": 1,
    }
    assert report["section_baseline"]["accuracy"] == pytest.approx(7 / 9)
    assert report["exact_match"] == pytest.approx(1 / 3)
    assert report["exact_match_baseline"] == pytest.approx(1 / 3)
    assert [d["path"] for d in report["disagreements"]] == ["b.md", "c.md"]
    assert "Notes with every heading right: 0.33" in ds.render(report)


def test_macro_f1_is_over_the_depths_that_occur() -> None:
    got = ds.summary([("core", "core"), ("core", "core"), ("deep", "core"), ("deep", "deep")])
    assert set(got["per_class"]) == {"core", "deep"}
    assert got["per_class"]["core"]["precision"] == pytest.approx(2 / 3)
    assert got["macro_f1"] == pytest.approx((0.8 + 2 / 3) / 2)
