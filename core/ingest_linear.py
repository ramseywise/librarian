"""Dump Linear issues → raw/linear/

Fetches issues for a project or team from Linear and saves as structured
markdown to raw/linear/YYYY-MM-DD-<project>.md.

Usage:
    uv run python core/ingest_linear.py                       # uses LINEAR_PROJECT_ID from .env
    uv run python core/ingest_linear.py --team <team-key>     # all issues for a team
    uv run python core/ingest_linear.py --project <project-id>
    uv run python core/ingest_linear.py --dry-run
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import httpx
import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.base import REPO_ROOT, ScraperBase

load_dotenv()
log = structlog.get_logger()

RAW_LINEAR = REPO_ROOT / "raw" / "linear"

LINEAR_API = "https://api.linear.app/graphql"


class Settings(BaseSettings):
    linear_api_key: str
    linear_project_id: str = ""


ISSUES_QUERY = """
query Issues($filter: IssueFilter, $first: Int) {
  issues(filter: $filter, first: $first, orderBy: updatedAt) {
    nodes {
      id
      identifier
      title
      description
      state { name }
      priority
      assignee { name }
      labels { nodes { name } }
      comments { nodes { body createdAt user { name } } }
      updatedAt
      url
    }
  }
}
"""


def fetch_issues(api_key: str, project_id: str = "", team_key: str = "") -> list[dict]:
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    filter_var: dict = {}
    if project_id:
        filter_var["project"] = {"id": {"eq": project_id}}
    if team_key:
        filter_var["team"] = {"key": {"eq": team_key}}

    with httpx.Client(headers=headers) as client:
        resp = client.post(
            LINEAR_API,
            json={"query": ISSUES_QUERY, "variables": {"filter": filter_var, "first": 100}},
        )
        resp.raise_for_status()
        data = resp.json()

    return data.get("data", {}).get("issues", {}).get("nodes", [])


def issue_to_markdown(issue: dict) -> str:
    lines = [
        f"### [{issue['identifier']}] {issue['title']}",
        f"**Status:** {issue['state']['name']}  ",
        f"**Priority:** {issue.get('priority', 'None')}  ",
        f"**Assignee:** {issue['assignee']['name'] if issue.get('assignee') else 'Unassigned'}  ",
        f"**Labels:** {', '.join(n['name'] for n in issue.get('labels', {}).get('nodes', [])) or 'None'}  ",
        f"**URL:** {issue['url']}  ",
        "",
        issue.get("description") or "_No description._",
    ]

    comments = issue.get("comments", {}).get("nodes", [])
    if comments:
        lines += ["", "**Comments:**"]
        for c in comments:
            author = c.get("user", {}).get("name", "Unknown")
            lines.append(f"> **{author}** ({c['createdAt'][:10]}): {c['body']}")

    return "\n".join(lines)


class LinearScraper(ScraperBase):
    source_name = "ingest-linear"
    output_dir = RAW_LINEAR

    def __init__(self, project_id: str = "", team_key: str = "") -> None:
        self._project_id = project_id
        self._team_key = team_key

    def run(self, dry_run: bool = False) -> list[Path]:
        settings = Settings()
        project_id = self._project_id or settings.linear_project_id
        team_key = self._team_key

        slug = team_key or project_id or "all"
        today = date.today().isoformat()
        out_path = self.output_dir / f"{today}-linear-{slug}.md"

        if dry_run:
            print(
                f"[would fetch] Linear issues (project={project_id or 'all'}, team={team_key or 'all'}) → {out_path}"
            )
            return [out_path]

        log.info("fetching_linear_issues", project_id=project_id, team_key=team_key)
        issues = fetch_issues(settings.linear_api_key, project_id, team_key)
        log.info("fetched_issues", count=len(issues))

        self.output_dir.mkdir(parents=True, exist_ok=True)

        sections = [
            f"# Linear Issues — {slug}\n\n**Fetched:** {today}  \n**Count:** {len(issues)}\n"
        ]
        for issue in issues:
            sections.append(issue_to_markdown(issue))

        out_path.write_text("\n\n---\n\n".join(sections), encoding="utf-8")
        log.info("saved_linear_dump", dest=str(out_path))
        print(f"Saved: {out_path}")
        print(f"Run /ingest {out_path} in Claude Code to compile into wiki.")

        return [out_path]

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--team",
            default="",
            metavar="TEAM_KEY",
            help="Linear team key (e.g. ENG)",
        )
        parser.add_argument(
            "--project",
            default="",
            metavar="PROJECT_ID",
            help="Linear project ID (overrides LINEAR_PROJECT_ID env var)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> LinearScraper:
        return cls(project_id=args.project, team_key=args.team)


if __name__ == "__main__":
    LinearScraper.cli(description="Dump Linear issues → raw/linear/")
