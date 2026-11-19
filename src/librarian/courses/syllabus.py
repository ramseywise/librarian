"""The whole syllabus on one page: every course, module and note, with the wiki pages each uses.

Generated, never edited: the text comes from the course itself and the links from the catalog.

- Course: summary, then outcomes, prerequisites and completion standard, quoted from
  `<course>/00-start-here/readme.md`.
- Module: the opening of its readme's `## What it is`, its unit section from the start-here
  readme (purpose, objectives, mastery lab, evidence, key sources) and its `## Builds on and
  feeds into` section, then a count of its practice material.
- Note, in reading order: tier (`librarian.courses.depth`), summary, the wiki pages it links
  (explicit, compiled from it, or named in its text) and, kept apart, the pages only the
  embedding says are near it. Each module counts its notes by tier.
- Module and course: every wiki page the module uses, and the pages in the course's wiki area
  (`librarian.wiki.areas`) that no note links. Last, the directories in no area.
- Competency map: for each glossary term with a public page, the note that introduces it (first
  in course order to link the page), the other modules that develop it and the labs that
  demonstrate it (a lab whose `demonstrates` names a note linking the page); then the pages
  linked from several modules, the candidates for duplication.

Private lessons and private or tombstoned wiki pages are left out (the catalog already hides
the pages), so the file is safe to commit.

    librarian courses syllabus [--out docs/syllabus.md]
"""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter

from librarian.config import get_settings
from librarian.courses import glossary, labs
from librarian.courses.catalog import COURSES_DIR, WIKI_DIR, Catalog, catalog
from librarian.courses.depth import TIERS
from librarian.log_config import get_logger
from librarian.wiki.areas import AREAS, area_of

log = get_logger(__name__)

FRONT = "00-start-here"
# The start-here sections quoted for a course, in this order.
COURSE_SECTIONS = ("Course outcomes", "Before you begin", "Completion standard")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
UNIT_RE = re.compile(r"^###\s+\[[^\]]+\]\(([^)]+)\)")
# A page linked from this many modules is listed as a candidate for duplication.
SHARED_MODULES = 3


def _flatten(text: str) -> str:
    """Links to their text: the targets are relative to the course repo and break here."""
    return LINK_RE.sub(lambda m: m.group(1), text).strip()


def _body(path: Path) -> list[str]:
    return frontmatter.load(path).content.splitlines() if path.is_file() else []


def _sections(lines: list[str], level: int) -> dict[str, list[str]]:
    """Heading text (links flattened) → the lines under it, up to the next heading this deep."""
    out: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in lines:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= level:
            current = out.setdefault(_flatten(m.group(2)), []) if len(m.group(1)) == level else None
            continue
        if current is not None:
            current.append(line)
    return out


def _text(lines: list[str]) -> str:
    return _flatten("\n".join(lines).strip().strip("-").strip())


def _units(course_dir: Path) -> dict[str, str]:
    """`course/module` → its `### [Unit](../module/readme.md)` section in the start-here readme."""
    out: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []
    front = course_dir / FRONT
    for line in [*_body(front / "readme.md"), "## end"]:
        if line.startswith(("## ", "### ")):
            if key:
                out[key] = _text(buf)
            m = UNIT_RE.match(line)
            target = (front / m.group(1)).resolve().parent if m else None
            key = (
                target.relative_to(COURSES_DIR.resolve()).as_posix()
                if target and target.is_relative_to(COURSES_DIR.resolve())
                else None
            )
            buf = []
        elif key:
            buf.append(line)
    return out


def _first_paragraph(lines: list[str]) -> str:
    para: list[str] = []
    for line in lines:
        if line.strip():
            if line.startswith(("#", "|", ">")):
                if para:
                    break
                continue
            para.append(line.strip())
        elif para:
            break
    return _flatten(" ".join(para))


class _Writer:
    def __init__(self, cat: Catalog, out: Path) -> None:
        self.cat = cat
        self.base = out.parent
        self.lines: list[str] = []
        self.paths = {
            p.stem: p
            for p in WIKI_DIR.rglob("*.md")
            if "private" not in p.relative_to(WIKI_DIR).parts
        }
        self.linked: set[str] = set()
        self.where: dict[str, list[str]] = {}  # page → the notes linking it, in course order
        self.module_of: dict[str, tuple[str, str]] = {}  # note → (module key, module title)

    def rel(self, path: Path) -> str:
        return os.path.relpath(path, self.base).replace(" ", "%20")

    def page(self, pid: str) -> str:
        ref = self.cat.wiki[pid]
        path = self.paths.get(pid)
        return f"[{ref.title}]({self.rel(path)})" if path else ref.title

    def add(self, *lines: str) -> None:
        self.lines.extend(lines)

    def quote(self, label: str, text: str) -> None:
        if text:
            self.add(f"**{label}**", "", text, "")


def _lesson(w: _Writer, lid: str) -> tuple[list[str], list[str]]:
    rec = w.cat.lessons[lid]
    split = len(rec.concepts) - rec.semantic
    linked, nearby = rec.concepts[:split], rec.concepts[split:]
    title = f"[{rec.title}]({w.rel(COURSES_DIR / f'{lid}.md')})"
    labels = [x for x in (rec.kind if rec.kind != "reading" else "", rec.tier) if x]
    label = f" *({', '.join(labels)})*" if labels else ""
    summary = f" — {rec.summary}" if rec.summary else ""
    w.add(f"- **{title}**{label}{summary}")
    for p in linked:
        w.where.setdefault(p, []).append(lid)
    if linked:
        w.add(f"  - Wiki: {' · '.join(w.page(p) for p in linked)}")
    if nearby:
        w.add(f"  - Nearby (embedding only): {' · '.join(w.page(p) for p in nearby)}")
    if not rec.concepts:
        w.add("  - Wiki: none")
    return linked, nearby


def _practice(module: dict[str, Any]) -> str:
    counts = [
        (len(module.get("decks") or []), "deck"),
        (module.get("flashcardCount", 0), "flashcard"),
        (module.get("quizCount", 0), "question"),
        (module.get("problemCount", 0), "worked problem"),
    ]
    return " · ".join(f"{n} {label}{'s' if n != 1 else ''}" for n, label in counts if n)


def _module(w: _Writer, course: dict[str, Any], module: dict[str, Any], unit: str) -> Counter[str]:
    mdir = COURSES_DIR / course["id"] / module["id"]
    readme = _sections(_body(mdir / "readme.md"), 2)
    w.add(f"### {module['title']}", "", f"`{course['id']}/{module['id']}`", "")
    what = _first_paragraph(readme.get("What it is", [])) or module.get("summary", "")
    w.quote("What it is", what)
    w.quote("From the syllabus", unit)
    w.quote("Builds on and feeds into", _text(readme.get("Builds on and feeds into", [])))
    if practice := _practice(module):
        w.add(f"**Practice:** {practice}", "")
    lessons = [x["id"] for x in module["lessons"] if not x.get("private")]
    uses: Counter[str] = Counter()
    nearby: Counter[str] = Counter()
    tiers = Counter(w.cat.lessons[lid].tier for lid in lessons)
    counts = [f"{tiers[t]} {t}" for t in TIERS if tiers[t]]
    if tiers[""]:
        counts.append(f"{tiers['']} not yet tiered")
    if counts:
        w.add(f"**Tier:** {' · '.join(counts)}", "")
    w.add(f"**Notes** ({len(lessons)}, in reading order)", "")
    section = ""
    for lid in lessons:
        rec = w.cat.lessons[lid]
        w.module_of[lid] = (f"{course['id']}/{module['id']}", module["title"])
        if rec.section and rec.section != section:
            section = rec.section
            w.add("", f"*{section}*", "")
        linked, near = _lesson(w, lid)
        uses.update(linked)
        nearby.update(near)
    w.add("")
    if uses:
        rows = [f"{w.page(p)} ({w.cat.wiki[p].domain}, {n})" for p, n in uses.most_common()]
        w.add(
            f"**Wiki pages this module links** ({len(uses)}; directory, notes linking): {' · '.join(rows)}",
            "",
        )
    else:
        w.add("**Wiki pages this module links:** none", "")
    w.linked.update(uses)
    return uses


def _course(w: _Writer, course: dict[str, Any]) -> set[str]:
    cdir = COURSES_DIR / course["id"]
    front = _sections(_body(cdir / FRONT / "readme.md"), 2)
    units = _units(cdir)
    w.add(f"## {course['title']}", "", course.get("summary", ""), "")
    for name in COURSE_SECTIONS:
        heading = next((h for h in front if h.startswith(name)), None)
        if heading:
            w.quote(heading, _text(front[heading]))
    seen: set[str] = set()
    pages: set[str] = set()
    for module in course["modules"]:
        key = f"{course['id']}/{module['id']}"
        seen.add(key)
        pages |= _module(w, course, module, units.get(key, "")).keys()
    # A unit taught in another course's module (data science 04 is generative AI 09).
    for key, text in units.items():
        if key not in seen and not key.startswith(f"{course['id']}/"):
            w.add(f"### {key} (taught in another course)", "", text, "")
    return pages


def _note(w: _Writer, lid: str) -> str:
    rec = w.cat.lessons[lid]
    tier = f", {rec.tier}" if rec.tier else ""
    return f"[{rec.title}]({w.rel(COURSES_DIR / f'{lid}.md')}) ({w.module_of[lid][1]}{tier})"


def _competencies(w: _Writer) -> None:
    by_note: dict[str, list[labs.Lab]] = {}
    for lab in labs.all_labs().values():
        for lid in lab.notes:
            by_note.setdefault(lid, []).append(lab)
    terms = [t for t in glossary.load_terms() if t.page in w.cat.wiki]
    untaught: list[str] = []
    undemonstrated = 0
    body: list[str] = []
    for term in sorted(terms, key=lambda t: t.label.lower()):
        page = term.page or ""
        notes = w.where.get(page, [])
        if not notes:
            untaught.append(f"{term.label} ({w.page(page)})")
            continue
        first = w.module_of[notes[0]][0]
        later = Counter(w.module_of[lid][1] for lid in notes if w.module_of[lid][0] != first)
        shown = {lab.id: lab for lid in notes for lab in by_note.get(lid, [])}
        undemonstrated += not shown
        body.append(f"- **{term.label}** → {w.page(page)}")
        body.append(f"  - Introduced: {_note(w, notes[0])}")
        if later:
            body.append(
                f"  - Developed in: {' · '.join(f'{m} ({n})' for m, n in later.most_common())}"
            )
        demo = " · ".join(f"[{lab.title}]({w.rel(COURSES_DIR / lab.id)})" for lab in shown.values())
        body.append(f"  - Demonstrated by: {demo or 'no lab'}")
    w.add(
        "## Competency map",
        "",
        "One entry per glossary term (`data/glossary.yaml`) whose page is public. **Introduced** is "
        "the first note, in course order, that links the term's page; **Developed in** counts the "
        "notes in other modules that link it; **Demonstrated by** is every lab whose manifest says "
        "it demonstrates one of those notes. Embedding-only links are not counted. "
        f"{len(terms) - len(untaught)} of {len(terms)} terms are taught; {undemonstrated} of those "
        "have no lab.",
        "",
        *body,
        "",
    )
    if untaught:
        w.add(f"**Terms no note links:** {' · '.join(untaught)}", "")
    shared = []
    for pid, notes in w.where.items():
        modules = {w.module_of[lid][0] for lid in notes}
        if len(modules) >= SHARED_MODULES:
            tiers = Counter(w.cat.lessons[lid].tier or "untiered" for lid in notes)
            shared.append((len(modules), len(notes), pid, tiers))
    shared.sort(key=lambda x: (-x[0], -x[1], w.cat.wiki[x[2]].title.lower()))
    w.add(
        f"### Pages linked from {SHARED_MODULES} or more modules",
        "",
        "Each is either a thread the course returns to on purpose or a topic taught twice. A "
        "page linked at the same tier in several modules is the likelier duplicate.",
        "",
        "| Page | Modules | Notes | Tiers |",
        "|---|---|---|---|",
        *(
            f"| {w.page(pid)} | {m} | {n} | "
            f"{' · '.join(f'{c} {t}' for t, c in tiers.most_common())} |"
            for m, n, pid, tiers in shared
        ),
        "",
    )


def _unlinked(w: _Writer) -> None:
    by_domain: dict[str, list[str]] = {}
    for pid, ref in w.cat.wiki.items():
        if pid not in w.linked:
            by_domain.setdefault(ref.domain, []).append(pid)
    w.add("## Wiki pages no note links", "")
    w.add("Grouped by the course whose wiki area holds the directory, then by directory.", "")
    for area_id, title, domains in [*AREAS, ("", "In no course area", ())]:
        here = sorted(d for d in by_domain if (d in domains if area_id else area_of(d) is None))
        if not here:
            continue
        w.add(f"### {title}", "")
        for d in here:
            pids = sorted(by_domain[d], key=lambda p: w.cat.wiki[p].title.lower())
            w.add(f"- **{d}/** ({len(pids)}): {' · '.join(w.page(p) for p in pids)}")
        w.add("")


def build(out: Path) -> str:
    cat = catalog()
    body = _Writer(cat, out)
    courses = [c for c in cat.courses if c["modules"]]
    rows: list[str] = []
    for course in courses:
        pages = _course(body, course)
        notes = [x["id"] for m in course["modules"] for x in m["lessons"] if not x.get("private")]
        tiered = sum(1 for lid in notes if cat.lessons[lid].tier)
        rows.append(
            f"| {course['title']} | {len(course['modules'])} | {len(notes)} | {tiered} "
            f"| {len(pages)} |"
        )
    _competencies(body)
    _unlinked(body)
    head: list[str] = []
    head.extend(
        (
            "# Syllabus",
            "",
            f"Generated by `uv run librarian courses syllabus` on {date.today().isoformat()} from "
            "`data/courses/` and `data/wiki/`; do not edit by hand. Every course, module and note in "
            "reading order, with each module's objectives quoted from its course's start-here readme "
            "and the wiki pages each note uses. How the pieces connect: "
            "[curriculum-and-wiki.md](curriculum-and-wiki.md).",
            "",
            "Under each note, **Wiki** lists the pages the note links, was compiled into, or names in "
            "its text; **Nearby** lists pages only the embedding matched, which are often wrong. A note's "
            "tier (foundations, practitioner, specialist) follows its title once set. After the "
            "courses: the competency map, then the wiki pages no note links. Private notes and "
            "pages are left out.",
            "",
            "| Course | Modules | Notes | Tiered | Wiki pages linked |",
            "|---|---|---|---|---|",
            *rows,
            "",
        )
    )
    log.info(
        "syllabus.built", courses=len(courses), lessons=len(cat.lessons), linked=len(body.linked)
    )
    return "\n".join([*head, *body.lines]).rstrip() + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses syllabus", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--out", type=Path, default=get_settings().root / "docs" / "syllabus.md")
    args = parser.parse_args(argv)
    args.out.write_text(build(args.out))
    print(f"wrote {args.out}")
    return 0
