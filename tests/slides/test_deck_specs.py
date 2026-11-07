"""Every course deck spec must be buildable from this repo alone."""

import re
from pathlib import Path

import pytest
import yaml

from librarian.courses import overlay
from librarian.slides import deck_graph

ROOT = Path(__file__).resolve().parents[2]

COURSES = ROOT / "data" / "courses"
SPECS = sorted([*COURSES.rglob("slides/deck.yaml"), *COURSES.rglob("slides/lectures/*.yaml")])


def _images(node: object) -> list[str]:
    if isinstance(node, dict):
        found = [node["image"]] if isinstance(node.get("image"), str) else []
        return found + [i for value in node.values() for i in _images(value)]
    if isinstance(node, list):
        return [i for value in node for i in _images(value)]
    return []


def test_every_course_with_decks_is_seeded() -> None:
    assert {spec.relative_to(COURSES).parts[0] for spec in SPECS} >= {
        "ai-engineering",
        "generative-ai",
        "data-analytics",
        "data-science",
        "data-engineering",
        "programming",
    }


@pytest.mark.parametrize("spec", SPECS, ids=lambda p: p.relative_to(COURSES).as_posix())
def test_images_resolve_inside_the_module(spec: Path) -> None:
    module = spec.parents[2 if spec.parent.name == "lectures" else 1]
    for image in _images(yaml.safe_load(spec.read_text(encoding="utf-8"))):
        target = (spec.parent / image).resolve()
        assert target.is_relative_to(module / "assets"), image
        if target.is_file():
            continue
        # Third-party book and paper figures live only in data/courses/private/, so a public
        # checkout cannot verify them; where the mirror exists every image must resolve.
        if (COURSES / overlay.PRIVATE).is_dir():
            assert overlay.resolve_asset(target, COURSES) is not None, image


def test_deck_graph_has_no_problems() -> None:
    assert deck_graph.problems(deck_graph.load_lectures(COURSES), COURSES) == []


def test_decks_map_is_not_a_lesson() -> None:
    # The course reader and search index skip underscore files.
    assert re.fullmatch(r"_.+\.md", deck_graph.DECKS_MD)
