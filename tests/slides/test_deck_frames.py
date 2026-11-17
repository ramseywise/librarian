"""The slide sequence both renderers read (`librarian.courses.deck_frames`), and the frames the app draws."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import yaml
from pptx import Presentation

from librarian.courses import deck_frames
from librarian.tools.slides import build_deck

SPEC = """
deck:
  title: Deck
  subtitle: Sub
parts:
  - title: Opening
    summary: What is coming
    overview: true
    slides:
      - {layout: statement, beat: problem, title: Why, statement: Because, notes: Say why}
      - {layout: cards, beat: wrap, title: Able, takeaway: T, cards: [{title: A, body: b}],
         narration: Heard not read}
  - title: No divider
    divider: false
    slides:
      - {layout: image, beat: fundamentals, title: Picture, image: ../assets/fig.png, takeaway: T}
      - {layout: table, title: No beat, header: [a], rows: [[b]], takeaway: T}
  - title: Wrap
    agenda: false
    divider: false
    slides:
      - {layout: bullets, beat: nonsense, title: Keep, bullets: [one]}
"""


def _spec(tmp_path: Path) -> tuple[Path, dict]:
    courses = tmp_path / "courses"
    spec = courses / "c" / "m" / "slides" / "deck.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(SPEC)
    return spec, yaml.safe_load(SPEC)


def test_frames_number_the_title_dividers_and_slides(tmp_path: Path) -> None:
    spec, data = _spec(tmp_path)
    frames = deck_frames.frames(spec, data, tmp_path / "courses")
    assert [(f["n"], f["kind"], f["title"]) for f in frames] == [
        (1, "title", "Deck"),
        (2, "divider", "Opening"),
        (3, "slide", "Why"),
        (4, "slide", "Able"),
        (5, "slide", "Picture"),
        (6, "slide", "No beat"),
        (7, "slide", "Keep"),
    ]
    assert [a["title"] for a in frames[0]["agenda"]] == ["Opening", "No divider"]
    assert frames[4]["part"] == {"n": 2, "title": "No divider", "of": 2}
    assert frames[6]["part"]["n"] is None  # a closing part has no number


def test_narration_falls_back_to_notes_and_a_divider_reads_its_summary(tmp_path: Path) -> None:
    spec, data = _spec(tmp_path)
    frames = deck_frames.frames(spec, data, tmp_path / "courses")
    assert frames[1]["narration"] == "Part 1. Opening. What is coming"
    assert frames[2]["narration"] == "Say why"
    assert frames[3]["narration"] == "Heard not read"


def test_an_unknown_beat_is_dropped_and_an_image_gets_a_served_url(tmp_path: Path) -> None:
    spec, data = _spec(tmp_path)
    frames = deck_frames.frames(spec, data, tmp_path / "courses")
    assert frames[5]["beat"] is None and frames[6]["beat"] is None
    assert frames[4]["body"]["image"] == "/api/courses/files/c/m/assets/fig.png"


def test_an_image_outside_the_courses_tree_has_no_url(tmp_path: Path) -> None:
    spec, data = _spec(tmp_path)
    data["parts"][1]["slides"][0]["image"] = "../../../../outside.png"
    frames = deck_frames.frames(spec, data, tmp_path / "courses")
    assert frames[4]["body"]["image"] is None


def test_the_pptx_has_the_same_slides_in_the_same_order(tmp_path: Path) -> None:
    spec, data = _spec(tmp_path)
    data["parts"][1]["slides"].pop(0)  # no image file to embed
    del data["parts"][2]["slides"][0]["beat"]  # the builder stops on a beat it does not know
    spec.write_text(yaml.safe_dump(data))
    out = build_deck.build(spec, out=tmp_path / "deck.pptx")
    frames = deck_frames.frames(spec, data, tmp_path / "courses")
    built = build_deck.slide_outline(out)
    assert len(built) == len(frames)
    for frame, drawn in zip(frames, built, strict=True):
        assert frame["title"] in drawn["text"], frame["n"]


def test_every_key_a_layout_draws_reaches_the_app() -> None:
    """A yaml key the .pptx reads but `BODY_KEYS` lacks would be drawn in one renderer and not the other."""
    common = {
        "layout", "title", "kicker", "lead", "takeaway", "recall", "source", "notes", "level",
        "beat", "revisits", "image", "section",
    }  # fmt: skip
    read: set[str] = set()
    for fn in build_deck.LAYOUTS.values():
        read |= set(re.findall(r"""spec(?:\.get\(|\[)["'](\w+)["']""", inspect.getsource(fn)))
    assert read - common - set(deck_frames.BODY_KEYS) == set()
    assert (
        Presentation
    )  # the builder's dependency is present, so the comparison above ran against real code
