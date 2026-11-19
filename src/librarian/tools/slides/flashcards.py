#!/usr/bin/env python3
"""Build each module's flashcards from its local deck specs and its lessons' interview checklists.

    uv run python src/librarian/tools/slides/flashcards.py            write every <course>/<module>/_flashcards.md
    uv run python src/librarian/tools/slides/flashcards.py --check    exit 1 if any file would change; write nothing

A module is `data/courses/<course>/<module>`. Its specs are every `slides/deck.yaml` and
`slides/lectures/*.yaml` below it, deck first, then lectures in name order. One card per slide
that is not a `statement` and has a `takeaway`: front is `recall`, else `title`; back is
`answer` (what the question asks for, written for the card), else `takeaway`; `card: false`
leaves the slide out. If `source:`
names a lesson file (relative to the folder that holds `slides/`) the card carries that
lesson's id, otherwise it belongs to the module. Three optional slide keys add to a card and
leave its front alone: `more` (the in-depth explanation behind the short answer), `depth` (the
card's own depth: intro, core or deep; `librarian.courses.depth`) and `refs` (the references the
answer rests on, one string or a list). A card whose front already
appeared in the module is dropped: the Leitner log keys a card on its module and front text,
so two cards with one front would share a schedule.

After the deck cards, every row of a lesson's `## Interview checklist` table is a card of that
lesson: front is the first cell, back the second, with links reduced to their text. Lessons go
in path order, and a row whose question a deck card (or an earlier row) already asks is dropped
by the same repeated-front rule, so deck cards keep their place and their schedule. A table may
add columns after the answer, named in its header: `More` or `In depth`, `Depth`, and `Source`
or `Sources` (references separated by `;`). A table with any other third column is read as
before, everything after the question being the answer.

A card's tier is not written here: it is its lesson's, read when the catalog loads.

A spec that does not parse warns and yields no cards. A module with no cards has no file. The
tool only deletes a file it wrote, which carries `generated_by` in its frontmatter.
Standard library, PyYAML and `librarian.courses.depth`.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from librarian.courses.depth import depth_of

COURSES_DIR = Path(__file__).resolve().parents[4] / "data" / "courses"
FLASHCARD_FILE = "_flashcards.md"
GENERATED_BY = "src/librarian/tools/slides/flashcards.py"
SKIP_DIRS = {"node_modules", ".venv", "__pycache__", "assets"}
_SLUG_RE = re.compile(r"[^a-z0-9]+")
CHECKLIST_HEADING = "## Interview checklist"
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_LOCAL_LINK_RE = re.compile(r"\[([^\]]+)\]\((?!https?://)[^)]*\)")
# Optional checklist columns after the answer, by header text: card field for each.
EXTRA_COLUMNS = {
    "more": "more",
    "in depth": "more",
    "depth": "depth",
    "source": "sources",
    "sources": "sources",
}
_SEPARATOR_RE = re.compile(r"^[\s:|-]+$")


def _warn(message: str) -> None:
    print(f"WARN {message}", file=sys.stderr)


def module_dirs(courses: Path) -> list[Path]:
    """`<course>/<module>` folders, skipping hidden and underscore ones."""
    out: list[Path] = []
    for course in sorted(courses.iterdir()) if courses.is_dir() else []:
        if not course.is_dir() or course.name.startswith((".", "_")):
            continue
        out += [
            m
            for m in sorted(course.iterdir())
            if m.is_dir() and not m.name.startswith((".", "_")) and m.name not in SKIP_DIRS
        ]
    return out


def find_specs(module: Path) -> list[Path]:
    """Deck specs below a module: each `slides/deck.yaml`, then its `slides/lectures/*.yaml`."""
    specs: list[Path] = []
    for dp, dns, _ in os.walk(module):
        dns[:] = sorted(d for d in dns if not d.startswith(".") and d not in SKIP_DIRS)
        here = Path(dp)
        if here.name != "slides":
            continue
        if (here / "deck.yaml").is_file():
            specs.append(here / "deck.yaml")
        specs += sorted((here / "lectures").glob("*.yaml"))
    return specs


def _slug(path: str) -> str:
    return "/".join(_SLUG_RE.sub("-", seg.lower()).strip("-") for seg in path.split("/"))


def lesson_index(module: Path, courses: Path) -> dict[str, str]:
    """Lesson id by comparable key, for every markdown lesson below the module.

    The id is the path below `data/courses` without its suffix, the id the courses API uses.
    Keys are lower-cased and slugified so `README.md` finds `readme.md`.
    """
    index: dict[str, str] = {}
    for dp, dns, fns in os.walk(module):
        dns[:] = sorted(d for d in dns if not d.startswith(".") and d not in SKIP_DIRS)
        for fn in fns:
            path = Path(dp) / fn
            if path.suffix != ".md" or fn.startswith("_"):
                continue
            lesson_id = path.relative_to(courses).with_suffix("").as_posix()
            index[_slug(lesson_id)] = lesson_id
    return index


def _card_text(value: object) -> str:
    """One line of card text; YAML folding can leave newlines and a value may not be a string."""
    return " ".join(str(value).split()) if value is not None else ""


def _card_lesson(source: object, base: Path, courses: Path, index: dict[str, str]) -> str | None:
    """Lesson id named by a slide's `source:` (relative to the folder holding `slides/`)."""
    if not isinstance(source, str) or not source.strip():
        return None
    path = source.strip().split("#")[0]
    try:
        rel = (base / path).resolve().relative_to(courses.resolve()).with_suffix("")
    except ValueError:
        return None
    return index.get(_slug(rel.as_posix()))


def _references(value: object) -> list[str]:
    """References as card text, from one string or a list. A web link is kept as written, since
    it is the reference; a link to a local file is reduced to its text, since a card is not shown
    beside the lesson the path was relative to."""
    items = value if isinstance(value, list) else [value]
    refs = [_card_text(_LOCAL_LINK_RE.sub(r"\1", str(item))) for item in items if item is not None]
    return [r for r in refs if r]


def _extras(more: object, depth: object, refs: object, where: str) -> dict[str, Any]:
    """The optional fields of a card, each present only when it was given and is usable."""
    out: dict[str, Any] = {}
    if _card_text(more):
        out["more"] = _card_text(more)
    if _card_text(depth):
        if depth_of(_card_text(depth)):
            out["depth"] = _card_text(depth)
        else:
            _warn(f"{where}: depth {_card_text(depth)!r} is not a depth, left out")
    if _references(refs):
        out["sources"] = _references(refs)
    return out


def spec_flashcards(spec: Path, courses: Path, index: dict[str, str]) -> list[dict[str, Any]]:
    """Cards from one spec. A spec that does not parse yields none and a warning, so one
    half-written deck never stops the build."""
    try:
        data = yaml.safe_load(spec.read_text(errors="replace"))
    except (OSError, yaml.YAMLError) as e:
        _warn(f"{spec}: unparseable ({e})")
        return []
    parts = data.get("parts") if isinstance(data, dict) else None
    cards: list[dict[str, Any]] = []
    for part in parts if isinstance(parts, list) else []:
        slides = part.get("slides") if isinstance(part, dict) else None
        for slide in slides if isinstance(slides, list) else []:
            if not isinstance(slide, dict) or slide.get("layout") == "statement":
                continue
            if (
                slide.get("card") is False
            ):  # about the lecture itself (agenda, objectives, what next)
                continue
            front = _card_text(slide.get("recall")) or _card_text(slide.get("title"))
            if not slide.get("takeaway"):
                continue
            back = _card_text(slide.get("answer")) or _card_text(slide.get("takeaway"))
            if not front or not back:
                continue
            card: dict[str, Any] = {"front": front, "back": back}
            card |= _extras(
                slide.get("more"), slide.get("depth"), slide.get("refs"), f"{spec}: {front!r}"
            )
            # deck.yaml sits in slides/, a lecture in slides/lectures/; `source:` is relative to
            # the folder that holds slides/.
            slides_dir = spec.parent.parent if spec.parent.name == "lectures" else spec.parent
            lesson = _card_lesson(slide.get("source"), slides_dir.parent, courses, index)
            if lesson:
                card["lesson"] = lesson
            cards.append(card)
    return cards


def _cell_text(cell: str) -> str:
    """A table cell as card text: escaped pipes restored, links reduced to their text (the card
    view renders bold and code only)."""
    return _card_text(_LINK_RE.sub(r"\1", cell.replace("\\|", "|")))


def _cells(row: str) -> list[str]:
    return _CELL_SPLIT_RE.split(row.strip().strip("|"))


def checklist_rows(text: str, where: str = "") -> list[dict[str, Any]]:
    """A card (front, back and any optional fields) for each row of the `## Interview checklist`
    table, header and separator skipped. In a two-column table, or one whose later columns are
    not all EXTRA_COLUMNS, a pipe inside the answer that was not escaped stays part of the answer."""
    rows: list[dict[str, Any]] = []
    inside = False
    # None until the header is read, then the card field of each column after the answer.
    extras: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == CHECKLIST_HEADING:
            inside, extras = True, None
            continue
        if not inside:
            continue
        if stripped.startswith(("# ", "## ")):
            break
        if not stripped.startswith("|"):
            continue
        if extras is None:  # the column titles
            named = [EXTRA_COLUMNS.get(c.strip().lower(), "") for c in _cells(stripped)[2:]]
            extras = named if all(named) else []
            continue
        if _SEPARATOR_RE.match(stripped):
            continue
        cells = _cells(stripped)
        question = _cell_text(cells[0])
        if not extras:
            answer = _cell_text("|".join(cells[1:]))
            if question and answer:
                rows.append({"front": question, "back": answer})
            continue
        if len(cells) > 2 + len(extras):
            _warn(f"{where}: {question!r} has more cells than the header (escape a pipe as \\|)")
            continue
        answer = _cell_text(cells[1]) if len(cells) > 1 else ""
        if not question or not answer:
            continue
        given = dict(zip(extras, cells[2:], strict=False))
        sources = [s for s in given.get("sources", "").split(";") if s.strip()]
        rows.append(
            {"front": question, "back": answer}
            | _extras(
                _cell_text(given.get("more", "")),
                given.get("depth"),
                [s.replace("\\|", "|") for s in sources],
                f"{where}: {question!r}",
            )
        )
    return rows


def checklist_flashcards(module: Path, courses: Path) -> list[dict[str, Any]]:
    """One card per interview-checklist row of every lesson below the module, in path order."""
    cards: list[dict[str, Any]] = []
    for dp, dns, fns in os.walk(module):
        dns[:] = sorted(d for d in dns if not d.startswith(".") and d not in SKIP_DIRS)
        for fn in sorted(fns):
            path = Path(dp) / fn
            if path.suffix != ".md" or fn.startswith("_"):
                continue
            try:
                text = path.read_text(errors="replace")
            except OSError as e:
                _warn(f"{path}: unreadable ({e})")
                continue
            lesson = path.relative_to(courses).with_suffix("").as_posix()
            cards += [row | {"lesson": lesson} for row in checklist_rows(text, str(path))]
    return cards


def module_flashcards(module: Path, courses: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    """The module's specs and its cards, deck cards then checklist rows, first card per front kept."""
    specs = find_specs(module)
    index = lesson_index(module, courses)
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()
    found = [card for spec in specs for card in spec_flashcards(spec, courses, index)]
    for card in found + checklist_flashcards(module, courses):
        if card["front"] in seen:
            continue
        seen.add(card["front"])
        cards.append(card)
    return specs, cards


def render(specs: list[Path], cards: list[dict[str, Any]], courses: Path) -> str:
    meta = {
        "generated_by": GENERATED_BY,
        "decks": [s.relative_to(courses).as_posix() for s in specs],
        "cards": cards,
    }
    head = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{head}---\n"


def _is_generated(path: Path) -> bool:
    try:
        head = path.read_text().split("---\n", 2)[1]
        return bool(yaml.safe_load(head).get("generated_by") == GENERATED_BY)
    except (OSError, IndexError, AttributeError, yaml.YAMLError):
        return False


def build(courses: Path = COURSES_DIR, check: bool = False) -> dict[str, int]:
    """Write (or with `check`, only count) every module's flashcards file."""
    stats = {"written": 0, "unchanged": 0, "removed": 0, "cards": 0}
    for module in module_dirs(courses):
        target = module / FLASHCARD_FILE
        specs, cards = module_flashcards(module, courses)
        if not cards:
            if target.exists() and _is_generated(target):
                stats["removed"] += 1
                if not check:
                    target.unlink()
            continue
        stats["cards"] += len(cards)
        text = render(specs, cards, courses)
        if target.exists() and target.read_text() == text:
            stats["unchanged"] += 1
            continue
        stats["written"] += 1
        if not check:
            target.write_text(text)
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if a file would change")
    parser.add_argument("--courses", type=Path, default=COURSES_DIR)
    args = parser.parse_args()
    stats = build(args.courses, check=args.check)
    print(", ".join(f"{k}={v}" for k, v in stats.items()))
    return 1 if args.check and (stats["written"] or stats["removed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
