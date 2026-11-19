#!/usr/bin/env python3
"""Check that the wiki's prerequisite links agree with the course's tiers.

    librarian courses check tiers

A page's tier is the lowest tier among the notes linking it (`courses.curriculum.placements`).
`- [[X]] — prerequisite-for` on page P says X comes before P, so X at a higher tier than P is an
inversion: either the link is wrong or a note teaching X is tiered too high. Pages no tiered note
links are skipped. Private pages are never read. Exit 1 on any inversion.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from librarian.courses import curriculum
from librarian.courses.depth import TIERS
from librarian.wiki.ontology import typed_edges
from librarian.wiki.pages import WIKI_DIR, PageLinks, _public_pages


def inversions(places: dict[str, dict], pages: list, links: PageLinks) -> list[str]:
    """One "prereq (tier) → page (tier)" line per prerequisite taught after the page it serves."""
    lines: list[str] = []
    for page, prereq in typed_edges(pages, links, "prerequisite-for"):
        tier = places.get(page.stem, {}).get("tier")
        before = places.get(prereq.stem, {}).get("tier")
        if tier and before and TIERS.index(before) > TIERS.index(tier):
            lines.append(f"{prereq.rel} ({before}) is a prerequisite for {page.rel} ({tier})")
    return sorted(lines)


def main(argv: Sequence[str] | None = None) -> int:
    argparse.ArgumentParser(
        prog="librarian courses check tiers",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    ).parse_args(argv)
    places = curriculum.placements(curriculum.snapshot())
    pages = _public_pages(WIKI_DIR)
    lines = inversions(places, pages, PageLinks(pages))
    tiered = sum(1 for p in places.values() if "tier" in p)
    print("\n".join(lines))
    print(f"tier-check: {tiered} tiered pages, {len(lines)} inversions")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
