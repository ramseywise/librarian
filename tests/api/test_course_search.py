"""Course lessons in the MCP server: domains, read_page guards, wiki isolation.

Two layers. `tree` is a small tmp wiki and course tree, for guards and index behaviour.
`real_corpus` runs against data/wiki and data/courses on disk (lexical only, so no model
load), for the acceptance queries. Lesson paths are discovered, not hardcoded, because a
re-import moves them.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest

from librarian import retrieval
from librarian.retrieval import corpus, embeddings, index, pages, ranking

REAL_WIKI = corpus.REPO_ROOT / "data" / "wiki"
REAL_COURSES = corpus.REPO_ROOT / "data" / "courses"

WIKI_PAGE = """---
title: {title}
tags: [rag, concept]
summary: {title} summary
updated: 2026-11-04
---

# {title}

{body}
"""

LESSON = """---
title: {title}
summary: {title} summary
order: 1
kind: reading
---

# {title}

{body}
"""


@pytest.fixture()
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Wiki + courses + private page under one tmp data/ root. Returns data/."""
    data = tmp_path / "data"
    wiki = data / "wiki"
    courses = data / "courses"
    for d in (wiki / "rag", wiki / "private", courses / "ai-engineering" / "01-prompt" / "sub"):
        d.mkdir(parents=True)
    (courses / "generative-ai" / "02-rag" / "assets").mkdir(parents=True)

    (wiki / "rag" / "chunking.md").write_text(
        WIKI_PAGE.format(title="Chunking", body="WIKIMARKER chunking retrieval notes.")
    )
    (wiki / "rag" / "reranking.md").write_text(
        WIKI_PAGE.format(title="Reranking", body="WIKIMARKER reranking notes.")
    )
    (wiki / "private" / "acme.md").write_text(
        WIKI_PAGE.format(title="Acme", body="SECRETMARKER client detail.")
    )
    (courses / "ai-engineering" / "_course.md").write_text(
        "---\ntitle: AI Engineering\nsummary: The course.\n---\n"
    )
    module = courses / "ai-engineering" / "01-prompt"
    (module / "_module.md").write_text(
        "---\ntitle: 01 Prompt\nsummary: MODULEONLYMARKER module blurb.\n---\n"
    )
    (module / "_flashcards.md").write_text("---\ncards: [{front: FLASHMARKER, back: b}]\n---\n")
    (module / "basics.md").write_text(
        LESSON.format(title="Prompt Basics", body="LESSONMARKER prompting fundamentals.")
    )
    (module / "sub" / "advanced.md").write_text(
        LESSON.format(title="Prompt Advanced", body="LESSONMARKER nested section lesson.")
    )
    rag = courses / "generative-ai" / "02-rag"
    (rag / "_module.md").write_text("---\ntitle: 02 RAG\nsummary: RAG.\n---\n")
    (rag / "assets" / "figure.png").write_bytes(b"\x89PNG\xff\xfe")
    # Same stem and title as a wiki page, and a wikilink to the other one. Neither may
    # hijack link resolution or add a backlink to a wiki page.
    (rag / "chunking.md").write_text(
        LESSON.format(
            title="Chunking", body="LESSONMARKER CRAG retrieve grade rewrite [[Reranking]]."
        )
    )

    monkeypatch.setattr(corpus, "WIKI_DIR", wiki)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki / "private")
    monkeypatch.setattr(corpus, "COURSES_DIR", courses)
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / "idx.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return data


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------


def test_course_lessons_indexed_apart_from_wiki(tree: Path) -> None:
    con = index.open_index()
    wiki = {Path(r[0]).name for r in con.execute("SELECT path FROM pages").fetchall()}
    lessons = {Path(r[0]).name for r in con.execute("SELECT path FROM course_pages").fetchall()}
    con.close()
    assert wiki == {"chunking.md", "reranking.md"}
    # The "_" filter holds: _course, _module and _flashcards are metadata, not lessons.
    assert lessons == {"basics.md", "advanced.md", "chunking.md"}


def test_lessons_do_not_touch_wiki_backlinks_or_edges(tree: Path) -> None:
    con = index.open_index()
    backlinks = dict(con.execute("SELECT path, backlinks FROM pages").fetchall())
    edges = con.execute("SELECT count(*) FROM edges").fetchone()[0]
    con.close()
    assert set(backlinks.values()) == {0}
    assert edges == 0


def test_stale_and_deleted_lessons_are_detected_and_healed(tree: Path) -> None:
    con = index.open_index()
    lesson = tree / "courses" / "ai-engineering" / "01-prompt" / "basics.md"
    assert index.stale_pages(con) == []

    lesson.write_text(LESSON.format(title="Prompt Basics", body="EDITEDMARKER"))
    assert index.stale_pages(con) == [lesson]
    index.build_index(con)
    assert index.stale_pages(con) == []
    body = con.execute("SELECT content FROM course_pages WHERE path = ?", [str(lesson)]).fetchone()
    assert "EDITEDMARKER" in body[0]

    lesson.unlink()
    assert index.has_deleted_pages(con)
    index.build_index(con)
    assert not index.has_deleted_pages(con)
    gone = con.execute("SELECT count(*) FROM course_pages WHERE path = ?", [str(lesson)]).fetchone()
    con.close()
    assert gone[0] == 0
    rows, _ = ranking.search_rows("EDITEDMARKER", domain="course")
    assert rows == []


def test_editing_a_lesson_leaves_wiki_rows_alone(tree: Path) -> None:
    con = index.open_index()
    before = con.execute("SELECT * FROM pages ORDER BY path").fetchall()
    lesson = tree / "courses" / "ai-engineering" / "01-prompt" / "basics.md"
    lesson.write_text(LESSON.format(title="Prompt Basics", body="[[Chunking]] [[Reranking]]"))
    index.build_index(con)
    after = con.execute("SELECT * FROM pages ORDER BY path").fetchall()
    con.close()
    assert before == after


def test_old_schema_index_rebuilds_with_courses(tree: Path) -> None:
    con = index.open_index()
    con.execute("UPDATE meta SET val = '7' WHERE key = 'schema_version'")
    con.execute("DROP TABLE course_pages")
    index.build_index(con)
    assert con.execute("SELECT count(*) FROM course_pages").fetchone()[0] == 3
    con.close()


# ---------------------------------------------------------------------------
# Domains and search
# ---------------------------------------------------------------------------


def test_domain_course_scopes_all_and_subject_scopes_one(tree: Path) -> None:
    every, _ = ranking.search_rows("LESSONMARKER", domain="course")
    one, _ = ranking.search_rows("LESSONMARKER", domain="course/ai-engineering")
    assert {Path(r[0]).name for r in every} == {"basics.md", "advanced.md", "chunking.md"}
    assert {Path(r[0]).name for r in one} == {"basics.md", "advanced.md"}


def test_course_domain_is_derived_from_path(tree: Path) -> None:
    lesson = tree / "courses" / "ai-engineering" / "01-prompt" / "sub" / "advanced.md"
    assert corpus.course_domain(str(lesson)) == "course/ai-engineering"
    assert corpus.course_ref(str(lesson)) == "course/ai-engineering/01-prompt/sub/advanced.md"


@pytest.mark.parametrize("domain", ["course/nope", "course/../wiki/private", "course/../.."])
def test_unknown_or_escaping_course_domain_finds_nothing(tree: Path, domain: str) -> None:
    rows, _ = ranking.search_rows("SECRETMARKER WIKIMARKER LESSONMARKER", domain=domain)
    assert rows == []


def test_course_scope_works_without_fts(tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index.open_index().close()
    monkeypatch.setattr(index, "ensure_fts", lambda con: False)
    rows, degraded = ranking.search_rows("LESSONMARKER", domain="course/generative-ai")
    assert [Path(r[0]).name for r in rows] == ["chunking.md"]
    assert "no_fts" in degraded


def test_wiki_domain_and_tag_filters_never_return_lessons(tree: Path) -> None:
    for domain in ("rag", "concept"):
        rows, _ = ranking.search_rows("LESSONMARKER chunking", domain=domain)
        assert rows, domain
        assert all(not r[0].startswith(str(corpus.COURSES_DIR)) for r in rows)


def test_unscoped_search_ranks_wiki_and_points_at_lessons(tree: Path) -> None:
    rows, _ = ranking.search_rows("chunking", domain="")
    assert all(r[0].startswith(str(corpus.WIKI_DIR)) for r in rows)

    out = retrieval.search("chunking")
    wiki_part, _, course_part = out.partition("**Course lessons")
    assert "wiki/rag/chunking.md" in wiki_part
    assert "courses/" not in wiki_part
    assert "course/generative-ai/02-rag/chunking.md" in course_part
    assert 'domain="course"' in course_part


def test_unscoped_section_is_absent_when_no_lesson_matches(tree: Path) -> None:
    out = retrieval.search("WIKIMARKER")
    assert "Course lessons" not in out


def test_unscoped_section_still_shows_when_wiki_is_empty_for_query(tree: Path) -> None:
    out = retrieval.search("LESSONMARKER")
    assert "No wiki pages found" in out
    assert "**Course lessons" in out


def test_scoped_search_output_gives_a_readable_ref(tree: Path) -> None:
    out = retrieval.search("LESSONMARKER", domain="course/generative-ai")
    assert "Page: `course/generative-ai/02-rag/chunking.md`" in out
    assert "Domain: course/generative-ai" in out
    assert "LESSONMARKER" in retrieval.read_page("course/generative-ai/02-rag/chunking.md")


def test_wiki_results_identical_with_and_without_courses(
    tree: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    queries = [("chunking retrieval", ""), ("WIKIMARKER", ""), ("WIKIMARKER", "rag")]
    with_courses = [ranking.search_rows(q, domain=d)[0] for q, d in queries]
    tool_output = retrieval.search("chunking retrieval")
    monkeypatch.setattr(corpus, "COURSES_DIR", tmp_path / "empty")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / "wiki-only.duckdb")
    assert [ranking.search_rows(q, domain=d)[0] for q, d in queries] == with_courses
    assert tool_output.partition("\n\n---\n\n**Course lessons")[0] == retrieval.search(
        "chunking retrieval"
    )


def test_course_searches_stay_out_of_wiki_telemetry(tree: Path) -> None:
    """/compact-wiki reads tool="search_wiki" lines as evidence about wiki pages."""
    retrieval.search("chunking")
    retrieval.search("LESSONMARKER", domain="course")
    entries = [json.loads(line) for line in corpus.RETRIEVAL_LOG.read_text().splitlines()]
    assert {e["tool"] for e in entries} == {"search_wiki", "search_courses"}
    for entry in entries:
        if entry["tool"] == "search_wiki":
            assert all(not p.startswith(str(corpus.COURSES_DIR)) for p in entry["top_paths"])


# ---------------------------------------------------------------------------
# read_page guards
# ---------------------------------------------------------------------------


def _is_not_found(result: str) -> bool:
    return result.startswith("Page not found")


def test_read_page_by_course_ref_with_and_without_suffix(tree: Path) -> None:
    assert "LESSONMARKER" in retrieval.read_page("course/ai-engineering/01-prompt/basics.md")
    assert "LESSONMARKER" in retrieval.read_page("course/ai-engineering/01-prompt/basics")


def test_read_page_by_absolute_lesson_path(tree: Path) -> None:
    lesson = tree / "courses" / "ai-engineering" / "01-prompt" / "basics.md"
    assert "LESSONMARKER" in retrieval.read_page(str(lesson))


def test_read_page_still_reads_wiki(tree: Path) -> None:
    assert "WIKIMARKER" in retrieval.read_page("rag/chunking.md")
    assert "WIKIMARKER" in retrieval.read_page(str(tree / "wiki" / "rag" / "chunking.md"))


def test_title_lookup_stays_wiki_only(tree: Path) -> None:
    assert "WIKIMARKER" in retrieval.read_page("Chunking")
    assert _is_not_found(retrieval.read_page("Prompt Basics"))


@pytest.mark.parametrize(
    "ref",
    [
        "course/../wiki/private/acme.md",
        "course/../wiki/rag/chunking.md",  # in the wiki root, but not by this prefix
        "course/ai-engineering/../../wiki/private/acme.md",
        "course/../outside.md",
        "course/../../../../../../../../etc/passwd",
        "course//etc/passwd",
        "course/ai-engineering",  # a directory
        "course/generative-ai/02-rag/assets/figure.png",  # not a page
        "course",
        "course/",
    ],
)
def test_course_prefix_cannot_escape_root(tree: Path, ref: str) -> None:
    (tree / "outside.md").write_text("OUTSIDEMARKER")
    assert _is_not_found(retrieval.read_page(ref))


def test_absolute_paths_outside_both_roots_are_refused(tree: Path) -> None:
    outside = tree / "outside.md"
    outside.write_text("OUTSIDEMARKER")
    assert _is_not_found(retrieval.read_page(str(outside)))
    assert _is_not_found(retrieval.read_page("../outside.md"))


def test_private_unreachable_by_every_route(tree: Path) -> None:
    secret = tree / "wiki" / "private" / "acme.md"
    for ref in (
        str(secret),
        "private/acme.md",
        "Acme",
        "acme",
        "course/../wiki/private/acme.md",
        str(tree / "courses" / ".." / "wiki" / "private" / "acme.md"),
    ):
        assert "SECRETMARKER" not in retrieval.read_page(ref), ref


def test_symlink_in_courses_cannot_reach_private_or_outside(tree: Path) -> None:
    secret = tree / "wiki" / "private" / "acme.md"
    outside = tree / "outside.md"
    outside.write_text("OUTSIDEMARKER")
    module = tree / "courses" / "ai-engineering" / "01-prompt"
    (module / "leak.md").symlink_to(secret)
    (module / "out.md").symlink_to(outside)

    ref = "course/ai-engineering/01-prompt/"
    assert _is_not_found(retrieval.read_page(ref + "leak.md"))
    assert _is_not_found(retrieval.read_page(ref + "out.md"))
    assert _is_not_found(retrieval.read_page(str(module / "leak.md")))

    rows, _ = ranking.search_rows("SECRETMARKER OUTSIDEMARKER", domain="course")
    assert rows == []
    listing = retrieval.list_domain("course/ai-engineering/01-prompt")
    assert "leak.md" not in listing
    assert "out.md" not in listing


def test_private_not_reachable_through_listing_tools(tree: Path) -> None:
    for domain in ("course/../wiki/private", "../wiki/private", "private"):
        assert "Unknown domain" in retrieval.list_domain(domain)
        assert "Unknown domain" in retrieval.domain_briefing(domain)
    with pytest.raises(ValueError):
        retrieval.list_pages(directory="course/../wiki/private")


def test_wiki_domain_cannot_escape_wiki_root(tree: Path) -> None:
    (tree / "outside.md").write_text("OUTSIDEMARKER")
    assert "Unknown domain" in retrieval.list_domain("..")
    assert "Unknown domain" in retrieval.domain_briefing("../courses/ai-engineering/01-prompt")


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------


def test_list_domain_course_lists_subjects(tree: Path) -> None:
    out = retrieval.list_domain("course")
    assert "course/ai-engineering" in out
    assert "course/generative-ai" in out


def test_list_domain_subject_lists_modules(tree: Path) -> None:
    out = retrieval.list_domain("course/ai-engineering")
    assert "01 Prompt" in out
    assert "course/ai-engineering/01-prompt" in out
    assert "2 lesson(s)" in out
    assert "generative-ai" not in out


def test_list_domain_module_lists_lessons_with_refs(tree: Path) -> None:
    out = retrieval.list_domain("course/ai-engineering/01-prompt")
    assert "course/ai-engineering/01-prompt/basics.md" in out
    assert "course/ai-engineering/01-prompt/sub/advanced.md" in out
    assert "_module" not in out
    assert "_flashcards" not in out


def test_list_domain_unknown_names_course_domains(tree: Path) -> None:
    out = retrieval.list_domain("nope")
    assert "Unknown domain" in out
    assert "rag" in out
    assert "course/ai-engineering" in out


def test_list_pages_walks_both_roots_and_scopes(tree: Path) -> None:
    both = retrieval.list_pages()
    assert "wiki/rag/chunking.md" in both
    assert "course/ai-engineering/01-prompt/basics.md" in both
    assert "acme" not in both.lower()

    scoped = retrieval.list_pages(directory="course/generative-ai")
    assert "course/generative-ai/02-rag/chunking.md" in scoped
    assert "wiki/rag" not in scoped

    wiki_only = retrieval.list_pages(directory="rag")
    assert "courses/" not in wiki_only
    assert "course/" not in wiki_only


def test_domain_briefing_for_course_scope(tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = retrieval.domain_briefing("course/ai-engineering/01-prompt")
    assert "Prompt Basics" in out
    assert "Prompt Advanced" in out
    assert "MODULEONLYMARKER" not in out

    monkeypatch.setattr(pages, "COURSE_BRIEFING_MAX_CHARS", 10)
    capped = retrieval.domain_briefing("course/ai-engineering/01-prompt")
    assert "LESSONMARKER" not in capped
    assert "too large" in capped


def test_wiki_domains_list_is_unchanged(tree: Path) -> None:
    assert corpus.wiki_domains() == ["rag"]


# ---------------------------------------------------------------------------
# Acceptance against the real corpus
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _real_dbs(tmp_path_factory: pytest.TempPathFactory) -> Iterator[tuple[Path, Path]]:
    """(wiki + courses index, wiki-only index) over the real data, built once, lexical only."""
    if not REAL_COURSES.is_dir() or not REAL_WIKI.is_dir():
        pytest.skip("real data/ not present")
    root = tmp_path_factory.mktemp("real")
    both, wiki_only = root / "both.duckdb", root / "wiki-only.duckdb"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(corpus, "WIKI_DIR", REAL_WIKI)
        mp.setattr(corpus, "PRIVATE_DIR", REAL_WIKI / "private")
        mp.setattr(embeddings, "HAS_EMBEDDINGS", False)
        mp.setattr(corpus, "COURSES_DIR", REAL_COURSES)
        with duckdb.connect(str(both)) as con:
            index.build_index(con)
        mp.setattr(corpus, "COURSES_DIR", root / "no-courses")
        with duckdb.connect(str(wiki_only)) as con:
            index.build_index(con)
    yield both, wiki_only


@pytest.fixture()
def real_corpus(_real_dbs: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(corpus, "WIKI_DIR", REAL_WIKI)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", REAL_WIKI / "private")
    monkeypatch.setattr(corpus, "COURSES_DIR", REAL_COURSES)
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    monkeypatch.setattr(corpus, "DB_PATH", _real_dbs[0])


def test_acceptance_crag_query_returns_a_course_lesson(real_corpus: None) -> None:
    rows, degraded = ranking.search_rows("CRAG retrieve grade rewrite", domain="course")
    assert rows
    assert all(Path(r[0]).is_relative_to(REAL_COURSES) for r in rows)
    assert "no_fts" not in degraded  # BM25 ranked these, not the LIKE fallback
    assert "crag" in rows[0][4].lower()
    assert "CRAG" in retrieval.search("CRAG retrieve grade rewrite", domain="course")


def test_acceptance_read_page_real_rag_lesson(real_corpus: None) -> None:
    module = REAL_COURSES / "generative-ai" / "02-rag-retrieval"
    lesson = next(p for p in sorted(module.rglob("*.md")) if not p.name.startswith("_"))
    ref = f"course/{lesson.relative_to(REAL_COURSES)}"
    assert retrieval.read_page(ref) == lesson.read_text(encoding="utf-8")


def test_acceptance_list_domain_real_subject_lists_modules(real_corpus: None) -> None:
    out = retrieval.list_domain("course/ai-engineering")
    modules = [
        d.name
        for d in (REAL_COURSES / "ai-engineering").iterdir()
        if d.is_dir() and any(p for p in d.rglob("*.md") if not p.name.startswith("_"))
    ]
    assert modules
    for module in modules:
        assert f"course/ai-engineering/{module}" in out


def test_acceptance_wiki_scoped_results_match_a_wiki_only_index(
    real_corpus: None, _real_dbs: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The regression gate: paths, order and scores all equal to an index without courses.

    Scores compare approximately: DuckDB's BM25 sum varies by ~1e-15 between runs on a
    multi-term query, and the blended score is proportional to it.
    """
    queries = ["retrieval strategies", "context compaction", "CRAG retrieve grade rewrite"]
    domains = corpus.wiki_domains()
    assert len(domains) > 5
    # Every query unscoped, every domain once: each search hashes the corpus, so a
    # full cross product takes close to a minute.
    cases = [(q, "") for q in queries] + [(queries[0], d) for d in domains]

    def run() -> list[list[tuple[str, float]]]:
        return [
            [(r[0], r[6]) for r in ranking.search_rows(q, domain=d, tool="test")[0]]
            for q, d in cases
        ]

    with_courses = run()
    monkeypatch.setattr(corpus, "COURSES_DIR", tmp_path / "no-courses")
    monkeypatch.setattr(corpus, "DB_PATH", _real_dbs[1])
    wiki_only = run()
    assert [[p for p, _ in r] for r in wiki_only] == [[p for p, _ in r] for r in with_courses]
    for got, want in zip(wiki_only, with_courses, strict=True):
        assert [s for _, s in got] == pytest.approx([s for _, s in want])
    assert any(with_courses)


def test_acceptance_real_private_pages_stay_out(real_corpus: None) -> None:
    con = index.open_index()
    paths = [r[0] for r in con.execute("SELECT path FROM pages").fetchall()]
    paths += [r[0] for r in con.execute("SELECT path FROM course_pages").fetchall()]
    con.close()
    assert paths
    assert not any(corpus.is_private(p) for p in paths)
