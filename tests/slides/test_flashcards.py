"""tools/slides/flashcards.py: module flashcards built from local deck and lecture specs."""

from pathlib import Path

import pytest
import yaml

from tools.slides import flashcards as fc

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
    slides:
      - {layout: bullets, title: From the README, takeaway: Anchor stripped., source: "README.md#rules"}
"""

LECTURE = """
parts:
  - slides:
      - {layout: bullets, title: A lecture card, takeaway: From a lecture., source: notes/01-estimation.md}
      - {layout: bullets, title: Falls back to the title, takeaway: Duplicate front, dropped.}
"""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _front(path: Path) -> dict:
    return yaml.safe_load(path.read_text().split("---\n")[1])


@pytest.fixture()
def courses(tmp_path: Path) -> Path:
    root = tmp_path / "courses"
    mod = root / "data-analytics" / "02-statistics"
    _write(mod / "_module.md", "---\ntitle: Statistics\n---\n")
    _write(mod / "readme.md", "# Statistics\n")
    _write(mod / "notes" / "01-estimation.md", "# Estimation\n")
    _write(mod / "slides" / "deck.yaml", DECK)
    return root


def test_deck_slides_become_cards(courses: Path) -> None:
    fc.build(courses)
    target = courses / "data-analytics" / "02-statistics" / "_flashcards.md"
    meta = _front(target)
    assert meta["generated_by"] == fc.GENERATED_BY
    assert meta["decks"] == ["data-analytics/02-statistics/slides/deck.yaml"]
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


def test_lecture_specs_add_cards_and_repeated_fronts_are_dropped(courses: Path) -> None:
    mod = courses / "data-analytics" / "02-statistics"
    _write(mod / "slides" / "lectures" / "01-estimation.yaml", LECTURE)
    fc.build(courses)
    meta = _front(mod / "_flashcards.md")
    assert meta["decks"][1] == "data-analytics/02-statistics/slides/lectures/01-estimation.yaml"
    fronts = [c["front"] for c in meta["cards"]]
    assert fronts[-1] == "A lecture card" and len(fronts) == len(set(fronts)) == 5
    assert meta["cards"][-1]["lesson"] == "data-analytics/02-statistics/notes/01-estimation"
    assert meta["cards"][1]["back"] == "Attaches to the module."  # the deck's card wins


def test_second_run_changes_nothing_and_edits_flow_through(courses: Path) -> None:
    mod = courses / "data-analytics" / "02-statistics"
    assert fc.build(courses)["written"] == 1
    assert fc.build(courses) == {"written": 0, "unchanged": 1, "removed": 0, "cards": 4}
    assert fc.build(courses, check=True)["written"] == 0

    (mod / "slides" / "deck.yaml").write_text(DECK.replace("Attaches to", "Changed to"))
    assert fc.build(courses, check=True)["written"] == 1  # check writes nothing
    assert "Attaches to" in (mod / "_flashcards.md").read_text()
    fc.build(courses)
    assert "Changed to the module." in (mod / "_flashcards.md").read_text()


def test_unparseable_spec_warns_and_yields_no_file(
    courses: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = courses / "data-analytics" / "02-statistics"
    (mod / "slides" / "deck.yaml").write_text("parts: [{slides: [unclosed\n")
    fc.build(courses)
    assert "unparseable" in capsys.readouterr().err
    assert not (mod / "_flashcards.md").exists()
    assert (mod / "readme.md").exists()


def test_only_generated_files_are_deleted(courses: Path) -> None:
    mod = courses / "data-analytics" / "02-statistics"
    fc.build(courses)
    (mod / "slides" / "deck.yaml").unlink()
    assert fc.build(courses)["removed"] == 1
    assert not (mod / "_flashcards.md").exists()

    other = courses / "data-analytics" / "03-hand-written"
    hand_written = _write(
        other / "_flashcards.md",
        "---\ntitle: hand written\ncards:\n- {front: Q, back: A}\n---\n",
    )
    assert fc.build(courses)["removed"] == 0
    assert hand_written.exists()


def test_nested_track_decks_attach_relative_to_their_own_folder(tmp_path: Path) -> None:
    root = tmp_path / "courses"
    py = root / "programming" / "python"
    _write(py / "01-foundations" / "notes" / "01-values.md", "# Values\n")
    _write(
        py / "01-foundations" / "slides" / "deck.yaml",
        "parts: [{slides: [{layout: code, title: T, takeaway: A, source: notes/01-values.md}]}]\n",
    )
    fc.build(root)
    meta = _front(py / "_flashcards.md")
    assert meta["cards"][0]["lesson"] == "programming/python/01-foundations/notes/01-values"


def test_real_courses_are_up_to_date() -> None:
    """The committed _flashcards.md files match their specs (run `make flashcards` if not)."""
    assert fc.build(fc.COURSES_DIR, check=True)["written"] == 0
