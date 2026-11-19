"""Propose a depth for every section of a note, with one model call per note (BILLABLE).

    librarian courses review depth-classify --gold GOLD.yaml [--out RUN.jsonl] [--model ID]
    librarian courses review depth-classify <note path under the courses dir> ...

The model is given the rubric (.claude/skills/pillar/references/depth-rubric.md), the note's path,
its headings and its body, and answers with a depth for each content heading plus the passages
that sit at another depth than their section (`mixed`: the note's rebuild list). It judges
sections only: a note has no depth of its own, and its tier is the curriculum steward's. It is
never given a label: `--gold` is read for its paths only. Private notes are refused. Each proposal
is turned into the stored form before it is written: `depth`, the default for the note's sections,
and `depth_sections`, the sections that differ. A depth for a heading that does not exist or
carries none (Pitfalls, Next, ...) is dropped, a content heading the model left out takes the
depth around it, and both are recorded on the row. Appends to `logs/review/depth/<date>-<model>.jsonl` (gitignored) unless --out
is given; a note already in the file is skipped, so a failed run can be repeated. Writes no note.
Score a run with `librarian courses review depth-score`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any

import anthropic
import yaml

from librarian.config import get_settings
from librarian.courses import depth
from librarian.courses.checks.common import split_front
from librarian.courses.review.depth_score import headings_of, read_predictions
from librarian.log_config import get_logger

log = get_logger(__name__)

RUBRIC = Path(".claude/skills/pillar/references/depth-rubric.md")
PRIVATE = "private"
MAX_TOKENS = 1500
DEFAULT = "core"
WORKERS = 4

TASK = """You tag the sections of course notes by depth, following the rubric below exactly.
You judge sections only: do not give the note a depth or a tier.

For the note you are given, decide:
1. `sections`: the depth of every content heading, as an object from heading to depth:
   {"The idea": "intro", "Building it": "core", "Why it works": "deep"}. Use the heading text
   exactly as listed, and give every heading its own depth, subsections included. Leave out the
   headings the rubric says carry no depth (Pitfalls, Try it, Labs, Interview checklist, Reading,
   Practice, Next) and anything under them.
2. `mixed`: passages at another depth than the section they sit in, by the rubric's rule for
   them, as {"heading": the heading they sit under, "passage": their first few words,
   "depth": the passage's depth}. Leave it [] when there are none.

Reply with one JSON object with exactly those two keys and nothing else.

<rubric>
"""


def system_prompt(root: Path) -> str:
    return TASK + (root / RUBRIC).read_text(encoding="utf-8") + "\n</rubric>"


def note_prompt(path: str, text: str) -> str:
    """What the model sees of one note: path, headings, body. No frontmatter, so no tag."""
    listing = "\n".join(f"{'#' * level} {heading}" for level, heading in headings_of(text))
    body = split_front(text)[1].strip()
    return f"Path: {path}\n\n<headings>\n{listing}\n</headings>\n\n<note>\n{body}\n</note>"


def parse(reply: str) -> dict[str, Any] | None:
    """The JSON object in a reply, or None. Tolerates a code fence or words around it."""
    start, end = reply.find("{"), reply.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        found = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return None
    return found if isinstance(found, dict) else None


def default_depth(depths: Sequence[str]) -> str:
    """The depth a note's unlisted sections take: `core` unless no section is, then the commonest."""
    if not depths or DEFAULT in depths:
        return DEFAULT
    return max(depth.DEPTHS, key=depths.count)


def clean(
    proposal: dict[str, Any], headings: Sequence[depth.Heading]
) -> tuple[dict[str, Any], list[str]]:
    """A proposal turned into the stored form, and what was dropped from it. No usable section
    depth gives an empty dict."""
    raw = proposal.get("sections")
    if not isinstance(raw, dict):
        return {}, [f"sections is a {type(raw).__name__}, not a mapping"]
    dropped = [f"{h!r}: {d!r} is not a depth" for h, d in raw.items() if not depth.depth_of(d)]
    given = depth.sections_of(raw)
    mask = depth.content_mask(headings)
    content = [text for (_, text), keep in zip(headings, mask, strict=True) if keep]
    texts = [text for _, text in headings]
    dropped += [f"{h!r}: no such heading" for h in given if h not in texts]
    dropped += [f"{h!r}: carries no depth" for h in given if h in texts and h not in content]
    dropped += [f"{h!r}: no depth given" for h in content if h not in given]
    wanted = {h: d for h, d in given.items() if h in content}
    if not wanted:
        return {}, dropped or ["no section was given a depth"]
    note = default_depth(list(wanted.values()))
    kept: dict[str, str] = {}
    # In heading order, so that an entry is judged against the kept entries above it.
    for at, (_, text) in enumerate(headings):
        if text not in wanted or text in kept:
            continue
        if wanted[text] != depth.section_depths(note, kept, headings)[at]:
            kept[text] = wanted[text]
    mixed = proposal.get("mixed")
    return {
        "depth": note,
        "depth_sections": kept,
        "mixed": mixed if isinstance(mixed, list) else [],
    }, dropped


def classify(
    client: anthropic.Anthropic, model: str, system: str, path: str, text: str
) -> dict[str, Any]:
    """One row for the run file. A reply that cannot be used gives a row with `error` and no depth."""
    row: dict[str, Any] = {"path": path, "model": model}
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": note_prompt(path, text)}],
        )
    except anthropic.APIError as e:
        log.warning("depth.classify_failed", path=path, error=type(e).__name__)
        return {**row, "error": f"{type(e).__name__}: {getattr(e, 'message', '')}"[:300]}
    reply = "".join(b.text for b in resp.content if b.type == "text")
    row["usage"] = {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens}
    proposal = parse(reply)
    if proposal is None:
        return {**row, "error": "reply is not JSON"}
    cleaned, dropped = clean(proposal, headings_of(text))
    if not cleaned:
        return {**row, "error": dropped[0]}
    return {**row, **cleaned, "dropped": dropped}


def note_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.paths)
    if args.gold:
        gold = yaml.safe_load(args.gold.read_text(encoding="utf-8"))
        paths += [n["path"] for n in gold["notes"]]  # the paths only, never a label
    return list(dict.fromkeys(paths))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses review depth-classify",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", help="notes, relative to the courses dir")
    parser.add_argument("--gold", type=Path, help="a gold file; its note paths are classified")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--model")
    args = parser.parse_args(argv)
    settings = get_settings()
    root = settings.courses_dir
    paths = note_paths(args)
    if not paths:
        parser.error("give note paths or --gold")
    refused = [p for p in paths if PRIVATE in Path(p).parts or not (root / p).is_file()]
    if refused:
        print("depth-classify: private or missing: " + ", ".join(refused), file=sys.stderr)
        return 2
    if not settings.anthropic_api_key:
        print("depth-classify: ANTHROPIC_API_KEY is not set", file=sys.stderr)
        return 2
    model = args.model or settings.anthropic_model
    out = args.out or settings.review_dir / "depth" / f"{date.today().isoformat()}-{model}.jsonl"
    done = read_predictions(out) if out.exists() else {}
    todo = [p for p in paths if not depth.depth_of(done.get(p, {}).get("depth"))]
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system = system_prompt(settings.root)

    def one(path: str) -> dict[str, Any]:
        return classify(client, model, system, path, (root / path).read_text(encoding="utf-8"))

    out.parent.mkdir(parents=True, exist_ok=True)
    failed = 0
    with ThreadPoolExecutor(WORKERS) as pool, out.open("a", encoding="utf-8") as fh:
        for row in pool.map(one, todo):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            failed += "error" in row
    print(f"{out}: {len(todo) - failed} classified, {failed} failed, {len(paths) - len(todo)} kept")
    return 1 if failed else 0
