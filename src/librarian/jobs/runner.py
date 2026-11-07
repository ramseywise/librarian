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
WRITE_TOOLS = ["Write", "Edit"]
LIBRARIAN_CLI = ["Bash(uv run librarian:*)"]
GIT_STAGE_ONLY = ["Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)"]
# Denied for every job, whatever the skill asks for. Deny rules win over allow rules.
ALWAYS_DENIED = [
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git reset:*)",
    "Bash(git stash:*)",
    "Bash(git rebase:*)",
    "Bash(git merge:*)",
    "Bash(git checkout:*)",
    "Bash(gh pr:*)",
    "Bash(rm:*)",
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
        allowed_tools=[*READ_TOOLS, *WRITE_TOOLS, *LIBRARIAN_CLI, *GIT_STAGE_ONLY],
        max_turns=150,
        max_budget_usd=10.0,
    ),
    "wiki-weekly": Job(
        description="the wiki's weekly review (/wiki-weekly); read-only, prints the report",
        prompt="/wiki-weekly",
        allowed_tools=[*READ_TOOLS, *LIBRARIAN_CLI],
    ),
    "weekly": Job(
        description="the course's weekly health report (/weekly); read-only, prints the report",
        prompt="/weekly",
        allowed_tools=[*READ_TOOLS, *LIBRARIAN_CLI, "Bash(uv run pytest:*)", "Bash(make:*)"],
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
