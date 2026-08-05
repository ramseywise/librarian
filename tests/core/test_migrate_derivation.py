"""Derived session notes must satisfy the contract their consumers already enforce.

`raw/sessions/` sat empty for weeks because nothing produced notes; `--facts` reads notes
that are not there, and `_update_wiki_session_log` renders rows from fields the old
renderer never filled. Deriving notes from JSONL only helps if what comes out actually
parses — a note that `_parse_one_session_note` rejects is indistinguishable, downstream,
from the empty directory we started with.

Each test below pins one of the three gaps in `migrate_jsonl_to_notes` that made its
output unusable for this purpose (#60):

1. date-level dedupe silently dropped every session after the first each day
2. `project: ~` was hardcoded, so the wiki log headed every group "unknown"
3. no `## Recent prompts` section, so every wiki row's topic column was "—"

See ramseywise/librarian#60.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.migrate import derive_notes
from shared.parser import _parse_one_session_note


def _fake_session(
    sid: str, start: str, *, cwd: str = "/Users/wiseer/workspace/librarian"
) -> dict[str, Any]:
    """The shape `parse_session` returns, trimmed to the fields the renderer reads."""
    return {
        "session_id": sid,
        "start_time": start,
        "end_time": start,
        "project_path": cwd,
        "session_repos": {"librarian": 3, "guacamayo": 1},
        "first_prompt": "why is the weekly cron emitting empty analyses?",
        "languages": {"python": 4},
        "tool_counts": {"Read": 6, "Bash": 2},
        "tool_errors": {},
        "skill_invocations": ["workflow-review"],
        "duration_minutes": 42,
        "files_modified": 3,
        "user_message_count": 9,
        "user_interruptions": 0,
        "bash_antipatterns": 0,
        "read_edit_ratio": 2.0,
        "input_tokens": 1200,
        "output_tokens": 340,
        "cache_write_tokens": 0,
        "cache_read_tokens": 0,
        "primary_model": "claude-opus-4-6",
    }


def test_derived_note_satisfies_parser_contract(tmp_path: Path) -> None:
    """The note must survive `_parse_one_session_note` with a truthy `work`.

    That parser returns `None` when `work` is missing, and `from_notes` drops `None`
    rows without comment — so a renderer regression here costs the whole ingest with no
    error anywhere. Asserting on the parsed dict, not on the raw text, is the point:
    the text can look right and still fail the only consumer that matters.
    """
    written = derive_notes([_fake_session("a1b2c3d4", "2026-07-30T09:00:00+00:00")], tmp_path)

    assert len(written) == 1
    note = _parse_one_session_note(written[0])
    assert note is not None, "parser rejected the derived note — from_notes would drop it"
    assert note["work"], "`work` is the one field _parse_one_session_note requires"


def test_same_day_sessions_each_get_a_note(tmp_path: Path) -> None:
    """Gap 1. Date-level dedupe kept one note per day and dropped the rest.

    Two sessions, one date. The old `existing_dates` check by `p.stem[:10]` wrote the
    first and skipped the second, which on a daily cadence loses most of the corpus.
    """
    sessions = [
        _fake_session("aaaa1111", "2026-07-30T09:00:00+00:00"),
        _fake_session("bbbb2222", "2026-07-30T14:00:00+00:00"),
    ]

    written = derive_notes(sessions, tmp_path)

    assert len(written) == 2, "same-day sessions collapsed — date dedupe is back"
    assert len({p.name for p in written}) == 2, "distinct sessions shared a filename"


def test_project_is_resolved_not_tilde(tmp_path: Path) -> None:
    """Gap 2. `project: ~` degrades two consumers at once.

    `_update_wiki_session_log` uses it as the date-group heading and `_tag_new_session_files`
    maps it to domain tags; with `~` the log heads every group "unknown" and tagging falls
    back to the default. Resolved from `session_repos` (highest count).
    """
    written = derive_notes([_fake_session("cccc3333", "2026-07-30T09:00:00+00:00")], tmp_path)

    note = _parse_one_session_note(written[0])
    assert note is not None
    assert note["project"] not in (None, "", "~"), "project stayed unresolved"
    assert note["project"] == "librarian", "should pick the highest-count repo"


def test_recent_prompts_section_is_present(tmp_path: Path) -> None:
    """Gap 3. `_update_wiki_session_log` scans for exactly this header (`cron.py:289`).

    Without it every wiki row's topic column renders "—". Asserted on the raw text
    because the consumer is a string scan, not the parser.
    """
    written = derive_notes([_fake_session("dddd4444", "2026-07-30T09:00:00+00:00")], tmp_path)

    text = written[0].read_text(encoding="utf-8")
    assert "## Recent prompts" in text, "wiki session-log topic column depends on this header"
    assert "why is the weekly cron" in text, "section present but the prompt never made it in"


def test_rerun_is_idempotent(tmp_path: Path) -> None:
    """A second run must derive nothing new — otherwise the daily `--facts` cadence
    rewrites the corpus every day and `raw/sessions/` grows without bound."""
    sessions = [_fake_session("eeee5555", "2026-07-30T09:00:00+00:00")]

    first = derive_notes(sessions, tmp_path)
    second = derive_notes(sessions, tmp_path)

    assert len(first) == 1
    assert second == [], "re-derived an existing note"


def test_since_window_excludes_older_sessions(tmp_path: Path) -> None:
    """The backfill window. 1004 JSONL sessions are available; deriving all of them in
    one run is the behaviour `--since` exists to prevent. Both directions asserted —
    a window that excluded everything would pass a one-sided test."""
    sessions = [
        _fake_session("old00001", "2026-01-01T09:00:00+00:00"),
        _fake_session("new00002", "2026-07-30T09:00:00+00:00"),
    ]

    written = derive_notes(sessions, tmp_path, since="2026-07-01")

    assert len(written) == 1, "the window let the old session through"
    assert "new00002" in written[0].stem, "the window kept the wrong session"
