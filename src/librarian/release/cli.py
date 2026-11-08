"""`librarian release build|pull|pin|unpin|list`."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from librarian.log_config import configure_logging


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian release", description="Content releases.")
    verbs = ap.add_subparsers(dest="verb", required=True)
    build = verbs.add_parser("build", help="package data/ as a release (CI runs this)")
    build.add_argument("--out", type=Path, default=Path("dist/release"))
    build.add_argument("--name", help="default: content-<git sha>")
    build.add_argument("--slides", type=Path, help="a directory of built decks to include")
    build.add_argument("--no-index", action="store_true", help="skip the search index")
    pull = verbs.add_parser("pull", help="install the pinned release, else the latest one")
    pull.add_argument("--url", help="default: LIBRARIAN_RELEASE_URL")
    pin = verbs.add_parser(
        "pin", help="serve a release (a name or git sha) and stop following latest"
    )
    pin.add_argument("ref")
    pin.add_argument("--url", help="default: LIBRARIAN_RELEASE_URL")
    verbs.add_parser("unpin", help="follow latest again from the next pull")
    verbs.add_parser("list", help="releases on disk")

    args = ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    from librarian import release

    try:
        if args.verb == "build":
            from librarian.release.package import build as build_release

            built = build_release(
                args.out, name=args.name, slides_dir=args.slides, build_index=not args.no_index
            )
            print(f"{built.archive}\n{built.checksum}")
        elif args.verb == "pull":
            print(json.dumps(release.pull(args.url).as_dict()))
        elif args.verb == "pin":
            print(json.dumps(release.pin(args.ref, args.url).as_dict()))
        elif args.verb == "unpin":
            release.unpin()
            print("unpinned: the next pull installs latest")
        else:
            for r in release.list_releases():
                flags = "".join(["*" if r["current"] else " ", "P" if r["pinned"] else " "])
                print(f"{flags} {r['name']}  {r.get('created_at') or '-'}")
    except (release.ReleaseError, ValueError, RuntimeError) as e:
        print(f"error: {e}")
        return 1
    return 0
