"""`librarian db import-attempts|import-drill-log`: copy old study history into one user's attempts.

Both are run by the owner on their own machine, once or after the source grows; re-running adds
nothing already there. `--user EMAIL` names whose history it becomes (default the owner,
`LIBRARIAN_OWNER_EMAIL`). The sources are only read.

    librarian db import-attempts [--from var/attempts.sqlite3] [--user EMAIL]
    librarian db import-drill-log [--from $SISYPHUS_DIR/drills/coding/drill-log.md] [--user EMAIL]
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from librarian import accounts
from librarian.config import get_settings
from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian db", description="Import old study history.")
    sub = ap.add_subparsers(dest="verb", required=True)
    for verb, help_text, default in (
        ("import-attempts", "copy the old attempts SQLite file in", "var/attempts.sqlite3"),
        ("import-drill-log", "import the sisyphus drill log", "$SISYPHUS_DIR/.../drill-log.md"),
    ):
        p = sub.add_parser(verb, help=help_text)
        p.add_argument("--from", dest="source", type=Path, help=f"default: {default}")
        p.add_argument("--user", metavar="EMAIL", help="whose history (default: the owner)")
    args = ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    from librarian.courses import drill_log
    from librarian.db.attempt_rows import import_sqlite_attempts
    from librarian.db.engine import get_engine
    from librarian.db.migrate import upgrade

    settings = get_settings()
    engine = get_engine()
    upgrade(engine)
    if args.user:
        user = accounts.get_user(engine, args.user)
        if user is None:
            print(f"librarian db: no user {args.user!r} (librarian users add)", file=sys.stderr)
            return 1
    else:
        user = accounts.ensure_owner(engine, settings.owner_email)

    if args.verb == "import-attempts":
        source: Path = args.source or settings.attempts_db
    else:
        source = args.source or settings.drill_log
    if not source.exists():
        print(f"librarian db: no such file: {source}", file=sys.stderr)
        return 1
    if args.verb == "import-attempts":
        if source.resolve() == Path(engine.url.database or "").resolve():
            print(f"librarian db: {source} is the target database itself", file=sys.stderr)
            return 1
        read, added, skipped = import_sqlite_attempts(source, user_id=user.id, engine=engine)
        why = "unreadable timestamp"
    else:
        read, added, skipped = drill_log.import_log(source, user.id, engine)
        why = "no QID or date"
    print(
        f"{source} -> {user.email}: {read} rows read, {added} added, "
        f"{read - added - skipped} already there, {skipped} skipped ({why}); the file is untouched"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
