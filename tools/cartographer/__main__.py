"""CLI entry point for the cartographer agent.

Usage:
    uv run cartographer --dry-run          # Extract stats only (JSON → stdout)
    uv run cartographer                    # HTML report from session notes (+ JSONL if present)
    uv run cartographer --cron             # Friction analysis → .claude/docs/insights/{date}.md
    uv run cartographer --migrate          # Convert JSONL sessions → skeleton session notes
    uv run cartographer --compare          # Diff JSONL vs session notes by date
    uv run cartographer --enrich           # Backfill cost + facet data into session note frontmatter
"""

from __future__ import annotations

import sys
from pathlib import Path

from app.log_config import configure_logging


def main() -> None:
    configure_logging()
    """Route to the appropriate cartographer subcommand."""
    if "--cron" in sys.argv:
        sys.argv.remove("--cron")
        from tools.cartographer.cron import run_cron

        run_cron()

    elif "--migrate" in sys.argv:
        sys.argv.remove("--migrate")
        _run_migrate()

    elif "--compare" in sys.argv:
        sys.argv.remove("--compare")
        _run_compare()

    elif "--enrich" in sys.argv:
        sys.argv.remove("--enrich")
        _run_enrich()

    elif "--facts" in sys.argv:
        sys.argv.remove("--facts")
        _run_facts()

    else:
        from tools.cartographer.parser import main as parser_main

        parser_main()


def _run_migrate() -> None:
    """Convert existing JSONL sessions into skeleton session notes."""
    import argparse
    import json
    from pathlib import Path

    from tools.cartographer.migrate import migrate_jsonl_to_notes
    from tools.cartographer.parser import iter_sessions

    p = argparse.ArgumentParser(description="Migrate JSONL sessions to session notes")
    p.add_argument("--projects-dir", default="~/.claude/projects")
    p.add_argument("--sessions-dir", default="~/.claude/sessions")
    args = p.parse_args()

    projects_dir = Path(args.projects_dir).expanduser()
    sessions_dir = Path(args.sessions_dir).expanduser()

    # Load facets for qualitative enrichment
    facets_dir = Path.home() / ".claude" / "usage-data" / "facets"
    facets: dict = {}
    if facets_dir.exists():
        for fp in facets_dir.glob("*.json"):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                sid = data.get("session_id") or fp.stem
                facets[sid] = data
            except Exception:
                pass
    if facets:
        print(f"Loaded {len(facets)} facets for enrichment.")

    sessions = iter_sessions(projects_dir)
    if not sessions:
        print("No JSONL sessions found.", file=sys.stderr)
        sys.exit(1)

    created = migrate_jsonl_to_notes(sessions, sessions_dir, facets=facets or None)
    print(f"Created {len(created)} skeleton note(s):")
    for path in created:
        print(f"  {path}")


def _run_compare() -> None:
    """Diff JSONL sessions against session notes by date."""
    import argparse
    from pathlib import Path

    from tools.cartographer.migrate import compare_sources
    from tools.cartographer.parser import iter_sessions, parse_session_notes

    p = argparse.ArgumentParser(description="Compare JSONL vs session notes")
    p.add_argument("--projects-dir", default="~/.claude/projects")
    p.add_argument("--sessions-dir", default=".claude/sessions")
    p.add_argument("--output", default=None, help="Write report to file (default: stdout)")
    args = p.parse_args()

    projects_dir = Path(args.projects_dir).expanduser()
    sessions_dir = Path(args.sessions_dir).expanduser()

    sessions = iter_sessions(projects_dir)
    notes = parse_session_notes(sessions_dir)

    if not sessions and not notes:
        print("No data found in either source.", file=sys.stderr)
        sys.exit(1)

    report = compare_sources(sessions, notes)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"Comparison written to {out}")
    else:
        print(report)


def _run_enrich() -> None:
    """Backfill cost + facet data into session note frontmatter."""
    import argparse
    from pathlib import Path

    from tools.cartographer.enrich import run_enrich

    p = argparse.ArgumentParser(description="Enrich session notes with cost + facet data")
    p.add_argument(
        "--dirs",
        nargs="*",
        default=None,
        help="Directories to scan (default: ~/.claude/sessions and librarian/raw/sessions)",
    )
    args = p.parse_args()

    scan_dirs = [Path(d).expanduser() for d in args.dirs] if args.dirs else None
    run_enrich(scan_dirs)


def _parse_ledger(path: Path) -> list:
    """Parse tooling-ledger.md into Experiment objects."""
    import re

    from tools.cartographer.dashboard import Experiment

    if not path.exists():
        return []
    experiments = []
    row_re = re.compile(r"^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|\s*([^|]+)\s*\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row_re.match(line)
        if not m:
            continue
        date_cell = m.group(1).strip()
        change_cell = m.group(2).strip()
        metric_cell = m.group(3).strip()
        status_cell = m.group(4).strip()
        if date_cell in ("Date", "---") or status_cell in ("Status", "---"):
            continue
        if "rollup" in status_cell or "batch" in status_cell:
            continue
        experiments.append(
            Experiment(
                name=change_cell,
                metric=metric_cell or "—",
                status=status_cell,
                date=date_cell,
            )
        )
    return experiments


def _run_facts() -> None:
    """Refresh the session fact table and re-render the dashboard.

    Capture is cheap and needs no API key, so this is the piece that runs daily —
    local JSONL rotates out in roughly five days, and anything not captured before
    then is gone for good.
    """
    import argparse
    from datetime import UTC, datetime
    from pathlib import Path

    from tools.cartographer.dashboard import write_dashboard
    from tools.cartographer.factstore import from_jsonl, from_notes, read_all, upsert

    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description="Refresh the session fact table + dashboard")
    p.add_argument("--store", default=str(repo_root / "data" / "sessions.db"))
    p.add_argument("--projects-dir", default="~/.claude/projects")
    p.add_argument("--notes-dir", default=str(repo_root / "raw" / "sessions"))
    p.add_argument(
        "--dashboard",
        default=str(Path("~/workspace/guacamayo/.sounding/dashboard.html").expanduser()),
        help="Rendered dashboard path (guacamayo consolidates; librarian aggregates)",
    )
    p.add_argument(
        "--growth-md",
        default=str(Path("~/workspace/guacamayo/.sounding/growth.md").expanduser()),
    )
    p.add_argument("--stale-days", type=int, default=3)
    p.add_argument("--no-dashboard", action="store_true", help="Refresh facts only")
    p.add_argument("--workspace", default="~/workspace", help="Root scanned for git repos")
    p.add_argument("--no-git", action="store_true", help="Skip repo-activity collection")
    p.add_argument(
        "--ledger",
        default=str(Path("~/workspace/guacamayo/.claude/docs/tooling-ledger.md").expanduser()),
        help="Tooling ledger for experiment tracking",
    )
    args = p.parse_args()

    store = Path(args.store).expanduser()
    rows = from_notes(Path(args.notes_dir).expanduser())
    rows += from_jsonl(Path(args.projects_dir).expanduser())
    written = upsert(rows, store)
    print(f"Fact table: {written} rows upserted -> {store}")

    if not args.no_git:
        from tools.cartographer.gitstore import refresh as refresh_git

        commits, prs = refresh_git(Path(args.workspace).expanduser(), store)
        print(f"Repo activity: {commits} commit-days, {prs} PRs")

    if not args.no_dashboard:
        growth_md = Path(args.growth_md).expanduser()
        ledger_path = Path(args.ledger).expanduser()
        experiments = _parse_ledger(ledger_path) if ledger_path.exists() else None
        out = write_dashboard(
            store,
            Path(args.dashboard).expanduser(),
            growth_md=growth_md if growth_md.exists() else None,
            experiments=experiments or None,
        )
        print(f"Dashboard: {out}")

    # Staleness guard: the newest row aging past --stale-days means capture is not
    # keeping up with the ~5-day JSONL retention window, i.e. history is being lost.
    stored = read_all(store)
    newest = max((r["date"] for r in stored), default="")
    if newest:
        age = (datetime.now(UTC).date() - datetime.fromisoformat(newest).date()).days
        if age > args.stale_days:
            print(
                f"WARNING: newest fact row is {age} days old ({newest}). "
                f"Local JSONL rotates in ~5 days — sessions may already be lost. "
                f"Check the scheduled --facts run.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
