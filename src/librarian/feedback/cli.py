"""`librarian feedback prune [--days N]`: delete feedback rows older than the retention window."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from librarian.config import get_settings
from librarian.db import get_engine
from librarian.feedback.store import prune
from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian feedback prune", description=__doc__)
    ap.add_argument(
        "--days", type=int, default=None, help="default LIBRARIAN_FEEDBACK_RETENTION_DAYS (180)"
    )
    args = ap.parse_args(list(argv) if argv is not None else None)
    days = args.days if args.days is not None else get_settings().feedback_retention_days
    if days < 1:
        ap.error("--days must be 1 or more")
    configure_logging()
    print(f"pruned {prune(get_engine(), days)} feedback rows older than {days} days")
    return 0
