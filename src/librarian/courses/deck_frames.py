"""A deck as the slides a viewer shows, straight from its yaml: title, part dividers, content.

`walk` is the one rule for which slides a deck has and how they are numbered. `build_deck.py` draws
the .pptx from it and `frames` gives the study UI the same sequence as data, so the HTML slides and
the export cannot drift apart. `frames` needs no build: it reads the yaml and nothing else.

A lecture file's two generated slides ("Where this lecture sits", "Where this leads") come from the
deck graph, which lives in `librarian.tools.slides` (not importable from here), so `frames` leaves
them out.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BEATS = ("problem", "fundamentals", "practice", "pitfalls", "wrap")
DEFAULT_LAYOUT = "bullets"
# The yaml keys a layout draws from, beyond the ones every slide has. Both renderers read these.
BODY_KEYS = (
    "statement", "attribution", "bullets", "aside", "emphasis", "left", "right", "cards", "header",
    "widths", "rows", "highlight", "bold_first", "steps", "loop", "end_accent", "caption", "axis",
    "lang", "code",
)  # fmt: skip


@dataclass(frozen=True)
class Step:
    """One slide of a deck in order. `slide` is None on a divider; `agenda_idx` is None on a closing part."""

    kind: str  # "divider" | "slide"
    number: int  # 1-based position in the deck; the title slide is 1
    part: dict[str, Any]
    agenda_idx: int | None
    slide: dict[str, Any] | None = None


def agenda_parts(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The numbered parts, the ones the title slide lists."""
    return [p for p in parts if p.get("agenda", True)]


def walk(parts: list[dict[str, Any]]) -> Iterator[Step]:
    """Every slide after the title slide, numbered from 2: an agenda part's divider, then its slides."""
    number = 1
    agenda_idx = 0
    for part in parts:
        in_agenda = part.get("agenda", True)
        idx = agenda_idx if in_agenda else None
        if in_agenda and part.get("divider", True):
            number += 1
            yield Step("divider", number, part, idx)
        for sl in part.get("slides") or []:
            number += 1
            yield Step("slide", number, part, idx, sl)
        if in_agenda:
            agenda_idx += 1


def crumb(step: Step) -> str:
    """The breadcrumb of a content slide: "Part 2 · Title", or the bare title of a closing part."""
    title = str(step.part.get("title", ""))
    return title if step.agenda_idx is None else f"Part {step.agenda_idx + 1} · {title}"


def _text(value: object) -> str:
    return str(value).strip() if isinstance(value, str | int | float) else ""


def _spoken(narration: object, notes: object, fallback: str = "") -> str:
    """What the player reads aloud: the slide's `narration`, else its speaker notes."""
    return _text(narration) or _text(notes) or fallback


def _image_url(spec: Path, image: object, courses_dir: Path) -> str | None:
    """The served URL of a slide's image, or None when it is not a file inside the courses tree."""
    if not isinstance(image, str) or not image:
        return None
    try:
        rel = (spec.parent / image).resolve().relative_to(courses_dir.resolve())
    except (OSError, ValueError):
        return None
    return f"/api/courses/files/{rel.as_posix()}"


def frames(spec: Path, data: dict[str, Any], courses_dir: Path) -> list[dict[str, Any]]:
    """The deck's slides for the viewer, the title slide first. [] when the yaml has no usable parts."""
    deck = data.get("deck")
    parts = [p for p in data.get("parts") or [] if isinstance(p, dict)]
    if not isinstance(deck, dict) or not parts:
        return []
    numbered = agenda_parts(parts)
    out: list[dict[str, Any]] = [
        {
            "n": 1,
            "kind": "title",
            "title": _text(deck.get("title")),
            "subtitle": _text(deck.get("subtitle")),
            "tagline": _text(deck.get("tagline")),
            "byline": _text(deck.get("byline")),
            "reference": _text(deck.get("reference")),
            "agenda": [
                {"n": i, "title": _text(p.get("title")), "summary": _text(p.get("summary"))}
                for i, p in enumerate(numbered, 1)
            ],
            "notes": _text(deck.get("notes")),
            "narration": _spoken(
                deck.get("narration"),
                deck.get("notes"),
                ". ".join(x for x in (_text(deck.get("title")), _text(deck.get("subtitle"))) if x),
            ),
        }
    ]
    for step in walk(parts):
        part_n = None if step.agenda_idx is None else step.agenda_idx + 1
        where = {"n": part_n, "title": _text(step.part.get("title")), "of": len(numbered)}
        if step.slide is None:
            summary = _text(step.part.get("summary"))
            out.append(
                {
                    "n": step.number,
                    "kind": "divider",
                    "title": where["title"],
                    "summary": summary,
                    "part": where,
                    "notes": _text(step.part.get("notes")),
                    "narration": _spoken(
                        step.part.get("narration"),
                        step.part.get("notes"),
                        ". ".join(x for x in (f"Part {part_n}", where["title"], summary) if x),
                    ),
                }
            )
            continue
        sl = step.slide if isinstance(step.slide, dict) else {}
        beat = sl.get("beat")
        body = {k: sl[k] for k in BODY_KEYS if k in sl}
        if "image" in sl:
            body["image"] = _image_url(spec, sl["image"], courses_dir)
        out.append(
            {
                "n": step.number,
                "kind": "slide",
                "layout": _text(sl.get("layout")) or DEFAULT_LAYOUT,
                "beat": beat if beat in BEATS else None,
                "level": _text(sl.get("level")) or "core",
                "title": _text(sl.get("title")),
                "kicker": _text(sl.get("kicker")),
                "lead": _text(sl.get("lead")),
                "takeaway": _text(sl.get("takeaway")),
                "source": _text(sl.get("source")),
                "part": where,
                "body": body,
                "notes": _text(sl.get("notes")),
                "narration": _spoken(sl.get("narration"), sl.get("notes")),
            }
        )
    return out
