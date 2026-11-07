"""`librarian db upgrade|import-attempts`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from librarian.config import get_settings
from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian db", description="User-state database.")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("upgrade", help="apply every pending migration (idempotent)")
    imp = sub.add_parser(
        "import-attempts", help="copy the old attempts SQLite file into the database, once"
    )
    imp.add_argument("--from", dest="source", type=Path, help="default: var/attempts.sqlite3")
    args = ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    from librarian.db.attempt_rows import import_sqlite_attempts
    from librarian.db.engine import get_engine
    from librarian.db.migrate import upgrade

    engine = get_engine()
    upgrade(engine)
    if args.verb == "upgrade":
        print(f"database up to date ({engine.url.render_as_string(hide_password=True)})")
        return 0
    source: Path = args.source or get_settings().attempts_db
    if not source.exists():
        print(f"librarian db: no such file: {source}", file=sys.stderr)
        return 1
    if source.resolve() == Path(engine.url.database or "").resolve():
        print(f"librarian db: {source} is the target database itself", file=sys.stderr)
        return 1
    read, added, skipped = import_sqlite_attempts(source, engine)
    print(
        f"{source}: {read} rows read, {added} added, {read - added - skipped} already there, "
        f"{skipped} skipped (unreadable timestamp); the file is untouched"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
