"""`librarian`: one entry point for the wiki, ingest, scrape, course, MCP and API commands.

Each verb is a thin dispatcher: it imports its module on demand and hands the remaining
arguments to that module's `main(argv)`, so `librarian wiki stats` and
`python -m librarian.wiki.telemetry stats` run the same code. Heavy dependencies (duckdb,
torch, fastapi) load only for the verbs that need them.

    librarian wiki stats|snapshot|check|gaps|log|ask   wiki health telemetry
    librarian wiki graph|rename|relink                 link graph, safe rename, link suggestions
    librarian ingest triage|lint-raw                   gate a raw source, validate raw filenames
    librarian ingest notion|linear|pdf                 pull a source into data/raw/
    librarian scrape sessions|docs|repos|feeds|arxiv|bookmarks
    librarian courses check chapters|curriculum|links|drills|manifest|crosswalk|smoke-labs
    librarian courses review findings|signals|score-eval
    librarian mcp [--rebuild]                          the wiki MCP server (stdio)
    librarian api [--port N] [--reload]                the FastAPI backend (uvicorn)
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
    },
    "ingest": {
        "triage": Verb("librarian.ingest.ingest_gate:main", ("triage",), "gate raw sources"),
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
    },
    "courses": {
        "check": Verb("librarian.cli:_run_check", help="chapters|curriculum|links|drills|..."),
        "review": Verb("librarian.cli:_run_review", help="findings|signals|score-eval"),
    },
}

# `courses check <name>` and `courses review <name>`: a second level of the same thin dispatch.
_CHECKS: dict[str, str] = {
    "chapters": "librarian.courses.checks.check_chapters:main",
    "curriculum": "librarian.courses.checks.curriculum_map:main",
    "links": "librarian.courses.checks.link_check:main",
    "drills": "librarian.courses.checks.check_drills:main",
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
    return int(_resolve("apps.mcp.server:main")(argv) or 0)


def _is_loopback(host: str) -> bool:
    return host in {"localhost", "::1"} or host.startswith("127.")


def _run_api(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="librarian api", description="FastAPI backend (uvicorn).")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reload", action="store_true", help="restart on code changes")
    args = ap.parse_args(argv)
    import uvicorn

    from librarian.config import get_settings
    from librarian.log_config import configure_logging, get_logger

    if not get_settings().api_token and not _is_loopback(args.host):
        configure_logging()
        get_logger(__name__).warning(
            "api.auth.open", host=args.host, hint="set LIBRARIAN_API_TOKEN"
        )
    # The app logs one structured line per request; uvicorn's access log would repeat it
    # with the query string.
    uvicorn.run(
        "apps.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        access_log=False,
    )
    return 0


def _usage() -> str:
    lines = ["usage: librarian <group> <verb> [args...]", ""]
    for group, verbs in GROUPS.items():
        lines.append(f"  {group}: " + ", ".join(verbs))
    lines += [
        "  mcp [--rebuild]",
        "  api [--host H] [--port N] [--reload]",
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
