"""`librarian db upgrade|check`. The import verbs are `librarian.courses.imports`: they need accounts."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from sqlalchemy.exc import SQLAlchemyError

from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian db", description="User-state database.")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("upgrade", help="apply every pending migration (idempotent)")
    sub.add_parser(
        "check", help="read-only: exit 1 if a migration is pending or the revision is unknown"
    )
    args = ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    if args.verb == "check":
        return _check()

    from librarian.db.engine import get_engine
    from librarian.db.migrate import upgrade

    engine = get_engine()
    upgrade(engine)
    print(f"database up to date ({engine.url.render_as_string(hide_password=True)})")
    return 0


def _check() -> int:
    """0 when the database is at this build's head; 1 (and why, on stderr) when it is not."""
    from librarian.db.engine import open_engine
    from librarian.db.migrate import MigrationStateError, pending

    try:
        engine = open_engine()
    except OSError as e:  # SQLite's directory cannot be created or reached
        print(f"librarian db check: cannot read the database ({type(e).__name__})", file=sys.stderr)
        return 1
    try:
        todo = pending(engine)
    except MigrationStateError as e:
        print(f"librarian db check: {e}", file=sys.stderr)
        return 1
    except SQLAlchemyError as e:
        print(f"librarian db check: cannot read the database ({type(e).__name__})", file=sys.stderr)
        return 1
    finally:
        engine.dispose()
    if todo:
        print(f"librarian db check: {len(todo)} pending: {', '.join(todo)}", file=sys.stderr)
        return 1
    print("database is at head: nothing pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
