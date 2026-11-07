"""Serving course images: the public-mode guard and the path check.

The courses root and `PUBLIC_MODE` are read from `librarian.courses.catalog` at call time, so a test
that patches them there still takes effect."""

from __future__ import annotations

from pathlib import Path

from librarian.courses import overlay
from librarian.courses.loader import PRIVATE_COURSES
from librarian.retrieval.corpus import is_under_private


def _cat():  # noqa: ANN202 - the catalog module; imported late because it imports this one
    from librarian.courses import catalog as module

    return module


ASSET_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


def is_private_asset(file_path: str) -> bool:
    """True in public mode when `file_path` names, or resolves into, a private/ tree."""
    if not _cat().PUBLIC_MODE:
        return False
    if any(p.lower() == PRIVATE_COURSES for p in Path(file_path).parts):
        return True
    try:
        target = (_cat().COURSES_DIR / file_path).resolve()
    except (OSError, ValueError, RuntimeError):
        return True
    return is_under_private(target, _cat().COURSES_DIR / PRIVATE_COURSES)


def asset_path(file_path: str) -> Path | None:
    """Absolute path of an image under COURSES_DIR, or None when `file_path` is not one.

    Two-step guard: reject traversal syntax, then confirm the resolved path is inside the
    courses root. Only images are served. A missing file falls back to the same relative path
    in the private mirror (book and paper figures live only there); a path that exists in
    neither comes back as the public path, so the route answers 404.
    """
    if ".." in Path(file_path).parts or file_path.startswith("/"):
        return None
    if "\0" in file_path or is_private_asset(file_path):
        return None
    root = _cat().COURSES_DIR.resolve()
    target = (_cat().COURSES_DIR / file_path).resolve()
    if not target.is_relative_to(root) or target.suffix.lower() not in ASSET_TYPES:
        return None
    if _cat().PUBLIC_MODE:
        return target  # the private mirror is not consulted
    found = overlay.resolve_asset(target, root)
    if found is not None and not found.resolve().is_relative_to(root):
        return None  # a symlink in the mirror pointing out of the tree
    return found or target
