#!/usr/bin/env python3
"""Check what can be computed about practice material.

    librarian courses check drills [path ...]      paths are under data/courses/ (default: programming/drills/, interviewing/)

Reads only public files git would track (never data/courses/private/), as crosswalk does. Exit 1 on any problem.
Checks:
- a schema drill (a Markdown file under drills/ with `track:` in its frontmatter, see programming/drills/readme.md)
  has valid required fields, no H1, the required sections in order, and its solution inside <details>;
- every tracked .py file parses (seeded-bug and stub files are meant to fail when run, so nothing is run);
- every tracked .sql seed loads into an in-memory SQLite database.

The importer turns a drill's `concepts` into `wiki` links and keeps `units`, so neither is required here. Only .md
files are imported, so in practice the .py and .sql checks find nothing in data/courses/; they run on a --root that
holds the sources.

Whether the answer is right is a judgement for the drill-reviewer agent, not this script.
"""

from __future__ import annotations

import argparse
import ast
import re
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path

from librarian.courses.checks.common import default_root, public_files

TRACKS = {"python", "sql", "typescript", "terraform", "tooling", "coding"}
DIFFICULTIES = {"easy", "medium", "hard"}
REQUIRED = ("title", "track", "topic", "difficulty", "timebox_min", "source")
SECTIONS = ("Prompt", "Starter", "Tests")
FENCE = re.compile(r"^\s*```.*?^\s*```", re.S | re.M)


def fields(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return {
        m.group(1): m.group(2) for m in re.finditer(r"^([a-z_]+):[ \t]*(.*)$", text[4:end], re.M)
    }


def check_drill(text: str) -> list[str]:
    """Problems in one schema drill. Files with no `track:` aren't schema drills and return nothing."""
    meta = fields(text)
    if not meta or "track" not in meta:
        return []
    problems = [f"missing frontmatter field: {k}" for k in REQUIRED if k not in meta]
    if meta["track"].strip() not in TRACKS:
        problems.append(f"unknown track: {meta['track']}")
    if "difficulty" in meta and meta["difficulty"].strip() not in DIFFICULTIES:
        problems.append(f"unknown difficulty: {meta['difficulty']}")
    if "timebox_min" in meta and not meta["timebox_min"].strip().isdigit():
        problems.append(f"timebox_min is not a whole number: {meta['timebox_min']}")
    body = FENCE.sub("", text[text.find("\n---", 4) + 4 :])
    if re.search(r"^# ", body, re.M):
        problems.append("H1 in the body: the title lives in frontmatter")
    headings = re.findall(r"^## +(.+?)\s*$", body, re.M)
    positions = []
    for section in SECTIONS:
        if section in headings:
            positions.append(headings.index(section))
        else:
            problems.append(f"no '## {section}' section")
    if positions != sorted(positions):
        problems.append(f"sections out of order: expected {', '.join(SECTIONS)}")
    if not re.search(r"<summary>\s*Solution", body, re.I):
        problems.append("no solution inside a <details> block")
    return problems


def check_python(text: str) -> list[str]:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        return [f"does not parse: line {exc.lineno}: {exc.msg}"]
    return []


def check_sql(text: str) -> list[str]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(text)
    except sqlite3.Error as exc:
        return [f"does not load in SQLite: {exc}"]
    finally:
        connection.close()
    return []


def check_file(path: str, text: str) -> list[str]:
    if path.endswith(".py"):
        return check_python(text)
    if path.endswith(".sql"):
        return check_sql(text)
    if path.endswith(".md") and "/drills/" in f"/{path}":
        return check_drill(text)
    return []


def run(root: Path, paths: Sequence[str]) -> tuple[int, list[str]]:
    """(files checked, "path: problem" lines) for the public files under `paths`."""
    files = 0
    lines: list[str] = []
    for path in public_files(root, *paths):
        target = root / path
        if target.suffix not in {".py", ".sql", ".md"} or not target.is_file():
            continue
        files += 1
        lines += [
            f"{path}: {problem}"
            for problem in check_file(path, target.read_text(encoding="utf-8", errors="replace"))
        ]
    return files, lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses check drills",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", default=["programming/drills/", "interviewing/"])
    parser.add_argument(
        "--root", type=Path, default=None, help="courses dir (default: data/courses)"
    )
    args = parser.parse_args(argv)
    root = (args.root or default_root()).resolve()
    paths = [p.removeprefix("data/courses/") for p in args.paths]
    files, lines = run(root, paths)
    print("\n".join(lines))
    print(f"drill-check: {files} files, {len(lines)} problems")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
