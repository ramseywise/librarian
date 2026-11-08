"""`librarian db upgrade`. The import verbs are `librarian.courses.imports`: they need accounts."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian db", description="User-state database.")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("upgrade", help="apply every pending migration (idempotent)")
    ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    from librarian.db.engine import get_engine
    from librarian.db.migrate import upgrade

    engine = get_engine()
    upgrade(engine)
    print(f"database up to date ({engine.url.render_as_string(hide_password=True)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
