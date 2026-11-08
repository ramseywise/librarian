"""`librarian`: one entry point for the wiki, ingest, scrape, course, MCP and API commands.

Each verb is a thin dispatcher: it imports its module on demand and hands the remaining
arguments to that module's `main(argv)`, so `librarian wiki stats` and
`python -m librarian.wiki.telemetry stats` run the same code. Heavy dependencies (duckdb,
torch, fastapi) load only for the verbs that need them.

    librarian wiki stats|snapshot|check|gaps|log|ask   wiki health telemetry
    librarian wiki graph|rename|relink                 link graph, safe rename, link suggestions
    librarian wiki lint|verify|index-add               lint findings, orphan/index check and index insert for new pages
    librarian wiki sync-check|compact-signals|week     taxonomy drift, compaction evidence, weekly trend
    librarian ingest mark|status|pending                manifest: record compiled files, show pending
    librarian jobs run <name>|list                     unattended jobs through the Agent SDK
    librarian ingest triage|lint-raw                   gate a raw source, validate raw filenames
    librarian ingest notion|linear|pdf                 pull a source into data/raw/
    librarian scrape sessions|docs|repos|feeds|arxiv|bookmarks
    librarian courses import                           mirror learn-ai-engineering coursework into data/courses/
    librarian courses check chapters|curriculum|links|drills|quiz|manifest|crosswalk|smoke-labs
    librarian courses review findings|signals|score-eval
    librarian db upgrade|import-attempts|import-drill-log   user-state database (DATABASE_URL)
    librarian ops backup|restore|upgrade|schedule|list    encrypted backups, fenced restore, upgrade gate
    librarian eval compare --experiment NAME           per-variant answer metrics from telemetry and ratings
    librarian metrics product|check-release            product numbers; exit 1 if a release hurt grounding or ratings
    librarian pricing check                            print the price table; exit 1 when its review is over 35 days old
    librarian feedback export|prune                    reader feedback to data/raw/, retention
    librarian users add|list|invite|invites|promote|disable|enable  accounts and who may sign in
    librarian keys create|list|revoke                  API keys (lk_…), each printed once
    librarian index build [--out FILE]                 build the search index file the servers read
    librarian release build|pull|pin|unpin|list        content releases the API pulls and swaps in
    librarian mcp [--rebuild]                          the wiki MCP server (stdio)
    librarian api [--port N] [--workers N] [--reload]  the FastAPI backend (uvicorn)
    librarian present <brief> [--out DIR] [--dry-run] [--no-images] [--yes]   brief to deck via build_deck
"""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Verb:
    """`module:function` to call with the remaining args, plus args to put in front of them."""

    target: str
    prefix: tuple[str, ...] = ()
    help: str = ""


# group -> verb -> target. `wiki` verbs without an entry here go to telemetry, which owns
# stats/snapshot/check/gaps/log/ask.
_TELEMETRY = "librarian.wiki.telemetry:main"

GROUPS: dict[str, dict[str, Verb]] = {
    "wiki": {
        **{
            v: Verb(_TELEMETRY, (v,), h)
            for v, h in {
                "stats": "print wiki health numbers",
                "snapshot": "stats plus one dated row in data/telemetry/metrics.jsonl",
                "check": "private-leak check (exit 1 on a link into private/ or a tracked private file)",
                "gaps": "regenerate data/telemetry/gaps.md",
                "log": "append an operations log entry",
                "ask": "record an unanswered question",
            }.items()
        },
        "graph": Verb("librarian.wiki.graph:main", help="hubs, bridges and clusters"),
        "rename": Verb("librarian.wiki.rename:main", help="rename a page and rewrite links"),
        "relink": Verb("librarian.wiki.relinker:main", help="suggest semantic links"),
        "lint": Verb(
            "librarian.wiki.lint:main", help="dead links, frontmatter, orphans, stale (ranked)"
        ),
        "verify": Verb(
            "librarian.wiki.landing:main", ("verify",), "orphan and index check for new pages"
        ),
        "index-add": Verb("librarian.wiki.landing:main", ("index-add",), "add pages to _index.md"),
        "sync-check": Verb(
            "librarian.wiki.sync_check:main",
            help="taxonomy drift: directories vs code domain lists",
        ),
        "compact-signals": Verb(
            "librarian.wiki.compact_signals:main",
            help="age, size, links, retrievals for compaction",
        ),
        "week": Verb("librarian.wiki.week:main", help="trend, operations and conflicts this week"),
    },
    "ingest": {
        "triage": Verb("librarian.ingest.ingest_gate:main", ("triage",), "gate raw sources"),
        "mark": Verb(
            "librarian.ingest.manifest:main", ("mark",), "record compiled files in the manifest"
        ),
        "status": Verb(
            "librarian.ingest.manifest:main", ("status",), "manifest counts and pending files"
        ),
        "pending": Verb(
            "librarian.ingest.manifest:main", ("pending",), "new or changed files among paths/globs"
        ),
        "lint-raw": Verb("librarian.ingest.lint_raw:main", help="validate data/raw/ filenames"),
        "notion": Verb("librarian.ingest.ingest_notion:main", help="Notion page export"),
        "linear": Verb("librarian.ingest.ingest_linear:main", help="Linear issues"),
        "pdf": Verb("librarian.ingest.ingest_pdf:main", help="PDF text extraction"),
    },
    "scrape": {
        "sessions": Verb(
            "librarian.ingest.scrape_sessions:main", help="Claude Code/Codex sessions"
        ),
        "docs": Verb(
            "librarian.ingest.scrape_claude_docs:main", help=".claude/ docs of all projects"
        ),
        "repos": Verb("librarian.ingest.scrape_repos:main", help="repos in repos.txt"),
        "feeds": Verb("librarian.ingest.scrape_feeds:main", help="RSS/blog feeds"),
        "arxiv": Verb("librarian.ingest.scrape_arxiv:main", help="arXiv papers"),
        "bookmarks": Verb("librarian.ingest.scrape_bookmarks:main", help="saved web pages"),
        "extractions": Verb(
            "librarian.ingest.scrape_extractions:main", help="course reading extractions"
        ),
    },
    "index": {
        "build": Verb("librarian.retrieval.artifact:main", help="build a search index artifact"),
    },
    "release": {
        v: Verb("librarian.release.cli:main", (v,), h)
        for v, h in {
            "build": "package wiki, courses, slides and index into content-<sha>.tar.zst",
            "pull": "download the latest release, verify it and swap it in",
            "pin": "serve one release and stop following latest",
            "unpin": "follow latest again",
            "list": "the releases on disk and which one is current",
        }.items()
    },
    "jobs": {
        "run": Verb("librarian.jobs.runner:main", help="run a scheduled job headless"),
        "list": Verb("librarian.jobs.runner:main", ("list",), "list the jobs"),
    },
    "ops": {
        v: Verb("librarian.ops.cli:main", (v,), h)
        for v, h in {
            "backup": "dump, encrypt with age, upload (alerts the owner on failure)",
            "restore": "fenced restore into a new database, check it, swap",
            "upgrade": "backup gate before an image change",
            "schedule": "daily backup loop (the compose backup service)",
            "list": "the backups in the bucket",
        }.items()
    },
    "feedback": {
        "export": Verb(
            "librarian.ingest.feedback_export:main", help="anonymised data/raw/feedback/ source"
        ),
        "prune": Verb("librarian.feedback.cli:main", help="delete rows older than --days (180)"),
    },
    "db": {
        "upgrade": Verb("librarian.db.cli:main", ("upgrade",), "apply the database migrations"),
        "import-attempts": Verb(
            "librarian.courses.imports:main",
            ("import-attempts",),
            "copy var/attempts.sqlite3 into a user's history",
        ),
        "import-drill-log": Verb(
            "librarian.courses.imports:main",
            ("import-drill-log",),
            "import the sisyphus drill log into a user's history (local only)",
        ),
    },
    "eval": {
        "compare": Verb(
            "librarian.metrics.cli:main", ("eval", "compare"), "compare experiment variants"
        ),
    },
    "metrics": {
        "product": Verb("librarian.metrics.cli:main", ("metrics", "product"), "product metrics"),
        "check-release": Verb(
            "librarian.metrics.cli:main", ("metrics", "check-release"), "grounding/rating check"
        ),
    },
    "pricing": {
        "check": Verb(
            "librarian.pricing:main", ("check",), "price table and its last-reviewed date"
        ),
    },
    "users": {
        "add": Verb("librarian.accounts.cli:main", ("users", "add"), "create a user"),
        "list": Verb("librarian.accounts.cli:main", ("users", "list"), "list the users"),
        "invite": Verb("librarian.accounts.cli:main", ("users", "invite"), "let an email sign in"),
        "invites": Verb("librarian.accounts.cli:main", ("users", "invites"), "the invite list"),
        "promote": Verb(
            "librarian.accounts.cli:main", ("users", "promote"), "make a user an admin"
        ),
        "disable": Verb(
            "librarian.accounts.cli:main", ("users", "disable"), "lock a user out, end sessions"
        ),
        "enable": Verb("librarian.accounts.cli:main", ("users", "enable"), "undo a disable"),
    },
    "keys": {
        "create": Verb(
            "librarian.accounts.cli:main", ("keys", "create"), "new API key, shown once"
        ),
        "list": Verb("librarian.accounts.cli:main", ("keys", "list"), "list API keys"),
        "revoke": Verb("librarian.accounts.cli:main", ("keys", "revoke"), "revoke an API key"),
    },
    "courses": {
        "import": Verb(
            "librarian.courses.importer:main",
            help="mirror learn-ai-engineering coursework into data/courses/",
        ),
        "check": Verb("librarian.cli:_run_check", help="chapters|curriculum|links|drills|quiz|..."),
        "review": Verb("librarian.cli:_run_review", help="findings|signals|score-eval"),
    },
}

# `courses check <name>` and `courses review <name>`: a second level of the same thin dispatch.
_CHECKS: dict[str, str] = {
    "chapters": "librarian.courses.checks.check_chapters:main",
    "curriculum": "librarian.courses.checks.curriculum_map:main",
    "links": "librarian.courses.checks.link_check:main",
    "drills": "librarian.courses.checks.check_drills:main",
    "quiz": "librarian.courses.checks.check_quiz:main",
    "manifest": "librarian.courses.checks.check_manifest:main",
    "crosswalk": "librarian.courses.checks.crosswalk:main",
    "smoke-labs": "librarian.courses.checks.smoke_labs:main",
}
_REVIEWS: dict[str, str] = {
    "findings": "librarian.courses.review.findings:main",
    "signals": "librarian.courses.review.signals:main",
    "score-eval": "librarian.courses.review.score_eval:main",
}


def _resolve(target: str) -> Callable[[list[str]], Any]:
    module, _, func = target.partition(":")
    return getattr(importlib.import_module(module), func)


def _run_nested(group: str, table: dict[str, str], argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(f"usage: librarian courses {group} <{'|'.join(table)}> [args...]")
        return 0
    target = table.get(argv[0])
    if target is None:
        print(
            f"librarian courses {group}: unknown name {argv[0]!r} (one of: {', '.join(table)})",
            file=sys.stderr,
        )
        return 2
    result = _resolve(target)(argv[1:])
    return result if isinstance(result, int) else 0


def _run_check(argv: list[str]) -> int:
    return _run_nested("check", _CHECKS, argv)


def _run_review(argv: list[str]) -> int:
    return _run_nested("review", _REVIEWS, argv)


def _run_mcp(argv: list[str]) -> int:
    return int(_resolve("librarian.mcp.server:main")(argv) or 0)


def _run_present(argv: list[str]) -> int:
    return int(_resolve("librarian.tools.presenter.pipeline:main")(argv) or 0)


def _run_api(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="librarian api", description="FastAPI backend (uvicorn).")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reload", action="store_true", help="restart on code changes")
    ap.add_argument(
        "--workers",
        type=int,
        default=None,
        help="worker processes (default LIBRARIAN_API_WORKERS, else 1); not with --reload",
    )
    ap.add_argument(
        "--insecure",
        action="store_true",
        help="allow a non-loopback host with no login and no LIBRARIAN_API_TOKEN",
    )
    ap.add_argument(
        "--check", action="store_true", help="validate the configuration and exit (1 on errors)"
    )
    args = ap.parse_args(argv)
    import uvicorn

    from librarian.api.startup import find_problems, is_loopback
    from librarian.config import get_settings
    from librarian.log_config import configure_logging, get_logger

    settings = get_settings()
    workers = settings.api_workers if args.workers is None else args.workers
    if workers < 1 or (args.reload and workers > 1):
        print("librarian api: --workers must be 1 or more, and 1 with --reload", file=sys.stderr)
        return 2
    errors, warnings = find_problems(settings, host=args.host, insecure=args.insecure)
    for line in warnings:
        print(f"librarian api: warning: {line}", file=sys.stderr)
    for line in errors:
        print(f"librarian api: error: {line}", file=sys.stderr)
    if errors:
        return 1
    if args.check:
        return 0
    if settings.open_mode and not is_loopback(args.host):
        configure_logging()
        get_logger(__name__).warning("api.auth.open", host=args.host, hint="--insecure")
    # /metrics across workers: the client's file directory must exist before they import it.
    from librarian.api.prom_env import prepare as prepare_metrics

    prepare_metrics(settings, workers)
    # The app logs one structured line per request; uvicorn's access log would repeat it
    # with the query string.
    uvicorn.run(
        "librarian.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=workers,
        access_log=False,
        proxy_headers=True,
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )
    return 0


def _usage() -> str:
    lines = ["usage: librarian <group> <verb> [args...]", ""]
    for group, verbs in GROUPS.items():
        lines.append(f"  {group}: " + ", ".join(verbs))
    lines += [
        "  mcp [--rebuild]",
        "  present <brief> [--out DIR] [--dry-run] [--no-images] [--yes]",
        "  api [--host H] [--port N] [--workers N] [--reload] [--insecure] [--check]",
        "",
        "Run a verb with --help for its options.",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(_usage())
        return 0
    group, rest = args[0], args[1:]
    if group == "mcp":
        return _run_mcp(rest)
    if group == "api":
        return _run_api(rest)
    if group == "present":
        return _run_present(rest)
    verbs = GROUPS.get(group)
    if verbs is None:
        print(f"librarian: unknown command {group!r}\n\n{_usage()}", file=sys.stderr)
        return 2
    if not rest or rest[0] in ("-h", "--help"):
        print(f"usage: librarian {group} <verb> [args...]\n")
        for name, verb in verbs.items():
            print(f"  {name:<10} {verb.help}")
        return 0
    verb = verbs.get(rest[0])
    if verb is None:
        print(
            f"librarian {group}: unknown verb {rest[0]!r} (one of: {', '.join(verbs)})",
            file=sys.stderr,
        )
        return 2
    result = _resolve(verb.target)([*verb.prefix, *rest[1:]])
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
