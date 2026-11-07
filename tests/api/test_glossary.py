"""Glossary terms as a graph layer (librarian/courses/glossary.py)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from librarian.api.routers import glossary as glossary_routes
from librarian.courses import glossary
from librarian.wiki import parser as wiki_parser


def _page(wiki: Path, rel: str, body: str, tags: str = "[rag, concept]") -> None:
    path = wiki / f"{rel}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {path.stem}\ntags: {tags}\nsummary: s\nupdated: 2026-11-05\n---\n\n{body}\n"
    )


def _write_terms(path: Path, text: str) -> None:
    path.write_text(text)


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    monkeypatch.setattr(wiki_parser, "WIKI_DIR", root)
    monkeypatch.setattr(wiki_parser, "_parsed", None)
    monkeypatch.setattr(glossary, "GLOSSARY_FILE", tmp_path / "glossary.yaml")
    monkeypatch.setattr(glossary, "_cached", None)
    return root


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(glossary_routes.router)
    return TestClient(app)


TERMS = """
- id: rag
  label: RAG
  aliases: [retrieval-augmented generation]
  def: Retrieve then answer.
  page: rag-page
- id: chunking
  label: Chunking
  def: Cut documents up.
- id: secret-term
  label: Project Nightjar
  def: Only private pages mention this.
  page: private-page
"""


def test_word_boundaries_and_case(wiki: Path) -> None:
    _write_terms(glossary.GLOSSARY_FILE, TERMS)
    _page(wiki, "rag/hit-acronym", "A RAG pipeline, and RAG-based tools.")
    _page(wiki, "rag/hit-alias", "Retrieval-Augmented Generation is the long form.")
    _page(wiki, "rag/miss-substring", "A fragment of storage, in a bragging tone.")
    _page(wiki, "rag/miss-lower-acronym", "He wore an old rag.")
    _page(wiki, "rag/hit-case-insensitive", "chunking and CHUNKING both count.")
    _page(wiki, "rag/miss-inside-word", "Unchunkings are not chunks of it.")

    mentions = glossary.term_mentions()

    assert mentions["rag"] == ["hit-acronym", "hit-alias"]
    assert mentions["chunking"] == ["hit-case-insensitive"]


def test_forms_ending_in_punctuation_still_match(wiki: Path) -> None:
    _write_terms(
        glossary.GLOSSARY_FILE,
        '- {id: b, label: "Bayes\' rule", def: d}\n- {id: a, label: A/B test, def: d}\n',
    )
    _page(wiki, "rag/one", "By Bayes' rule, an A/B test.")
    assert glossary.term_mentions() == {"a": ["one"], "b": ["one"]}


def test_private_pages_give_no_mentions_and_no_terms(wiki: Path, client: TestClient) -> None:
    _write_terms(glossary.GLOSSARY_FILE, TERMS)
    _page(wiki, "rag/public", "This one covers RAG.")
    _page(wiki, "private/private-page", "RAG for Project Nightjar, with Chunking.")

    assert glossary.term_mentions() == {"rag": ["public"]}

    terms = client.get("/api/glossary").json()["terms"]
    assert [t["id"] for t in terms] == ["rag"]
    assert "Nightjar" not in client.get("/api/glossary").text
    assert "private-page" not in client.get("/api/glossary/mentions").text


def test_tombstones_give_no_mentions_and_no_page_link(wiki: Path, client: TestClient) -> None:
    _write_terms(glossary.GLOSSARY_FILE, TERMS)
    _page(wiki, "rag/rag-page", "Retired RAG page.", tags="[rag, tombstone]")
    _page(wiki, "rag/live", "Live RAG page.")

    assert glossary.term_mentions()["rag"] == ["live"]
    term = client.get("/api/glossary").json()["terms"][0]
    assert term["page"] is None


def test_term_page_counts_even_when_its_body_never_says_the_label(wiki: Path) -> None:
    _write_terms(glossary.GLOSSARY_FILE, TERMS)
    _page(wiki, "rag/rag-page", "All about fetching before answering.")
    assert glossary.term_mentions()["rag"] == ["rag-page"]


def test_cache_follows_the_wiki_and_the_glossary(wiki: Path) -> None:
    _write_terms(glossary.GLOSSARY_FILE, TERMS)
    _page(wiki, "rag/one", "RAG here.")
    assert glossary.term_mentions()["rag"] == ["one"]
    _page(wiki, "rag/two", "More RAG, and a longer body than before.")
    assert glossary.term_mentions()["rag"] == ["one", "two"]
    _write_terms(glossary.GLOSSARY_FILE, "- {id: more, label: longer, def: d}\n")
    assert glossary.term_mentions() == {"more": ["two"]}


@pytest.mark.parametrize(
    "content", ["- {id: x}\n", "{broken: [", "- {id: x, label: y, def: z, extra: 1}\n"]
)
def test_bad_file_reads_as_empty(wiki: Path, content: str) -> None:
    _write_terms(glossary.GLOSSARY_FILE, content)
    _page(wiki, "rag/one", "RAG here.")
    assert glossary.term_mentions() == {}


class TestSeededGlossary:
    """The real data/glossary.yaml against the real wiki."""

    @pytest.fixture()
    def terms(self) -> list[glossary.GlossaryTerm]:
        terms = glossary.load_terms()
        assert terms, "data/glossary.yaml did not load"
        return terms

    def test_ids_and_forms_are_unique(self, terms: list[glossary.GlossaryTerm]) -> None:
        ids = [t.id for t in terms]
        assert len(ids) == len(set(ids))
        forms = [f.lower() for t in terms for f in t.forms()]
        assert sorted(f for f in set(forms) if forms.count(f) > 1) == []

    def test_every_page_is_public_and_live(self, terms: list[glossary.GlossaryTerm]) -> None:
        public = wiki_parser.public_page_ids()
        assert [t.id for t in terms if t.page and t.page not in public] == []

    def test_definitions_are_one_line_and_short(self, terms: list[glossary.GlossaryTerm]) -> None:
        too_long = [t.id for t in terms if "\n" in t.definition or len(t.definition) > 160]
        assert too_long == []

    def test_every_term_is_mentioned(self, terms: list[glossary.GlossaryTerm]) -> None:
        mentions = glossary.term_mentions()
        assert [t.id for t in terms if t.id not in mentions] == []


def test_an_empty_alias_is_rejected() -> None:
    with pytest.raises(ValidationError):
        glossary.GlossaryTerm.model_validate({"id": "x", "label": "X", "aliases": [""], "def": "d"})
