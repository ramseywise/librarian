"""`librarian feedback export`: anonymised, gated by the sensitive-term check, append-only."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from librarian import accounts, feedback
from librarian.db import get_engine
from librarian.ingest import feedback_export
from librarian.ingest.feedback_export import ExportError, export


@pytest.fixture()
def wiki(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    (wiki / "private").mkdir(parents=True)
    (wiki / "private" / "_sensitive-terms.txt").write_text("# terms\nAcmeCorp\n")
    (wiki / "private" / "secret-client-plan.md").write_text("---\ntitle: Secret Client Plan\n---\n")
    return wiki


def _rows(*items: tuple[str, str, str | None, int | None]) -> list[feedback.Feedback]:
    engine = get_engine()
    user = accounts.add_user(engine, "reader@example.com")
    for kind, target, body, rating in items:
        feedback.record(engine, user_id=user.id, kind=kind, target=target, body=body, rating=rating)
    return feedback.since(engine, datetime(2026, 1, 1, tzinfo=UTC))


def _run(rows: list[feedback.Feedback], wiki: Path, tmp_path: Path) -> str:
    path = export(rows, date(2026, 11, 1), tmp_path / "out", today=date(2026, 11, 8), wiki_dir=wiki)
    assert path.name == "2026-11-08.md"
    return path.read_text()


def test_frontmatter_sections_and_verbatim_notes(wiki: Path, tmp_path: Path) -> None:
    text = _run(
        _rows(
            ("page", "rag-chunking", "The overlap advice is outdated.", None),
            ("page", "rag-chunking", None, None),
            ("lesson", "gen-ai/01-rag/intro", "Typo in the second example.", None),
            ("answer", "0123456789abcdef0123456789abcdef", "No sources given.", -1),
            ("unanswered", "how do I shard a vector index?", None, None),
        ),
        wiki,
        tmp_path,
    )
    meta = yaml.safe_load(text.split("---")[1])
    assert meta["source_type"] == "feedback" and meta["confidence"] == "low"
    assert meta["period"] == "2026-11-01..2026-11-08" and meta["title"]
    assert "### `rag-chunking`\n\n- Reports: 2" in text
    assert "> The overlap advice is outdated." in text
    assert "### `gen-ai/01-rag/intro`" in text
    assert "- Rated down: 1" in text and "> No sources given." in text
    assert "how do I shard a vector index?" in text
    assert "0123456789abcdef" not in text  # answer ids are not given
    assert "reader@example.com" not in text


@pytest.mark.parametrize(
    "note",
    [
        "Ask me at jo@gmail.com about it.",
        "Call +44 20 7946 0958 for details.",
        "Call (555) 123-4567 for details.",
        "See https://www.linkedin.com/in/jane-doe for context.",
        "Credit to @janedoe for this.",
        "We use AcmeCorp internally.",
        "This contradicts the Secret Client Plan.",
        "key sk-ant-abcdefghijklmnopqrstuvwxyz0123",
    ],
)
def test_notes_that_identify_someone_or_something_private_are_dropped(
    note: str, wiki: Path, tmp_path: Path
) -> None:
    text = _run(
        _rows(("page", "rag-chunking", note, None), ("page", "rag-chunking", "Fine note.", None)),
        wiki,
        tmp_path,
    )
    assert "> Fine note." in text
    assert note not in text
    assert "1 notes and 0 items were left out" in text
    assert "- Reports: 2" in text  # the signal still counts


def test_targets_naming_a_private_page_or_term_are_skipped(wiki: Path, tmp_path: Path) -> None:
    text = _run(
        _rows(
            ("page", "secret-client-plan", "Wrong.", None),
            ("lesson", "private/leetcode/two-sum", "Wrong.", None),
            ("unanswered", "what did AcmeCorp decide?", None, None),
            ("unanswered", "mail me at x@gmail.com", None, None),
            ("page", "rag-chunking", "Ok.", None),
        ),
        wiki,
        tmp_path,
    )
    assert "secret-client-plan" not in text and "leetcode" not in text
    assert "AcmeCorp" not in text and "gmail" not in text
    assert "4 items were left out" in text
    assert "rag-chunking" in text


def test_it_refuses_to_overwrite(wiki: Path, tmp_path: Path) -> None:
    rows = _rows(("page", "p", "Note.", None))
    first = export(
        rows, date(2026, 11, 1), tmp_path / "out", today=date(2026, 11, 8), wiki_dir=wiki
    )
    before = first.read_text()
    with pytest.raises(ExportError, match="append-only"):
        export(rows, date(2026, 11, 1), tmp_path / "out", today=date(2026, 11, 8), wiki_dir=wiki)
    assert first.read_text() == before


def test_main_writes_to_out_and_refuses_a_second_run(
    wiki: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _rows(("page", "p", "Note.", None))
    monkeypatch.setattr(feedback_export, "_names", lambda _w: None)
    out = tmp_path / "raw" / "feedback"
    assert feedback_export.main(["--since", "2026-01-01", "--out", str(out)]) == 0
    assert len(list(out.glob("*.md"))) == 1
    assert feedback_export.main(["--since", "2026-01-01", "--out", str(out)]) == 1
    assert feedback_export.main(["--since", "yesterday", "--out", str(out)]) == 2
    assert "append-only" in capsys.readouterr().err
