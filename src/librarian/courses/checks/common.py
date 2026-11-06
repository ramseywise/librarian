"""Shared helpers for the course checks: where the courses live, what counts as public, git visibility.

Every check takes a `root` (default: the courses dir from `get_settings()`) and reads only the
public tree. `data/courses/private/` is skipped by default and never named in output; links into
it are `librarian.wiki.course_leaks`' business, not the checks'.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable
from pathlib import Path

from librarian.config import get_settings
from librarian.courses.overlay import PRIVATE
from librarian.retrieval.corpus import is_under_private

FENCE = re.compile(r"^\s*```.*?^\s*```", re.S | re.M)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".ipynb_checkpoints", ".preview"}


def default_root() -> Path:
    """The courses dir: `$COURSES_DIR`, else `data/courses/` under the repo root."""
    return get_settings().courses_dir


def split_front(text: str) -> tuple[str, str]:
    """(frontmatter, body). The frontmatter is empty when the file has none."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[3:end], text[end + 4 :]
    return "", text


def is_private(path: Path, root: Path) -> bool:
    """Whether `path` lies in `root/private/` (resolved, so `..` cannot slip past)."""
    return is_under_private(path, root / PRIVATE)


def rel(path: Path, root: Path) -> str:
    """`path` relative to `root` as posix; the absolute path if it is outside."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_arg(arg: str | Path, root: Path) -> Path:
    """A CLI path: as given if it exists, else relative to `root`. `data/courses/` is stripped."""
    path = Path(arg)
    if path.exists():
        return path
    text = path.as_posix().removeprefix("./")
    for prefix in ("data/courses/", "courses/"):
        text = text.removeprefix(prefix)
    return root / text


def git_visible(root: Path, *subpaths: str) -> set[str] | None:
    """Root-relative files git would track (tracked or untracked and not ignored).

    None when `root` is not in a git checkout (a temp dir in a test): callers then walk the disk.
    """
    cmd = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "-co",
        "--exclude-standard",
        "--",
        *(subpaths or (".",)),
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return {line for line in out.stdout.splitlines() if line}


def git_ignored(root: Path, paths: Iterable[str]) -> set[str]:
    """The subset of root-relative `paths` that git ignores. Empty outside a checkout."""
    wanted = sorted(set(paths))
    if not wanted:
        return set()
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--stdin"],
            input="\n".join(wanted),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return set()
    if out.returncode not in (0, 1):
        return set()
    return set(out.stdout.splitlines())


def public_files(root: Path, *subpaths: str) -> list[str]:
    """Root-relative public files (never under `private/`), sorted.

    Uses git's view when `root` is in a checkout, so gitignored local files are not read;
    otherwise walks the disk.
    """
    visible = git_visible(root, *subpaths)
    if visible is None:
        bases = [root / s for s in subpaths] if subpaths else [root]
        visible = {
            rel(p, root)
            for base in bases
            for p in ([base] if base.is_file() else base.rglob("*"))
            if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(root).parts)
        }
    return sorted(p for p in visible if p.split("/", 1)[0] != PRIVATE)
