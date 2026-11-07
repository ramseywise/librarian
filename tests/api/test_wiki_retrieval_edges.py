"""Small wiki/retrieval bugs from the 2026-11-07 code review (F17)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from librarian import retrieval
from librarian.retrieval import corpus, embeddings, index
from librarian.wiki import relinker
from librarian.wiki.common import WIKILINK_RE, parse_frontmatter
from librarian.wiki.rename import apply_plan, build_plan

PAGE = "---\ntitle: {t}\ntags: [{tags}]\nsummary: s\nupdated: 2026-01-01\n---\n\n# {t}\n\n{b}\n"


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "rag").mkdir(parents=True)
    (wiki_dir / "rag" / "chunking.md").write_text(PAGE.format(t="Chunking", tags="rag", b="x"))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(corpus, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(corpus, "RETRIEVAL_LOG", tmp_path / "logs" / "retrieval.jsonl")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    return wiki_dir


def test_read_page_directory_name_is_not_found(wiki: Path) -> None:
    # "zzz" directory: no fuzzy match either, so the plain not-found text comes back.
    (wiki / "zzz").mkdir()
    assert retrieval.read_page("zzz").startswith("Page not found")
    assert retrieval.read_page(str(wiki / "zzz")).startswith("Page not found")


@pytest.mark.parametrize("title", ["foo[bar", "what? *", "a[", "]"])
def test_read_page_glob_metacharacters_do_not_raise(wiki: Path, title: str) -> None:
    assert retrieval.read_page(title).startswith("Page not found")


def test_broken_frontmatter_is_not_indexed_as_live(wiki: Path) -> None:
    bad = wiki / "rag" / "broken.md"
    bad.write_text("---\ntitle: [unclosed\ntags: [rag, tombstone]\n---\n\nbody\n")
    assert parse_frontmatter(bad.read_text()) == {}
    assert index.read_pages([bad]) == []
    assert index._is_unindexed(bad)


def test_wikilinks_skip_fences_and_embeds() -> None:
    text = "[[A]] ![[img.png]]\n```\n[[Fenced]]\n```\n~~~\n[[Tilde]]\n~~~\n[[B|label]]\n"
    assert [m.group(1) for m in WIKILINK_RE.finditer(text)] == ["A", "B"]
    assert WIKILINK_RE.search("![[only]]") is None


def test_retrieval_log_rotates(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(corpus, "RETRIEVAL_LOG_MAX_BYTES", 100)
    for i in range(10):
        corpus.log_retrieval("search_wiki", query=f"q{i}")
    log = corpus.RETRIEVAL_LOG
    assert log.with_name(log.name + ".1").exists()
    assert log.stat().st_size <= 300


def test_relinker_skips_tombstones(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (wiki / "rag" / "old.md").write_text(PAGE.format(t="Old", tags="rag, tombstone", b="gone"))
    monkeypatch.setattr(relinker, "WIKI_DIR", wiki)
    assert set(relinker.load_pages()) == {"chunking"}


def test_relinker_keeps_first_seen_dates(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (wiki / "rag" / "other.md").write_text(PAGE.format(t="Other", tags="rag", b="y"))
    monkeypatch.setattr(relinker, "WIKI_DIR", wiki)
    pages = relinker.load_pages()
    out = wiki / "_relink_suggestions.md"
    # A legacy undated entry takes the file's own updated date; a dated one keeps its date.
    out.write_text(
        "---\nupdated: 2026-01-02\n---\n"
        "- [[Chunking]] → [[Other]] (score: 0.700)\n"
        "- [[Other]] → [[Chunking]] (score: 0.600) · first seen 2026-03-04\n"
    )
    report = relinker.RelinkReport(
        [("chunking", "other", 0.7), ("other", "chunking", 0.6)], [], [], []
    )
    relinker.write_suggestions(report, pages)
    text = out.read_text()
    assert "[[Chunking]] → [[Other]] (score: 0.700) · first seen 2026-01-02" in text
    assert "[[Other]] → [[Chunking]] (score: 0.600) · first seen 2026-03-04" in text
    relinker.write_suggestions(report, pages)  # idempotent
    assert out.read_text() == text


def _rename_wiki(tmp_path: Path) -> Path:
    root = tmp_path / "rw"
    (root / "rag").mkdir(parents=True)
    return root


def test_rename_unindented_aliases_and_crlf(tmp_path: Path) -> None:
    root = _rename_wiki(tmp_path)
    page = root / "rag" / "old-page.md"
    page.write_bytes(
        b"---\r\ntitle: Old Page\r\naliases:\r\n- Ancient\r\ntags: [rag, concept]\r\n"
        b"summary: s\r\nupdated: 2026-01-01\r\n---\r\n\r\n# Old Page\r\n\r\nbody\r\n"
    )
    plan = build_plan("Old Page", "New Page", root, date(2026, 11, 5), courses_dir=tmp_path / "c")
    apply_plan(plan)
    data = (root / "rag" / "new-page.md").read_bytes()
    assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b"")
    text = data.decode().replace("\r\n", "\n")
    assert text.count("aliases:") == 1
    assert "  - Ancient" in text and "  - Old Page" in text
    assert "\n- Ancient\n" not in text


def test_rename_skips_non_utf8_page(tmp_path: Path) -> None:
    root = _rename_wiki(tmp_path)
    (root / "rag" / "old-page.md").write_text(PAGE.format(t="Old Page", tags="rag", b="x"))
    latin = root / "rag" / "latin.md"
    raw = PAGE.format(t="Latin", tags="rag", b="[[Old Page]] caf\xe9").encode("latin-1")
    latin.write_bytes(raw)
    plan = build_plan("Old Page", "New Page", root, date(2026, 11, 5), courses_dir=tmp_path / "c")
    assert plan.skipped == ["rag/latin.md"]
    apply_plan(plan)
    assert latin.read_bytes() == raw
