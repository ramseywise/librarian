"""Course sources (`COURSE_SOURCES_DIR`): the PDF library lessons link to with `sources/...`.

The sources repo is third-party material and never lives in this one. Lessons keep their
relative links (`sources/x.pdf`, `../sources/x.pdf`, ...), which are dead in librarian. At
render time `source_links` maps each such link to a course-relative path, only when the file
exists in the sources dir, and the API serves it at `/api/courses/sources/<path>`. The route is
local only: `SERVE_COURSE_SOURCES=false` (a deployment) turns it and the mapping off.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import unquote

from librarian.config import get_settings

_settings = get_settings()
SOURCES_DIR = _settings.course_sources_dir
SERVE_SOURCES = _settings.serve_course_sources
PUBLIC_MODE = _settings.public_mode

# A subject's root files sit in `00-start-here`; in the sources repo they sit
# at the course root, so their relative links start one level higher.
ROOT_MODULE = "00-start-here"

_MD_TARGET_RE = re.compile(r"\]\(\s*<?([^)\s>]+)")
_HTML_ATTR_RE = re.compile(r"""\b(?:src|href)\s*=\s*["']([^"']+)["']""", re.I)
_REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?\s*$", re.M)
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def sources_root() -> Path | None:
    """The resolved sources dir; None when serving is off or the dir is missing."""
    if not SERVE_SOURCES:
        return None
    try:
        root = SOURCES_DIR.resolve()
    except OSError:
        return None
    return root if root.is_dir() else None


def source_file(rel: str) -> Path | None:
    """Absolute path of `rel` inside the sources dir, or None.

    None for: serving off, no such dir, absolute or `..` paths, NUL bytes, dot-segments
    (`.git`, `.env`), anything that resolves outside the dir (symlinks included), and
    anything that is not a regular file.
    """
    root = sources_root()
    if root is None or not rel or "\0" in rel or rel.startswith(("/", "\\")):
        return None
    parts = Path(rel).parts
    if ".." in parts or any(p.startswith(".") for p in parts):
        return None
    if PUBLIC_MODE and any(p.lower() == "private" for p in parts):
        return None
    try:
        target = (root / rel).resolve()
    except (OSError, ValueError):
        return None
    if not target.is_relative_to(root) or not target.is_file():
        return None
    # Only the PDF library: the sibling repo also holds drills, ledgers and scripts, which
    # this route has no reason to serve. Same rule as resolve_link.
    resolved_parts = target.relative_to(root).parts
    if "sources" not in resolved_parts[:-1]:
        return None
    if PUBLIC_MODE and any(p.lower() == "private" for p in resolved_parts):
        return None  # a symlink into a private/ tree
    return target


def resolve_link(lesson_id: str, href: str) -> str | None:
    """Course-root-relative path of a lesson link that points into a `sources/` folder."""
    path = unquote(href.split("#", 1)[0].split("?", 1)[0])
    if not path or path.startswith("/") or _SCHEME_RE.match(path):
        return None
    base = lesson_id.split("/")[:-1]
    if len(base) >= 2 and base[1] == ROOT_MODULE:
        del base[1]
    resolved = os.path.normpath("/".join([*base, path]))
    parts = Path(resolved).parts
    if resolved.startswith("..") or "sources" not in parts[:-1] or "assets" in parts:
        return None
    return resolved


def source_links(lesson_id: str, body: str) -> dict[str, str]:
    """href as written → sources path, for every link in `body` whose file exists."""
    if sources_root() is None:
        return {}
    hrefs = {m.group(1) for m in _MD_TARGET_RE.finditer(body)}
    hrefs |= {m.group(1) for m in _HTML_ATTR_RE.finditer(body)}
    hrefs |= {m.group(1) for m in _REF_DEF_RE.finditer(body)}
    found: dict[str, str] = {}
    for href in sorted(hrefs):
        rel = resolve_link(lesson_id, href)
        if rel and source_file(rel):
            found[href.split("#", 1)[0]] = rel
    return found
