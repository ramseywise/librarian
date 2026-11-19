"""Agent-log retention (security review S10): old lines go, everything else stays."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from librarian.config import get_settings
from librarian.ops import cli
from librarian.ops.logs import prune_agent_log

NOW = datetime(2026, 11, 17, 12, 0, tzinfo=UTC)


def _line(days_ago: float, **extra: object) -> str:
    ts = (NOW - timedelta(days=days_ago)).isoformat()
    return json.dumps({"ts": ts, "query": f"q{days_ago}", **extra}) + "\n"


def _log(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "agent.jsonl"
    path.write_text("".join(lines), encoding="utf-8")
    return path


def test_lines_past_the_window_are_removed_and_newer_ones_kept(tmp_path: Path) -> None:
    path = _log(tmp_path, _line(200), _line(91), _line(89), _line(1))
    res = prune_agent_log(tmp_path, 90, now=NOW)
    assert (res.removed, res.kept) == (2, 2)
    assert [json.loads(x)["query"] for x in path.read_text().splitlines()] == ["q89", "q1"]


def test_unreadable_lines_and_a_half_written_last_line_are_kept(tmp_path: Path) -> None:
    path = _log(tmp_path, _line(200), "not json\n", '{"no_ts": 1}\n', _line(1))
    with path.open("a") as f:
        f.write('{"ts": "2026-01-01T00:00:00+00:00", "que')  # a writer mid-line
    res = prune_agent_log(tmp_path, 90, now=NOW)
    assert res.removed == 1 and res.unreadable == 2
    text = path.read_text()
    assert "not json" in text and '"no_ts"' in text and text.endswith('"que')


def test_dry_run_and_zero_days_change_nothing(tmp_path: Path) -> None:
    path = _log(tmp_path, _line(200), _line(1))
    before = path.read_bytes()
    assert prune_agent_log(tmp_path, 90, now=NOW, dry_run=True).removed == 1
    assert prune_agent_log(tmp_path, 0, now=NOW).removed == 0
    assert path.read_bytes() == before


def test_a_missing_log_is_not_an_error_and_no_other_file_is_touched(tmp_path: Path) -> None:
    assert prune_agent_log(tmp_path, 90, now=NOW).removed == 0
    other = tmp_path / "retrieval.jsonl"
    other.write_text(_line(500))
    _log(tmp_path, _line(500))
    prune_agent_log(tmp_path, 90, now=NOW)
    assert other.read_text() == _line(500)


def test_a_held_lock_skips_the_run(tmp_path: Path) -> None:
    import fcntl

    path = _log(tmp_path, _line(200))
    with (tmp_path / ".agent.jsonl.prune.lock").open("a") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        res = prune_agent_log(tmp_path, 90, now=NOW)
    assert res.skipped and path.read_text() == _line(200)


def test_the_cli_uses_the_setting_and_a_days_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LIBRARIAN_LOGS_DIR", str(tmp_path))
    monkeypatch.setenv("LIBRARIAN_AGENT_LOG_RETENTION_DAYS", "30")
    get_settings.cache_clear()
    real = datetime.now(UTC)
    path = tmp_path / "agent.jsonl"
    path.write_text(
        "".join(json.dumps({"ts": (real - timedelta(days=d)).isoformat()}) + "\n" for d in (60, 1))
    )
    assert cli.main(["prune-logs", "--dry-run"]) == 0
    assert "would remove 1" in capsys.readouterr().out and len(path.read_text().splitlines()) == 2
    assert cli.main(["prune-logs"]) == 0
    assert "removed 1" in capsys.readouterr().out and len(path.read_text().splitlines()) == 1
    get_settings.cache_clear()


def test_the_setting_is_a_known_env_name() -> None:
    from librarian.config import known_env_names

    assert "LIBRARIAN_AGENT_LOG_RETENTION_DAYS" in known_env_names()
    assert get_settings().agent_log_retention_days == 90


def test_the_api_task_prunes_the_redirected_logs_dir_then_sleeps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    from librarian.api import main as api_main
    from librarian.retrieval import corpus

    real = datetime.now(UTC)
    path = tmp_path / "agent.jsonl"
    path.write_text(json.dumps({"ts": (real - timedelta(days=400)).isoformat()}) + "\n")
    monkeypatch.setattr(corpus, "LOGS_DIR", tmp_path)

    async def stop(_s: float) -> None:
        raise asyncio.CancelledError

    monkeypatch.setattr(api_main.asyncio, "sleep", stop)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(api_main.prune_agent_log_daily())
    assert path.read_text() == ""
