"""Section split (librarian.retrieval.sections): headings, See Also, merge, split, fences, tables."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest

from librarian.retrieval import corpus, embeddings, format, index, pages, ranking
from librarian.retrieval.sections import (
    Section,
    embed_text,
    find_section,
    query_terms,
    split_sections,
    term_score,
)

PAGE = """---
title: Hybrid Search
tags: [rag, concept]
summary: BM25 plus vectors.
updated: 2026-11-16
---

# Hybrid Search

Intro paragraph about why one retriever is not enough for every query.

## Mechanism

BM25 scores terms; the vector side scores meaning. The two are blended per query.

### Normalisation

Scores are normalised against the best BM25 match before the blend.

## See Also

- [[RRF Fusion]] — alternative-to
"""


def _split(text: str = PAGE, lo: int = 0, hi: int = 10_000) -> list[Section]:
    return split_sections(text, min_chars=lo, max_chars=hi)


def test_heading_paths_and_order() -> None:
    secs = _split()
    assert [s.heading_path for s in secs] == ["", "Mechanism", "Mechanism › Normalisation"]
    assert [s.ordinal for s in secs] == [0, 1, 2]
    assert secs[1].text.startswith("## Mechanism")


def test_see_also_dropped_with_its_subsections() -> None:
    text = PAGE + "\n### Older links\n\n- [[X]]\n"
    assert all("See Also" not in s.heading_path for s in _split(text))
    assert all("[[X]]" not in s.text for s in _split(text))


def test_frontmatter_not_in_any_section() -> None:
    assert all("summary:" not in s.text for s in _split())


def test_short_sections_fold_into_the_next() -> None:
    secs = _split(lo=100)
    # Intro (70 chars) folds into Mechanism; Mechanism+intro is long enough to stand.
    assert secs[0].heading_path == "Mechanism"
    assert "Intro paragraph" in secs[0].text


def test_folded_heading_names_the_merged_section() -> None:
    text = "# T\n\n## Why\n\nShort.\n\n## How\n\n" + "Long enough text. " * 10
    secs = _split(text, lo=100)
    assert [s.heading_path for s in secs] == ["Why"]
    assert secs[0].text.startswith("## Why")


def test_short_last_section_folds_back() -> None:
    secs = _split(lo=80)
    assert "Scores are normalised" in secs[-1].text
    assert secs[-1].heading_path != "Mechanism › Normalisation" or len(secs[-1].text) >= 80


def test_heading_inside_fence_is_not_a_split() -> None:
    text = "# T\n\n## Code\n\n```python\n# not a heading\nx = 1\n```\n"
    secs = _split(text)
    assert [s.heading_path for s in secs] == ["Code"]
    assert "# not a heading" in secs[0].text


def test_long_section_cut_at_blank_lines_not_inside_fence() -> None:
    fence = "```\n" + "\n\n".join(f"line {i}" for i in range(40)) + "\n```"
    text = "# T\n\n## Long\n\n" + "\n\n".join(["para " * 20] * 6) + "\n\n" + fence
    secs = _split(text, hi=250)
    assert len(secs) > 1
    assert all(s.heading_path == "Long" for s in secs)
    # The fenced block, blank lines and all, stays in one part.
    assert sum(1 for s in secs if "```" in s.text) == 1
    assert next(s for s in secs if "```" in s.text).text.count("```") == 2


def test_long_table_split_by_rows_under_its_header() -> None:
    rows = "\n".join(f"| paper {i} | why {i} |" for i in range(200))
    text = f"# T\n\n## Papers\n\n| Paper | Why |\n|---|---|\n{rows}\n"
    secs = _split(text, hi=1000)
    assert len(secs) > 3
    for s in secs:
        body = s.text.removeprefix("## Papers\n\n")
        assert body.startswith("| Paper | Why |\n|---|---|")
    assert sum(s.text.count("| paper ") for s in secs) == 200


def test_page_without_headings_is_one_section() -> None:
    secs = _split("---\ntitle: X\n---\n\nJust text.\n")
    assert [(s.heading_path, s.text) for s in secs] == [("", "Just text.")]


def test_find_section_by_last_heading_or_full_path() -> None:
    # Under the default 300-char floor, Normalisation is folded into a neighbour: still found.
    assert "Scores are normalised" in find_section(PAGE, "normalisation").text
    assert find_section(PAGE, "Mechanism › Normalisation") is not None
    assert find_section(PAGE, "See Also") is None
    assert find_section(PAGE, "Nope") is None


def test_embed_text_carries_title_and_path() -> None:
    sec = _split()[2]
    assert embed_text("Hybrid Search", sec).startswith("Hybrid Search › Mechanism › Normalisation")
    assert embed_text("Hybrid Search", _split()[0]).startswith("Hybrid Search\n\n")


def test_term_score_ignores_stopwords_and_matches_stems() -> None:
    terms = query_terms("How does chunking work for RAG?")
    assert "how" not in terms and "does" not in terms
    assert term_score(terms, "We chunk documents before embedding.") > 0
    assert term_score([], "anything") == 0.0


# ---------------------------------------------------------------------------
# Index: section tables follow the page tables through build, edit and delete
# ---------------------------------------------------------------------------

LONG = """---
title: Chunking
tags: [rag, concept]
summary: How documents are cut before embedding.
updated: 2026-11-16
---

# Chunking

Chunking cuts a document into pieces small enough to embed and to return as context.

## Fixed size

Fixed-size chunking cuts every N tokens with an overlap, ignoring the document's structure,
so a chunk can start mid-sentence and end inside a table.

## Heading aware

Heading-aware chunking cuts at markdown headings, so each chunk is one idea with its title,
and a reranker sees a coherent passage instead of an arbitrary window.

## See Also

- [[Embeddings]] — prerequisite-for
"""


@pytest.fixture()
def idx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    wiki = tmp_path / "wiki" / "rag"
    wiki.mkdir(parents=True)
    (wiki / "chunking.md").write_text(LONG)
    (wiki / "other.md").write_text(PAGE)
    private = tmp_path / "wiki" / "private" / "meta"
    private.mkdir(parents=True)
    (private / "secret.md").write_text(LONG.replace("Chunking", "Secret Chunking"))
    lessons = tmp_path / "courses" / "generative-ai" / "02-rag"
    lessons.mkdir(parents=True)
    (lessons / "chunking-lesson.md").write_text(LONG.replace("title: Chunking", "title: Lesson"))
    monkeypatch.setattr(corpus, "WIKI_DIR", tmp_path / "wiki")
    monkeypatch.setattr(corpus, "PRIVATE_DIR", tmp_path / "wiki" / "private")
    monkeypatch.setattr(corpus, "COURSES_DIR", tmp_path / "courses")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    monkeypatch.setenv("LIBRARIAN_SECTION_MIN_CHARS", "0")
    from librarian.config import get_settings

    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()


def _sections(table: str = "sections") -> list[tuple]:
    con = duckdb.connect(str(corpus.DB_PATH))
    try:
        return con.execute(
            f"SELECT path, ordinal, heading_path FROM {table} ORDER BY ALL"
        ).fetchall()
    finally:
        con.close()


def test_build_writes_sections_for_wiki_and_lessons_never_private(idx: Path) -> None:
    index.open_index().close()
    wiki_rows = _sections()
    assert {p.rsplit("/", 1)[-1] for p, *_ in wiki_rows} == {"chunking.md", "other.md"}
    assert ("Fixed size" in {h for *_, h in wiki_rows}) and not any(
        "See Also" in h for *_, h in wiki_rows
    )
    lesson_rows = _sections("course_sections")
    assert {p.rsplit("/", 1)[-1] for p, *_ in lesson_rows} == {"chunking-lesson.md"}


def test_edit_replaces_only_that_pages_sections(idx: Path) -> None:
    index.open_index().close()
    other_before = [r for r in _sections() if r[0].endswith("other.md")]
    page = idx / "wiki" / "rag" / "chunking.md"
    page.write_text(LONG.replace("## Heading aware", "## Semantic"))
    index.open_index().close()
    headings = {h for p, _, h in _sections() if p.endswith("chunking.md")}
    assert "Semantic" in headings and "Heading aware" not in headings
    assert [r for r in _sections() if r[0].endswith("other.md")] == other_before


def test_deleted_page_and_lesson_lose_their_sections(idx: Path) -> None:
    index.open_index().close()
    (idx / "wiki" / "rag" / "chunking.md").unlink()
    (idx / "courses" / "generative-ai" / "02-rag" / "chunking-lesson.md").unlink()
    index.open_index().close()
    assert not any(p.endswith("chunking.md") for p, *_ in _sections())
    assert _sections("course_sections") == []


def test_best_section_matches_the_query_not_the_intro(idx: Path) -> None:
    index.open_index().close()
    path = str(idx / "wiki" / "rag" / "chunking.md")
    best = ranking.best_sections("heading aware reranker coherent", [path])
    assert best[path][0] == "Heading aware"


def test_best_sections_empty_on_an_index_without_section_tables(
    idx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index.open_index().close()
    con = duckdb.connect(str(corpus.DB_PATH))
    con.execute("DROP TABLE sections")
    con.close()
    # A server can still be serving a build made before the section tables existed.
    monkeypatch.setattr(index, "build_index", lambda con, force=False: None)
    assert ranking.best_sections("chunking", [str(idx / "wiki" / "rag" / "chunking.md")]) == {}


def test_search_text_carries_the_best_section(idx: Path) -> None:
    out = format.search_text("heading aware chunking reranker")
    assert "Best section: Heading aware" in out
    assert "a reranker sees a coherent passage" in out


def test_read_page_section_and_unknown_section(idx: Path) -> None:
    out = pages.read_page("chunking#Fixed size")
    assert out.startswith("# Chunking\n\n## Fixed size")
    assert "Heading-aware" not in out
    missing = pages.read_page("chunking#Nope")
    assert "No section 'Nope'" in missing and "Heading aware" in missing
    assert pages.read_page("secret-chunking#Fixed size").startswith("Page not found")


def test_cap_section_cuts_at_a_paragraph() -> None:
    text = "a" * 50 + "\n\n" + "b" * 50
    assert format.cap_section(text, 80) == "a" * 50 + "\n\n[… section continues]"
    assert format.cap_section(text, 500) == text


def test_output_cap_zero_turns_section_output_off(
    idx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from librarian.config import get_settings

    monkeypatch.setenv("LIBRARIAN_SECTION_OUTPUT_CHARS", "0")
    get_settings.cache_clear()
    out = format.search_text("heading aware chunking reranker")
    assert "Best section" not in out and "Snippet:" in out


# ---------------------------------------------------------------------------
# Experiments section-*: the best section's cosine as a ranking signal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("variant", "mode", "combined"),
    [
        ("", "", 0.2),
        ("section-sim", ranking.SECTION_SIM_EXPERIMENT, 0.8),
        ("section-blend", ranking.SECTION_BLEND_EXPERIMENT, 0.5),
        ("a+section-union", ranking.SECTION_UNION_EXPERIMENT, 0.8),
    ],
)
def test_section_mode_and_how_the_section_cosine_combines(
    monkeypatch: pytest.MonkeyPatch, variant: str, mode: str, combined: float
) -> None:
    monkeypatch.setattr(ranking, "experiment", lambda: variant)
    assert ranking._section_mode() == mode
    if mode:
        assert ranking._combine_section(0.2, 0.8) == pytest.approx(combined)
    assert ranking._combine_section(0.2, None) == 0.2


def _vec(*xs: float) -> bytes:
    import struct

    return struct.pack(f"{len(xs)}f", *xs)


def _rows(con: duckdb.DuckDBPyConnection, *names: str) -> list[tuple]:
    return [
        (*r, 1.0)
        for r in con.execute(
            "SELECT path, title, tags, summary, content, backlinks, embedding FROM pages "
            "WHERE path LIKE ?",
            [f"%{names[0]}"],
        ).fetchall()
    ]


def test_section_signal_scores_candidates_and_union_adds_pages(
    idx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import numpy as np

    index.open_index().close()
    chunking = str(idx / "wiki" / "rag" / "chunking.md")
    other = str(idx / "wiki" / "rag" / "other.md")
    con = duckdb.connect(str(corpus.DB_PATH))
    con.execute("UPDATE sections SET embedding = ? WHERE path = ?", [_vec(1, 0), chunking])
    con.execute("UPDATE sections SET embedding = ? WHERE path = ?", [_vec(0.6, 0.8), other])
    rows = _rows(con, "chunking.md")
    con.close()
    monkeypatch.setattr(embeddings, "encode", lambda texts: np.array([[1.0, 0.0]]))

    monkeypatch.setattr(ranking, "experiment", lambda: "section-sim")
    out, best = ranking._with_section_signal("q", rows, "pages", "", [], 5)
    assert out == rows  # sim mode rescores, never adds
    assert best is not None
    assert best[chunking] == pytest.approx(1.0) and best[other] == pytest.approx(0.6)

    monkeypatch.setattr(ranking, "experiment", lambda: "section-union")
    out, _ = ranking._with_section_signal("q", rows, "pages", "", [], 5)
    assert [r[0] for r in out] == [chunking, other]
    assert out[1][7] == 0.0  # a page brought in by its sections has no hybrid score of its own


def test_section_signal_failure_leaves_rows_unchanged(
    idx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(texts: list[str]) -> None:
        raise RuntimeError("no model")

    monkeypatch.setattr(embeddings, "encode", boom)
    monkeypatch.setattr(ranking, "experiment", lambda: "section-sim")
    rows = [("p", "T", [], "s", "c", 0, None, 1.0)]
    assert ranking._with_section_signal("q", rows, "pages", "", [], 5) == (rows, None)
