"""Pre-ingest triage: duplicates and changes, sensitive routing, and what it may print."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from librarian.ingest import ingest_gate, manifest
from librarian.ingest.sensitive import private_names, scan_text, terms_pattern

PRIVATE_STEM = "acme-renewal-notes"
# Assembled so this test file doesn't itself look like a leaked key.
# Joined at runtime so the detect-private-key pre-commit hook does not match this fixture.
PEM_HEADER = "-----BEGIN RSA PRIVATE" + " KEY-----"
FAKE_SECRET = "sk-" + "a" * 30


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "data" / "raw").mkdir(parents=True)
    private = tmp_path / "data" / "wiki" / "private"
    private.mkdir(parents=True)
    (private / f"{PRIVATE_STEM}.md").write_text("---\ntitle: Short\n---\n\nbody\n")
    (private / "_sensitive-terms.txt").write_text("# comment\nGlobex\n")
    with (
        patch.object(manifest, "REPO_ROOT", tmp_path),
        patch.object(manifest, "MANIFEST_PATH", tmp_path / "data" / "raw" / "manifest.jsonl"),
        patch.object(ingest_gate, "REPO_ROOT", tmp_path),
    ):
        yield tmp_path


def raw(repo: Path, name: str, text: str) -> Path:
    path = repo / "data" / "raw" / name
    path.write_text(text)
    return path


def run(repo: Path, *paths: Path) -> list[ingest_gate.Triage]:
    return ingest_gate.triage(paths, repo / "data" / "wiki")


class TestStatus:
    def test_new_then_unchanged_then_changed(self, repo: Path) -> None:
        path = raw(repo, "a.md", "first version\n")
        assert run(repo, path)[0].status == "new"

        manifest.mark(path, ["data/wiki/rag/a.md"])
        assert run(repo, path)[0].status == "unchanged"

        path.write_text("second version\n")
        result = run(repo, path)[0]
        assert (result.status, result.wiki_pages) == ("changed", ["data/wiki/rag/a.md"])

    def test_same_content_under_another_path_is_a_duplicate(self, repo: Path) -> None:
        first = raw(repo, "a.md", "the same body\n")
        manifest.mark(first, ["data/wiki/rag/a.md"])

        result = run(repo, raw(repo, "copy.md", "the same body\n"))[0]

        assert result.status == "duplicate"
        assert result.duplicate_of == "data/raw/a.md"
        assert result.wiki_pages == ["data/wiki/rag/a.md"]

    def test_a_rescrape_with_new_frontmatter_and_spacing_is_a_duplicate(self, repo: Path) -> None:
        first = raw(repo, "a.md", "---\nscraped: 2026-01-01\n---\n\nthe same body\n")
        manifest.mark(first, [])

        copy = raw(repo, "b.md", "---\nscraped: 2026-11-05\n---\n\nthe   same\nbody\n")

        assert run(repo, copy)[0].status == "duplicate"

    def test_duplicates_within_one_batch_compile_once(self, repo: Path) -> None:
        results = run(repo, raw(repo, "a.md", "body\n"), raw(repo, "b.md", "body\n"))
        assert [r.status for r in results] == ["new", "duplicate"]

    def test_private_pages_count_but_are_not_listed(self, repo: Path) -> None:
        first = raw(repo, "a.md", "body\n")
        manifest.mark(first, ["data/wiki/rag/a.md", f"data/wiki/private/{PRIVATE_STEM}.md"])
        result = run(repo, raw(repo, "copy.md", "body\n"))[0]
        assert result.wiki_pages == ["data/wiki/rag/a.md"]
        assert result.private_wiki_pages == 1

    def test_older_raw_prefixed_manifest_rows_still_match_content(self, repo: Path) -> None:
        path = raw(repo, "a.md", "old body\n")
        (repo / "data" / "raw" / "manifest.jsonl").write_text(
            json.dumps(
                {
                    "path": "raw/a.md",
                    "hash": "sha256:x",
                    "ingested_at": "2026-01-01",
                    "wiki_pages": [],
                }
            )
            + "\n"
        )
        assert run(repo, raw(repo, "b.md", "old body\n"))[0].duplicate_of == "raw/a.md"
        assert path.exists()


class TestRoute:
    @pytest.mark.parametrize(
        ("text", "route", "category"),
        [
            ("plain notes about chunking\n", "clear", None),
            ("mail jane.doe@realcorp.io\n", "strip", "email"),
            ("call +45 12 34 56 78 today\n", "strip", "phone"),
            ("pay to DE89370400440532013000\n", "strip", "iban"),
            ("work done for GLOBEX last year\n", "decide", "term"),
            (f"see {PRIVATE_STEM}-prep for details\n", "decide", "private-name"),
            (f"key is {FAKE_SECRET}\n", "stop", "secret"),
            (
                f"{PEM_HEADER}\nmail a@realcorp.io\n{FAKE_SECRET}\n",
                "stop",
                "secret",
            ),
        ],
    )
    def test_route(self, repo: Path, text: str, route: str, category: str | None) -> None:
        result = run(repo, raw(repo, "a.md", text))[0]
        assert result.route == route
        if category:
            assert category in result.findings

    @pytest.mark.parametrize(
        "text",
        [
            "user@example.com is a placeholder\n",
            "noreply@anthropic.com\n",
            "sa@project.iam.gserviceaccount.com\n",
            "AB12CDEFGHIJKLMNOP fails the IBAN checksum\n",
            "globexcorp contains the term but isn't the word\n",
            "version +1.2.3 and 1234567890\n",
        ],
    )
    def test_harmless_lookalikes_stay_clear(self, repo: Path, text: str) -> None:
        assert run(repo, raw(repo, "a.md", text))[0].route == "clear"

    def test_a_sensitive_file_name_needs_a_decision_even_with_a_clean_body(
        self, repo: Path
    ) -> None:
        result = run(repo, raw(repo, f"{PRIVATE_STEM}-prep.md", "plain notes\n"))[0]
        assert result.route == "decide"
        assert "path" in result.findings

    def test_scan_reports_line_numbers(self) -> None:
        findings = scan_text("ok\nGlobex\nok\n", terms_pattern(["Globex"]))
        assert [(f.line, f.category) for f in findings] == [(2, "term")]


class TestOutput:
    @pytest.mark.parametrize("as_json", [False, True])
    def test_output_never_carries_a_value_or_private_name(
        self, repo: Path, capsys: pytest.CaptureFixture[str], as_json: bool
    ) -> None:
        path = raw(
            repo,
            f"{PRIVATE_STEM}-prep.md",
            f"{FAKE_SECRET} jane.doe@realcorp.io Globex {PRIVATE_STEM}\n",
        )
        argv = ["triage", str(path), "--wiki-dir", str(repo / "data" / "wiki")]
        assert ingest_gate.main(argv + (["--json"] if as_json else [])) == 1

        out = capsys.readouterr().out
        for value in (FAKE_SECRET, "jane.doe", "realcorp", "Globex", PRIVATE_STEM):
            assert value not in out
        assert ingest_gate.WITHHELD in out

    def test_says_so_when_no_terms_are_listed(
        self, repo: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (repo / "data" / "wiki" / "private" / "_sensitive-terms.txt").unlink()
        path = raw(repo, "a.md", "plain\n")
        assert (
            ingest_gate.main(["triage", str(path), "--wiki-dir", str(repo / "data" / "wiki")]) == 0
        )
        assert "NONE LISTED" in capsys.readouterr().out

    def test_directory_target_walks_markdown(self, repo: Path) -> None:
        raw(repo, "a.md", "body\n")
        assert [r.path for r in run(repo, repo / "data" / "raw")] == ["data/raw/a.md"]

    def test_missing_path_is_an_error_not_a_clean_run(self, repo: Path) -> None:
        assert ingest_gate.main(["triage", str(repo / "nope.md")]) == 2


class TestTermBoundaries:
    @pytest.mark.parametrize(
        "text", ["Globex-led rollout", "globex_prod", "the Globex.", "(globex)"]
    )
    def test_hyphen_underscore_and_punctuation_do_not_hide_a_term(self, text: str) -> None:
        assert [f.category for f in scan_text(text, terms_pattern(["Globex"]))] == ["term"]

    def test_a_longer_word_is_not_the_term(self) -> None:
        assert scan_text("reglobexed", terms_pattern(["Globex"])) == []


def test_private_names_survive_broken_frontmatter(tmp_path: Path) -> None:
    private = tmp_path / "private"
    private.mkdir()
    (private / "broken-page.md").write_text("---\ntitle: Broken: Page With Colon\n---\n\nbody\n")
    assert private_names(tmp_path) == {"broken-page", "Broken: Page With Colon"}
