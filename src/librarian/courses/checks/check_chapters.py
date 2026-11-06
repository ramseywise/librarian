#!/usr/bin/env python3
"""Check lessons against the chapter standard in .claude/skills/pillar/references/pillar-layout.md.

    librarian courses check chapters data-analytics/06-applied-analyses [more paths] [--strict]
    librarian courses check chapters --all          # the whole gate, as `make chapter-check-all`

A path is a module folder (course/module, under data/courses/) or a single lesson. Prints one line per
shortfall. --strict exits 1 on any. Lessons marked `status: skeleton` in frontmatter are reported as
skeletons, not failed, but their metadata is checked. A module whose readme has neither a Builds on nor a
Feeds into table gets a warning line. A warning never counts as a shortfall.

Imported lessons carry only the importer's frontmatter (title, summary, order, kind, section, source), so
`origin` and `sources` are checked when a lesson has them and are not required unless --require-origin is
given. The rules that read the body always apply.

Metadata rules, which count as shortfalls and apply everywhere the chapter shape does:
- `origin`, when present (or required), is one of LEGAL_ORIGINS;
- each `sources` entry holds a URL or DOI, a path that exists, or a dated citation in the layout's form
  ("Huyen, AI Engineering (O'Reilly, 2025), ch. 6"), is a plain string, and names no local PDF;
- no `~/.claude/`, `~/workspace/` or a macOS home path anywhere in the file, code fences and frontmatter included;
- the checklist heading is exactly `## Interview checklist`;
- every arXiv id and DOI the body links is in `sources` (only for lessons that have `sources`).

--metadata-only applies those rules and skips the chapter shape, for programming/ modules the layout exempts.

TypeScript 01-09 and the SQL capstone (LANGUAGE_SUBSET) keep the length exemption and are held to a subset of
the shape: Pitfalls and Next, plus Try it when the prose names a lab under practice/, in that order.

--advisory prints what is reported and not gated: Interview checklist rows under one per ADVISORY_WORDS_PER_ROW
words, body links other than papers that `sources` does not name, and `sources` URLs the body never cites.
Private lessons (data/courses/private/) are never read.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from collections.abc import Sequence
from fnmatch import fnmatch
from pathlib import Path

from librarian.courses.checks.common import (
    default_root,
    is_private,
    rel,
    resolve_arg,
    split_front,
)

MIN_WORDS, MAX_WORDS = 1500, 7000
SECTIONS = [
    ("Pitfalls", r"pitfall"),
    ("Try it", r"try it"),
    ("Interview checklist", r"interview"),
    ("Next", r"next\b"),
]
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
FIGURE = re.compile(r"!\[[^\]]*\]\(|<img\s|^```(mermaid|text|ascii)\b", re.M)
LINK_TABLE = re.compile(r"^(?:#+ +|\*\*)(?:Builds on|Feeds into)\b[^\n]*\n+\|", re.M | re.I)
PILLARED = {"ai-engineering", "generative-ai", "data-analytics", "data-science", "data-engineering"}
LEGAL_ORIGINS = {"synthesis", "book-condensed", "web-authored", "curated"}
CHECKLIST_HEADING = "Interview checklist"
LANGUAGE_SUBSET = (
    ("programming", "typescript", "notes", "*"),
    ("programming", "sql", "notes", "10-*"),
)
LAB_REFERENCE = re.compile(r"\bpractice/")
ADVISORY_WORDS_PER_ROW = 500
PERSONAL_PATH = re.compile(
    r"~/\.claude\b|~/workspace\b|/User[s]/"
)  # [s]: keeps the repo's own hook quiet
URL = re.compile(r"https?://[^\s)\]>\"'`]+")
DOI = re.compile(r"\b10\.\d{4,9}/(?:[^\s()\]>\"'`,;]|\([^\s()]*\))+", re.I)
ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", re.I)
LOCAL_PDF = re.compile(r"\.pdf\b", re.I)
YEAR = re.compile(r"\b(?:19|20)\d\d\b")

__all__ = ["FENCE", "check", "main", "metadata_problems"]


def origin_of(front: str) -> str | None:
    match = re.search(r"^origin:[ \t]*(.*)$", front, re.M)
    if not match:
        return None
    return re.sub(r"\s+#.*$", "", match.group(1)).strip().strip("'\"")


def sources_of(front: str) -> list[str]:
    """The raw `sources` entries, quotes included. A continuation line belongs to the entry above it;
    a YAML comment is no entry."""
    lines = front.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"sources:", line):
            continue
        rest = line[len("sources:") :].strip()
        if rest:
            return [e.strip() for e in rest.strip("[]").split(",") if e.strip()]
        entries: list[str] = []
        for item in lines[i + 1 :]:
            if item.strip().startswith("#"):
                continue
            if re.match(r"\s*- ", item) or item.strip() == "-":
                entries.append(item.strip()[1:].strip())
            elif item.startswith(" ") and entries:
                entries[-1] += " " + item.strip()
            elif item.strip():
                break
        return entries
    return []


def source_problem(entry: str, note: Path, root: Path | None = None) -> str | None:
    """Why one `sources` entry is illegal, or None. A path entry resolves against the note's
    folder, its parent, or `root`."""
    root = root or default_root()
    plain = entry
    if plain[:1] in "'\"":
        plain = plain.strip("'\"")
    elif ": " in plain:
        return f"source is not a plain string, quote it: {entry}"
    bare = URL.sub("", plain)
    if LOCAL_PDF.search(bare):
        return f"source names a local PDF, use the public URL or a citation: {entry}"
    if URL.search(plain) or DOI.search(plain):
        return None
    path = re.split(r"\s+\(", plain, maxsplit=1)[0].strip()
    first = path.split()[0] if path else ""
    if "/" in first or re.search(r"\.\w{1,8}$", first):
        bases = (note.parent, note.parent.parent, root)
        found = any((base / path).exists() for base in bases)
        return None if found else f"source path does not exist: {entry}"
    if YEAR.search(plain) and "," in plain:
        return None
    return f"source is not a URL, DOI, repo path or dated citation: {entry}"


def paper_ids(text: str) -> set[str]:
    """arXiv ids and DOIs in text, lower-cased with trailing punctuation dropped."""
    return {m.lower() for m in ARXIV.findall(text)} | {
        m.rstrip(".").lower() for m in DOI.findall(text)
    }


def metadata_problems(
    text: str, note: Path, root: Path | None = None, require_origin: bool = False
) -> list[str]:
    front, body = split_front(text)
    problems = []
    origin = origin_of(front)
    if origin is None:
        if require_origin:
            problems.append("no origin in frontmatter")
    elif origin not in LEGAL_ORIGINS:
        problems.append(f"origin {origin!r} is not one of {', '.join(sorted(LEGAL_ORIGINS))}")
    entries = sources_of(front)
    problems += [p for p in (source_problem(e, note, root) for e in entries) if p]
    for match in sorted(set(PERSONAL_PATH.findall(text))):
        problems.append(f"personal path {match} in a tracked note")
    prose = FENCE.sub("", body)
    variants = [
        h
        for h in re.findall(r"^##+ +(.+?)\s*$", prose, re.M)
        if re.search(r"interview", h, re.I) and h != CHECKLIST_HEADING
    ]
    problems += [f"heading '{h}' must be '## {CHECKLIST_HEADING}'" for h in variants]
    if re.search(rf"^###+ +{CHECKLIST_HEADING}\s*$", prose, re.M):
        problems.append(f"'{CHECKLIST_HEADING}' must be an H2")
    if entries:  # a lesson with no `sources` has nothing to compare the body's papers against
        for paper in sorted(paper_ids(prose) - paper_ids(front)):
            problems.append(f"body cites {paper}, not in frontmatter sources")
    return problems


def checklist_rows(body: str) -> int:
    """Answer rows in the Interview checklist table: its table lines minus header and separator."""
    match = re.search(rf"^## {CHECKLIST_HEADING}\s*$(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not match:
        return 0
    return max(0, sum(line.startswith("|") for line in match.group(1).splitlines()) - 2)


def advisories(text: str) -> list[str]:
    """What is reported and not gated."""
    front, body = split_front(text)
    prose = FENCE.sub("", body)
    out = []
    words, rows = len(body.split()), checklist_rows(body)
    if rows < words // ADVISORY_WORDS_PER_ROW:
        out.append(
            f"checklist floor: {rows} rows for {words} words, floor {words // ADVISORY_WORDS_PER_ROW}"
        )

    def clean(found: list[str]) -> set[str]:
        return {u.rstrip(".,;") for u in found}

    body_urls, front_urls = clean(URL.findall(prose)), clean(URL.findall(front))
    out += [
        f"body link not in sources: {u}" for u in sorted(body_urls - front_urls) if not paper_ids(u)
    ]
    out += [
        f"source never cited in the body: {u}"
        for u in sorted(front_urls - body_urls)
        if not (paper_ids(u) & paper_ids(prose))
    ]
    return out


def in_language_subset(note: Path) -> bool:
    """Whether a note is one of the programming modules held to the subset of the chapter shape."""
    parts = note.resolve().with_suffix("").parts
    return any(
        len(parts) >= len(rule)
        and all(fnmatch(p, r) for p, r in zip(parts[-len(rule) :], rule, strict=True))
        for rule in LANGUAGE_SUBSET
    )


def language_subset_problems(text: str) -> list[str]:
    """The subset: Pitfalls and Next, Try it where the prose names a lab, and those sections in order."""
    prose = FENCE.sub("", text)
    headings = [h.lower() for h in re.findall(r"^##+ +(.+)$", prose, re.M)]
    needed = [label for label, _ in SECTIONS if label in ("Pitfalls", "Next")]
    if LAB_REFERENCE.search(prose):
        needed.insert(1, "Try it")
    patterns = dict(SECTIONS)
    positions = {
        label: next((i for i, h in enumerate(headings) if re.match(patterns[label], h)), None)
        for label in needed
    }
    problems = [f"no '{label}' section" for label, at in positions.items() if at is None]
    found = [at for at in positions.values() if at is not None]
    if found != sorted(found):
        problems.append(f"{', '.join(needed)} are out of order")
    return problems


def check(
    note: Path,
    metadata_only: bool = False,
    root: Path | None = None,
    require_origin: bool = False,
) -> list[str]:
    raw = note.read_text(encoding="utf-8")
    meta = metadata_problems(raw, note, root, require_origin)
    if metadata_only:
        return meta
    front, text = split_front(raw)
    if in_language_subset(note):
        return meta + language_subset_problems(text)
    if re.search(r"^status:\s*skeleton", front, re.M):
        return ["skeleton (status: skeleton)", *meta]
    problems = meta
    words = len(text.split())
    if words < MIN_WORDS:
        problems.append(f"{words} words, under {MIN_WORDS}")
    if words > MAX_WORDS:
        problems.append(f"{words} words, over {MAX_WORDS}: split it")
    if not FIGURE.search(text):
        problems.append("no figure or diagram")
    if "```" not in text:
        problems.append("no code block")
    prose = FENCE.sub("", text)
    first_h2 = re.search(r"^## ", prose, re.M)
    head = prose[: first_h2.start()] if first_h2 else prose
    if len(re.sub(r"^#.*$", "", head, flags=re.M).split()) < 25:
        problems.append("no hook paragraph before the first H2")
    headings = [h.lower() for h in re.findall(r"^##+ +(.+)$", prose, re.M)]
    for label, pattern in SECTIONS:
        if not any(re.search(pattern, h) for h in headings):
            problems.append(f"no '{label}' section")
    order = [
        next((i for i, h in enumerate(headings) if re.search(p, h)), None) for _, p in SECTIONS
    ]
    found = [i for i in order if i is not None]
    if found != sorted(found):
        problems.append("Pitfalls, Try it, Interview checklist and Next are out of order")
    return problems


def missing_link_tables(module: Path) -> Path | None:
    """The module's readme, if it is in a pillared course and has neither table."""
    readme = next((module / n for n in ("readme.md", "README.md") if (module / n).is_file()), None)
    if readme is None or PILLARED.isdisjoint(module.resolve().parts):
        return None
    return None if LINK_TABLE.search(readme.read_text(encoding="utf-8")) else readme


def lessons_of(paths: Sequence[Path], root: Path) -> list[Path]:
    """The lessons the paths name: a file itself, or `notes/*.md` of a module folder.
    Anything under `private/` is dropped without being listed."""
    notes: list[Path] = []
    for path in paths:
        found = [path] if path.is_file() else sorted((path / "notes").glob("*.md"))
        notes += [n for n in found if not is_private(n, root)]
    return notes


def run(
    paths: Sequence[Path],
    root: Path,
    *,
    metadata_only: bool = False,
    advisory: bool = False,
    require_origin: bool = False,
    quiet: bool = False,
) -> tuple[int, int, list[str]]:
    """(lessons checked, lessons with a shortfall, output lines)."""
    lines: list[str] = []
    notes = lessons_of(paths, root)
    if advisory:
        counts: Counter[str] = Counter()
        for note in notes:
            for line in advisories(note.read_text(encoding="utf-8")):
                lines.append(f"{rel(note, root)}: {line}")
                counts[line.split(":")[0]] += 1
        lines.append(
            "advisory, not gated: "
            + (", ".join(f"{n} {k}" for k, n in sorted(counts.items())) or "none")
        )
        return len(notes), 0, lines
    for path in paths:
        readme = None if path.is_file() or is_private(path, root) else missing_link_tables(path)
        if readme:
            lines.append(f"warning: {rel(readme, root)}: no Builds on or Feeds into table")
    bad = 0
    for note in notes:
        problems = check(note, metadata_only, root, require_origin)
        lines += [f"{rel(note, root)}: {problem}" for problem in problems]
        bad += bool(problems)
    standard = "the metadata rules" if metadata_only else "the chapter standard"
    lines.append(f"{len(notes) - bad} of {len(notes)} notes meet {standard}")
    if quiet:
        lines = lines[-1:]
    return len(notes), bad, lines


def _modules(root: Path, pattern: str) -> list[Path]:
    return sorted(p for p in root.glob(pattern) if p.is_dir() and not is_private(p, root))


def run_all(root: Path, require_origin: bool = False) -> int:
    """The gate `make chapter-check-all` runs. Returns 1 when a gated step has a shortfall."""
    pillared = [m for c in sorted(PILLARED) for m in _modules(root, f"{c}/*")]
    programming = _modules(root, "programming/*") + _modules(root, "programming/python/*")
    subset = _modules(root, "programming/typescript") + sorted(
        root.glob("programming/sql/notes/10-*.md")
    )
    steps = [
        ("chapter standard, pillared courses", pillared, {}, True),
        ("metadata rules, programming/", programming, {"metadata_only": True}, True),
        ("language subset, TypeScript and SQL capstone", subset, {}, True),
        ("programming/ chapter shape (reported only)", programming, {}, False),
        ("advisories (reported only)", pillared, {"advisory": True}, False),
    ]
    failed = False
    for label, paths, opts, gated in steps:
        _, bad, lines = run(paths, root, require_origin=require_origin, **opts)  # type: ignore[arg-type]
        print(f"{label}: {lines[-1]}")
        failed = failed or (gated and bad > 0)
    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="librarian courses check chapters", description=(__doc__ or "").split("\n")[0]
    )
    ap.add_argument("paths", nargs="*", help="module folders or lessons, under the courses dir")
    ap.add_argument("--root", type=Path, default=None, help="courses dir (default: data/courses)")
    ap.add_argument("--all", action="store_true", help="run the whole gate across every course")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any shortfall")
    ap.add_argument("--metadata-only", action="store_true", help="skip the chapter shape")
    ap.add_argument("--advisory", action="store_true", help="print what is not gated, then exit 0")
    ap.add_argument("--require-origin", action="store_true", help="a lesson without `origin` fails")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args(argv)
    root = (args.root or default_root()).resolve()
    if args.all:
        return run_all(root, args.require_origin)
    if not args.paths:
        ap.error("give a module folder or lesson, or --all")
    paths = [resolve_arg(p, root) for p in args.paths]
    _, bad, lines = run(
        paths,
        root,
        metadata_only=args.metadata_only,
        advisory=args.advisory,
        require_origin=args.require_origin,
        quiet=args.quiet,
    )
    print("\n".join(lines))
    return 1 if bad and args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
