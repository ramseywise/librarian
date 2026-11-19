"""Tier and depth: the two axes course content is classified on.

Tier is set on a lesson as a whole and says who should meet the topic at all: `foundations`,
`practitioner` or `specialist`, the same three names as a learner's placement. Depth is set on
each section of a lesson, and on each quiz question and flashcard, and says how far the passage
takes the reader: `intro` gives the main ideas, `core` is what doing the task or passing the
interview takes, and `deep` is research and senior depth. Rubric:
.claude/skills/pillar/references/depth-rubric.md. Neither is a "level": that word names the three
study formats (see `librarian.courses.quiz`).

A lesson's frontmatter carries `tier`, and `depth_sections: {<exact heading text>: <depth>}` for
the sections that are not at `depth`, which is only the default for the sections not listed and
says nothing about the lesson as a whole. A section's depth covers its subsections, and a
subsection with its own entry overrides that. All three fields are authored in the source repo and
kept by the importer.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

TIERS = ("foundations", "practitioner", "specialist")
DEPTHS = ("intro", "core", "deep")
DEPTH_KEYS = ("tier", "depth", "depth_sections")
# The headings of the chapter template: they carry no depth, and neither do their subsections.
TEMPLATE_HEADINGS = frozenset(
    {"pitfalls", "try it", "labs", "interview checklist", "reading", "practice", "next"}
)

Heading = tuple[int, str]  # (level, text as written): 2 for `##`, 3 for `###`


def tier_of(value: object) -> str:
    """`value` as a tier, or "" when it is missing or not one."""
    return value if isinstance(value, str) and value in TIERS else ""


def depth_of(value: object) -> str:
    """`value` as a depth, or "" when it is missing or not one."""
    return value if isinstance(value, str) and value in DEPTHS else ""


def sections_of(value: object) -> dict[str, str]:
    """The legal entries of a `depth_sections` mapping: heading text → depth."""
    if not isinstance(value, dict):
        return {}
    return {str(h).strip(): d for h, d in value.items() if depth_of(d) and str(h).strip()}


def covered(depth: str, sections: dict[str, str]) -> set[str]:
    """Every depth a lesson has something at: its own, plus those of its marked sections."""
    return {d for d in (depth, *sections.values()) if d}


def section_depths(depth: str, sections: dict[str, str], headings: Sequence[Heading]) -> list[str]:
    """The depth of each heading's section, in order: its own entry, else that of the nearest
    heading above it (a lower level number) that has one, else the lesson's."""
    out: list[str] = []
    open_sections: list[tuple[int, str]] = []  # (level, depth) of the headings this one sits under
    for level, text in headings:
        while open_sections and open_sections[-1][0] >= level:
            open_sections.pop()
        own = sections.get(text) or (open_sections[-1][1] if open_sections else depth)
        open_sections.append((level, own))
        out.append(own)
    return out


def content_mask(headings: Sequence[Heading]) -> list[bool]:
    """True for each heading that has a depth: not a template heading, and not under one."""
    mask: list[bool] = []
    under: int | None = None  # level of the template heading we are inside
    for level, text in headings:
        if under is not None and level > under:
            mask.append(False)
            continue
        under = level if text.strip().lower() in TEMPLATE_HEADINGS else None
        mask.append(under is None)
    return mask


def order_breaks(depth: str, sections: dict[str, str], headings: Sequence[Heading]) -> list[str]:
    """The content headings that step back down in depth: each one shallower than a content
    heading above it, as "<heading> (<its depth> after <the deeper one>)". A lesson written in
    depth order (intro, then core, then deep) has none."""
    breaks: list[str] = []
    deepest = ""
    each = section_depths(depth, sections, headings)
    for (_, text), keep, own in zip(headings, content_mask(headings), each, strict=True):
        if not keep or not own:
            continue
        if deepest and DEPTHS.index(own) < DEPTHS.index(deepest):
            breaks.append(f"{text} ({own} after {deepest})")
        else:
            deepest = own
    return breaks


def meta_problems(meta: dict[str, Any], headings: Sequence[Heading]) -> list[str]:
    """What is wrong with the tier and depth fields of one lesson's frontmatter. `headings` are
    the lesson's headings in order; a section entry must name one of them exactly, and must
    change the depth that section would have without it."""
    problems: list[str] = []
    tier = meta.get("tier")
    if tier is not None and not tier_of(tier):
        problems.append(f"tier {tier!r} is not one of {', '.join(TIERS)}")
    legal = ", ".join(DEPTHS)
    given = meta.get("depth")
    if given is not None and not depth_of(given):
        problems.append(f"depth {given!r} is not one of {legal}")
    sections = meta.get("depth_sections")
    if sections is None:
        return problems
    if not isinstance(sections, dict):
        return [*problems, "depth_sections must be a mapping of heading to depth"]
    marked = sections_of(sections)
    texts = [text for _, text in headings]
    for heading, value in sections.items():
        key = str(heading).strip()
        if not depth_of(value):
            problems.append(f"depth_sections: {heading!r} has depth {value!r}, not one of {legal}")
        if key not in texts:
            problems.append(f"depth_sections: no heading {heading!r} in the lesson")
            continue
        at = texts.index(key)
        without = {h: d for h, d in marked.items() if h != key}
        if value == section_depths(depth_of(given), without, headings)[at]:
            problems.append(f"depth_sections: {heading!r} repeats the depth it already has")
    return problems
