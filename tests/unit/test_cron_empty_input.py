"""The weekly cron must not report success when nothing reached it.

For eleven days `run_cron()` exited 0 while producing a 67-byte report reading
"No session data available for analysis." — indistinguishable, from the outside, from a
run that worked. That is the failure shape this file exists to prevent: a pipeline that
cannot tell "no input" from "fine".

Every test asserts BOTH directions. A guard that always fired would pass the empty cases
and fail the populated ones, so this suite cannot go green on a cron that always exits 1.

See ramseywise/librarian#60.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.cartographer import cron

# The exact sentinel that used to be written to disk at exit 0.
PLACEHOLDER = "No session data available for analysis."


@pytest.fixture
def wired(tmp_path: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point every cron input and output at a temp dir. Returns that dir.

    Also neutralises the two functions that reach outside it: `_rotate_hook_log` reads
    and can RENAME the real ~/.claude/.hook-log.jsonl, and the analysis call would hit
    the network.
    """
    root = Path(tmp_path)
    for name in ("SESSIONS_DIR", "FRICTION_LOG", "COMMANDS_DIR", "INSIGHTS_DIR", "FACETS_DIR"):
        monkeypatch.setattr(cron, name, root / name.lower())
    monkeypatch.setattr(cron, "SESSION_META_DIR", root / "session_meta")
    monkeypatch.setattr(cron, "LIBRARIAN_RAW_SESSIONS", root / "raw_sessions")
    monkeypatch.setattr(cron, "LIBRARIAN_WIKI_DIR", root / "wiki")
    monkeypatch.setattr(cron, "_rotate_hook_log", lambda: None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    return root


def _populate(root: Path) -> None:
    """Give the pipeline one real session note — the minimum that counts as input."""
    sessions = root / "sessions_dir"
    sessions.mkdir(parents=True, exist_ok=True)
    (sessions / "2099-01-01_120000_librarian.md").write_text(
        "# Session\n\nDid some work.\n", encoding="utf-8"
    )


def _stub_api(monkeypatch: pytest.MonkeyPatch, text: str = "## Findings\n\nSomething.") -> None:
    """Replace the Anthropic call so the populated path never touches the network."""

    class _Block:
        def __init__(self, t: str) -> None:
            self.text = t

    class _Message:
        def __init__(self, t: str) -> None:
            self.content = [_Block(t)]

    class _Messages:
        def create(self, **_: object) -> _Message:
            return _Message(text)

    class _Client:
        def __init__(self, **_: object) -> None:
            self.messages = _Messages()

    monkeypatch.setattr(cron.anthropic, "Anthropic", _Client)


# --- run_analysis: empty input raises rather than returning a placeholder -------------


def test_run_analysis_raises_on_empty_input(wired: Path) -> None:
    with pytest.raises(cron.EmptyInputError) as exc:
        cron.run_analysis()
    # The message must name where it looked, or the operator cannot act on it.
    assert str(wired / "sessions_dir") in str(exc.value)


def test_run_analysis_returns_report_when_input_exists(
    wired: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _populate(wired)
    _stub_api(monkeypatch)
    assert "Something." in cron.run_analysis()


# --- run_cron: non-zero exit, and no placeholder file --------------------------------


def test_run_cron_exits_non_zero_on_empty_input(wired: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cron.run_cron()
    assert exc.value.code != 0, "empty input must not exit 0"


def test_run_cron_writes_no_report_on_empty_input(wired: Path) -> None:
    with pytest.raises(SystemExit):
        cron.run_cron()
    written = list((wired / "insights_dir").glob("*.md"))
    assert written == [], f"empty input wrote a report anyway: {written}"


def test_placeholder_string_is_never_written(wired: Path) -> None:
    """The specific 67-byte artifact from #60 must not reappear under any name."""
    with pytest.raises(SystemExit):
        cron.run_cron()
    for path in wired.rglob("*"):
        if path.is_file():
            assert PLACEHOLDER not in path.read_text(encoding="utf-8", errors="ignore"), (
                f"placeholder resurfaced in {path}"
            )


def test_run_cron_succeeds_when_input_exists(wired: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The positive direction — proves the guard is not simply always-on."""
    _populate(wired)
    _stub_api(monkeypatch)
    cron.run_cron()  # must not raise SystemExit
    reports = list((wired / "insights_dir").glob("*.md"))
    assert len(reports) == 1
    assert PLACEHOLDER not in reports[0].read_text(encoding="utf-8")


# --- the failure is recorded, not just signalled --------------------------------------


def test_summary_records_the_problem_on_empty_input(wired: Path) -> None:
    """latest.json is the durable trace — it must say why, not just stop existing."""
    with pytest.raises(SystemExit):
        cron.run_cron()
    summary_path = wired / "insights_dir" / "latest.json"
    assert summary_path.exists(), "no summary written — the failure left no trace"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["problems"], "summary claims no problems on a failing run"
    assert summary["report"] is None


def test_summary_is_clean_when_input_exists(wired: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _populate(wired)
    _stub_api(monkeypatch)
    cron.run_cron()
    summary = json.loads((wired / "insights_dir" / "latest.json").read_text(encoding="utf-8"))
    assert summary["problems"] == []
    assert summary["report"] is not None


# --- stages 1-3 starvation is its own signal ------------------------------------------


def test_starved_sync_is_reported_even_when_analysis_has_data(
    wired: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Facets alone satisfy the analysis, but an empty raw/sessions/ is still a fault.

    This is the exact live condition on 2026-08-02: raw/sessions/ empty while other
    inputs are fine. It must not pass silently.
    """
    facets = wired / "facets_dir"
    facets.mkdir(parents=True)
    (facets / "s1.json").write_text(json.dumps({"session_id": "s1"}), encoding="utf-8")
    _stub_api(monkeypatch)

    with pytest.raises(SystemExit) as exc:
        cron.run_cron()
    assert exc.value.code != 0

    summary = json.loads((wired / "insights_dir" / "latest.json").read_text(encoding="utf-8"))
    assert any("raw_sessions" in p for p in summary["problems"])
    # The analysis still ran and its output was still saved — starvation is a signal,
    # not a reason to throw away work that succeeded.
    assert summary["report"] is not None


def test_populated_sync_is_not_reported(wired: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _populate(wired)
    _stub_api(monkeypatch)
    cron.run_cron()
    synced = list((wired / "raw_sessions").glob("*.md"))
    assert len(synced) == 1, "the note did not reach raw/sessions/"
