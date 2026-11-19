"""Tier inversions between wiki prerequisite links and course tiers (courses/checks/tier_order.py)."""

from __future__ import annotations

from pathlib import Path

from librarian.courses.checks.tier_order import inversions
from librarian.wiki.pages import PageLinks, _public_pages


def _page(wiki: Path, rel: str, see_also: str = "") -> None:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    title = path.stem.replace("-", " ").title()
    path.write_text(
        f"---\ntitle: {title}\ntags: [rag, concept]\n---\n\n# {title}\n\n## See Also\n{see_also}\n"
    )


def test_prerequisite_tiered_above_its_page_is_an_inversion(tmp_path: Path) -> None:
    _page(
        tmp_path,
        "rag/basics.md",
        "- [[Advanced]] — prerequisite-for\n- [[Middle]] — prerequisite-for",
    )
    _page(tmp_path, "rag/advanced.md")
    _page(tmp_path, "rag/middle.md")
    _page(tmp_path, "rag/untiered.md", "- [[Advanced]] — prerequisite-for")
    pages = _public_pages(tmp_path)
    places = {
        "basics": {"tier": "foundations"},
        "advanced": {"tier": "specialist"},
        "middle": {"tier": "foundations"},
        "untiered": {"modules": ["ai/rag"]},
    }
    assert inversions(places, pages, PageLinks(pages)) == [
        "rag/advanced.md (specialist) is a prerequisite for rag/basics.md (foundations)"
    ]
