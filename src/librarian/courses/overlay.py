"""The private overlay: what is withheld from the public course tree and where it lives.

`data/courses/private/<course>/<module>/...` mirrors the public layout. Two kinds of file are
withheld from the public tree and live only in that mirror:

- figures cropped from books and papers with no licence to redistribute them: everything under
  `<module>/assets/sources/...`, plus individual figures elsewhere in `assets/` (the Müller &
  Guido and Sarkar figures). Public lessons and decks keep their relative image links; the asset
  route and the deck builder fall back to the mirror for any asset path, and the frontend hides
  the image when neither exists.
- a module's `readings:` list (the PDF catalogue). A mirror `_module.md` carries only that
  list; the catalog merges it in, and the public `_module.md` keeps a `readings_count`.

Library code only: no web framework here, so the catalog and `tools/slides` can
all use it.
"""

from __future__ import annotations

import itertools
import os
from pathlib import Path

PRIVATE = "private"


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
