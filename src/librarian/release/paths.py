"""Where releases live on disk, and the one atomic operation on them: repointing `current`."""

from __future__ import annotations

import os
import re
from pathlib import Path

from librarian.config import get_settings

RELEASES = "releases"
CURRENT = "current"
PIN = "pin"
LATEST = "latest"
MANIFEST = "manifest.json"
ARCHIVE_SUFFIX = ".tar.zst"
# A release name is a path component and part of a URL: keep it boring.
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def check_name(name: str) -> str:
    if not _NAME_RE.match(name) or ".." in name:
        raise ValueError(f"not a release name: {name!r}")
    return name


def content_root() -> Path:
    """`<state>/content`: the parent of `current`, `releases/` and `pin`."""
    return get_settings().var_dir / "content"


def read_current(root: Path) -> str | None:
    """The release name `current` points at, or None (no pointer, or not a release)."""
    try:
        target = os.readlink(root / CURRENT)
    except OSError:
        return None
    parts = Path(target).parts
    if len(parts) == 2 and parts[0] == RELEASES:
        return parts[1]
    return None


def repoint(root: Path, release_dir: Path) -> None:
    """Atomically point `<root>/current` at `release_dir` (a directory in `<root>/releases`)."""
    tmp = root / f".{CURRENT}.{os.getpid()}"
    tmp.unlink(missing_ok=True)
    tmp.symlink_to(Path(RELEASES) / release_dir.name, target_is_directory=True)
    os.replace(tmp, root / CURRENT)
