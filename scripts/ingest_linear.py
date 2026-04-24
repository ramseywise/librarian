"""Dump Linear issues → raw/linear/

Fetches issues for a project or team from Linear and saves as structured
markdown to raw/linear/YYYY-MM-DD-<project>.md.

Usage:
    uv run python scripts/ingest_linear.py                       # uses LINEAR_PROJECT_ID from .env
    uv run python scripts/ingest_linear.py --team <team-key>     # all issues for a team
    uv run python scripts/ingest_linear.py --project <project-id>
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import httpx
import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
log = structlog.get_logger()

RAW_LINEAR = Path("raw/linear")

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


def main() -> None:
    settings = Settings()

    team_key = ""
    project_id = settings.linear_project_id

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--team" and i + 1 < len(args):
            team_key = args[i + 1]
        if arg == "--project" and i + 1 < len(args):
            project_id = args[i + 1]

    log.info("fetching_linear_issues", project_id=project_id, team_key=team_key)
    issues = fetch_issues(settings.linear_api_key, project_id, team_key)
    log.info("fetched_issues", count=len(issues))

    today = date.today().isoformat()
    slug = team_key or project_id or "all"
    out_path = RAW_LINEAR / f"{today}-linear-{slug}.md"
    RAW_LINEAR.mkdir(parents=True, exist_ok=True)

    sections = [f"# Linear Issues — {slug}\n\n**Fetched:** {today}  \n**Count:** {len(issues)}\n"]
    for issue in issues:
        sections.append(issue_to_markdown(issue))

    out_path.write_text("\n\n---\n\n".join(sections), encoding="utf-8")
    log.info("saved_linear_dump", dest=str(out_path))
    print(f"Saved: {out_path}")
    print(f"Run /ingest {out_path} in Claude Code to compile into wiki.")


if __name__ == "__main__":
    main()
