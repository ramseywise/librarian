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


def main() -> None:
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
    p.add_argument(
        "--output", default=None, help="Write report to file (default: stdout)"
    )
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


if __name__ == "__main__":
    main()
