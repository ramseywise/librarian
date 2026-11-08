"""`librarian wiki compact-signals`: the mechanical evidence phase of `/compact-wiki`.

Per public page: age, line count, inbound links and retrievals in a window, from
`logs/retrieval.jsonl`. Lists stale pages, pages over 300 lines, retire candidates (stale, at
most one inbound link, never retrieved in the window) and page pairs retrieved together in at
least three result sets. Read-only; private pages are never read into the output. Similarity
(`_relink_suggestions.md`) and the merge/retire decision stay with the skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Any

from librarian.config import get_settings
from librarian.wiki.oplog import _read_loose_jsonl  # pyright: ignore[reportPrivateUsage]
from librarian.wiki.pages import (
    _link_index,  # pyright: ignore[reportPrivateUsage]
    _public_pages,  # pyright: ignore[reportPrivateUsage]
)
from librarian.wiki.stats import (
    STALE_DAYS,
    _link_edges,  # pyright: ignore[reportPrivateUsage]
)

WIKI_DIR = get_settings().wiki_dir
RETRIEVAL_LOG = get_settings().retrieval_log
LARGE_LINES = 300
CO_RETRIEVAL_MIN = 3
RETIRE_MAX_INBOUND = 1
RETRIEVAL_TOOLS = {"search_wiki", "get_domain_briefing", "read_page"}


def _rel(path: str, known: set[str]) -> str | None:
    """A logged path as a wiki-relative page path, or None (outside the wiki, or private)."""
    norm = path.replace("\\", "/")
    if "/wiki/" in norm:
        norm = norm.split("/wiki/", 1)[1]
    return norm if norm in known else None


def _in_window(row: dict[str, Any], since: datetime) -> bool:
    try:
        ts = datetime.fromisoformat(str(row.get("ts", "")))
    except ValueError:
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts >= since


def compute(wiki_dir: Path, retrieval_log: Path, today: date, days: int = 30) -> dict[str, Any]:
    public = _public_pages(wiki_dir)
    scored = [p for p in public if p.scored]
    _, inbound = _link_edges(scored, _link_index(public))
    known = {p.rel for p in scored}
    since = datetime.combine(today, datetime.min.time(), tzinfo=UTC) - timedelta(days=days)
    rows = [r for r in _read_loose_jsonl(retrieval_log) if _in_window(r, since)]
    rows = [r for r in rows if r.get("tool") in RETRIEVAL_TOOLS]

    hits: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    for row in rows:
        raw = row.get("top_paths") or ([row["path"]] if row.get("path") else [])
        found = sorted({r for r in (_rel(str(p), known) for p in raw) if r})
        hits.update(found)
        pairs.update(combinations(found, 2))

    stale: list[dict[str, Any]] = []
    large: list[dict[str, Any]] = []
    retire: list[dict[str, Any]] = []
    for page in scored:
        age = (today - page.updated).days if page.updated else None
        lines = len(page.path.read_text(errors="replace").splitlines())
        info = {
            "page": page.rel,
            "age_days": age,
            "lines": lines,
            "inbound": len(inbound[page.rel]),
        }
        if age is not None and age > STALE_DAYS:
            stale.append({**info, "retrievals": hits[page.rel]})
            if len(inbound[page.rel]) <= RETIRE_MAX_INBOUND and not hits[page.rel]:
                retire.append(info)
        if lines > LARGE_LINES:
            large.append(info)
    stale.sort(key=lambda r: -(r["age_days"] or 0))
    large.sort(key=lambda r: -r["lines"])
    retire.sort(key=lambda r: -(r["age_days"] or 0))
    return {
        "pages": len(scored),
        "window_days": days,
        "retrieval_rows": len(rows),
        "stale": stale,
        "large": large,
        "retire_candidates": retire,
        "retrieved": [{"page": p, "count": n} for p, n in hits.most_common(20)],
        "co_retrieved": [
            {"pages": list(pair), "count": n}
            for pair, n in pairs.most_common()
            if n >= CO_RETRIEVAL_MIN
        ][:30],
    }


def _render(report: dict[str, Any]) -> str:
    out = [
        f"pages {report['pages']}; retrieval rows in the last {report['window_days']} days: "
        f"{report['retrieval_rows']}"
    ]
    if not report["retrieval_rows"]:
        out.append("no retrieval telemetry in the window: age, size and similarity only")
    for title, key in (
        (f"Stale (> {STALE_DAYS} days)", "stale"),
        (f"Over {LARGE_LINES} lines", "large"),
        ("Retire candidates (stale, <=1 inbound, 0 retrievals)", "retire_candidates"),
    ):
        out.append(f"\n{title}: {len(report[key])}")
        out += [
            f"  {r['page']}  age {r['age_days']}d  {r['lines']} lines  {r['inbound']} inbound"
            for r in report[key][:40]
        ]
    out.append(f"\nCo-retrieved >= {CO_RETRIEVAL_MIN}x: {len(report['co_retrieved'])}")
    out += [f"  {r['count']}x  {r['pages'][0]}  +  {r['pages'][1]}" for r in report["co_retrieved"]]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--retrieval-log", type=Path, default=RETRIEVAL_LOG)
    parser.add_argument("--days", type=int, default=30, help="retrieval window (default 30)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--today", type=date.fromisoformat, default=None, help="for tests")
    args = parser.parse_args(argv)
    if not args.wiki_dir.is_dir():
        print(f"compact-signals: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    report = compute(args.wiki_dir, args.retrieval_log, args.today or date.today(), args.days)
    print(json.dumps(report, indent=2) if args.json else _render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
