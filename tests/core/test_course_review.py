"""The reviewer findings log, eval scorer and signals report (`librarian courses review ...`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from librarian.config import get_settings
from librarian.courses.review import findings as fl
from librarian.courses.review import score_eval as se
from librarian.courses.review import signals as sg


def row(**over: str) -> str:
    base = {
        "run": "r1",
        "reviewer": "drill-reviewer",
        "target": "a.md",
        "kind": "wrong-answer",
        "decision": "applied",
        "summary": "bad row",
    }
    return json.dumps({**base, **over})


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for name in ("a.md", "b.md", "c.md"):
        (tmp_path / name).touch()
    return tmp_path


def test_add_refuses_a_missing_target_and_writes_nothing(repo: Path) -> None:
    log = repo / "logs" / "log.jsonl"
    with pytest.raises(ValueError, match=r"line 2: target gone\.md does not exist"):
        fl.add(log, [row(), row(summary="x", target="gone.md")], "2026-11-06", repo)
    assert fl.read_rows(log) == []


def test_add_decide_and_report(repo: Path) -> None:
    log = repo / "logs" / "log.jsonl"
    ids = fl.add(log, [row(decision="listed")], "2026-11-06", repo)
    assert len(ids) == 1
    assert "1 open" in "\n".join(fl.report_lines(fl.read_rows(log)))
    with pytest.raises(ValueError, match="needs a reason"):
        fl.decide(log, ids[0], "rejected", "", "2026-11-06")
    fl.decide(log, ids[0], "rejected", "not a fault", "2026-11-06")
    assert fl.current(fl.read_rows(log))[ids[0]]["decision"] == "rejected"
    with pytest.raises(ValueError, match="no finding"):
        fl.decide(log, "deadbeef", "applied", "", "2026-11-06")


def test_validate_rules() -> None:
    assert fl.validate(json.loads(row())) is None
    assert "missing" in (fl.validate({"run": "r"}) or "")
    assert "rejected" in (fl.validate(json.loads(row(decision="rejected"))) or "")


def test_pattern_promotion_candidate(repo: Path) -> None:
    log = repo / "log.jsonl"
    lines = [
        row(target=t, summary=f"s{i}", pattern="p") for i, t in enumerate(("a.md", "b.md", "c.md"))
    ]
    fl.add(log, lines, "2026-11-06", repo)
    assert fl.candidates(fl.read_rows(log)) == [("p", 3, 3)]
    fl.append(log, [{"type": "promotion", "pattern": "p", "to": "check"}])
    assert fl.candidates(fl.read_rows(log)) == []


def test_cli_findings_uses_the_given_log(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = repo / "x" / "log.jsonl"
    assert fl.main(["--log", str(log), "report"]) == 0
    assert "No findings" in capsys.readouterr().out


def test_default_log_is_under_the_gitignored_logs_dir() -> None:
    settings = get_settings()
    assert settings.review_findings_log.is_relative_to(settings.logs_dir)
    assert settings.signals_dir.is_relative_to(settings.logs_dir)


def test_score_eval(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cases = [
        {"id": "c1", "reviewer": "r", "planted": [{"id": "f1", "any": ["wrong answer"]}]},
        {"id": "c2", "reviewer": "r", "planted": []},
    ]
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(cases))
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "c1.txt").write_text("FINDINGS\n- major: the Wrong Answer in step 2\n")
    (reports / "c2.txt").write_text("FINDINGS\n")
    assert se.main(["r", "--cases", str(cases_file), "--reports", str(reports)]) == 0
    assert "recall 1/1, 0 findings on clean controls" in capsys.readouterr().out
    assert se.main(["nobody", "--cases", str(cases_file), "--reports", str(reports)]) == 1
    assert se.main(["r", "--cases", str(tmp_path / "none.json"), "--reports", str(reports)]) == 1


def test_signals_reads_logs_and_never_the_drill_note(tmp_path: Path) -> None:
    courses = tmp_path / "courses"
    (courses / "programming" / "drills").mkdir(parents=True)
    cards = [{"deck": "d", "front": "Q?", "result": "missed", "source": "s"} for _ in range(3)]
    search = tmp_path / "retrieval.jsonl"
    search.write_text(json.dumps({"tool": "search_wiki", "query": "zzz", "n_results": 0}) + "\n")
    drill_log = tmp_path / "drill-log.md"
    drill_log.write_text(
        "| Date | QID | Aid | Score | Note |\n|---|---|---|---|---|\n"
        "| 2026-11-01 | two-sum | 3 | ✗✗ | PRIVATE-NOTE-TEXT |\n"
    )
    text = sg.build(courses, cards, search, drill_log, tmp_path / "none.jsonl")
    assert "100% missed of 3" in text
    assert '1x "zzz"' in text
    assert "two-sum" in text
    assert "PRIVATE-NOTE-TEXT" not in text


def test_signals_without_any_logs_still_builds(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert "Coursework signals" in sg.build(tmp_path, [], missing, missing, missing)


def test_review_real_tree_completes(capsys: pytest.CaptureFixture[str]) -> None:
    assert sg.main([]) == 0
    assert "Coursework signals" in capsys.readouterr().out
    assert fl.main(["report"]) == 0
