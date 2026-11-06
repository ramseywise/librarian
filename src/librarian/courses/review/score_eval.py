"""Score a reviewer's reports against the faults planted in its fixtures.

    librarian courses review score-eval drill-reviewer --cases cases.json --reports DIR [--record]

Reads <reports>/<case id>.txt for each case of that reviewer in the cases file (a JSON list of
{id, reviewer, planted: [{id, any: [...]}]}; the default is `logs/review/evals/cases.json`, gitignored,
since the fixtures are not part of this repo). A planted fault counts as caught when a
single finding mentions one of its `any` phrases, case-insensitively. A case with no planted faults is a clean control,
and every finding on it is a possible false positive to read by hand. Keyword matching only sorts reports for a person to
read; it doesn't judge whether a finding is right. --record appends the score to `logs/review/evals/results.jsonl`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from librarian.config import get_settings


def evals_dir() -> Path:
    return get_settings().review_dir / "evals"


def split_findings(report: str) -> list[str]:
    """The report's findings, one string each. Everything before the FINDINGS heading is ignored."""
    match = re.search(r"^FINDINGS\b.*$", report, re.M)
    if not match:
        return []
    return [
        f for f in re.split(r"^\s*- (?=\w+:)", report[match.end() :], flags=re.M)[1:] if f.strip()
    ]


def score_case(case: dict, report: str) -> dict:
    findings = split_findings(report)
    caught, missed = [], []
    for fault in case["planted"]:
        phrases = [p.lower() for p in fault["any"]]
        hit = any(any(p in f.lower() for p in phrases) for f in findings)
        (caught if hit else missed).append(fault["id"])
    return {"case": case["id"], "findings": len(findings), "caught": caught, "missed": missed}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses review score-eval",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("reviewer")
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument(
        "--cases",
        type=Path,
        default=None,
        help="cases.json (default: logs/review/evals/cases.json)",
    )
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args(argv)
    cases_file = args.cases or evals_dir() / "cases.json"
    if not cases_file.is_file():
        print(f"no cases file: {cases_file}", file=sys.stderr)
        return 1
    cases = [
        c
        for c in json.loads(cases_file.read_text(encoding="utf-8"))
        if c["reviewer"] == args.reviewer
    ]
    if not cases:
        print(f"no cases for {args.reviewer}", file=sys.stderr)
        return 1
    results = []
    for case in cases:
        path = args.reports / f"{case['id']}.txt"
        if not path.exists():
            print(f"missing report: {path}", file=sys.stderr)
            return 1
        result = score_case(case, path.read_text(encoding="utf-8"))
        results.append(result)
        print(
            f"{case['id']}: caught {len(result['caught'])} of {len(case['planted'])}, {result['findings']} findings"
            + (f", missed {', '.join(result['missed'])}" if result["missed"] else "")
        )
    planted = sum(len(c["planted"]) for c in cases)
    caught = sum(len(r["caught"]) for r in results)
    control = sum(r["findings"] for c, r in zip(cases, results, strict=True) if not c["planted"])
    print(f"{args.reviewer}: recall {caught}/{planted}, {control} findings on clean controls")
    if args.record:
        row = {
            "ts": date.today().isoformat(),
            "reviewer": args.reviewer,
            "caught": caught,
            "planted": planted,
            "control_findings": control,
            "missed": [m for r in results for m in r["missed"]],
        }
        out = evals_dir() / "results.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
