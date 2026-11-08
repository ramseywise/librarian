"""`librarian jobs run <name>`: unattended jobs through the Claude Agent SDK.

A job is zero or more plain commands (scrapers, the indexer) followed by an optional skill run
headless with the same `.claude/skills/` the human uses. The agent runs in `dontAsk`
mode: any tool not on the job's allow list is denied, never prompted for. Git is stage-only,
the user's global rule: `commit`, `push`, `reset`, `stash`, `rebase` and `merge` are disallowed
for every job. Install the SDK with `uv sync --extra jobs`.

    librarian jobs list
    librarian jobs run wiki-weekly --dry-run     # print the plan, call nothing
    librarian jobs run feeds-ingest
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from librarian.config import get_settings

# Read-only tools and the wiki's own MCP search every skill job may use.
READ_TOOLS = [
    "Read",
    "Glob",
    "Grep",
    "Skill",
    "mcp__librarian__search_wiki",
    "mcp__librarian__read_page",
]


def _cli(*verbs: str) -> list[str]:
    """Allow rules for exact `librarian` verbs (prefix match, so arguments are free)."""
    return [f"Bash(uv run librarian {verb}:*)" for verb in verbs]


# Per job, only the verbs it needs. Never `scrape`, `ingest notion|linear|pdf`, `wiki rename` or
# anything else that fetches or rewrites existing pages.
WIKI_WEEKLY_CLI = _cli(
    "wiki stats",
    "wiki week",
    "wiki snapshot",
    "wiki check",
    "wiki graph",
    "wiki gaps",
    "wiki log weekly",
)
WEEKLY_CLI = _cli("wiki stats", "wiki check", "courses check")
# Ingest of the fetched queue files: triage, compile, verify, mark. The scrapers are the job's
# own `commands`, not the agent's.
FEEDS_INGEST_CLI = _cli(
    "ingest triage",
    "ingest status",
    "ingest pending",
    "ingest mark",
    "ingest lint-raw",
    "wiki stats",
    "wiki check",
    "wiki index-add",
    "wiki verify",
    "wiki relink",
    "wiki log ingest",
)
WEEKLY_MAKE = ["Bash(make review-findings)", "Bash(make signals)", "Bash(make deck-check)"]
# The agent compiles into the wiki and nowhere else; the manifest is written by `ingest mark`.
FEEDS_INGEST_WRITE = ["Write(data/wiki/**)", "Edit(data/wiki/**)"]
GIT_STAGE_ONLY = ["Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)"]

# No job may change these: `data/raw/` is append-only (the scrapers, run as the job's `commands`,
# are its only writer), and the skills, git state and secrets are not the agent's to edit.
NO_WRITE_PATHS = ["data/raw/**", "**/private/**", ".claude/**", ".git/**", ".env", ".env.*"]
# No job may read these: private pages never leave the machine.
NO_READ_PATHS = ["**/private/**", ".env", ".env.*"]
# Commands that change files behind a path rule's back (the rules guard the file tools, not the
# shell). None is on an allow list; the deny keeps it so if an allow rule is ever widened.
SHELL_BYPASSES = [
    "mv",
    "cp",
    "rm",
    "ln",
    "rsync",
    "tee",
    "dd",
    "sed",
    "truncate",
    "install",
    "git restore",
    "git checkout",
    "git switch",
    "git clean",
    "git rm",
    "git mv",
    "git apply",
    "git revert",
    "git cherry-pick",
    "git config",
]
# Denied for every job, whatever the skill asks for. Deny rules win over allow rules.
ALWAYS_DENIED = [
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git reset:*)",
    "Bash(git stash:*)",
    "Bash(git rebase:*)",
    "Bash(git merge:*)",
    "Bash(gh pr:*)",
    *(f"Bash({command}:*)" for command in SHELL_BYPASSES),
    *(f"Read({path})" for path in NO_READ_PATHS),
    *(f"{tool}({path})" for path in NO_WRITE_PATHS for tool in ("Write", "Edit")),
    "WebFetch",
    "WebSearch",
]


@dataclass(frozen=True)
class Job:
    description: str
    commands: tuple[tuple[str, ...], ...] = ()  # run first, in order, plain subprocesses
    prompt: str | None = None  # the skill invocation; None = commands only
    allowed_tools: list[str] = field(default_factory=list)
    max_turns: int = 60
    max_budget_usd: float = 5.0


JOBS: dict[str, Job] = {
    "feeds-ingest": Job(
        description="scrape feeds and arXiv, then /learn on the new items (stages, never commits)",
        commands=(
            ("uv", "run", "librarian", "scrape", "feeds"),
            ("uv", "run", "librarian", "scrape", "arxiv"),
        ),
        prompt="/learn",
        allowed_tools=[*READ_TOOLS, *FEEDS_INGEST_WRITE, *FEEDS_INGEST_CLI, *GIT_STAGE_ONLY],
        max_turns=150,
        max_budget_usd=10.0,
    ),
    "wiki-weekly": Job(
        description="the wiki's weekly review (/wiki-weekly); read-only, prints the report",
        prompt="/wiki-weekly",
        allowed_tools=[*READ_TOOLS, *WIKI_WEEKLY_CLI],
    ),
    "weekly": Job(
        description="the course's weekly health report (/weekly); read-only, prints the report",
        prompt="/weekly",
        allowed_tools=[*READ_TOOLS, *WEEKLY_CLI, *WEEKLY_MAKE, "Bash(uv run pytest:*)"],
    ),
    "codemap": Job(
        description="reindex the configured repos (no model involved)",
        commands=(("uv", "run", "codemap"),),
    ),
}


def build_options(job: Job, cwd: Path) -> dict[str, Any]:
    """The `ClaudeAgentOptions` fields for a job, as a dict so tests can read them without the SDK."""
    return {
        "cwd": str(cwd),
        "permission_mode": "dontAsk",
        "allowed_tools": list(job.allowed_tools),
        "disallowed_tools": list(ALWAYS_DENIED),
        "setting_sources": ["project"],  # loads .claude/skills/ and CLAUDE.md
        "max_turns": job.max_turns,
        "max_budget_usd": job.max_budget_usd,
    }


def _log(name: str, row: dict[str, Any]) -> None:
    path = get_settings().logs_dir / "jobs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"time": datetime.now().isoformat(timespec="seconds"), "job": name, **row}
    with path.open("a") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


async def _run_agent(job: Job, cwd: Path) -> dict[str, Any]:
    try:
        from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
    except ImportError:
        print("jobs: claude-agent-sdk missing; run `uv sync --extra jobs`", file=sys.stderr)
        return {"ok": False, "error": "sdk missing"}
    assert job.prompt is not None
    options = ClaudeAgentOptions(**build_options(job, cwd))
    outcome: dict[str, Any] = {"ok": False, "error": "no result message"}
    async for message in query(prompt=job.prompt, options=options):
        if isinstance(message, ResultMessage):
            if message.result:
                print(message.result)
            outcome = {
                "ok": not message.is_error,
                "turns": message.num_turns,
                "cost_usd": message.total_cost_usd,
                "denials": len(message.permission_denials or []),
            }
    return outcome


def run_job(name: str, dry_run: bool = False, cwd: Path | None = None) -> int:
    job = JOBS[name]
    cwd = cwd or get_settings().root
    if dry_run:
        for command in job.commands:
            print("command:", " ".join(command))
        if job.prompt:
            print("prompt: ", job.prompt)
            print(json.dumps(build_options(job, cwd), indent=2))
        return 0
    for command in job.commands:
        done = subprocess.run(command, cwd=cwd, check=False)
        if done.returncode != 0:
            _log(name, {"ok": False, "failed_command": " ".join(command), "code": done.returncode})
            return done.returncode
    outcome: dict[str, Any] = {"ok": True}
    if job.prompt:
        outcome = asyncio.run(_run_agent(job, cwd))
    _log(name, outcome)
    return 0 if outcome.get("ok") else 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["list"]:
        for name, job in JOBS.items():
            print(f"{name:<14} {job.description}")
        return 0
    parser = argparse.ArgumentParser(
        prog="librarian jobs run", description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("name", choices=sorted(JOBS))
    parser.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    ns = parser.parse_args(args)
    return run_job(ns.name, ns.dry_run)


if __name__ == "__main__":
    sys.exit(main())
