"""Curriculum facet of the graph: which wiki pages each course, module and note covers.

An overlay on the course catalog, not a taxonomy: wiki directories stay the canonical
domains (CLAUDE.md). A page may sit under several modules, and pages no lesson links to
stay reachable through `beyond`, grouped by directory.

The catalog's cold build takes 6-26 s, which must not hold up the map's filter panel, so
the facet is saved to a snapshot after each build and served from it straight away.
`stale: true` tells the client a newer snapshot is coming. Private lessons (data/courses/private/) are
left out of it. Private pages can't leak from
an old snapshot: the catalog excludes them and `_present` filters against the current
public set.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from typing import Any

from librarian.config import get_settings
from librarian.courses.catalog import COURSES_DIR, WIKI_DIR, Catalog, _signature, catalog
from librarian.courses.depth import TIERS
from librarian.log_config import get_logger
from librarian.wiki.parser import public_page_domains

log = get_logger(__name__)

SNAPSHOT = get_settings().curriculum_snapshot
# Orientation pages and reading lists rather than a subject: the first would link to
# everything, the second is always empty and would read as a gap in the wiki.
SKIPPED_MODULES = {"00-start-here", "sources"}
# About the wiki or a project, not a topic: most wrong links in the 2026-11-04 audit landed
# here (LC 207 "Course Schedule" → the learn-ai-engineering project page).
SKIPPED_DOMAINS = {"projects", "meta"}


def _current_signature() -> list[int]:
    return list(_signature(COURSES_DIR, WIKI_DIR))


def _build(cat: Catalog, signature: list[int]) -> dict[str, Any]:
    """Course → module → pages, best-linked first, plus each page's main course.

    Each module also lists its notes in reading order with the pages each links: the map's
    third level, and the order "Course order" reads pages in.
    """
    votes: dict[str, Counter[str]] = {}
    courses: list[dict[str, Any]] = []
    for course in cat.courses:
        modules: list[dict[str, Any]] = []
        for module in course["modules"]:
            # Private lessons add nothing: the snapshot feeds the public map, and a module
            # only they make up would put its name there.
            public_lessons = [lesson for lesson in module["lessons"] if not lesson.get("private")]
            if module["id"] in SKIPPED_MODULES or module.get("private"):
                continue
            links: Counter[str] = Counter()
            notes: list[dict[str, Any]] = []
            for outline in public_lessons:
                rec = cat.lessons[outline["id"]]
                pages = [
                    pid
                    for pid in rec.concepts
                    if pid in cat.wiki and cat.wiki[pid].domain not in SKIPPED_DOMAINS
                ]
                links.update(pages)
                notes.append(
                    {
                        "id": rec.id,
                        "title": rec.title,
                        **({"tier": rec.tier} if rec.tier else {}),
                        "pageIds": pages,
                    }
                )
            for pid, n in links.items():
                votes.setdefault(pid, Counter())[course["id"]] += n
            modules.append(
                {
                    "id": module["id"],
                    "title": module["title"],
                    "firstLesson": public_lessons[0]["id"] if public_lessons else None,
                    "pageIds": [pid for pid, _ in links.most_common()],
                    "notes": notes,
                }
            )
        if modules:  # an empty directory under data/courses/ is listed but has nothing to filter
            courses.append({"id": course["id"], "title": course["title"], "modules": modules})
    # most_common keeps first-seen order on a tie, so the earlier course wins.
    primary = {pid: c.most_common(1)[0][0] for pid, c in votes.items()}
    return {"signature": signature, "courses": courses, "primaryCourse": primary}


def placements(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Page → where the course teaches it: `tier`, the lowest tier among the notes linking it
    (omitted while none of them is tiered), and `modules`, each `course/module` in course order.

    Derived, never written to wiki frontmatter: it moves whenever a note is tiered or relinked.
    """
    out: dict[str, dict[str, Any]] = {}
    for course in snapshot["courses"]:
        for module in course["modules"]:
            key = f"{course['id']}/{module['id']}"
            for note in module.get("notes", []):
                for pid in note["pageIds"]:
                    place = out.setdefault(pid, {"modules": []})
                    if key not in place["modules"]:
                        place["modules"].append(key)
                    tier = note.get("tier")
                    if tier in TIERS and (
                        "tier" not in place or TIERS.index(tier) < TIERS.index(place["tier"])
                    ):
                        place["tier"] = tier
    return out


def placement(page_id: str) -> dict[str, Any] | None:
    """`placements()` for one page from the saved snapshot; None with no snapshot or no
    linking note. Never builds the catalog, so a caller like MCP `read_page` stays fast."""
    snapshot = _read_snapshot()
    return None if snapshot is None else placements(snapshot).get(page_id)


def _present(snapshot: dict[str, Any], signature: list[int]) -> dict[str, Any]:
    """Client payload: snapshot narrowed to current public pages, the rest under `beyond`."""
    domains = public_page_domains()
    placed: set[str] = set()
    courses = []
    for course in snapshot["courses"]:
        modules = []
        for module in course["modules"]:
            pages = [pid for pid in module["pageIds"] if pid in domains]
            placed.update(pages)
            # A snapshot from before notes were listed has none; the next build adds them.
            notes = [
                {**n, "pageIds": [pid for pid in n["pageIds"] if pid in domains]}
                for n in module.get("notes", [])
            ]
            modules.append({**module, "pageIds": pages, "notes": notes})
        pages = list(dict.fromkeys(pid for m in modules for pid in m["pageIds"]))
        courses.append({**course, "modules": modules, "pageIds": pages})
    beyond: dict[str, list[str]] = {}
    for pid in sorted(domains.keys() - placed):
        beyond.setdefault(domains[pid], []).append(pid)
    return {
        "courses": courses,
        "beyond": [{"domain": d, "pageIds": beyond[d]} for d in sorted(beyond)],
        "primaryCourse": {p: c for p, c in snapshot["primaryCourse"].items() if p in placed},
        # Foundations first on the map: only tiered pages, the rest read as not yet tiered.
        "pageTier": {
            pid: place["tier"]
            for pid, place in placements(snapshot).items()
            if pid in placed and "tier" in place
        },
        "stale": snapshot["signature"] != signature,
    }


def _read_snapshot() -> dict[str, Any] | None:
    try:
        return json.loads(SNAPSHOT.read_text())
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        log.warning("curriculum.snapshot.unreadable", error=str(e))
        return None


def write_snapshot() -> dict[str, Any] | None:
    """Rebuild the snapshot from the catalog. Never raises: it is a startup optimisation."""
    try:
        # Taken before the catalog, so a change during the build reads as stale.
        snapshot = _build(catalog(), _current_signature())
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        tmp = SNAPSHOT.with_suffix(".tmp")
        tmp.write_text(json.dumps(snapshot))
        os.replace(tmp, SNAPSHOT)
    except Exception as e:  # the route builds on demand and reports real errors
        log.warning("curriculum.snapshot.failed", error=str(e))
        return None
    return snapshot


def snapshot() -> dict[str, Any]:
    """The saved snapshot, or a fresh build when there is none yet."""
    return _read_snapshot() or _build(catalog(), _current_signature())


def current_curriculum() -> dict[str, Any]:
    """The facet for the current catalog; with no snapshot yet it waits on the catalog build."""
    signature = _current_signature()
    snapshot = _read_snapshot() or _build(catalog(), signature)
    return _present(snapshot, signature)
