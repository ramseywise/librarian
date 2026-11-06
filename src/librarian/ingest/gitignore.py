"""Ask git which files under a subject directory are ignored.

Shared by the course importer (the publication allowlist for fail-closed subjects) and the
repo scraper (it honours the same allowlist for `practice/`). It lives in `ingest/` so the
dependency between the two sub-packages runs one way: `courses` imports `ingest`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_ignored(source: Path, subject_dir: Path) -> set[str] | None:
    """Repo-relative paths of untracked gitignored files under a subject.

    An ignored directory git will not descend into (a nested repo) comes back as one entry
    with a trailing slash, so test membership with `matches_ignored`. None when `source` is
    not a git checkout: there is nothing to go on, which each caller has to decide about.
    """
    try:
        out = subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "ls-files",
                "-z",
                "-o",
                "-i",
                "--exclude-standard",
                "--",
                str(subject_dir.relative_to(source)),
            ],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.decode(errors="replace").split("\0") if p}


def matches_ignored(rel: str, ignored: set[str]) -> bool:
    """Is repo-relative `rel` ignored, or inside an ignored directory entry?"""
    return rel in ignored or any(p.endswith("/") and rel.startswith(p) for p in ignored)
