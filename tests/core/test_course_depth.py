"""Depth tags on lessons and their sections (librarian/courses/depth.py) and the checks that read them."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from librarian.courses import depth
from librarian.courses.checks import check_chapters, curriculum_map

# Setup holds Proof and Aside; Next stands alone.
HEADINGS = [(2, "Setup"), (3, "Proof"), (3, "Aside"), (2, "Next")]


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_only_the_three_depths_are_depths() -> None:
    assert [depth.depth_of(d) for d in depth.DEPTHS] == ["intro", "core", "deep"]
    assert [depth.depth_of(v) for v in ("beginner", "Core", 2, None, ["core"])] == [""] * 5


def test_sections_keep_legal_entries_and_covered_unions_them() -> None:
    sections = depth.sections_of({" Proof ": "deep", "Bad": "expert", "": "intro"})
    assert sections == {"Proof": "deep"}
    assert depth.sections_of(["Proof"]) == {}
    assert depth.covered("core", sections) == {"core", "deep"}
    assert depth.covered("", {}) == set()


@pytest.mark.parametrize(
    ("meta", "fragment"),
    [
        ({"depth": "expert"}, "depth 'expert' is not one of intro, core, deep"),
        ({"depth": "core", "depth_sections": ["Proof"]}, "must be a mapping"),
        ({"depth": "core", "depth_sections": {"Proof": "hard"}}, "'Proof' has depth 'hard'"),
        ({"depth": "core", "depth_sections": {"Gone": "deep"}}, "no heading 'Gone'"),
        (
            {"depth": "core", "depth_sections": {"Proof": "core"}},
            "repeats the depth it already has",
        ),
        (
            {"depth": "core", "depth_sections": {"Setup": "deep", "Proof": "deep"}},
            "'Proof' repeats the depth it already has",  # inherited from Setup, the section above it
        ),
    ],
)
def test_meta_problems_name_each_fault(meta: dict, fragment: str) -> None:
    assert any(fragment in p for p in depth.meta_problems(meta, HEADINGS))


def test_a_subsection_overrides_the_section_it_sits_in() -> None:
    sections = {"Setup": "deep", "Proof": "core"}
    assert depth.section_depths("core", sections, HEADINGS) == ["deep", "core", "deep", "core"]
    assert depth.meta_problems({"depth": "core", "depth_sections": sections}, HEADINGS) == []
    assert depth.section_depths("", {}, HEADINGS) == [""] * 4


def test_untagged_and_well_tagged_lessons_have_no_problems() -> None:
    assert depth.meta_problems({}, []) == []
    assert (
        depth.meta_problems({"depth": "core", "depth_sections": {"Proof": "deep"}}, HEADINGS) == []
    )


def test_chapter_check_reads_depth_against_the_headings(tmp_path: Path) -> None:
    body = "# T\n\n## Setup\n\nText.\n\n### Proof\n\nMore.\n\n```\n## Fenced\n```\n"
    good = _write(
        tmp_path / "c" / "m" / "01-a.md",
        f"---\ntitle: T\ndepth: core\ndepth_sections:\n  Proof: deep\n---\n{body}",
    )
    assert check_chapters.metadata_problems(good.read_text(), good, tmp_path) == []
    bad = _write(
        tmp_path / "c" / "m" / "02-b.md",
        f"---\ntitle: T\ndepth: senior\ndepth_sections:\n  Fenced: deep\n---\n{body}",
    )
    problems = check_chapters.metadata_problems(bad.read_text(), bad, tmp_path)
    assert any("depth 'senior'" in p for p in problems)
    assert any(
        "no heading 'Fenced'" in p for p in problems
    )  # a heading inside a code fence is not one


def _map(root: Path, tmp_path: Path) -> dict:
    out = tmp_path / "map.json"
    assert curriculum_map.main(["--root", str(root), "--out", str(out), "build"]) == 0
    return json.loads(out.read_text())


def test_curriculum_map_counts_depths_and_flags_a_missing_one(tmp_path: Path) -> None:
    notes = tmp_path / "courses" / "generative-ai" / "01-a" / "notes"
    _write(notes / "01-one.md", "---\ntitle: One\ndepth: core\n---\n# One\n")
    _write(
        notes / "02-two.md",
        "---\ntitle: Two\ndepth: core\ndepth_sections:\n  Proof: deep\n---\n# Two\n\n## Proof\n",
    )
    _write(notes / "03-three.md", "---\ntitle: Three\n---\n# Three\n")
    data = _map(tmp_path / "courses", tmp_path)
    pillar = data["pillars"]["generative-ai/01-a"]
    assert pillar["depths"] == {"intro": 0, "core": 2, "deep": 1} and pillar["untagged"] == 1
    assert data["notes"]["generative-ai/01-a/notes/02-two.md"]["depths"] == ["core", "deep"]
    missing = [i for i in data["issues"] if i["kind"] == "no_unit_at_depth"]
    assert [(i["path"], i["detail"]) for i in missing] == [
        ("generative-ai/01-a", "no lesson or section at intro")
    ]
    assert (
        "no_unit_at_depth" in curriculum_map.INFO_KINDS
    )  # reported, not gated, while tagging runs


def test_an_untagged_module_raises_no_depth_issue(tmp_path: Path) -> None:
    _write(tmp_path / "courses" / "generative-ai" / "01-a" / "notes" / "01-one.md", "# One\n")
    data = _map(tmp_path / "courses", tmp_path)
    assert not [i for i in data["issues"] if i["kind"] == "no_unit_at_depth"]


def test_a_tier_is_one_of_three_and_is_checked_on_its_own(tmp_path: Path) -> None:
    assert depth.tier_of("specialist") == "specialist"
    assert depth.tier_of("senior") == "" and depth.tier_of(None) == ""
    assert depth.meta_problems({"tier": "practitioner"}, []) == []
    assert depth.meta_problems({"tier": "senior"}, []) == [
        "tier 'senior' is not one of foundations, practitioner, specialist"
    ]
    # a lesson with a tier and no depth is still read by the chapter check
    bad = _write(tmp_path / "c" / "m" / "01-a.md", "---\ntitle: T\ntier: expert\n---\n# T\n")
    problems = check_chapters.metadata_problems(bad.read_text(), bad, tmp_path)
    assert any("tier 'expert'" in p for p in problems)


def test_placement_and_lessons_share_one_list_of_tiers() -> None:
    from librarian.courses import placement

    assert placement.TIERS is depth.TIERS


ORDERED = [(2, "The idea"), (2, "Building it"), (3, "A detail"), (2, "Why it works"), (2, "Next")]


def test_sections_that_step_back_down_are_named() -> None:
    in_order = {"The idea": "intro", "Why it works": "deep"}
    assert depth.order_breaks("core", in_order, ORDERED) == []
    stepping = {"The idea": "deep", "A detail": "intro"}
    assert depth.order_breaks("core", stepping, ORDERED) == [
        "Building it (core after deep)",
        "A detail (intro after deep)",
        "Why it works (core after deep)",
    ]
    # template headings carry no depth, and an untagged lesson has no order to break
    assert depth.order_breaks("deep", {"Next": "intro"}, ORDERED) == []
    assert depth.order_breaks("", {}, ORDERED) == []


def test_curriculum_map_carries_tier_and_reports_the_untiered_and_the_out_of_order(
    tmp_path: Path,
) -> None:
    notes = tmp_path / "courses" / "generative-ai" / "01-a" / "notes"
    _write(notes / "01-one.md", "---\ntitle: One\ntier: foundations\n---\n# One\n")
    _write(
        notes / "02-two.md",
        "---\ntitle: Two\ndepth: core\ndepth_sections:\n  Proof: deep\n---\n"
        "# Two\n\n## Proof\n\n## Using it\n\n## Next\n",
    )
    data = _map(tmp_path / "courses", tmp_path)
    assert data["pillars"]["generative-ai/01-a"]["tiers"] == {
        "foundations": 1,
        "practitioner": 0,
        "specialist": 0,
    }
    assert data["notes"]["generative-ai/01-a/notes/01-one.md"]["tier"] == "foundations"
    found = {(i["kind"], i["path"], i["detail"]) for i in data["issues"]}
    two = "generative-ai/01-a/notes/02-two.md"
    assert ("no_tier", two, "no tier, and another lesson of the module has one") in found
    assert ("depth_order", two, "steps back down: Using it (core after deep)") in found
    assert {"no_tier", "depth_order"} <= curriculum_map.INFO_KINDS


def test_a_module_with_no_tier_at_all_raises_no_tier_issue(tmp_path: Path) -> None:
    _write(tmp_path / "courses" / "generative-ai" / "01-a" / "notes" / "01-one.md", "# One\n")
    data = _map(tmp_path / "courses", tmp_path)
    assert not [i for i in data["issues"] if i["kind"] in {"no_tier", "depth_order"}]
