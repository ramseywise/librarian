from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from etl.researcher.extractor import extract_toc

MAX_CHUNK_PAGES = 20

TOC_PATTERNS = [
    re.compile(
        r"^(Chapter\s+\d+[:.–-]?\s*.+?)\s+(\d+)\s*$", re.MULTILINE | re.IGNORECASE
    ),
    re.compile(r"^(\d+\.\s+[A-Z].+?)\s+(\d+)\s*$", re.MULTILINE),
    re.compile(r"^(\d+\s+[A-Z][a-z].+?)\s+(\d+)\s*$", re.MULTILINE),
]


class Chunk(BaseModel):
    start_page: int
    end_page: int
    title: str


def _parse_toc(toc_text: str, total_pages: int) -> list[tuple[str, int]]:
    """Return list of (section_title, start_page) sorted by page number.

    Returns empty list if no TOC patterns matched.
    """
    hits: dict[int, str] = {}
    for pattern in TOC_PATTERNS:
        for match in pattern.finditer(toc_text):
            title = match.group(1).strip()
            page = int(match.group(2))
            if 1 <= page <= total_pages and page not in hits:
                hits[page] = title

    if not hits:
        return []

    # Return as (title, page) sorted by page number
    return [(title, page) for page, title in sorted(hits.items())]


def _hard_split(page_count: int) -> list[Chunk]:
    """Split at MAX_CHUNK_PAGES boundaries with titles 'Part 1', 'Part 2', etc."""
    chunks: list[Chunk] = []
    start = 1
    part = 1
    while start <= page_count:
        end = min(start + MAX_CHUNK_PAGES - 1, page_count)
        chunks.append(Chunk(start_page=start, end_page=end, title=f"Part {part}"))
        start = end + 1
        part += 1
    return chunks


def _sections_to_chunks(
    sections: list[tuple[str, int]], page_count: int
) -> list[Chunk]:
    """Convert sorted (title, start_page) pairs into Chunk objects respecting MAX_CHUNK_PAGES.

    If a chapter spans more than MAX_CHUNK_PAGES, it is sub-split with title suffixes.
    """
    chunks: list[Chunk] = []

    for i, (title, start) in enumerate(sections):
        end = sections[i + 1][1] - 1 if i + 1 < len(sections) else page_count
        span = end - start + 1

        if span <= MAX_CHUNK_PAGES:
            chunks.append(Chunk(start_page=start, end_page=end, title=title))
        else:
            # Sub-split the oversized section
            part = 1
            sub_start = start
            while sub_start <= end:
                sub_end = min(sub_start + MAX_CHUNK_PAGES - 1, end)
                chunks.append(
                    Chunk(
                        start_page=sub_start,
                        end_page=sub_end,
                        title=f"{title} (Part {part})",
                    )
                )
                sub_start = sub_end + 1
                part += 1

    return chunks


def plan_chunks(pdf_path: Path, page_count: int) -> list[Chunk]:
    """Return a list of Chunk objects covering all pages of the PDF.

    - Single chunk if page_count <= MAX_CHUNK_PAGES.
    - TOC-detected section chunks if TOC is parseable.
    - Hard-split fallback otherwise.
    """
    if page_count <= MAX_CHUNK_PAGES:
        return [Chunk(start_page=1, end_page=page_count, title="Full Document")]

    toc_text = extract_toc(pdf_path)
    sections = _parse_toc(toc_text, page_count)

    if sections:
        return _sections_to_chunks(sections, page_count)

    return _hard_split(page_count)
