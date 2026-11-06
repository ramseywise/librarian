"""Course-side private checks for `librarian wiki check`.

`data/courses/private/` is gitignored, like `data/wiki/private/`. Two checks keep it that way:

- `tracked_private_files`: no file under either private tree may be in the git index, so a
  `git add -f` cannot slip through. Reports a count, never a name.
- `scan_public_lessons`: no lesson outside `private/` may reach into `data/courses/private/`
  (markdown link, image, HTML src/href, reference-style link, any path-like frontmatter
  value such as a lesson id in `cards[].lesson`) or name a private wiki page (`[[...]]` or
  a `wiki:` / `concepts:` entry). Reports name the public file and line, never the target.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path
from urllib.parse import unquote

import frontmatter
import yaml

from librarian.wiki.common import WIKILINK_RE, fm

PRIVATE_DIRS = ("data/wiki/private", "data/courses/private")
COURSES_PRIVATE = "private"

_MD_TARGET_RE = re.compile(r"\]\(\s*<?([^)\s>]+)")
_HTML_ATTR_RE = re.compile(r"""\b(?:src|href)\s*=\s*["']([^"']+)["']""", re.I)
_REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?\s*$")
_PATH_MENTION_RE = re.compile(r"courses/private(?:/|\b)")
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_PATHLIKE_RE = re.compile(r"^[^\s]+$")
# Frontmatter keys whose entries are wiki page names.
_WIKI_KEYS = ("wiki", "concepts")


def tracked_private_files(repo_root: Path) -> list[str] | None:
    """Files under either private tree that git tracks; None when this is not a git checkout."""
    try:
        run = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return None
    if run.returncode != 0:
        return None
    # Filtered here, not by pathspec: git refuses a pathspec beyond a symlink, and in a worktree
    # private/ is one.
    return [f for f in run.stdout.split("\0") if f.startswith(tuple(f"{d}/" for d in PRIVATE_DIRS))]


def _under_private(candidate: str, private_root: str) -> bool:
    return candidate == private_root or candidate.startswith(private_root + os.sep)


def reaches_private(target: str, source: Path, courses_dir: Path) -> bool:
    """Whether a link or lesson-id string, read from `source`, points into courses/private/.

    Read both relative to the file (a markdown link) and to the course root (a lesson id).
    Lexical, so a dangling link and a CI checkout without private/ are caught as well.
    """
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target or _SCHEME_RE.match(target):
        return False
    private_root = os.path.normpath(courses_dir / COURSES_PRIVATE)
    bases = (source.parent, courses_dir)
    if target.startswith("/"):
        bases = (courses_dir,)
        target = target.lstrip("/")
    for base in bases:
        joined = os.path.normpath(os.path.join(base, target))
        if _under_private(joined, private_root) or _under_private(
            joined.removesuffix(".md"), private_root
        ):
            return True
    return False


def _strings(value: object) -> Iterator[str]:
    """Every string in a parsed frontmatter value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _line_of(lines: list[str], needle: str) -> int:
    return next((n for n, line in enumerate(lines, start=1) if needle in line), 1)


def _public_lessons(courses_dir: Path) -> list[Path]:
    private_root = courses_dir / COURSES_PRIVATE
    return sorted(
        p for p in courses_dir.rglob("*.md") if private_root not in p.parents and p != private_root
    )


def _line_targets(line: str) -> list[str]:
    found = [m.group(1) for m in _MD_TARGET_RE.finditer(line)]
    found += [m.group(1) for m in _HTML_ATTR_RE.finditer(line)]
    if ref := _REF_DEF_RE.match(line):
        found.append(ref.group(1))
    return found


def scan_public_lessons(
    courses_dir: Path,
    names_private_wiki_page: Callable[[str], bool],
    display: Callable[[Path], str] = str,
) -> tuple[list[str], int]:
    """(blockers, files scanned) for lessons outside courses_dir/private/."""
    blockers: list[str] = []
    if not courses_dir.is_dir():
        return blockers, 0
    files = _public_lessons(courses_dir)
    for md in files:
        text = md.read_text(errors="replace")
        lines = text.splitlines()
        seen: set[tuple[int, str]] = set()

        def flag(
            number: int, message: str, md: Path = md, seen: set[tuple[int, str]] = seen
        ) -> None:
            if (number, message) not in seen:
                seen.add((number, message))
                blockers.append(f"{display(md)}:{number} {message}")

        for number, line in enumerate(lines, start=1):
            if _PATH_MENTION_RE.search(line) or any(
                reaches_private(t, md, courses_dir) for t in _line_targets(line)
            ):
                flag(number, "links into data/courses/private/")
            if any(names_private_wiki_page(m.group(1)) for m in WIKILINK_RE.finditer(line)):
                flag(number, "wikilink resolves to a private page")
        if not text.startswith("---"):
            continue
        try:
            meta = fm(frontmatter.loads(text))
        except (yaml.YAMLError, ValueError):
            continue
        for key, value in meta.items():
            for s in _strings(value):
                if key in _WIKI_KEYS and names_private_wiki_page(s):
                    flag(_line_of(lines, s), "frontmatter wiki entry names a private page")
                pathlike = _PATHLIKE_RE.match(s) and ("/" in s or s.endswith(".md"))
                if pathlike and reaches_private(s, md, courses_dir):
                    flag(_line_of(lines, s), "links into data/courses/private/")
    return blockers, len(files)
