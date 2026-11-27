"""Public links to where a wiki page came from: the paper on arXiv, its PDF, an article's URL.

`data/raw/` is gitignored, so a page's `sources:` paths lead nowhere for a reader. This reads
each source's frontmatter and keeps only what is safe to show anyone: an arXiv id, an http(s)
`url:`, and a PDF in the public course repo (`extracted_from: learn-ai-engineering/...pdf`).
Only `papers/`, `articles/`, `web/`, `pdfs/` and `books/` are read. Sessions, meetings,
Notion, scraped repos and anything else is never opened and is only counted, so no raw path,
title or private name leaves the server.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, urlparse

import yaml

from librarian.log_config import get_logger

log = get_logger(__name__)

COURSE_REPO_BLOB = "https://github.com/ramseywise/learn-ai-engineering/blob/main"
COURSE_REPO_PREFIX = "learn-ai-engineering/"

# Raw source types whose frontmatter names a public origin.
LINKABLE_DIRS = frozenset({"papers", "articles", "web", "pdfs", "books"})
# Each page lists at most this many origins; the rest are still counted.
MAX_ORIGINS = 8

_ARXIV_RE = re.compile(r"^(\d{4}\.\d{4,5}|[a-z-]+(\.[A-Z]{2})?/\d{7})(v\d+)?$")
_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.S)


def _frontmatter(path: Path) -> dict:
    """The YAML header only: raw files can be large, and the body is never needed."""
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            head = fh.read(8192)
    except OSError:
        return {}
    m = _FM_RE.match(head)
    if not m:
        return {}
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {}
    return meta if isinstance(meta, dict) else {}


def _safe_parts(rel: str) -> tuple[str, ...] | None:
    parts = Path(rel).parts
    if not parts or rel.startswith(("/", "\\")) or "\0" in rel:
        return None
    if any(p == ".." or p.startswith(".") or p.lower() == "private" for p in parts):
        return None
    return parts


def _pdf_href(extracted_from: object, course_dir: Path | None) -> str | None:
    if not isinstance(extracted_from, str) or not extracted_from.startswith(COURSE_REPO_PREFIX):
        return None
    rel = extracted_from[len(COURSE_REPO_PREFIX) :]
    parts = _safe_parts(rel)
    if parts is None or not rel.lower().endswith(".pdf") or "sources" not in parts[:-1]:
        return None
    # With the course repo checked out next to this one, skip a PDF that has since moved.
    if course_dir is not None and course_dir.is_dir() and not (course_dir / rel).is_file():
        return None
    return f"{COURSE_REPO_BLOB}/{quote(rel)}"


def _web_href(url: object) -> str | None:
    if not isinstance(url, str):
        return None
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return parsed.geturl()


def resolve_origin(source: str, raw_dir: Path, course_dir: Path | None) -> dict | None:
    """One `sources:` entry → {title, links: [{kind, href}]}, or None when nothing is public."""
    if not source.startswith("data/raw/"):
        return None
    rel = source[len("data/raw/") :]
    parts = _safe_parts(rel)
    if parts is None or len(parts) < 2 or parts[0] not in LINKABLE_DIRS:
        return None
    path = raw_dir / rel
    try:
        if not path.resolve().is_relative_to(raw_dir.resolve()) or not path.is_file():
            return None
    except OSError:
        return None

    meta = _frontmatter(path)
    links: list[dict] = []
    arxiv = str(meta.get("arxiv") or "").strip()
    if _ARXIV_RE.match(arxiv):
        links.append({"kind": "arxiv", "href": f"https://arxiv.org/abs/{arxiv}"})
    if pdf := _pdf_href(meta.get("extracted_from"), course_dir):
        links.append({"kind": "pdf", "href": pdf})
    if web := _web_href(meta.get("url")):
        links.append({"kind": "web", "href": web})
    if not links:
        return None
    title = meta.get("title")
    return {"title": str(title).strip() if title else Path(rel).stem, "links": links}


class OriginResolver:
    """resolve_origin() with a per-parse cache: papers are cited by many pages."""

    def __init__(self, raw_dir: Path, course_dir: Path | None) -> None:
        self.raw_dir = raw_dir
        self.course_dir = course_dir
        self._cache: dict[str, dict | None] = {}

    def __call__(self, sources: object) -> tuple[list[dict], int]:
        """A page's `sources:` → (public origins, how many sources it lists in all)."""
        if not isinstance(sources, list):
            return [], 0
        names = [str(s) for s in sources if s]
        origins: list[dict] = []
        seen: set[str] = set()
        for name in names:
            if name not in self._cache:
                self._cache[name] = resolve_origin(name, self.raw_dir, self.course_dir)
            origin = self._cache[name]
            if origin is None:
                continue
            key = origin["links"][0]["href"]
            if key in seen:
                continue
            seen.add(key)
            origins.append(origin)
            if len(origins) >= MAX_ORIGINS:
                break
        return origins, len(names)
