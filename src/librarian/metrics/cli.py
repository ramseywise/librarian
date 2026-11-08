"""`librarian eval compare` and `librarian metrics product|check-release`."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from librarian.db.engine import get_engine
from librarian.metrics import reports
from librarian.metrics.data import since_from_date


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian")
    sub = parser.add_subparsers(dest="group", required=True)

    ev = sub.add_parser("eval", help="compare experiment variants").add_subparsers(
        dest="verb", required=True
    )
    c = ev.add_parser("compare", help="per-variant grounding, rating, latency, pages, cost")
    c.add_argument("--experiment", required=True, help="experiment name, e.g. ranking")
    c.add_argument("--since", help="YYYY-MM-DD")
    c.add_argument("--json", action="store_true")

    mt = sub.add_parser("metrics", help="product metrics").add_subparsers(
        dest="verb", required=True
    )
    p = mt.add_parser("product", help="answers, grounding, ratings, spend, study counts")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--by", choices=["release", "experiment"], default="release")
    p.add_argument("--json", action="store_true")
    k = mt.add_parser("check-release", help="exit 1 if grounding or ratings fell after a release")
    k.add_argument("--days", type=int, default=30)
    k.add_argument("--current", help="release id (default: the one answering most recently)")
    k.add_argument("--previous", help="release id (default: the one before it)")

    args = parser.parse_args(list(argv) if argv is not None else sys.argv[1:])
    engine = get_engine()

    if args.group == "eval":
        cmp = reports.compare(args.experiment, engine=engine, since=since_from_date(args.since))
        print(json.dumps(cmp.to_json(), indent=2) if args.json else cmp.render())
        return 0
    if args.verb == "product":
        rep = reports.product(engine=engine, days=args.days, by=args.by)
        print(json.dumps(rep.to_json(), indent=2) if args.json else rep.render())
        return 0
    check = reports.check_release(
        engine=engine, days=args.days, current=args.current, previous=args.previous
    )
    print(check.render())
    return 0 if check.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
