"""`librarian wiki week`: the file-reading half of `/wiki-weekly`, as one read-only report.

The window is the seven days ending today. It gives the trend (current numbers against the
latest `metrics.jsonl` row, and whether a new snapshot is due), the operations logged in the
window, and the open conflicts, with a check that their count agrees with `wiki stats`.
Writes nothing: `wiki snapshot` and `wiki log weekly` stay separate verbs the skill runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from librarian.config import get_settings
from librarian.wiki.lint import open_conflicts
from librarian.wiki.oplog import (
    METRICS_FILE,
    OPERATIONS_FILE,
    _read_tracked_jsonl,  # pyright: ignore[reportPrivateUsage]
)
from librarian.wiki.stats import compute_stats

WIKI_DIR = get_settings().wiki_dir
TELEMETRY_DIR = get_settings().telemetry_dir
WINDOW_DAYS = 7
MAX_OPERATIONS = 10


def _day(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def report(wiki_dir: Path, telemetry_dir: Path, today: date) -> dict[str, Any]:
    stats = compute_stats(wiki_dir, today)
    rows = [r for r in _read_tracked_jsonl(telemetry_dir / METRICS_FILE) if _day(r.get("date"))]
    latest = rows[-1] if rows else None
    latest_day = _day(latest["date"]) if latest else None
    start = today - timedelta(days=WINDOW_DAYS)
    trend: dict[str, Any] = {}
    if latest is not None:
        for name, now in stats["metrics"].items():
            before = (latest.get("metrics") or {}).get(name, {})
            trend[name] = {
                "before": before.get("value"),
                "after": now["value"],
                "status": now["status"],
                "changed": before.get("value") != now["value"],
            }
    ops = [
        r
        for r in _read_tracked_jsonl(telemetry_dir / OPERATIONS_FILE)
        if "month" not in r and (d := _day(r.get("date"))) and start <= d <= today
    ]
    ops.sort(key=lambda r: str(r["date"]), reverse=True)
    titles = open_conflicts(wiki_dir)
    return {
        "window": {"start": start.isoformat(), "end": today.isoformat()},
        "latest_row": latest_day.isoformat() if latest_day else None,
        "snapshot_needed": latest_day is None or (today - latest_day).days >= WINDOW_DAYS,
        "trend": trend,
        "added": ops[:MAX_OPERATIONS],
        "added_more": max(len(ops) - MAX_OPERATIONS, 0),
        "open_conflicts": titles,
        "open_conflicts_match_stats": len(titles) == stats["open_conflicts"],
        "stats_open_conflicts": stats["open_conflicts"],
    }


def _render(r: dict[str, Any]) -> str:
    out = [f"Wiki week: {r['window']['start']} to {r['window']['end']}"]
    out.append(
        f"Latest metrics row: {r['latest_row'] or 'none'}"
        f" (snapshot {'needed' if r['snapshot_needed'] else 'not needed'})"
    )
    if not r["trend"]:
        out.append("Trend: first row")
    for name, t in r["trend"].items():
        mark = "changed" if t["changed"] else "no change"
        out.append(f"  {name}: {t['before']} -> {t['after']} ({t['status']}, {mark})")
    out.append("Added:" if r["added"] else "Added: nothing logged this week")
    out += [f"  {o['date']} {o['op']} {o['detail']}" for o in r["added"]]
    if r["added_more"]:
        out.append(f"  ... and {r['added_more']} more")
    out.append(f"Open conflicts: {len(r['open_conflicts'])}")
    out += [f"  {t}" for t in r["open_conflicts"]]
    if not r["open_conflicts_match_stats"]:
        out.append(f"  MISMATCH: wiki stats counts {r['stats_open_conflicts']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--telemetry-dir", type=Path, default=TELEMETRY_DIR)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--today", type=date.fromisoformat, default=None, help="for tests")
    args = parser.parse_args(argv)
    if not args.wiki_dir.is_dir():
        print(f"week: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    data = report(args.wiki_dir, args.telemetry_dir, args.today or date.today())
    print(json.dumps(data, indent=2) if args.json else _render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
