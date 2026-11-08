"""Wiki health telemetry: deterministic numbers, an operation log and a gaps list.

No model calls: the output depends only on the files read and the date. Everything written
goes to data/telemetry/, outside data/wiki/, so the MCP index, relinker and graph never see it.

    uv run librarian wiki stats [--json]
    uv run librarian wiki snapshot            # stats + one row in metrics.jsonl
    uv run librarian wiki check [--file PATH] # private-leak check, exit 1 on BLOCKER;
                                              # ontology findings (ONT001-004) only warn
    uv run librarian wiki log <op> "<detail>" # exit 2 if detail names a private page
    uv run librarian wiki log ingest --counts "<source>"  # counts from the diff against HEAD
    uv run librarian wiki ask "<topic>"       # gitignored asked.jsonl
    uv run librarian wiki gaps                # regenerate gitignored gaps.md

`metrics.jsonl` and `operations.jsonl` are tracked in a public repo. Private pages are never
scored, hub-listed or printed: reports name the public file and line, never the private page.

This module is the CLI (`python -m librarian.wiki.telemetry`, `librarian wiki <verb>`) and a facade:
the code is in `pages` (reading the wiki), `stats`, `oplog` (the telemetry files), `leak_check`
and `gaps`, and every name that lived here is re-exported so importers keep working.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from librarian.ingest.sensitive import load_terms, scan_text, terms_pattern
from librarian.wiki import course_leaks
from librarian.wiki.gaps import (
    _GAP_LINE_RE as _GAP_LINE_RE,
)
from librarian.wiki.gaps import (
    _INLINE_CODE_RE as _INLINE_CODE_RE,
)
from librarian.wiki.gaps import (
    ASKED_FLOOR_NOTE as ASKED_FLOOR_NOTE,
)
from librarian.wiki.gaps import (
    QUERY_TOOLS as QUERY_TOOLS,
)
from librarian.wiki.gaps import (
    TOP_GAPS as TOP_GAPS,
)
from librarian.wiki.gaps import (
    AskedGaps as AskedGaps,
)
from librarian.wiki.gaps import (
    CourseGaps as CourseGaps,
)
from librarian.wiki.gaps import (
    Gap as Gap,
)
from librarian.wiki.gaps import (
    _apply_first_seen as _apply_first_seen,
)
from librarian.wiki.gaps import (
    _asked_gaps as _asked_gaps,
)
from librarian.wiki.gaps import (
    _course_gaps as _course_gaps,
)
from librarian.wiki.gaps import (
    _gap_lines as _gap_lines,
)
from librarian.wiki.gaps import (
    _sorted_gaps as _sorted_gaps,
)
from librarian.wiki.gaps import (
    regenerate_gaps as regenerate_gaps,
)
from librarian.wiki.leak_check import (
    CONTACT_CATEGORIES as CONTACT_CATEGORIES,
)
from librarian.wiki.leak_check import (
    TITLE_LEAK_MIN_WORDS as TITLE_LEAK_MIN_WORDS,
)
from librarian.wiki.leak_check import (
    LeakReport as LeakReport,
)
from librarian.wiki.leak_check import (
    _embedded_private_stems as _embedded_private_stems,
)
from librarian.wiki.leak_check import (
    _names_pattern as _names_pattern,
)
from librarian.wiki.leak_check import (
    _names_private_page as _names_private_page,
)
from librarian.wiki.leak_check import (
    _private_name_pattern as _private_name_pattern,
)
from librarian.wiki.leak_check import (
    _private_path_pattern as _private_path_pattern,
)
from librarian.wiki.leak_check import (
    _sensitive_issues as _sensitive_issues,
)
from librarian.wiki.leak_check import (
    _title_leak_pattern as _title_leak_pattern,
)
from librarian.wiki.leak_check import (
    check_file as check_file,
)
from librarian.wiki.leak_check import (
    run_check as run_check,
)
from librarian.wiki.ontology import check_ontology
from librarian.wiki.oplog import (
    _OP_RE as _OP_RE,
)
from librarian.wiki.oplog import (
    ASKED_FILE as ASKED_FILE,
)
from librarian.wiki.oplog import (
    GAPS_FILE as GAPS_FILE,
)
from librarian.wiki.oplog import (
    METRICS_FILE as METRICS_FILE,
)
from librarian.wiki.oplog import (
    METRICS_MAX_ROWS as METRICS_MAX_ROWS,
)
from librarian.wiki.oplog import (
    OPERATIONS_FILE as OPERATIONS_FILE,
)
from librarian.wiki.oplog import (
    OPERATIONS_KEEP_FULL as OPERATIONS_KEEP_FULL,
)
from librarian.wiki.oplog import (
    UNTRACKED_TELEMETRY as UNTRACKED_TELEMETRY,
)
from librarian.wiki.oplog import (
    TelemetryFileError as TelemetryFileError,
)
from librarian.wiki.oplog import (
    _display as _display,
)
from librarian.wiki.oplog import (
    _read_loose_jsonl as _read_loose_jsonl,
)
from librarian.wiki.oplog import (
    _read_tracked_jsonl as _read_tracked_jsonl,
)
from librarian.wiki.oplog import (
    _write_jsonl as _write_jsonl,
)
from librarian.wiki.oplog import (
    _write_text as _write_text,
)
from librarian.wiki.oplog import (
    ingest_counts as ingest_counts,
)
from librarian.wiki.oplog import (
    roll_operations as roll_operations,
)
from librarian.wiki.oplog import (
    write_snapshot as write_snapshot,
)
from librarian.wiki.pages import (
    _FM_BLOCK_RE as _FM_BLOCK_RE,
)
from librarian.wiki.pages import (
    _FM_TITLE_RE as _FM_TITLE_RE,
)
from librarian.wiki.pages import (
    COURSES_DIR as COURSES_DIR,
)
from librarian.wiki.pages import (
    REPO_ROOT as REPO_ROOT,
)
from librarian.wiki.pages import (
    RETRIEVAL_LOG as RETRIEVAL_LOG,
)
from librarian.wiki.pages import (
    TELEMETRY_DIR as TELEMETRY_DIR,
)
from librarian.wiki.pages import (
    WIKI_DIR as WIKI_DIR,
)
from librarian.wiki.pages import (
    Page as Page,
)
from librarian.wiki.pages import (
    PageLinks as PageLinks,
)
from librarian.wiki.pages import (
    _link_index as _link_index,
)
from librarian.wiki.pages import (
    _links_to_private as _links_to_private,
)
from librarian.wiki.pages import (
    _load_page as _load_page,
)
from librarian.wiki.pages import (
    _private_pages as _private_pages,
)
from librarian.wiki.pages import (
    _public_files as _public_files,
)
from librarian.wiki.pages import (
    _public_pages as _public_pages,
)
from librarian.wiki.pages import (
    _to_date as _to_date,
)
from librarian.wiki.pages import (
    _via_private_path as _via_private_path,
)
from librarian.wiki.stats import (
    _HEADING_RE as _HEADING_RE,
)
from librarian.wiki.stats import (
    _SEE_ALSO_RE as _SEE_ALSO_RE,
)
from librarian.wiki.stats import (
    _STATUS_RE as _STATUS_RE,
)
from librarian.wiki.stats import (
    COMPONENT_BROKEN as COMPONENT_BROKEN,
)
from librarian.wiki.stats import (
    COMPONENT_HEALTHY as COMPONENT_HEALTHY,
)
from librarian.wiki.stats import (
    DEGREE_BROKEN as DEGREE_BROKEN,
)
from librarian.wiki.stats import (
    DEGREE_HEALTHY_MAX as DEGREE_HEALTHY_MAX,
)
from librarian.wiki.stats import (
    DEGREE_HEALTHY_MIN as DEGREE_HEALTHY_MIN,
)
from librarian.wiki.stats import (
    METRIC_LABELS as METRIC_LABELS,
)
from librarian.wiki.stats import (
    ORPHAN_BROKEN as ORPHAN_BROKEN,
)
from librarian.wiki.stats import (
    ORPHAN_HEALTHY as ORPHAN_HEALTHY,
)
from librarian.wiki.stats import (
    STALE_DAYS as STALE_DAYS,
)
from librarian.wiki.stats import (
    STUB_HEALTHY as STUB_HEALTHY,
)
from librarian.wiki.stats import (
    STUB_WORDS as STUB_WORDS,
)
from librarian.wiki.stats import (
    TOP_HUBS as TOP_HUBS,
)
from librarian.wiki.stats import (
    TYPED_HEALTHY as TYPED_HEALTHY,
)
from librarian.wiki.stats import (
    _band_status as _band_status,
)
from librarian.wiki.stats import (
    _link_edges as _link_edges,
)
from librarian.wiki.stats import (
    _main_component_size as _main_component_size,
)
from librarian.wiki.stats import (
    _open_conflicts as _open_conflicts,
)
from librarian.wiki.stats import (
    _rate as _rate,
)
from librarian.wiki.stats import (
    _render_stats as _render_stats,
)
from librarian.wiki.stats import (
    _see_also_counts as _see_also_counts,
)
from librarian.wiki.stats import (
    compute_stats as compute_stats,
)


def _cmd_stats(args: argparse.Namespace) -> int:
    stats = compute_stats(args.wiki_dir, args.today)
    print(json.dumps(stats, indent=2, ensure_ascii=False) if args.json else _render_stats(stats))
    return 0


def _graph_shape(wiki_dir: Path) -> dict[str, Any]:
    """Cluster count, unsettled pages and stability for a snapshot row: report-only, no bands."""
    # Imported here: wiki_graph imports this module, and only snapshots need networkx and sklearn.
    from librarian.wiki.graph import analyse, load_graph

    report = analyse(load_graph(wiki_dir))
    return {
        "clusters": len(report.clusters),
        "unsettled": report.unsettled,
        "stability": report.stability,
    }


def _cmd_snapshot(args: argparse.Namespace) -> int:
    stats = compute_stats(args.wiki_dir, args.today)
    write_snapshot({**stats, **_graph_shape(args.wiki_dir)}, args.telemetry_dir)
    print(_render_stats(stats))
    print(f"\nSnapshot {stats['date']} written to {_display(args.telemetry_dir / METRICS_FILE)}")
    return 0


def _tracked_private_blockers(repo_root: Path) -> list[str]:
    """One blocker per private tree with tracked files, counting them and naming none."""
    tracked = course_leaks.tracked_private_files(repo_root)
    return [
        f"{len(hits)} tracked file(s) under {tree}/: remove them from the index (git rm --cached)"
        for tree in course_leaks.PRIVATE_DIRS
        if (hits := [f for f in tracked or [] if f.startswith(f"{tree}/")])
    ]


def _cmd_check(args: argparse.Namespace) -> int:
    if args.tracked_only:
        tracked = _tracked_private_blockers(args.repo_root)
        for line in tracked:
            print(f"BLOCKER {line}")
        return 1 if tracked else 0
    if args.file:  # the post-write hook: one file's wikilinks, no git call
        if not (args.wiki_dir / "private").is_dir():
            print("check: no private/ directory here, nothing to compare against")
            return 0
        blockers = check_file(args.file, args.wiki_dir)
        for line in blockers:
            print(f"BLOCKER {line}")
        return 1 if blockers else 0
    report = run_check(args.wiki_dir, args.telemetry_dir, args.courses_dir)
    assert report is not None  # a courses_dir is always passed
    if not (args.wiki_dir / "private").is_dir():
        print("check: no private/ directory here, nothing to compare against")
    report.blockers[:0] = _tracked_private_blockers(args.repo_root)
    # Ontology findings only ever warn: they never change the exit code.
    report.warnings.extend(check_ontology(args.wiki_dir))
    for line in report.blockers:
        print(f"BLOCKER {line}")
    for line in report.warnings:
        print(f"WARN {line}")
    print(
        f"check: {len(report.blockers)} blocker(s), {len(report.warnings)} warning(s), "
        f"{report.files_scanned} files against {report.private_pages} private pages, "
        f"{report.terms_listed} sensitive terms"
    )
    return 1 if report.blockers else 0


def _cmd_log(args: argparse.Namespace) -> int:
    if not _OP_RE.match(args.op):
        print("log: op must be one lowercase word, e.g. ingest", file=sys.stderr)
        return 2
    if args.counts:
        if "->" in args.detail:
            print(
                "log: with --counts, give only the source; the counts are computed", file=sys.stderr
            )
            return 2
        counts = ingest_counts(args.repo_root, args.wiki_dir)
        if counts is None:
            print(
                "log: --counts needs the wiki inside a git checkout at --repo-root", file=sys.stderr
            )
            return 2
        args.detail = (
            f"{args.detail} -> {counts['new']} new, {counts['updated']} updated, "
            f"{counts['links']} links, {counts['conflicts']} conflicts"
        )
    pattern = _private_name_pattern(_private_pages(args.wiki_dir))
    if _names_private_page(f"{args.op} {args.detail}", pattern):
        print(
            "log: refused, this text names a private page and operations.jsonl is public",
            file=sys.stderr,
        )
        return 2
    findings = scan_text(f"{args.op} {args.detail}", terms_pattern(load_terms(args.wiki_dir)))
    if findings:
        categories = ", ".join(sorted({f.category for f in findings}))
        print(
            f"log: refused, operations.jsonl is public and this text has: {categories}",
            file=sys.stderr,
        )
        return 2
    path = args.telemetry_dir / OPERATIONS_FILE
    rows = _read_tracked_jsonl(path)
    rows.append({"date": args.today.isoformat(), "op": args.op, "detail": args.detail})
    _write_jsonl(path, roll_operations(rows))
    if args.counts:
        print(args.detail)
    return 0


def _cmd_ask(args: argparse.Namespace) -> int:
    path = args.telemetry_dir / ASKED_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        row = {"date": args.today.isoformat(), "topic": args.topic}
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return 0


def _cmd_gaps(args: argparse.Namespace) -> int:
    top = regenerate_gaps(
        args.wiki_dir, args.telemetry_dir, args.courses_dir, args.retrieval_log, args.today
    )
    print(f"Wrote {_display(args.telemetry_dir / GAPS_FILE)}. Top {len(top)}:")
    for line in top:
        print(f"  {line}")
    return 0


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    common.add_argument("--telemetry-dir", type=Path, default=TELEMETRY_DIR)
    common.add_argument("--courses-dir", type=Path, default=COURSES_DIR)
    common.add_argument("--retrieval-log", type=Path, default=RETRIEVAL_LOG)
    common.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    common.add_argument(
        "--today", type=date.fromisoformat, default=None, help="YYYY-MM-DD, for tests"
    )

    parser = argparse.ArgumentParser(description="Deterministic wiki health telemetry.")
    commands = parser.add_subparsers(dest="command", required=True)
    stats = commands.add_parser("stats", parents=[common], help="print the health numbers")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(func=_cmd_stats)
    snapshot = commands.add_parser("snapshot", parents=[common], help="stats + one metrics row")
    snapshot.set_defaults(func=_cmd_snapshot)
    check = commands.add_parser("check", parents=[common], help="private-leak check")
    check.add_argument("--file", type=Path, help="only this file's wikilinks (post-write hook)")
    check.add_argument(
        "--tracked-only",
        action="store_true",
        help="only fail if git tracks a file under data/wiki/private/ or data/courses/private/",
    )
    check.set_defaults(func=_cmd_check)
    log = commands.add_parser("log", parents=[common], help="append to operations.jsonl")
    log.add_argument("op")
    log.add_argument("detail")
    log.add_argument(
        "--counts",
        action="store_true",
        help="detail is the source; append new/updated/links/conflicts from git diff HEAD",
    )
    log.set_defaults(func=_cmd_log)
    ask = commands.add_parser("ask", parents=[common], help="append to asked.jsonl")
    ask.add_argument("topic")
    ask.set_defaults(func=_cmd_ask)
    gaps = commands.add_parser("gaps", parents=[common], help="regenerate gaps.md")
    gaps.set_defaults(func=_cmd_gaps)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    args.today = args.today or date.today()
    if not args.wiki_dir.is_dir():
        print(f"{args.command}: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except TelemetryFileError as e:
        print(f"{args.command}: {e}; fix the line and re-run", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
