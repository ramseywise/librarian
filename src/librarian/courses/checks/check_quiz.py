#!/usr/bin/env python3
"""Check the multiple-choice quiz files of the modules.

    librarian courses check quiz [path ...]      paths are under data/courses/ (default: everything)

Reads every public `<course>/<module>/_quiz.md` (never data/courses/private/). Exit 1 on any problem.
A question needs a prompt, two or more distinct options, an answer that is one of them, an id made of
letters, digits, `.`, `_` and `-` (given, or the hash of the prompt) that no other question in the file
uses, and, when it names a `lesson`, a lesson of the same module. Whether the answer is right is a
judgement for the drill-reviewer agent, not this script.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from librarian.courses import quiz
from librarian.courses.checks.common import default_root, public_files


def module_lessons(root: Path, module_dir: Path) -> set[str]:
    """Ids (path under `root`, no `.md`) of the lessons a module's quiz may point at."""
    return {
        p.relative_to(root).with_suffix("").as_posix()
        for p in module_dir.rglob("*.md")
        if not p.name.startswith("_") and "private" not in p.relative_to(module_dir).parts
    }


def run(root: Path, paths: Sequence[str]) -> tuple[int, list[str]]:
    """(quiz files checked, "path: problem" lines) for the public quiz files under `paths`."""
    files = 0
    lines: list[str] = []
    for path in public_files(root, *paths):
        target = root / path
        if target.name != quiz.QUIZ_FILE or not target.is_file():
            continue
        files += 1
        lessons = module_lessons(root, target.parent)
        lines += [f"{path}: {p}" for p in quiz.problems_in(target, lessons)]
    return files, lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="librarian courses check quiz",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", default=[])
    parser.add_argument(
        "--root", type=Path, default=None, help="courses dir (default: data/courses)"
    )
    args = parser.parse_args(argv)
    root = (args.root or default_root()).resolve()
    paths = [p.removeprefix("data/courses/") for p in args.paths]
    files, lines = run(root, paths)
    print("\n".join(lines))
    print(f"quiz-check: {files} files, {len(lines)} problems")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
