"""CLI entry point for the codemap indexer.

Usage:
    uv run codemap                    # reindex all configured repos
    uv run codemap --repo librarian   # reindex just one repo
    uv run codemap --dry-run          # report what would be (re)parsed, no writes
"""

from __future__ import annotations

import argparse
import sys

from app.log_config import configure_logging
from tools.codemap.indexer import run


def main() -> None:
    configure_logging()
    p = argparse.ArgumentParser(description="Reindex configured repos into .code_index.duckdb")
    p.add_argument("--repo", default=None, help="Only reindex this repo_id")
    p.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = p.parse_args()

    totals = run(only_repo=args.repo, dry_run=args.dry_run)

    if not totals:
        print("No repos configured — add one to tools/codemap/repos.txt", file=sys.stderr)
        sys.exit(1)

    for repo_id, counts in totals.items():
        print(
            f"{repo_id}: parsed={counts['parsed']} skipped={counts['skipped']} "
            f"removed={counts['removed']} errors={counts['errors']}"
        )


if __name__ == "__main__":
    main()
