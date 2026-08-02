"""The scheduled jobs must not report success when nothing reached them.

For eleven days the weekly cron exited 0 while producing a 67-byte report reading
"No session data available for analysis." — indistinguishable, from the outside, from a
run that worked. That is the failure shape this file exists to prevent: a pipeline that
cannot tell "no input" from "fine".

The guard has moved with the work. The LLM analysis stage was retired in #60, so the
empty-input check now lives where the daily job actually reads: `cartographer --facts`,
which derives session notes from JSONL before anything consumes them. `--cron` keeps its
own starvation check for the sync/tag/wiki stages.

Every test asserts BOTH directions. A guard that always fired would pass the empty cases
and fail the populated ones, so this suite cannot go green on a job that always exits 1.

See ramseywise/librarian#60.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.cartographer import __main__ as cli
from tools.cartographer import cron
from tools.cartographer import parser as parser_module

# The exact sentinel that used to be written to disk at exit 0.
PLACEHOLDER = "No session data available for analysis."


# ---------------------------------------------------------------------------
# --facts — the daily job, where the empty-input guard lives now
# ---------------------------------------------------------------------------


def _fake_session(sid: str, start: str) -> dict[str, Any]:
    """The shape `parse_session` returns, trimmed to the fields the renderer reads."""
    return {
        "session_id": sid,
        "start_time": start,
        "end_time": start,
        "project_path": "/Users/wiseer/workspace/librarian",
        "session_repos": {"librarian": 2},
        "first_prompt": "why is the daily job emitting nothing?",
        "languages": {"python": 1},
        "tool_counts": {"Read": 3},
        "tool_errors": {},
        "skill_invocations": [],
        "duration_minutes": 5,
        "files_modified": 1,
        "user_message_count": 2,
        "user_interruptions": 0,
        "bash_antipatterns": 0,
        "read_edit_ratio": 1.0,
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_write_tokens": 0,
        "cache_read_tokens": 0,
        "primary_model": "claude-opus-4-6",
    }


class FactsRun:
    """Runs `_run_facts` fully inside a temp dir, and remembers where it pointed it.

    Everything that reaches outside — git scan, dashboard render, ledger verdicts — is
    switched off by flag, so a call exercises exactly the derive → parse → upsert path.
    """

    def __init__(self, root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.root = root
        self.projects = root / "projects"
        self.projects.mkdir()
        self.notes = root / "raw_sessions"
        self._monkeypatch = monkeypatch

    def __call__(self, sessions: list[dict[str, Any]]) -> None:
        self._monkeypatch.setattr(parser_module, "iter_sessions", lambda _dir: sessions)
        self._monkeypatch.setattr(
            "sys.argv",
            [
                "cartographer",
                "--store",
                str(self.root / "sessions.db"),
                "--projects-dir",
                str(self.projects),
                "--notes-dir",
                str(self.notes),
                "--findings",
                str(self.root / "findings.jsonl"),
                "--since",
                "2000-01-01",
                "--no-dashboard",
                "--no-inject",
                "--no-git",
                "--no-verdicts",
            ],
        )
        cli._run_facts()


@pytest.fixture
def facts_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FactsRun:
    return FactsRun(tmp_path, monkeypatch)


def test_facts_exits_non_zero_on_empty_input(facts_run: FactsRun) -> None:
    """No JSONL means no notes, no rows, and an empty fact table — at exit 0 that is
    byte-for-byte a healthy run. It must be a hard failure instead."""
    with pytest.raises(SystemExit) as exc:
        facts_run([])
    assert exc.value.code != 0, "empty input must not exit 0"


def test_facts_names_where_it_looked(
    facts_run: FactsRun, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failure that does not say which directory was empty is not actionable."""
    with pytest.raises(SystemExit):
        facts_run([])
    err = capsys.readouterr().err
    assert "FATAL" in err
    assert str(facts_run.projects) in err


def test_facts_writes_no_notes_on_empty_input(facts_run: FactsRun) -> None:
    with pytest.raises(SystemExit):
        facts_run([])
    written = list(facts_run.notes.glob("*.md")) if facts_run.notes.exists() else []
    assert written == [], f"empty input derived notes anyway: {written}"


def test_facts_succeeds_when_input_exists(facts_run: FactsRun) -> None:
    """The positive direction — proves the guard is not simply always-on."""
    facts_run([_fake_session("aaaa1111", "2026-07-30T09:00:00+00:00")])  # must not raise

    notes = list(facts_run.notes.glob("*.md"))
    assert len(notes) == 1, "a session was available but no note was derived"


def test_placeholder_string_is_never_written(facts_run: FactsRun, tmp_path: Path) -> None:
    """The specific 67-byte artifact from #60 must not reappear under any name."""
    facts_run([_fake_session("bbbb2222", "2026-07-30T09:00:00+00:00")])
    for path in tmp_path.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".txt"}:
            assert PLACEHOLDER not in path.read_text(encoding="utf-8", errors="ignore"), (
                f"placeholder resurfaced in {path}"
            )


# ---------------------------------------------------------------------------
# --cron — the weekly corpus sweep keeps its own starvation check
# ---------------------------------------------------------------------------


@pytest.fixture
def wired(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point every cron input and output at a temp dir. Returns that dir.

    `_rotate_hook_log` is neutralised because it reads and can RENAME the real
    ~/.claude/.hook-log.jsonl.
    """
    root = tmp_path
    monkeypatch.setattr(cron, "SESSIONS_DIR", root / "sessions_dir")
    monkeypatch.setattr(cron, "INSIGHTS_DIR", root / "insights_dir")
    monkeypatch.setattr(cron, "LIBRARIAN_RAW_SESSIONS", root / "raw_sessions")
    monkeypatch.setattr(cron, "LIBRARIAN_WIKI_DIR", root / "wiki")
    monkeypatch.setattr(cron, "_rotate_hook_log", lambda: None)
    return root


def _populate(root: Path) -> None:
    """Give the sweep one real session note — the minimum that counts as input."""
    sessions = root / "sessions_dir"
    sessions.mkdir(parents=True, exist_ok=True)
    (sessions / "2099-01-01_120000_librarian.md").write_text(
        "# Session\n\nDid some work.\n", encoding="utf-8"
    )


def test_run_cron_exits_non_zero_when_sessions_are_starved(wired: Path) -> None:
    """Stages 1-3 all read raw/sessions/. An empty one means every stage no-op'd."""
    with pytest.raises(SystemExit) as exc:
        cron.run_cron()
    assert exc.value.code != 0, "starved sync must not exit 0"


def test_run_cron_succeeds_when_input_exists(wired: Path) -> None:
    """The positive direction — proves the starvation guard is not always-on."""
    _populate(wired)
    cron.run_cron()  # must not raise SystemExit
    synced = list((wired / "raw_sessions").glob("*.md"))
    assert len(synced) == 1, "the note did not reach raw/sessions/"


def test_summary_records_the_problem_when_starved(wired: Path) -> None:
    """latest.json is the durable trace — it must say why, not just stop existing."""
    with pytest.raises(SystemExit):
        cron.run_cron()
    summary_path = wired / "insights_dir" / "latest.json"
    assert summary_path.exists(), "no summary written — the failure left no trace"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert any("raw_sessions" in p for p in summary["problems"])


def test_summary_is_clean_when_input_exists(wired: Path) -> None:
    _populate(wired)
    cron.run_cron()
    summary = json.loads((wired / "insights_dir" / "latest.json").read_text(encoding="utf-8"))
    assert summary["problems"] == []


def test_cron_needs_no_api_key(wired: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The sweep is deterministic since #60 retired the analysis stage.

    FAILS IF: an LLM call comes back into `run_cron` — the missing key would exit 1.
    """
    _populate(wired)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cron.run_cron()  # must not raise
