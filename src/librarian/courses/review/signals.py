"""Collect what learners and reviewers show about the coursework into one list to look at.

    librarian courses review signals             # print
    librarian courses review signals --write     # also write logs/signals/<date>.md (gitignored)

Reads, and never changes:
- the owner's attempts in the user-state database (it imports the old logs/flashcards.jsonl): self-graded cards
- logs/retrieval.jsonl: real wiki searches that found nothing. Eval and sweep rows are ignored
- sisyphus's drills/coding/drill-log.md ($SISYPHUS_DIR): the Date, QID, Aid and Score columns, never the Note
- logs/review/findings.jsonl: open decisions and recurring faults

The output proposes what to re-read. With one learner a missed card can mean a topic not learned yet rather than a bad
card, so nothing here is evidence that content is wrong. The output holds personal history, so it goes to the
gitignored logs/ tree. Private courses are not searched for drill or deck matches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from librarian import accounts
from librarian.config import get_settings
from librarian.courses import attempts as attempt_store
from librarian.courses.checks.common import is_private, public_files
from librarian.courses.drill_log import parse as parse_drill_log
from librarian.courses.review import findings as fl
from librarian.db import get_engine

SOURCE_PREFIX = "learn-ai-engineering/"
MIN_CARD_ATTEMPTS = 3  # Fewer than this says nothing about one card
MISS_RATE = 0.5
STRUGGLE_AID = 2  # Hint rung from which a drill counts as needing help


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def deck_location(root: Path, source: str, deck: str, front: str) -> str:
    """`<pillar>/slides/deck.yaml:<line>` for the slide this card came from, or "" if it can't be found."""
    note = source.removeprefix(SOURCE_PREFIX)
    pillar = note.split("/notes/")[0] if "/notes/" in note else deck
    path = root / pillar / "slides" / "deck.yaml"
    if is_private(path, root) or not path.exists():
        return ""
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"\s*(- )?(title|recall):", line) and front in line:
            return f"{pillar}/slides/deck.yaml:{n}"
    return ""


def flashcard_section(rows: list[dict], root: Path) -> list[str]:
    cards: dict[tuple[str, str], Counter] = defaultdict(Counter)
    source: dict[tuple[str, str], str] = {}
    for row in rows:
        key = (row.get("deck", ""), row.get("front", ""))
        cards[key][row.get("result", "")] += 1
        source[key] = row.get("source", "")
    flagged = []
    for key, counts in cards.items():
        total = counts["knew"] + counts["missed"]
        if total >= MIN_CARD_ATTEMPTS and counts["missed"] / total >= MISS_RATE:
            flagged.append((counts["missed"] / total, total, key))
    lines = [
        f"{len(rows)} grades on {len(cards)} cards. Flagged at {MIN_CARD_ATTEMPTS}+ attempts and {MISS_RATE:.0%}+ missed."
    ]
    for rate, total, (deck, front) in sorted(flagged, key=lambda f: (-f[0], -f[1])):
        where = (
            deck_location(root, source[(deck, front)], deck, front) or source[(deck, front)] or deck
        )
        lines.append(f'- {rate:.0%} missed of {total}: "{front}" ({where})')
    return lines


def drill_files(root: Path) -> dict[str, str]:
    return {
        Path(p).stem: p
        for p in public_files(root, "programming/drills")
        if p.endswith((".md", ".py"))
    }


def drill_section(rows: list[dict], files: dict[str, str]) -> list[str]:
    by_qid: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_qid[row["qid"]].append(row)
    flagged = []
    for qid, attempts in by_qid.items():
        last = attempts[-1]
        misses, marks = (
            last["score"].count("✗"),
            last["score"].count("✓") + last["score"].count("✗"),
        )
        aid = int(last["aid"]) if last["aid"].isdigit() else 0
        if aid >= STRUGGLE_AID or (marks and misses / marks >= MISS_RATE):
            flagged.append((misses, aid, qid, len(attempts), last["score"]))
    matched = sum(1 for q in by_qid if q in files)
    lines = [
        f"{len(rows)} attempts on {len(by_qid)} drills; {matched} match a drill file here by slug. "
        f"Flagged on the latest attempt at hint rung {STRUGGLE_AID}+ or half the marks missed."
    ]
    for _, aid, qid, n, score in sorted(flagged, reverse=True):
        lines.append(
            f"- {qid}: {n} attempt(s), hint rung {aid}, {score} ({files.get(qid, 'no drill file here')})"
        )
    return lines


def search_section(rows: list[dict]) -> list[str]:
    real = [r for r in rows if r.get("tool") == "search_wiki" and r.get("query")]
    empty = Counter(r["query"] for r in real if not r.get("n_results"))
    lines = [
        f"{len(real)} real wiki searches, {sum(empty.values())} found nothing. {len(rows) - len(real)} other rows ignored."
    ]
    lines += [f'- {n}x "{q}"' for q, n in empty.most_common(15)]
    return lines


def build(
    root: Path, flashcards: list[dict], retrieval: Path, drill_log: Path, findings_log: Path
) -> str:
    drills = parse_drill_log(drill_log.read_text(encoding="utf-8")) if drill_log.exists() else []
    parts = [
        f"# Coursework signals, {date.today().isoformat()}",
        "",
        "Proposals to re-read, not evidence that content is wrong. One learner can miss a card simply by not "
        "having learned the topic yet.",
        "",
        "## Flashcards",
        *flashcard_section(flashcards, root),
        "",
        "## Drills",
        *drill_section(drills, drill_files(root)),
        "",
        "## Wiki searches",
        *search_section(read_jsonl(retrieval)),
        "",
        "## Reviewers",
        *fl.report_lines(fl.read_rows(findings_log)),
        "",
    ]
    return "\n".join(parts)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses review signals",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    cfg = get_settings()
    owner = accounts.ensure_owner(get_engine(), cfg.owner_email)
    text = build(
        cfg.courses_dir,
        attempt_store.flashcard_rows(owner.id),
        cfg.retrieval_log,
        cfg.drill_log,
        cfg.review_findings_log,
    )
    print(text)
    if args.write:
        out = cfg.signals_dir / f"{date.today().isoformat()}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
