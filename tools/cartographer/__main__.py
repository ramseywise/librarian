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


def _run_facts() -> None:
    """Refresh the session fact table and re-render the dashboard.

    Capture is cheap and needs no API key, so this is the piece that runs daily —
    local JSONL rotates out in roughly five days, and anything not captured before
    then is gone for good.
    """
    import argparse
    from datetime import UTC, datetime
    from pathlib import Path

    from tools.cartographer.factstore import from_jsonl, from_notes, read_all, upsert

    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description="Refresh the session fact table + dashboard")
    p.add_argument("--store", default=str(repo_root / "data" / "sessions.db"))
    p.add_argument("--projects-dir", default="~/.claude/projects")
    p.add_argument("--notes-dir", default=str(repo_root / "raw" / "sessions"))
    p.add_argument(
        "--dashboard",
        default=str(repo_root / "data" / "dashboard.html"),
        help=(
            "Rendered dashboard path (engine artifact, librarian-local). "
            "Never guacamayo/.sounding/dashboard.html — deprecated; the shared artifact "
            "is context-dashboard.html, region-injected, not full-page rendered (LIB #68)"
        ),
    )
    p.add_argument(
        "--context-dashboard",
        default=str(Path("~/workspace/guacamayo/.sounding/context-dashboard.html").expanduser()),
        help=(
            "Path to the shared context-dashboard.html for region injection. "
            "Cartographer injects only the regions it owns (REVIEW-FINDINGS, "
            "EXPERIMENTS-LIFECYCLE); all other regions and hand-written content "
            "are left untouched."
        ),
    )
    p.add_argument(
        "--growth-md",
        default=str(Path("~/workspace/guacamayo/.sounding/growth.md").expanduser()),
    )
    p.add_argument("--stale-days", type=int, default=3)
    p.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Skip the full-page dashboard render (does not affect region injection)",
    )
    p.add_argument(
        "--no-inject", action="store_true", help="Skip region injection into context-dashboard.html"
    )
    p.add_argument("--workspace", default="~/workspace", help="Root scanned for git repos")
    p.add_argument("--no-git", action="store_true", help="Skip repo-activity collection")
    p.add_argument(
        "--findings",
        default=str(Path("~/workspace/guacamayo/.claude/docs/review-findings.jsonl").expanduser()),
        help="Review findings JSONL for the review card",
    )
    p.add_argument(
        "--ledger",
        default=str(Path("~/workspace/guacamayo/.sounding/tooling-ledger.md").expanduser()),
        help="Tooling ledger path for the experiments card",
    )
    p.add_argument(
        "--ledger-log",
        default=None,
        help="Tooling ledger log path (optional, for archived experiments)",
    )
    p.add_argument(
        "--no-verdicts",
        action="store_true",
        help="Skip deterministic verdict scoring against the tooling ledger",
    )
    p.add_argument(
        "--hook-log",
        default=str(Path("~/.claude/.hook-log.jsonl").expanduser()),
        help="Guard-hook event log (blocks/warns) for the hook-activity card",
    )
    p.add_argument(
        "--hook-pass-log",
        default=str(Path("~/.claude/.hook-pass-log.jsonl").expanduser()),
        help="Guard-hook pass log (silent OKs) for the hook-activity card",
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

    if not args.no_verdicts:
        from tools.cartographer.dashboard import parse_ledger
        from tools.cartographer.factstore import append_verdicts, read_all
        from tools.cartographer.verdicts import score_metric

        ledger_path = Path(args.ledger).expanduser()
        ledger_log_path = Path(args.ledger_log).expanduser() if args.ledger_log else None
        if ledger_path.exists():
            experiments = parse_ledger(ledger_path, ledger_log_path)
            scored_rows = read_all(store)
            run_at = datetime.now(UTC).isoformat()
            verdict_rows = []
            for exp in experiments:
                verdict = score_metric(exp.metric, scored_rows)
                verdict_rows.append(
                    {
                        "experiment": exp.name,
                        "date": exp.date,
                        "metric": exp.metric,
                        "verdict": verdict.verdict,
                        "evidence": verdict.evidence,
                    }
                )
            appended = append_verdicts(verdict_rows, store, run_at)
            print(f"Verdicts: {appended} scored -> {store}")
        else:
            print(f"Verdicts: skipped — ledger not found at {ledger_path}")

    if not args.no_dashboard:
        from tools.cartographer.dashboard import (
            parse_findings,
            patch_experiments_card,
            patch_friction_regroup_card,
            patch_hook_activity_card,
            patch_input_tokens_card,
            patch_review_findings,
            patch_skill_economics_card,
            patch_tool_trends_card,
        )

        dashboard = Path(args.dashboard).expanduser()
        findings_path = Path(args.findings).expanduser()
        ledger_path = Path(args.ledger).expanduser()
        ledger_log_path = Path(args.ledger_log).expanduser() if args.ledger_log else None

        findings = parse_findings(findings_path) if findings_path.exists() else []
        if patch_review_findings(dashboard, findings):
            print(f"Dashboard: review card refreshed ({len(findings)} findings) -> {dashboard}")
        else:
            print(f"Dashboard: skipped — {dashboard} missing or has no REVIEW-FINDINGS markers")

        if patch_input_tokens_card(dashboard, store):
            print("Dashboard: input-tokens card refreshed")
        else:
            print("Dashboard: input-tokens card skipped (missing markers)")

        if patch_skill_economics_card(dashboard, store):
            print("Dashboard: skill-economics card refreshed")
        else:
            print("Dashboard: skill-economics card skipped (missing markers)")

        if patch_tool_trends_card(dashboard, store):
            print("Dashboard: tool-trends card refreshed")
        else:
            print("Dashboard: tool-trends card skipped (missing markers)")

        if patch_friction_regroup_card(dashboard, store):
            print("Dashboard: friction-regroup card refreshed")
        else:
            print("Dashboard: friction-regroup card skipped (missing markers)")

        if patch_experiments_card(
            dashboard, ledger_path=ledger_path, ledger_log_path=ledger_log_path
        ):
            print("Dashboard: experiments card refreshed")
        else:
            print("Dashboard: experiments card skipped (missing markers)")

        hook_log = Path(args.hook_log).expanduser()
        hook_pass_log = Path(args.hook_pass_log).expanduser()
        if patch_hook_activity_card(dashboard, hook_log, hook_pass_log):
            print("Dashboard: hook-activity card refreshed")
        else:
            print("Dashboard: hook-activity card skipped (missing markers)")

    # Deliberately NOT gated on --no-dashboard. The daily cron passes that flag to
    # suppress the deprecated full-page render (cartographer-cron.sh:61), and region
    # injection is the behaviour meant to replace it — coupling them would mean the
    # daily job never refreshes a region. --no-inject is the only opt-out.
    if not args.no_inject:
        from tools.cartographer.dashboard import (
            inject_regions,
            parse_findings,
            parse_ledger,
            render_experiments_region,
            render_friction_regroup_card,
            render_input_tokens_card,
            render_review_findings_region,
            render_skill_economics_card,
            render_tool_trends_card,
        )

        ctx_path = Path(args.context_dashboard).expanduser()
        if ctx_path.exists():
            ledger_path = Path(args.ledger).expanduser()
            ledger_log_path = Path(args.ledger_log).expanduser() if args.ledger_log else None
            experiments = (
                parse_ledger(ledger_path, ledger_log_path) if ledger_path.exists() else None
            )
            findings_path = Path(args.findings).expanduser()
            review_findings = parse_findings(findings_path) if findings_path.exists() else None

            regions: dict[str, str] = {
                "REVIEW-FINDINGS": render_review_findings_region(review_findings),
                "EXPERIMENTS-LIFECYCLE": render_experiments_region(experiments or None),
                "INPUT-TOKENS": render_input_tokens_card(store),
                "SKILL-ECONOMICS": render_skill_economics_card(store),
                "TOOL-TRENDS": render_tool_trends_card(store),
                "FRICTION-REGROUP": render_friction_regroup_card(store),
            }
            injected = inject_regions(ctx_path, regions)
            print(f"Region injection: {injected}")
        else:
            print(f"context-dashboard not found, skipping injection: {ctx_path}", flush=True)

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
