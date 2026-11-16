"""The atlas's area table (librarian/wiki/areas.py) and where it reaches the payload."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.wiki import areas


@pytest.mark.unit
def test_every_directory_is_in_at_most_one_area() -> None:
    seen: list[str] = []
    for _, _, domains in areas.AREAS:
        seen.extend(domains)
    assert len(seen) == len(set(seen))
    assert len({a for a, _, _ in areas.AREAS}) == len(areas.AREAS)


@pytest.mark.unit
def test_areas_for_keeps_only_directories_on_disk_and_their_order() -> None:
    out = areas.areas_for(["eval", "rag", "deep-agents", "data-science"])
    assert out == [
        {"id": "data-science", "title": "Data Science", "domains": ["data-science"]},
        {"id": "generative-ai", "title": "Generative AI", "domains": ["rag", "eval"]},
    ]
    assert areas.unmapped(["eval", "rag", "deep-agents", "data-science"]) == ["deep-agents"]
    assert "frameworks" in areas.ghost_area_domains(["eval", "rag"])
    assert areas.area_of("mcp") == "ai-engineering"
    assert areas.area_of("frameworks") == "generative-ai"
    assert areas.area_of("patterns") is None


@pytest.mark.unit
def test_area_table_matches_the_wiki_on_disk() -> None:
    """Every public directory is in an area: the internal ones (patterns, meta, projects) and
    interview prep live under private/, which is never on the map."""
    wiki = Path(__file__).resolve().parents[2] / "data" / "wiki"
    if not wiki.is_dir():
        pytest.skip("no data/wiki/ checkout")
    on_disk = {d.name for d in wiki.iterdir() if d.is_dir() and d.name != "private"}
    assert areas.ghost_area_domains(on_disk) == []
    assert areas.unmapped(on_disk) == []
