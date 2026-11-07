"""The health numbers: orphan rate, degree, main component, typed-link and stub rates, against their bands."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from librarian.wiki.common import (
    TYPED_LINK_RE,
    WIKILINK_RE,
)
from librarian.wiki.pages import Page, PageLinks, _link_index, _public_pages

# Local heuristics, not research results. Orphan bands and the 80% component line are from
# second-brain-os, whose own docs cite nothing. Degree counts both ends of a link and theirs
# counts one, so their "below two" is the floor of 4 here. The 8-20 band, 200-word stub line,
# 60% component floor and 5% stub rate were chosen here, some after the first snapshot
# (2026-11-05: page degree median 11, p5-p95 5-34; body words p1 191, median 600). The typed
# line is this repo's lint rule. Change them only on evidence from metrics.jsonl snapshots.
ORPHAN_HEALTHY, ORPHAN_BROKEN = 0.05, 0.15
DEGREE_HEALTHY_MIN, DEGREE_HEALTHY_MAX, DEGREE_BROKEN = 8.0, 20.0, 4.0
COMPONENT_HEALTHY, COMPONENT_BROKEN = 0.80, 0.60
TYPED_HEALTHY = 0.50
STUB_HEALTHY = 0.05
STALE_DAYS = 60
STUB_WORDS = 200
TOP_HUBS = 10
_SEE_ALSO_RE = re.compile(r"^(#{1,6})\s+see also\b", re.IGNORECASE)
_HEADING_RE = re.compile(r"^(#{1,6})\s")
_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(\S+)", re.MULTILINE)


def _rate(part: float, whole: float) -> float:
    return part / whole if whole else 0.0


def _see_also_counts(body: str) -> tuple[int, int]:
    """(entries, typed entries) across a page's See Also sections."""
    entries = typed = 0
    level = 0  # heading level of the open See Also section, 0 when outside one
    for line in body.splitlines():
        if heading := _HEADING_RE.match(line):
            see_also = _SEE_ALSO_RE.match(line)
            if see_also:
                level = len(see_also.group(1))
            elif level and len(heading.group(1)) <= level:
                level = 0
            continue
        stripped = line.strip()
        if level and stripped.startswith(("-", "*")) and WIKILINK_RE.search(stripped):
            entries += 1
            typed += bool(TYPED_LINK_RE.match(stripped))
    return entries, typed


def _main_component_size(nodes: list[str], edges: dict[str, set[str]]) -> int:
    """Largest weakly connected component: link direction doesn't matter here."""
    neighbours: dict[str, set[str]] = defaultdict(set)
    for source, targets in edges.items():
        for target in targets:
            neighbours[source].add(target)
            neighbours[target].add(source)
    seen: set[str] = set()
    largest = 0
    for start in nodes:
        if start in seen:
            continue
        stack, size = [start], 0
        seen.add(start)
        while stack:
            size += 1
            for next_node in neighbours[stack.pop()] - seen:
                seen.add(next_node)
                stack.append(next_node)
        largest = max(largest, size)
    return largest


def _open_conflicts(wiki_dir: Path) -> int:
    """Conflict entries whose status isn't Resolved, so an odd status still surfaces."""
    path = wiki_dir / "_conflicts.md"
    if not path.is_file():
        return 0
    return sum(
        not status.lower().startswith("resolved") for status in _STATUS_RE.findall(path.read_text())
    )


def _band_status(healthy: bool, broken: bool) -> str:
    return "healthy" if healthy else "broken" if broken else "watch"


def _link_edges(
    pages: list[Page], links: PageLinks
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Distinct (outbound, inbound) links between scored pages, keyed by rel. No self-links."""
    outbound: dict[str, set[str]] = {p.rel: set() for p in pages}
    inbound: dict[str, set[str]] = {p.rel: set() for p in pages}
    for page in pages:
        for match in WIKILINK_RE.finditer(page.body):
            target = links.resolve(match.group(1))
            if target is not None and target.scored and target.rel != page.rel:
                outbound[page.rel].add(target.rel)
                inbound[target.rel].add(page.rel)
    return outbound, inbound


def compute_stats(wiki_dir: Path, today: date) -> dict[str, Any]:
    """The six health numbers plus page count, hubs, domains and open conflicts.

    Private pages, tombstones and underscore files are out of every rate. Links to or from
    them make no edge. Degree counts distinct directed page pairs, so a page linking the
    same target twice adds one edge. Word counts cover the body including See Also.
    """
    public = _public_pages(wiki_dir)
    pages = [p for p in public if p.scored]
    links = _link_index(public)
    total = len(pages)

    outbound, inbound = _link_edges(pages, links)
    see_also = typed = stale = undated = stubs = 0
    cutoff = today - timedelta(days=STALE_DAYS)
    for page in pages:
        entries, typed_entries = _see_also_counts(page.body)
        see_also += entries
        typed += typed_entries
        if page.updated is None:
            undated += 1
        elif page.updated < cutoff:
            stale += 1
        stubs += len(page.body.split()) < STUB_WORDS

    orphan = _rate(sum(not inbound[p.rel] for p in pages), total)
    degree = _rate(sum(len(v) for v in outbound.values()) * 2, total)
    component = _rate(_main_component_size([p.rel for p in pages], outbound), total)
    stale_rate = _rate(stale, total)
    typed_rate = _rate(typed, see_also)
    stub_rate = _rate(stubs, total)

    def metric(value: float, status: str) -> dict[str, Any]:
        return {"value": round(value, 4), "status": status if total else "no-data"}

    hubs = sorted(pages, key=lambda p: (-(len(inbound[p.rel]) + len(outbound[p.rel])), p.rel))
    return {
        "date": today.isoformat(),
        "pages": total,
        "metrics": {
            "orphan_rate": metric(
                orphan, _band_status(orphan < ORPHAN_HEALTHY, orphan > ORPHAN_BROKEN)
            ),
            "average_degree": metric(
                degree,
                _band_status(
                    DEGREE_HEALTHY_MIN <= degree <= DEGREE_HEALTHY_MAX, degree < DEGREE_BROKEN
                ),
            ),
            "main_component": metric(
                component,
                _band_status(component >= COMPONENT_HEALTHY, component < COMPONENT_BROKEN),
            ),
            "stale_rate": metric(stale_rate, "report"),
            "typed_link_rate": metric(typed_rate, _band_status(typed_rate >= TYPED_HEALTHY, False)),
            "stub_rate": metric(stub_rate, _band_status(stub_rate < STUB_HEALTHY, False)),
        },
        "hubs": [
            {
                "page": p.rel.removesuffix(".md"),
                "title": p.title,
                "inbound": len(inbound[p.rel]),
                "outbound": len(outbound[p.rel]),
            }
            for p in hubs[:TOP_HUBS]
        ],
        "domains": dict(sorted(Counter(p.domain for p in pages).items())),
        "open_conflicts": _open_conflicts(wiki_dir),
        "undated_pages": undated,  # no usable `updated`: not counted as stale, not known fresh
        "unparsed_pages": sum(not p.parsed for p in pages),
    }


METRIC_LABELS = {
    "orphan_rate": ("Orphan rate", True),
    "average_degree": ("Average degree", False),
    "main_component": ("Main component", True),
    "stale_rate": ("Stale rate", True),
    "typed_link_rate": ("Typed-link rate", True),
    "stub_rate": ("Stub rate", True),
}


def _render_stats(stats: dict[str, Any]) -> str:
    lines = []
    for key, (label, is_rate) in METRIC_LABELS.items():
        metric = stats["metrics"][key]
        value = f"{metric['value']:.1%}" if is_rate else f"{metric['value']:.2f}"
        lines.append(f"{label:<16} {value:>7}  {metric['status']}")
    lines += ["", f"Pages: {stats['pages']}", "", "Top hubs (in + out):"]
    lines += [
        f"  {h['inbound'] + h['outbound']:>4}  {h['page']}  ({h['inbound']} in, {h['outbound']} out)"
        for h in stats["hubs"]
    ]
    lines += ["", "Pages per domain:"]
    lines += [f"  {count:>4}  {domain}" for domain, count in stats["domains"].items()]
    lines += ["", f"Open conflicts: {stats['open_conflicts']}"]
    if stats["undated_pages"]:
        lines.append(f"Undated pages: {stats['undated_pages']}")
    if stats["unparsed_pages"]:
        lines.append(f"Pages with broken frontmatter: {stats['unparsed_pages']}")
    return "\n".join(lines)
