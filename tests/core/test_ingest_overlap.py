"""librarian.ingest.overlap: runs of words a page shares with its raw sources."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.ingest.overlap import main, overlaps

SOURCE = (
    "The agent never tried to use the second GPU in the logs inspected. "
    "Scores were similar across hardware settings."
)


def _page(tmp_path: Path, body: str, sources: list[Path]) -> Path:
    listed = "\n".join(f"  - {s}" for s in sources)
    page = tmp_path / "page.md"
    page.write_text(
        f"---\ntitle: Page\ntags: [eval, concept]\nsources:\n{listed}\n---\n\n# Page\n\n{body}\n"
    )
    return page


def test_reports_a_copied_run_at_its_line(tmp_path: Path) -> None:
    raw = tmp_path / "raw.md"
    raw.write_text(SOURCE)
    page = _page(
        tmp_path, "Intro line.\n\nIn short, the agent never tried to use the second GPU.", [raw]
    )
    [match] = overlaps(page)
    assert match.phrase == "the agent never tried to use the second gpu"
    lines = page.read_text().splitlines()
    assert lines[match.line - 1].startswith("In short, the agent")


def test_paraphrase_and_short_runs_pass(tmp_path: Path) -> None:
    raw = tmp_path / "raw.md"
    raw.write_text(SOURCE)
    page = _page(
        tmp_path, "No logged attempt put the extra GPU to work; the second GPU idled.", [raw]
    )
    assert overlaps(page) == []


def test_see_also_and_wikilinks_are_ignored(tmp_path: Path) -> None:
    raw = tmp_path / "raw.md"
    raw.write_text(SOURCE)
    body = "Paraphrased.\n\n## See Also\n- the agent never tried to use the second GPU in the logs"
    assert overlaps(_page(tmp_path, body, [raw])) == []


def test_explicit_source_and_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    raw = tmp_path / "raw.md"
    raw.write_text(SOURCE)
    page = _page(tmp_path, "Scores were similar across hardware settings, it says.", [])
    assert main([str(page)]) == 0
    assert main([str(page), "--source", str(raw), "--words", "6"]) == 1
    assert '"scores were similar across hardware settings"' in capsys.readouterr().out
