#!/usr/bin/env python3
"""Build each module's flashcards from its local deck specs.

    uv run python tools/slides/flashcards.py            write every <course>/<module>/_flashcards.md
    uv run python tools/slides/flashcards.py --check    exit 1 if any file would change; write nothing

A module is `data/courses/<course>/<module>`. Its specs are every `slides/deck.yaml` and
`slides/lectures/*.yaml` below it, deck first, then lectures in name order. One card per slide
that is not a `statement` and has a `takeaway`: front is `recall`, else `title`; back is
`takeaway`. If `source:` names a lesson file (relative to the folder that holds `slides/`) the
card carries that lesson's id, otherwise it belongs to the module. A card whose front already
appeared in the module is dropped: the Leitner log keys a card on its module and front text,
so two cards with one front would share a schedule.

A spec that does not parse warns and yields no cards. A module with no cards has no file. The
tool only deletes a file it wrote, which carries `generated_by` in its frontmatter.
Standard library plus PyYAML.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

COURSES_DIR = Path(__file__).resolve().parents[2] / "data" / "courses"
FLASHCARD_FILE = "_flashcards.md"
GENERATED_BY = "tools/slides/flashcards.py"
SKIP_DIRS = {"node_modules", ".venv", "__pycache__", "assets"}
_SLUG_RE = re.compile(r"[^a-z0-9]+")


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


def spec_flashcards(spec: Path, courses: Path, index: dict[str, str]) -> list[dict[str, str]]:
    """Cards from one spec. A spec that does not parse yields none and a warning, so one
    half-written deck never stops the build."""
    try:
        data = yaml.safe_load(spec.read_text(errors="replace"))
    except (OSError, yaml.YAMLError) as e:
        _warn(f"{spec}: unparseable ({e})")
        return []
    parts = data.get("parts") if isinstance(data, dict) else None
    cards: list[dict[str, str]] = []
    for part in parts if isinstance(parts, list) else []:
        slides = part.get("slides") if isinstance(part, dict) else None
        for slide in slides if isinstance(slides, list) else []:
            if not isinstance(slide, dict) or slide.get("layout") == "statement":
                continue
            front = _card_text(slide.get("recall")) or _card_text(slide.get("title"))
            back = _card_text(slide.get("takeaway"))
            if not front or not back:
                continue
            card = {"front": front, "back": back}
            # deck.yaml sits in slides/, a lecture in slides/lectures/; `source:` is relative to
            # the folder that holds slides/.
            slides_dir = spec.parent.parent if spec.parent.name == "lectures" else spec.parent
            lesson = _card_lesson(slide.get("source"), slides_dir.parent, courses, index)
            if lesson:
                card["lesson"] = lesson
            cards.append(card)
    return cards


def module_flashcards(module: Path, courses: Path) -> tuple[list[Path], list[dict[str, str]]]:
    """The module's specs and its cards, first card per front kept."""
    specs = find_specs(module)
    index = lesson_index(module, courses)
    cards: list[dict[str, str]] = []
    seen: set[str] = set()
    for spec in specs:
        for card in spec_flashcards(spec, courses, index):
            if card["front"] in seen:
                continue
            seen.add(card["front"])
            cards.append(card)
    return specs, cards


def render(specs: list[Path], cards: list[dict[str, str]], courses: Path) -> str:
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
