"""The gaps list: unanswered questions, curriculum modules with no page and lesson links with no page."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from librarian.wiki.common import (
    WIKILINK_RE,
    fm,
    link_name,
    slugify,
)
from librarian.wiki.leak_check import _names_private_page, _private_name_pattern
from librarian.wiki.oplog import ASKED_FILE, GAPS_FILE, _read_loose_jsonl, _write_text
from librarian.wiki.pages import PageLinks, _link_index, _private_pages, _public_pages

TOP_GAPS = 5
# Real questions only: `eval`, `sweep`, `diag` and `review_smoke` rows are harness traffic.
QUERY_TOOLS = {"search_wiki", "search_courses"}
# The retrieval log has no score field, and the blended score the server computes is
# rank-based, with no absolute meaning. So the only defensible floor is "returned nothing".
ASKED_FLOOR_NOTE = (
    "Floor: a query counts as unanswered only if its latest healthy search returned zero results. "
    "logs/retrieval.jsonl carries no scores, so weak matches are invisible here."
)
_GAP_LINE_RE = re.compile(r"^- (.+) \| first seen (\d{4}-\d{2}-\d{2}) \| count \d+$", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass
class Gap:
    name: str
    first_seen: str
    count: int


@dataclass
class AskedGaps:
    gaps: list[Gap]
    withheld: int  # named a private page, so not written out
    degraded_skipped: int  # zero results while retrieval was degraded: no evidence either way


def _asked_gaps(
    telemetry_dir: Path,
    retrieval_log: Path,
    public: PageLinks,
    private_names: re.Pattern[str] | None,
) -> AskedGaps:
    seen: dict[str, dict[str, Any]] = {}

    def add(topic: str, day: str) -> None:
        key = " ".join(topic.lower().split())
        entry = seen.setdefault(key, {"name": " ".join(topic.split()), "first": day, "count": 0})
        entry["first"] = min(entry["first"], day)
        entry["count"] += 1

    for row in _read_loose_jsonl(telemetry_dir / ASKED_FILE):
        if row.get("topic"):
            add(str(row["topic"]), str(row.get("date", ""))[:10])

    # A query later answered is no longer a gap, so only the latest healthy search counts.
    misses: dict[str, list[tuple[str, str]]] = defaultdict(list)
    latest_hit: dict[str, bool] = {}
    degraded_skipped = 0
    for row in _read_loose_jsonl(retrieval_log):
        if row.get("tool") not in QUERY_TOOLS or not row.get("query"):
            continue
        key = " ".join(str(row["query"]).lower().split())
        hit = bool(row.get("n_results"))
        if row.get("degraded"):
            degraded_skipped += not hit
            continue
        latest_hit[key] = hit
        if not hit:
            misses[key].append((str(row["query"]), str(row.get("ts", ""))[:10]))
    for key, rows in misses.items():
        if not latest_hit[key]:
            for query, day in rows:
                add(query, day)

    gaps: list[Gap] = []
    withheld = 0
    for key, entry in seen.items():
        if _names_private_page(entry["name"], private_names):
            withheld += 1
        elif (page := public.resolve(key, include_tombstones=True)) is None or not page.scored:
            gaps.append(Gap(entry["name"], entry["first"], entry["count"]))
    return AskedGaps(gaps, withheld, degraded_skipped)


@dataclass
class CourseGaps:
    modules: list[Gap]  # first_seen filled in by _apply_first_seen
    links: list[Gap]
    withheld: int  # lesson links into private pages or tombstones
    note: str | None  # why the course sections couldn't be computed


def _course_gaps(
    courses_dir: Path, wiki_dir: Path, public: PageLinks, private: PageLinks
) -> CourseGaps:
    """Empty curriculum modules and lesson links with no page.

    Builds the catalog with semantic linking off: that path loads an embedding model, and
    a gap list that shifts with the model's state wouldn't be deterministic. A module counts
    as covered through explicit, compiled or title-mention links, a stricter bar than the
    map's filter panel, which also shows embedding neighbours.
    """
    try:
        from librarian.courses import catalog as courses
        from librarian.courses import curriculum
    except ImportError as e:
        return CourseGaps(
            [], [], 0, f"unavailable: {e.name or 'import'} missing (needs the api extra)"
        )

    original = courses._semantic_neighbours
    courses._semantic_neighbours = lambda *_: None
    try:
        signature = courses._signature(courses_dir, wiki_dir)
        cat = courses._load(courses_dir, wiki_dir, signature)
        built = curriculum._build(cat, [])
    except (yaml.YAMLError, OSError, ValueError) as e:
        return CourseGaps([], [], 0, f"unavailable: {type(e).__name__} while reading the courses")
    finally:
        courses._semantic_neighbours = original

    # Private lessons (data/courses/private/) never count: gaps.md must not name their modules
    # or the pages they link to.
    lesson_counts = {
        (c["id"], m["id"]): sum(not lesson.get("private") for lesson in m["lessons"])
        for c in cat.courses
        for m in c["modules"]
    }
    modules: list[Gap] = []
    for course in built["courses"]:
        for module in course["modules"]:
            lessons = lesson_counts.get((course["id"], module["id"]), 0)
            if lessons and not module["pageIds"]:
                name = f"{course['id']}/{module['id']}: {module['title']}"
                modules.append(Gap(name, "", lessons))

    linking: dict[str, set[str]] = defaultdict(set)
    names: dict[str, str] = {}
    withheld: set[str] = set()
    for lesson_id, rec in cat.lessons.items():
        if rec.private:
            continue
        post = frontmatter.load(courses_dir / f"{lesson_id}.md")
        targets = [str(t) for t in fm(post).get("wiki") or []]
        # Code holds things like [[1, 2]]: not links.
        prose = _INLINE_CODE_RE.sub("", courses._prose(post.content))
        targets += [m.group(1) for m in WIKILINK_RE.finditer(prose)]
        for target in targets:
            slug = slugify(link_name(target))
            if not re.search(r"[a-z]", slug):
                continue
            if (page := public.resolve(target, include_tombstones=True)) is not None:
                if not page.scored:
                    withheld.add(slug)
            elif private.resolve(target, only_private=True) is not None:
                withheld.add(slug)
            else:
                linking[slug].add(lesson_id)
                names.setdefault(slug, target.strip())
    links = [Gap(names[slug], "", len(ids)) for slug, ids in linking.items()]
    return CourseGaps(modules, links, len(withheld), None)


def _apply_first_seen(gaps: list[Gap], previous: dict[str, str], today: str) -> None:
    """Earliest of what the sources say and what the last gaps.md recorded."""
    for gap in gaps:
        known = [d for d in (gap.first_seen, previous.get(gap.name)) if d]
        gap.first_seen = min(known) if known else today


def _sorted_gaps(gaps: list[Gap]) -> list[Gap]:
    return sorted(gaps, key=lambda g: (-g.count, g.first_seen, g.name.lower()))


def _gap_lines(gaps: list[Gap]) -> list[str]:
    return [f"- {g.name} | first seen {g.first_seen} | count {g.count}" for g in gaps] or ["- none"]


def regenerate_gaps(
    wiki_dir: Path, telemetry_dir: Path, courses_dir: Path, retrieval_log: Path, today: date
) -> list[str]:
    """Write gaps.md; returns its top five lines, real demand (asked) ranked first."""
    public_pages = _public_pages(wiki_dir)
    private_pages = _private_pages(wiki_dir)
    public = _link_index(public_pages)
    private = _link_index(private_pages)
    path = telemetry_dir / GAPS_FILE
    previous = dict(_GAP_LINE_RE.findall(path.read_text())) if path.is_file() else {}

    asked = _asked_gaps(telemetry_dir, retrieval_log, public, _private_name_pattern(private_pages))
    course = _course_gaps(courses_dir, wiki_dir, public, private)
    day = today.isoformat()
    for group in (asked.gaps, course.modules, course.links):
        _apply_first_seen(group, previous, day)
    asked_sorted = _sorted_gaps(asked.gaps)
    modules = _sorted_gaps(course.modules)
    links = _sorted_gaps(course.links)

    lines = [
        f"# Wiki gaps ({day})",
        "",
        "Generated by `librarian wiki gaps`; do not edit. Gitignored: holds query history.",
        "",
        "## Asked, not answered",
        "",
        ASKED_FLOOR_NOTE,
    ]
    if asked.degraded_skipped:
        lines.append(f"Skipped {asked.degraded_skipped} empty results from degraded retrieval.")
    if asked.withheld:
        lines.append(f"Withheld {asked.withheld} that name a private page.")
    lines += ["", *_gap_lines(asked_sorted), "", "## Curriculum modules with no page", ""]
    lines.append(
        "Covered means an explicit, compiled or title-mention link from a lesson; "
        "embedding neighbours don't count. Count is the module's lessons."
    )
    lines += ["", *([f"- {course.note}"] if course.note else _gap_lines(modules))]
    lines += ["", "## Linked from lessons, missing in wiki", ""]
    lines.append("Count is the lessons linking it.")
    if course.withheld:
        lines.append(f"Withheld {course.withheld} that point at a private or retired page.")
    lines += ["", *([f"- {course.note}"] if course.note else _gap_lines(links)), ""]
    _write_text(path, "\n".join(lines))

    ranked = [
        *(("asked", g) for g in asked_sorted),
        *(("lesson link", g) for g in links),
        *(("module", g) for g in modules),
    ]
    return [
        f"{kind}: {g.name} (first seen {g.first_seen}, count {g.count})"
        for kind, g in ranked[:TOP_GAPS]
    ]
