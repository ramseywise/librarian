"""The private overlay: what is withheld from the public course tree and where it lives.

`data/courses/private/<course>/<module>/...` mirrors the public layout. Two kinds of file are
withheld from the public tree and live only in that mirror:

- figures cropped from books and papers, `<module>/assets/sources/...`. Public lessons keep
  their relative image links; the asset route falls back to the mirror when the public file is
  missing, and the frontend hides the image when neither exists.
- a module's `readings:` list (the PDF catalogue). A mirror `_module.md` carries only that
  list; the catalog merges it in, and the public `_module.md` keeps a `readings_count`.

Library code only: no web framework here, so the importer, the catalog and `tools/slides` can
all use it.
"""

from __future__ import annotations

import itertools
import os
import re
from pathlib import Path

PRIVATE = "private"

_URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)


def is_sources_asset(parts: tuple[str, ...]) -> bool:
    """Whether a path (relative to a module dir, or to the courses root) is under `assets/sources/`."""
    return any(a == "assets" and b == "sources" for a, b in itertools.pairwise(parts))


def private_mirror(path: Path, courses_dir: Path) -> Path | None:
    """The same relative path under `courses_dir/private/`; None if `path` is outside the tree
    or already inside the mirror."""
    try:
        rel = Path(os.path.normpath(path)).relative_to(os.path.normpath(courses_dir))
    except ValueError:
        return None
    if not rel.parts or rel.parts[0] == PRIVATE:
        return None
    return courses_dir / PRIVATE / rel


def resolve_asset(path: Path, courses_dir: Path) -> Path | None:
    """`path` if it is a file, else its private-mirror twin if that is a file, else None."""
    if path.is_file():
        return path
    mirror = private_mirror(path, courses_dir)
    return mirror if mirror is not None and mirror.is_file() else None


def is_external_reading(reading: object) -> bool:
    """A reading that is a web link, not a path into the sources library."""
    source = reading.get("source", "") if isinstance(reading, dict) else str(reading)
    return bool(_URL_RE.match(str(source)))


def split_readings[T](readings: list[T]) -> tuple[list[T], list[T]]:
    """(public, private). External URLs reveal nothing about the PDF library, so they stay
    public; every path into a sources folder goes to the mirror."""
    public = [r for r in readings if is_external_reading(r)]
    private = [r for r in readings if not is_external_reading(r)]
    return public, private
