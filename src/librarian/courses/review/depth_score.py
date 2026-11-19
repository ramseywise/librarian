"""Score proposed section depths against hand-tagged notes.

    librarian courses review depth-score --gold GOLD.yaml --predictions RUN.jsonl [--json]

The gold file is YAML with `notes: [{path, depth, depth_sections}]`; a predictions file is what
`depth-classify` writes, one JSON object per note. Both are in the stored form, where `depth` is
only the default for the sections not listed, so the unit that is scored is the content heading:
its own entry, else its parent's, else the default. A note has no depth to score, and a tier is
not this tool's.

- Accuracy, precision and recall per depth, and macro F1 over the depths that occur.
- Exact match: the share of notes with every content heading right.
- Headings the rubric leaves out (Pitfalls, Try it, ...) are not counted, nor are their subsections.

Each number is shown beside the same number for a classifier that answers `core` for every
heading, since most headings are `core`. Scores nothing it was not given: a gold note with no
prediction is reported and left out.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import yaml

from librarian.config import get_settings
from librarian.courses import depth
from librarian.courses.checks.common import FENCE, split_front

BASELINE = "core"

Pair = tuple[str, str]  # (gold, predicted)


def headings_of(text: str) -> list[depth.Heading]:
    """A note's headings below the title, in order, as (level, text as written)."""
    prose = FENCE.sub("", split_front(text)[1])
    return [(len(m[0]), m[1]) for m in re.findall(r"^(##+) +(.+?)\s*$", prose, re.M)]


def per_class(pairs: Iterable[Pair]) -> dict[str, dict[str, float]]:
    """Precision, recall, F1 and support for every depth that occurs in gold or prediction."""
    pairs = list(pairs)
    out: dict[str, dict[str, float]] = {}
    for d in depth.DEPTHS:
        tp = sum(g == d and p == d for g, p in pairs)
        said = sum(p == d for _, p in pairs)
        support = sum(g == d for g, _ in pairs)
        if not said and not support:
            continue
        precision = tp / said if said else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out[d] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
    return out


def summary(pairs: Iterable[Pair]) -> dict[str, Any]:
    pairs = list(pairs)
    classes = per_class(pairs)
    return {
        "n": len(pairs),
        "accuracy": sum(g == p for g, p in pairs) / len(pairs) if pairs else 0.0,
        "macro_f1": sum(c["f1"] for c in classes.values()) / len(classes) if classes else 0.0,
        "per_class": classes,
        "confusion": {f"{g}->{p}": n for (g, p), n in sorted(Counter(pairs).items())},
    }


def score(
    gold: Sequence[dict[str, Any]], predictions: dict[str, dict[str, Any]], root: Path
) -> dict[str, Any]:
    """The report for every gold note that has a prediction. `root` is the courses dir."""
    pairs: list[Pair] = []
    scored = exact = base_exact = 0
    disagreements: list[dict[str, Any]] = []
    missing: list[str] = []
    for note in gold:
        path = note["path"]
        pred = predictions.get(path)
        if pred is None or not depth.depth_of(pred.get("depth")):
            missing.append(path)
            continue
        headings = headings_of((root / path).read_text(encoding="utf-8"))
        g_each = depth.section_depths(
            note["depth"], depth.sections_of(note.get("depth_sections")), headings
        )
        p_each = depth.section_depths(
            pred["depth"], depth.sections_of(pred.get("depth_sections")), headings
        )
        mine: list[Pair] = []
        wrong = []
        for (_, text), keep, g, p in zip(
            headings, depth.content_mask(headings), g_each, p_each, strict=True
        ):
            if not keep:
                continue
            mine.append((g, p))
            if g != p:
                wrong.append({"heading": text, "gold": g, "predicted": p})
        pairs += mine
        scored += 1
        exact += not wrong
        base_exact += all(g == BASELINE for g, _ in mine)
        if wrong:
            disagreements.append(
                {
                    "path": path,
                    "sections": wrong,
                    "mixed": pred.get("mixed") or [],
                    "review_status": note.get("review_status", ""),
                }
            )
    return {
        "scored": scored,
        "missing": missing,
        "section": summary(pairs),
        "section_baseline": summary([(g, BASELINE) for g, _ in pairs]),
        "exact_match": exact / scored if scored else 0.0,
        "exact_match_baseline": base_exact / scored if scored else 0.0,
        "disagreements": disagreements,
    }


def read_predictions(path: Path) -> dict[str, dict[str, Any]]:
    """Predictions by note path; a later line for the same note replaces an earlier one."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {r["path"]: r for r in rows}


def _table(title: str, got: dict[str, Any], base: dict[str, Any]) -> list[str]:
    lines = [
        f"{title} (n={got['n']})",
        f"  accuracy  {got['accuracy']:.2f}   all-{BASELINE}: {base['accuracy']:.2f}",
        f"  macro F1  {got['macro_f1']:.2f}   all-{BASELINE}: {base['macro_f1']:.2f}",
    ]
    for d, c in got["per_class"].items():
        lines.append(
            f"  {d:<5} precision {c['precision']:.2f}  recall {c['recall']:.2f}  "
            f"F1 {c['f1']:.2f}  (gold: {c['support']:.0f})"
        )
    lines.append("  gold->predicted: " + ", ".join(f"{k} {v}" for k, v in got["confusion"].items()))
    return lines


def render(report: dict[str, Any]) -> str:
    lines = [
        *_table(
            "Section depth, per content heading", report["section"], report["section_baseline"]
        ),
        "",
        f"Notes with every heading right: {report['exact_match']:.2f}   "
        f"all-{BASELINE}: {report['exact_match_baseline']:.2f}",
    ]
    if report["missing"]:
        lines += ["", f"No prediction for {len(report['missing'])} gold notes:"]
        lines += [f"  {p}" for p in report["missing"]]
    if report["disagreements"]:
        lines += ["", f"Disagreements ({len(report['disagreements'])} notes):"]
    for d in report["disagreements"]:
        lines.append(f"- {d['path']}  [{d['review_status']}]")
        lines += [f"    {s['gold']}->{s['predicted']}  {s['heading']}" for s in d["sections"]]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses review depth-score",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)
    gold = yaml.safe_load(args.gold.read_text(encoding="utf-8"))["notes"]
    report = score(gold, read_predictions(args.predictions), get_settings().courses_dir)
    print(json.dumps(report, indent=2) if args.json else render(report))
    if not report["scored"]:
        print("depth-score: no gold note has a prediction", file=sys.stderr)
        return 1
    return 0
