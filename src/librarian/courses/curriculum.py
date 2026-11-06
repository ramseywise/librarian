"""Curriculum facet of the graph: which wiki pages each course and module covers.

An overlay on the course catalog, not a taxonomy: wiki directories stay the canonical
domains (CLAUDE.md). A page may sit under several modules, and pages no lesson links to
stay reachable through `beyond`, grouped by directory.

The catalog's cold build takes 6-26 s, which must not hold up the map's filter panel, so
the facet is saved to a snapshot after each build and served from it straight away.
`stale: true` tells the client a newer snapshot is coming. Private pages can't leak from
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
    """Course → module → pages, best-linked first, plus each page's main course."""
    votes: dict[str, Counter[str]] = {}
    courses: list[dict[str, Any]] = []
    for course in cat.courses:
        modules: list[dict[str, Any]] = []
        for module in course["modules"]:
            if module["id"] in SKIPPED_MODULES:
                continue
            links: Counter[str] = Counter()
            for outline in module["lessons"]:
                links.update(
                    pid
                    for pid in cat.lessons[outline["id"]].concepts
                    if pid in cat.wiki and cat.wiki[pid].domain not in SKIPPED_DOMAINS
                )
            for pid, n in links.items():
                votes.setdefault(pid, Counter())[course["id"]] += n
            modules.append(
                {
                    "id": module["id"],
                    "title": module["title"],
                    "firstLesson": module["lessons"][0]["id"] if module["lessons"] else None,
                    "pageIds": [pid for pid, _ in links.most_common()],
                }
            )
        if modules:  # an empty directory under data/courses/ is listed but has nothing to filter
            courses.append({"id": course["id"], "title": course["title"], "modules": modules})
    # most_common keeps first-seen order on a tie, so the earlier course wins.
    primary = {pid: c.most_common(1)[0][0] for pid, c in votes.items()}
    return {"signature": signature, "courses": courses, "primaryCourse": primary}


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
            modules.append({**module, "pageIds": pages})
        pages = list(dict.fromkeys(pid for m in modules for pid in m["pageIds"]))
        courses.append({**course, "modules": modules, "pageIds": pages})
    beyond: dict[str, list[str]] = {}
    for pid in sorted(domains.keys() - placed):
        beyond.setdefault(domains[pid], []).append(pid)
    return {
        "courses": courses,
        "beyond": [{"domain": d, "pageIds": beyond[d]} for d in sorted(beyond)],
        "primaryCourse": {p: c for p, c in snapshot["primaryCourse"].items() if p in placed},
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


def current_curriculum() -> dict[str, Any]:
    """The facet for the current catalog; with no snapshot yet it waits on the catalog build."""
    signature = _current_signature()
    snapshot = _read_snapshot() or _build(catalog(), signature)
    return _present(snapshot, signature)
