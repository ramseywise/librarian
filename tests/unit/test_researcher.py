"""Unit tests for core/researcher/ — chunker, models, writer."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from core.researcher.chunker import (
    _hard_split,
    _parse_toc,
    _sections_to_chunks,
    plan_chunks,
)
from core.researcher.models import Note, NoteMetadata
from core.researcher.writer import render_note, sanitize_filename

# ===========================================================================
# chunker.py
# ===========================================================================


class TestParseToc:
    def test_chapter_pattern_matched(self) -> None:
        toc = "Chapter 1: Introduction     5\nChapter 2: Methods     25\n"
        result = _parse_toc(toc, total_pages=100)
        assert len(result) == 2
        titles = [r[0] for r in result]
        assert any("Introduction" in t for t in titles)

    def test_numbered_section_pattern(self) -> None:
        toc = "1. Background Information     3\n2. Related Work     15\n"
        result = _parse_toc(toc, total_pages=50)
        assert len(result) == 2

    def test_empty_text_returns_empty(self) -> None:
        result = _parse_toc("", total_pages=50)
        assert result == []

    def test_no_matching_patterns_returns_empty(self) -> None:
        result = _parse_toc("Just some random text without TOC", total_pages=50)
        assert result == []

    def test_page_numbers_out_of_range_filtered(self) -> None:
        toc = "Chapter 1: Intro     500\nChapter 2: Body     10\n"
        result = _parse_toc(toc, total_pages=50)
        # Page 500 is out of range; only page 10 should survive
        pages = [r[1] for r in result]
        assert 500 not in pages
        assert 10 in pages

    def test_sorted_by_page_number(self) -> None:
        toc = "Chapter 3: Last     40\nChapter 1: First     5\nChapter 2: Middle     20\n"
        result = _parse_toc(toc, total_pages=100)
        pages = [r[1] for r in result]
        assert pages == sorted(pages)

    def test_deduplicates_page_numbers(self) -> None:
        # Two patterns matching the same page — only first wins
        toc = "Chapter 1: Intro     5\n1. Introduction     5\n"
        result = _parse_toc(toc, total_pages=50)
        pages = [r[1] for r in result]
        assert pages.count(5) == 1


class TestHardSplit:
    def test_single_chunk_for_exactly_max(self) -> None:
        chunks = _hard_split(20)
        assert len(chunks) == 1
        assert chunks[0].start_page == 1
        assert chunks[0].end_page == 20

    def test_two_chunks_for_21_pages(self) -> None:
        chunks = _hard_split(21)
        assert len(chunks) == 2
        assert chunks[0].end_page == 20
        assert chunks[1].start_page == 21
        assert chunks[1].end_page == 21

    def test_titles_are_part_n(self) -> None:
        chunks = _hard_split(40)
        assert chunks[0].title == "Part 1"
        assert chunks[1].title == "Part 2"

    def test_covers_all_pages(self) -> None:
        page_count = 55
        chunks = _hard_split(page_count)
        # First start is 1, last end is page_count
        assert chunks[0].start_page == 1
        assert chunks[-1].end_page == page_count
        # No gaps: each chunk end+1 == next chunk start
        for i in range(len(chunks) - 1):
            assert chunks[i].end_page + 1 == chunks[i + 1].start_page


class TestPlanChunks:
    def test_short_pdf_single_chunk(self) -> None:
        """Documents <= MAX_CHUNK_PAGES return one chunk."""
        fake_pdf = Path("/fake/doc.pdf")
        with patch("core.researcher.chunker.extract_toc", return_value=""):
            chunks = plan_chunks(fake_pdf, page_count=10)
        assert len(chunks) == 1
        assert chunks[0].title == "Full Document"

    def test_toc_detected_uses_toc_chunks(self) -> None:
        toc_text = "Chapter 1: Intro     5\nChapter 2: Methods     25\n"
        fake_pdf = Path("/fake/doc.pdf")
        with patch("core.researcher.chunker.extract_toc", return_value=toc_text):
            chunks = plan_chunks(fake_pdf, page_count=50)
        assert len(chunks) >= 2
        titles = [c.title for c in chunks]
        assert any("Intro" in t for t in titles)

    def test_no_toc_falls_back_to_hard_split(self) -> None:
        fake_pdf = Path("/fake/doc.pdf")
        with patch("core.researcher.chunker.extract_toc", return_value="no toc here"):
            chunks = plan_chunks(fake_pdf, page_count=50)
        # Hard-split produces "Part N" titles
        assert all(c.title.startswith("Part ") for c in chunks)

    def test_oversized_chapter_sub_split(self) -> None:
        # One section spanning 50 pages — exceeds MAX_CHUNK_PAGES=20
        sections = [("Big Chapter", 1)]
        chunks = _sections_to_chunks(sections, page_count=50)
        assert len(chunks) > 1
        assert all("Big Chapter" in c.title for c in chunks)
        assert chunks[0].title == "Big Chapter (Part 1)"


# ===========================================================================
# models.py
# ===========================================================================


def _make_metadata(**overrides: object) -> NoteMetadata:
    defaults = {
        "title": "Test Note",
        "source": "paper",
        "topic": "rag",
        "tags": ["rag", "concept"],
        "date": "2026-07-25",
        "relevance": 3,
        "source_file": "raw/pdfs/test.pdf",
        "pages": "1-20",
    }
    defaults.update(overrides)
    return NoteMetadata(**defaults)


class TestNoteMetadata:
    def test_valid_metadata_constructs(self) -> None:
        m = _make_metadata()
        assert m.title == "Test Note"
        assert m.relevance == 3

    def test_relevance_below_1_raises(self) -> None:
        with pytest.raises(ValueError):
            _make_metadata(relevance=0)

    def test_relevance_above_5_raises(self) -> None:
        with pytest.raises(ValueError):
            _make_metadata(relevance=6)

    def test_relevance_boundary_1_valid(self) -> None:
        m = _make_metadata(relevance=1)
        assert m.relevance == 1

    def test_relevance_boundary_5_valid(self) -> None:
        m = _make_metadata(relevance=5)
        assert m.relevance == 5

    def test_invalid_source_raises(self) -> None:
        with pytest.raises(ValueError):
            _make_metadata(source="blog")

    def test_all_valid_source_types(self) -> None:
        for src in ("book-chapter", "paper", "course", "article"):
            m = _make_metadata(source=src)
            assert m.source == src


class TestResolveTopic:
    def test_known_folder_maps_correctly(self, tmp_path: Path) -> None:
        from core.researcher.models import resolve_topic

        vault = tmp_path / "Obsidian"
        (vault / "topics").mkdir(parents=True)

        with patch("core.researcher.models.OBSIDIAN_TOPICS", vault / "topics"):
            result = resolve_topic(Path("/some/path/0.rag/paper.pdf"))

        assert result == "rag"
        assert (vault / "topics" / "rag").is_dir()

    def test_unknown_folder_raises_value_error(self, tmp_path: Path) -> None:
        from core.researcher.models import resolve_topic

        vault = tmp_path / "Obsidian"
        (vault / "topics").mkdir(parents=True)

        with (
            patch("core.researcher.models.OBSIDIAN_TOPICS", vault / "topics"),
            pytest.raises(ValueError, match="No known source folder"),
        ):
            resolve_topic(Path("/unrecognized/folder/paper.pdf"))

    def test_ai_engineering_folder_maps_agentic_ai(self, tmp_path: Path) -> None:
        from core.researcher.models import resolve_topic

        vault = tmp_path / "Obsidian"
        (vault / "topics").mkdir(parents=True)

        with patch("core.researcher.models.OBSIDIAN_TOPICS", vault / "topics"):
            result = resolve_topic(Path("/dropbox/ai_engineering/paper.pdf"))

        assert result == "agentic-ai"


# ===========================================================================
# writer.py
# ===========================================================================


def _make_note(**overrides: object) -> Note:
    meta = _make_metadata(**overrides)
    return Note(metadata=meta, body="## Summary\n\nKey insight here.\n")


class TestSanitizeFilename:
    def test_lowercase_kebab(self) -> None:
        assert sanitize_filename("Hello World") == "hello-world.md"

    def test_removes_special_chars(self) -> None:
        assert sanitize_filename("Test: A/B") == "test-ab.md"

    def test_collapses_multiple_spaces(self) -> None:
        name = sanitize_filename("A  B  C")
        assert "--" not in name

    def test_truncates_at_80_chars(self) -> None:
        long_title = "a" * 100
        result = sanitize_filename(long_title)
        assert len(result) <= 84  # 80 chars + ".md"

    def test_ends_with_md(self) -> None:
        assert sanitize_filename("any title").endswith(".md")


class TestRenderNote:
    def test_contains_frontmatter_delimiters(self) -> None:
        note = _make_note()
        rendered = render_note(note)
        lines = rendered.splitlines()
        assert lines[0] == "---"
        # Second --- ends the frontmatter
        close_idx = lines.index("---", 1)
        assert close_idx > 1

    def test_title_in_frontmatter(self) -> None:
        note = _make_note(title="RAG Survey")
        rendered = render_note(note)
        assert "title: RAG Survey" in rendered

    def test_tags_formatted_as_list(self) -> None:
        note = _make_note(tags=["rag", "concept"])
        rendered = render_note(note)
        assert "tags: [rag, concept]" in rendered

    def test_body_appended_after_frontmatter(self) -> None:
        note = _make_note()
        rendered = render_note(note)
        assert "## Summary" in rendered
        assert "Key insight here." in rendered

    def test_relevance_in_frontmatter(self) -> None:
        note = _make_note(relevance=4)
        rendered = render_note(note)
        assert "relevance: 4" in rendered

    def test_source_file_in_frontmatter(self) -> None:
        note = _make_note(source_file="raw/pdfs/my-paper.pdf")
        rendered = render_note(note)
        assert "source_file: raw/pdfs/my-paper.pdf" in rendered

    def test_pages_in_frontmatter(self) -> None:
        note = _make_note(pages="5-30")
        rendered = render_note(note)
        assert "pages: 5-30" in rendered
