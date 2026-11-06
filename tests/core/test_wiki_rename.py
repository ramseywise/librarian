"""librarian.wiki.rename and alias resolution against synthetic wikis. All names here are made up."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import frontmatter
import pytest

from librarian import retrieval
from librarian.courses import catalog as course_catalog
from librarian.retrieval import corpus
from librarian.retrieval.graph_expansion import build_typed_edges
from librarian.wiki import parser as wiki_parser
from librarian.wiki.common import page_aliases, text_aliases
from librarian.wiki.relinker import build_link_graph, load_pages
from librarian.wiki.rename import apply_plan, build_plan, main
from librarian.wiki.telemetry import _public_pages, _slug_map, compute_stats

TODAY = date(2026, 11, 5)
PRIVATE_TITLE = "Acme Secret Roadmap"


def write(wiki: Path, rel: str, title: str, body: str = "", extra: str = "") -> Path:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\n{extra}tags: [rag, concept]\nsummary: s\nupdated: 2026-01-01\n"
        f"sources:\n  - data/raw/web/old-page.md\n---\n\n# {title}\n\n{body}\n"
    )
    return path


@pytest.fixture
def wiki(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    write(root, "rag/old-page.md", "Old Page", "Links out to [[Reader One]].")
    write(
        root,
        "rag/reader-one.md",
        "Reader One",
        "By title [[Old Page]], by stem [[old-page]], labelled [[Old Page|the page]], "
        "anchored [[Old Page#Heading]], by path [[rag/old-page]], [[See also: Old Page]], "
        "and [a file](old-page.md).\n\n## See Also\n- [[Old Page]] — extends\n- [[Other]]",
    )
    write(root, "eval/other.md", "Other", "Mentions Old Page in plain words, no link.")
    write(root, "private/internal.md", PRIVATE_TITLE, "Private view of [[Old Page]].")
    write(root, "_index.md", "Wiki Index", "- [[Old Page]]")
    return root


def run(wiki: Path, *args: str) -> int:
    courses = wiki.parent / "courses"
    return main(
        [*args, "--wiki-dir", str(wiki), "--courses-dir", str(courses), "--today", "2026-11-05"]
    )


class TestPlan:
    def test_dry_run_writes_nothing(self, wiki: Path, capsys: pytest.CaptureFixture[str]) -> None:
        before = {p: p.read_text() for p in wiki.rglob("*.md")}
        assert run(wiki, "Old Page", "New Name") == 0
        assert {p: p.read_text() for p in wiki.rglob("*.md")} == before
        assert "Dry run" in capsys.readouterr().out

    @pytest.mark.parametrize("old", ["Old Page", "old-page"])
    def test_finds_the_page_by_title_or_stem(self, wiki: Path, old: str) -> None:
        assert build_plan(old, "New Name", wiki, TODAY, courses_dir=wiki).page.stem == "old-page"


class TestApply:
    @pytest.fixture
    def renamed(self, wiki: Path) -> Path:
        assert run(wiki, "Old Page", "New Name", "--apply") == 0
        return wiki

    def test_moves_file_and_rewrites_frontmatter_and_heading(self, renamed: Path) -> None:
        assert not (renamed / "rag/old-page.md").exists()
        post = frontmatter.load(renamed / "rag/new-name.md")
        assert post["title"] == "New Name"
        assert post["aliases"] == ["Old Page"]
        assert str(post["updated"]) == "2026-11-05"
        assert post.content.startswith("# New Name")
        # The page's raw source keeps the name it has on disk.
        assert post["sources"] == ["data/raw/web/old-page.md"]

    def test_rewrites_every_link_form_and_keeps_its_decoration(self, renamed: Path) -> None:
        text = (renamed / "rag/reader-one.md").read_text()
        assert "By title [[New Name]]" in text
        assert "by stem [[new-name]]" in text
        assert "[[New Name|the page]]" in text
        assert "[[New Name#Heading]]" in text
        assert "[[rag/new-name]]" in text
        assert "[[See also: New Name]]" in text
        assert "[a file](new-name.md)" in text
        assert "- [[New Name]] — extends" in text
        assert "Old Page" not in text

    def test_untouched_page_keeps_its_date_and_plain_words(self, renamed: Path) -> None:
        text = (renamed / "eval/other.md").read_text()
        assert "Mentions Old Page in plain words" in text
        assert "updated: 2026-01-01" in text

    def test_rewrites_inside_index_and_private_pages(self, renamed: Path) -> None:
        assert "[[New Name]]" in (renamed / "_index.md").read_text()
        assert "[[New Name]]" in (renamed / "private/internal.md").read_text()

    def test_link_numbers_do_not_move(self, wiki: Path) -> None:
        before = compute_stats(wiki, TODAY)["metrics"]
        assert run(wiki, "Old Page", "New Name", "--apply") == 0
        after = compute_stats(wiki, TODAY)["metrics"]
        # Stale rate does move: every rewritten page gets today's `updated`.
        before.pop("stale_rate")
        after.pop("stale_rate")
        assert after == before

    def test_report_counts_private_pages_without_naming_them(
        self, wiki: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(wiki, "Old Page", "New Name", "--apply") == 0
        out = capsys.readouterr().out
        assert "(1 private)" in out
        assert PRIVATE_TITLE not in out
        assert "internal" not in out

    def test_title_only_change_keeps_file_and_adds_no_alias(self, wiki: Path) -> None:
        assert run(wiki, "Old Page", "OLD Page", "--apply") == 0
        post = frontmatter.load(wiki / "rag/old-page.md")
        assert post["title"] == "OLD Page"
        assert "aliases" not in post.metadata

    def test_rename_back_drops_the_alias_it_returns_to(self, wiki: Path) -> None:
        assert run(wiki, "Old Page", "New Name", "--apply") == 0
        assert run(wiki, "New Name", "Old Page", "--apply") == 0
        post = frontmatter.load(wiki / "rag/old-page.md")
        assert post["aliases"] == ["New Name"]

    def test_title_needing_quotes_stays_valid_yaml(self, wiki: Path) -> None:
        assert run(wiki, "Old Page", "RAG: A Field Guide", "--apply") == 0
        assert frontmatter.load(wiki / "rag/rag-a-field-guide.md")["title"] == "RAG: A Field Guide"

    def test_no_alias_flag(self, wiki: Path) -> None:
        assert run(wiki, "Old Page", "New Name", "--apply", "--no-alias") == 0
        assert "aliases" not in frontmatter.load(wiki / "rag/new-name.md").metadata

    def test_sensitive_old_name_is_not_kept_as_an_alias(self, wiki: Path) -> None:
        (wiki / "private/_sensitive-terms.txt").write_text("Old Page\n")
        assert run(wiki, "Old Page", "New Name", "--apply") == 0
        assert "aliases" not in frontmatter.load(wiki / "rag/new-name.md").metadata

    def test_failed_write_restores_every_file(
        self, wiki: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        plan = build_plan("Old Page", "New Name", wiki, TODAY, courses_dir=wiki)
        before = {p: p.read_text() for p in wiki.rglob("*.md")}
        real = Path.unlink

        def fail_on_old(self: Path, missing_ok: bool = False) -> None:
            if self == plan.page.path:
                raise OSError("disk full")
            real(self, missing_ok=missing_ok)

        monkeypatch.setattr(Path, "unlink", fail_on_old)
        with pytest.raises(OSError):
            apply_plan(plan)
        assert {p: p.read_text() for p in wiki.rglob("*.md")} == before


class TestRefusals:
    @pytest.mark.parametrize(
        ("old", "new"),
        [
            ("No Such Page", "New Name"),
            ("Old Page", "Other"),  # another page's title
            ("Old Page", "Old Page"),  # no change
            ("Old Page", "!!!"),  # makes no file name
            (PRIVATE_TITLE, "New Name"),  # a private page is not a public page
            ("Old Page", PRIVATE_TITLE),  # the file name would publish it
        ],
    )
    def test_refused_and_nothing_written(self, wiki: Path, old: str, new: str) -> None:
        before = {p: p.read_text() for p in wiki.rglob("*.md")}
        assert run(wiki, old, new, "--apply") == 2
        assert {p: p.read_text() for p in wiki.rglob("*.md")} == before

    def test_another_pages_alias_is_taken(self, wiki: Path) -> None:
        write(wiki, "rag/holder.md", "Holder", extra="aliases:\n  - Taken Name\n")
        assert run(wiki, "Old Page", "Taken Name", "--apply") == 2

    def test_listed_term_in_new_name(self, wiki: Path) -> None:
        (wiki / "private/_sensitive-terms.txt").write_text("Globex\n")
        assert run(wiki, "Old Page", "Globex Notes", "--apply") == 2

    def test_tombstone(self, wiki: Path) -> None:
        path = wiki / "rag/gone.md"
        path.write_text("---\ntitle: Gone\ntags: [rag, tombstone]\n---\n\n# Gone\n")
        assert run(wiki, "Gone", "New Name", "--apply") == 2

    def test_refusal_never_names_a_private_page(
        self, wiki: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(wiki, "Old Page", "internal") == 2
        assert PRIVATE_TITLE not in capsys.readouterr().err


class TestRemainingReferences:
    def test_course_files_are_counted_not_edited(self, wiki: Path) -> None:
        courses = wiki.parent / "courses"
        courses.mkdir()
        linked = courses / "a.md"
        linked.write_text("---\nimported_hash: x\n---\nSee [[Old Page]].\n")
        (courses / "b.md").write_text("---\nwiki: [old-page]\n---\nBody.\n")
        (courses / "c.md").write_text("---\nwiki: [other]\n---\nBody.\n")
        before = linked.read_text()
        plan = build_plan("Old Page", "New Name", wiki, TODAY, courses_dir=courses)
        apply_plan(plan)
        assert plan.course_files == 2
        assert linked.read_text() == before


class TestAliasResolution:
    @pytest.fixture
    def aliased(self, tmp_path: Path) -> Path:
        root = tmp_path / "wiki"
        write(root, "rag/current.md", "Current", extra="aliases:\n  - Former Name\n")
        write(root, "rag/reader.md", "Reader", "Uses [[Former Name]].")
        return root

    def test_page_aliases_shapes(self) -> None:
        assert page_aliases({"aliases": ["A", 2]}) == ["A", "2"]
        assert page_aliases({"aliases": "A"}) == ["A"]
        assert page_aliases({}) == []
        assert page_aliases({"aliases": {"a": 1}}) == []

    def test_text_aliases_survives_bad_yaml(self) -> None:
        assert text_aliases("---\naliases: [\n---\nbody") == []
        assert text_aliases("no frontmatter, aliases: here") == []

    def test_telemetry_resolves_and_no_dead_link(self, aliased: Path) -> None:
        slugs = _slug_map(_public_pages(aliased))
        assert slugs["former-name"].stem == "current"

    def test_current_name_beats_another_pages_alias(self, aliased: Path) -> None:
        write(aliased, "rag/former-name.md", "Former Name")
        assert _slug_map(_public_pages(aliased))["former-name"].stem == "former-name"

    def test_relinker_resolves(self, aliased: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("librarian.wiki.relinker.WIKI_DIR", aliased)
        pages = load_pages()
        build_link_graph(pages)
        assert pages["reader"].outgoing_links == {"current"}

    def test_typed_edges_resolve(self) -> None:
        pages = [
            ("a.md", "A", "---\naliases: [Former]\n---\nbody"),
            ("b.md", "B", "- [[Former]] — extends"),
        ]
        assert build_typed_edges(pages) == [("b.md", "a.md", "extends")]

    def test_real_name_beats_alias_in_typed_edges(self) -> None:
        pages = [
            ("a.md", "A", "---\naliases: [C]\n---\nbody"),
            ("c.md", "C", "body"),
            ("b.md", "B", "- [[C]] — extends"),
        ]
        assert build_typed_edges(pages) == [("b.md", "c.md", "extends")]

    def test_map_draws_the_edge(self, aliased: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wiki_parser, "WIKI_DIR", aliased)
        edges = wiki_parser.parse_wiki()["edges"]
        assert [(e["source"], e["target"]) for e in edges] == [("reader", "current")]

    def test_lesson_link_to_the_old_name_resolves(self, aliased: Path) -> None:
        refs = course_catalog._load_wiki(aliased)
        slugs = course_catalog._wiki_slugs(refs)
        assert course_catalog._resolve_wikilink("Former Name", refs, slugs) == "current"

    def test_read_page_finds_the_old_name(
        self, aliased: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(corpus, "WIKI_DIR", aliased)
        assert "# Current" in retrieval.read_page("Former Name")

    def test_read_page_does_not_answer_from_a_private_alias(
        self, aliased: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        write(aliased, "private/hidden.md", "Hidden", extra="aliases:\n  - Quiet Words\n")
        monkeypatch.setattr(corpus, "WIKI_DIR", aliased)
        monkeypatch.setattr(corpus, "PRIVATE_DIR", aliased / "private")
        assert retrieval.read_page("Quiet Words").startswith("Page not found")
