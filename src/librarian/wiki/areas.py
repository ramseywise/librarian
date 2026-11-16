"""Areas: the atlas ring's coarse grouping of `data/wiki/` directories.

An area reads a few directories as one sector, at the grain of the courses: the directories a
learner meets in the same course share a sector and its colour (an area id is a course id, so
`theme/domains.ts` colours it from the course table). It is an overlay for the map only.
Directories stay the canonical domains for tags, MCP and `/lint`, and no page moves because of
this table. The four subject directories are each their own area; `llm`, `rag`, `eval`,
`memory` and `frameworks/` (adk, langgraph) make Generative AI; the agent-building directories
make AI Engineering. Internal pages (patterns, meta, projects) and interview prep live under
`private/` and are never on the map. A directory in no area is drawn as its own sector;
`librarian wiki sync-check` notes it so the table and the disk cannot drift apart silently.

The sidebar's Domain view is this table as a tree: course (= area), its modules, then pages.
"""

from __future__ import annotations

from typing import Any

# (area id = course id, title, directories). Order is the order of sectors round the ring.
AREAS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("programming", "Programming", ("programming",)),
    ("data-analytics", "Data Analytics", ("data-analytics",)),
    ("data-science", "Data Science", ("data-science",)),
    ("data-engineering", "Data Engineering", ("data-engineering",)),
    ("generative-ai", "Generative AI", ("llm", "rag", "eval", "memory", "frameworks")),
    (
        "ai-engineering",
        "AI Engineering",
        ("prompting", "context", "harness", "loop", "graph", "infra", "mcp", "multimodal"),
    ),
)


def area_of(domain: str) -> str | None:
    """The area a directory belongs to, or None when it is drawn as its own sector."""
    for area_id, _, domains in AREAS:
        if domain in domains:
            return area_id
    return None


def areas_for(domains: list[str] | set[str]) -> list[dict[str, Any]]:
    """The graph payload's `areas`: each area with the directories of it that exist on disk.

    An area none of whose directories exists is left out, so the ring never shows an empty
    sector; directories in no area are absent here and fall back to their own sector.
    """
    present = set(domains)
    out: list[dict[str, Any]] = []
    for area_id, title, area_domains in AREAS:
        here = [d for d in area_domains if d in present]
        if here:
            out.append({"id": area_id, "title": title, "domains": here})
    return out


def unmapped(domains: list[str] | set[str]) -> list[str]:
    """Directories in no area: each is its own sector on the ring."""
    return sorted(d for d in domains if area_of(d) is None)


def ghost_area_domains(domains: list[str] | set[str]) -> list[str]:
    """Directories the table names that are not on disk."""
    present = set(domains)
    return sorted(d for _, _, ds in AREAS for d in ds if d not in present)
