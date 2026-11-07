"""Job definitions: restrictive by construction, and `--dry-run` calls nothing."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from librarian.jobs.runner import ALWAYS_DENIED, JOBS, Job, build_options, main, run_job


def _glob(pattern: str) -> re.Pattern[str]:
    """A gitignore-style path glob: `**/` any depth (or none), `**` anything, `*` within a segment."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + "$")


def _matches(rule: str, tool: str, target: str) -> bool:
    """Whether a `Tool(spec)` rule covers `target` (a command or a repo-relative path)."""
    m = re.fullmatch(r"(\w+)(?:\((.*)\))?", rule)
    if not m or m.group(1) != tool:
        return False
    spec = m.group(2)
    if spec is None:
        return True
    if tool == "Bash":
        if spec.endswith(":*"):
            prefix = spec[:-2]
            return target == prefix or target.startswith(prefix + " ")
        return target == spec
    return bool(_glob(spec).match(target))


def _permitted(name: str, tool: str, target: str) -> bool:
    """The order of dontAsk mode: a deny always wins, then only an allow admits."""
    opts = build_options(JOBS[name], Path("/repo"))
    if any(_matches(r, tool, target) for r in opts["disallowed_tools"]):
        return False
    return any(_matches(r, tool, target) for r in opts["allowed_tools"])


WRITING_VERBS = [
    "scrape feeds",
    "scrape repos",
    "ingest notion",
    "ingest linear",
    "ingest pdf",
    "wiki rename Old New",
    "mcp --rebuild",
    "api",
]


@pytest.mark.parametrize("verb", WRITING_VERBS)
@pytest.mark.parametrize("name", sorted(JOBS))
def test_no_job_admits_fetching_or_rewriting_verbs(name: str, verb: str) -> None:
    assert not _permitted(name, "Bash", f"uv run librarian {verb}")


def test_each_job_admits_only_its_verbs() -> None:
    assert _permitted("wiki-weekly", "Bash", "uv run librarian wiki stats --json")
    assert _permitted("wiki-weekly", "Bash", "uv run librarian wiki log weekly x")
    assert not _permitted("wiki-weekly", "Bash", "uv run librarian wiki relink")
    assert _permitted("feeds-ingest", "Bash", "uv run librarian wiki relink")
    assert not _permitted("feeds-ingest", "Bash", "uv run librarian wiki rename A B")
    assert not _permitted("weekly", "Bash", "uv run librarian ingest mark x")
    assert not _permitted("weekly", "Bash", "make scrape")


PROTECTED_FILES = [
    "data/raw/web/2026-11-01-feed-x.md",
    "data/wiki/private/secret.md",
    "data/courses/private/leetcode/a.md",
    ".claude/skills/learn/SKILL.md",
    ".git/config",
    ".env",
]


@pytest.mark.parametrize("path", PROTECTED_FILES)
@pytest.mark.parametrize("tool", ["Write", "Edit"])
@pytest.mark.parametrize("name", sorted(JOBS))
def test_no_job_writes_protected_paths(name: str, tool: str, path: str) -> None:
    assert not _permitted(name, tool, path)


def test_feeds_ingest_writes_the_wiki_only() -> None:
    assert _permitted("feeds-ingest", "Write", "data/wiki/rag/new-page.md")
    assert _permitted("feeds-ingest", "Edit", "data/wiki/_index.md")
    assert not _permitted("feeds-ingest", "Write", "data/wiki/private/x.md")
    assert not _permitted("feeds-ingest", "Write", "data/courses/programming/a.md")
    assert not _permitted("feeds-ingest", "Write", "src/librarian/config.py")


@pytest.mark.parametrize("path", ["data/wiki/private/a.md", "data/courses/private/b/c.md", ".env"])
@pytest.mark.parametrize("name", sorted(JOBS))
def test_no_job_reads_private_or_secrets(name: str, path: str) -> None:
    assert not _permitted(name, "Read", path)


def test_jobs_still_read_raw_sources() -> None:
    assert _permitted("feeds-ingest", "Read", "data/raw/web/x.md")


# Each of these would sidestep the path rules on the file tools. They are denied outright, so a
# later widening of an allow rule cannot admit them.
SHELL_BYPASS_COMMANDS = [
    "mv data/wiki/a.md data/raw/web/a.md",
    "cp data/wiki/a.md data/raw/web/a.md",
    "rm data/raw/web/a.md",
    "git restore data/raw/web/a.md",
    "git checkout -- data/raw/web/a.md",
    "git checkout HEAD~1 -- data/raw",
    "git switch -",
    "git clean -fd",
    "git rm data/raw/web/a.md",
    "git mv data/raw/a.md data/raw/b.md",
    "git apply patch.diff",
    "git revert HEAD",
    "git cherry-pick abc123",
    "sed -i s/a/b/ data/raw/web/a.md",
    "tee data/raw/web/a.md",
    "ln -sf /etc/passwd data/wiki/a.md",
    "rsync -a x/ data/raw/",
    "dd of=data/raw/web/a.md",
    "truncate -s 0 data/raw/web/a.md",
    "git config core.hooksPath /tmp/h",
]


@pytest.mark.parametrize("command", SHELL_BYPASS_COMMANDS)
@pytest.mark.parametrize("name", sorted(JOBS))
def test_shell_bypasses_are_refused(name: str, command: str) -> None:
    assert not _permitted(name, "Bash", command)
    opts = build_options(JOBS[name], Path("/repo"))
    assert any(_matches(r, "Bash", command) for r in opts["disallowed_tools"])


@pytest.mark.parametrize("command", SHELL_BYPASS_COMMANDS)
def test_a_widened_allow_still_loses_to_the_deny(command: str) -> None:
    widened = Job(description="x", prompt="/learn", allowed_tools=["Bash(mv:*)", "Bash(git:*)"])
    opts = build_options(widened, Path("/repo"))
    assert any(_matches(r, "Bash", command) for r in opts["disallowed_tools"])


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
