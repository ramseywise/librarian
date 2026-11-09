"""librarian.ingest.precheck: mechanical defects ingest reviews keep finding."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import librarian.ingest.overlap as overlap_module
from librarian.ingest.overlap import added_lines
from librarian.ingest.precheck import main, precheck

SOURCE = (
    "Authors: Jane Smith. Venue: n/a.\n\n"
    'SOURCE: "A Paper", Jane Smith, Raj Patel (Univ. of Melbourne). arXiv:2601.00001.\n'
    "We train with GRPO and report ESS. Retrieval-Augmented Generation (RAG) helps.\n"
)


def _page(tmp_path: Path, body: str, source: str = SOURCE, summary: str = "S.") -> Path:
    raw = tmp_path / "raw.md"
    raw.write_text(source)
    page = tmp_path / "page.md"
    page.write_text(
        f"---\ntitle: Page\ntags: [eval, concept]\nsummary: {summary}\nsources:\n  - {raw}\n---\n\n"
        f"# Page\n\n{body}\n\n## See Also\n- [[X]] — consistent with Google\n"
    )
    return page


def _checks(page: Path) -> list[str]:
    return [f.check for f in precheck(page)]


def test_clean_page_passes(tmp_path: Path) -> None:
    body = "Smith et al. (University of Melbourne) use GRPO; Retrieval-Augmented Generation (RAG)."
    assert _checks(_page(tmp_path, body)) == []


def test_acronym_expansion_not_in_source(tmp_path: Path) -> None:
    page = _page(
        tmp_path,
        "They use group relative policy optimisation (GRPO) and ESS (effective sample size).",
    )
    assert _checks(page) == ["acronym", "acronym"]


def test_affiliation_not_in_source(tmp_path: Path) -> None:
    assert _checks(_page(tmp_path, "Smith et al. (Google DeepMind) report gains.")) == [
        "affiliation"
    ]


def test_strip_route_names(tmp_path: Path) -> None:
    source = SOURCE + "Contact: jane.smith@unimelb.edu.au\n"
    page = _page(tmp_path, "Patel and colleagues report gains.", source, summary="Smith shows x.")
    assert _checks(page) == ["strip-name", "strip-name"]
    assert _checks(_page(tmp_path, "Patel and colleagues report gains.")) == []


def test_cross_page_claim(tmp_path: Path) -> None:
    page = _page(tmp_path, "This is consistent with [[Other Page]], which found little gain.")
    assert _checks(page) == ["cross-page"]


def test_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(_page(tmp_path, "Unlike [[Other]], it works."))]) == 1
    assert "[cross-page]" in capsys.readouterr().out


def test_added_lines_since_revision(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    page = tmp_path / "p.md"
    page.write_text("a\nb\nc\n")
    git("add", "p.md")
    git("commit", "-qm", "x")
    page.write_text("a\nb\nnew\nc\n")
    monkeypatch.setattr(overlap_module, "REPO_ROOT", tmp_path)
    assert added_lines(page, "HEAD") == {3}
    assert added_lines(tmp_path / "untracked.md", "HEAD") is None
