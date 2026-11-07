"""Job definitions: restrictive by construction, and `--dry-run` calls nothing."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.jobs.runner import ALWAYS_DENIED, JOBS, build_options, main, run_job


@pytest.mark.parametrize("name", sorted(JOBS))
def test_every_job_denies_commit_and_push(name: str) -> None:
    opts = build_options(JOBS[name], Path("/repo"))
    assert opts["permission_mode"] == "dontAsk"
    assert "Bash(git commit:*)" in opts["disallowed_tools"]
    assert "Bash(git push:*)" in opts["disallowed_tools"]
    assert opts["disallowed_tools"] == ALWAYS_DENIED


@pytest.mark.parametrize("name", sorted(JOBS))
def test_no_job_allows_open_bash_or_git_write(name: str) -> None:
    allowed = JOBS[name].allowed_tools
    assert "Bash" not in allowed
    assert not any(t.startswith(("Bash(git commit", "Bash(git push")) for t in allowed)


def test_read_only_jobs_have_no_write_tools() -> None:
    for name in ("wiki-weekly", "weekly"):
        assert not {"Write", "Edit"} & set(JOBS[name].allowed_tools)


def test_prompts_are_existing_skills() -> None:
    skills = Path(__file__).parents[2] / ".claude" / "skills"
    for job in JOBS.values():
        if job.prompt:
            assert (skills / job.prompt.lstrip("/") / "SKILL.md").is_file()


def test_dry_run_prints_plan(capsys: pytest.CaptureFixture[str]) -> None:
    assert run_job("feeds-ingest", dry_run=True, cwd=Path("/repo")) == 0
    out = capsys.readouterr().out
    assert "scrape feeds" in out and "/learn" in out and "dontAsk" in out


def test_list_and_unknown(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list"]) == 0
    assert "wiki-weekly" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        main(["nope"])
