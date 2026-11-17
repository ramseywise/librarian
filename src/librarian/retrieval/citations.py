"""Citation fingerprints: what a cited page looked like when an answer was written, and whether
it still looks that way.

An answer keeps `{id, hash}` for each page it cites. `check` compares that hash with the page
on disk, so a client can mark a citation whose page was edited, renamed or deleted since.
Private pages never count: one looks exactly like a page that does not exist.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Literal, TypedDict

from librarian.retrieval import corpus
from librarian.wiki.common import slugify, text_aliases

# A page id is a file stem: no glob characters or separators (it reaches rglob).
PAGE_ID_PATTERN = r"[A-Za-z0-9][A-Za-z0-9_\-]*"
_PAGE_ID_RE = re.compile(PAGE_ID_PATTERN)

# Hex characters of the sha256 kept. 64 bits is ample to tell two versions of one page apart,
# and the hash goes on every telemetry line.
HASH_CHARS = 16

Status = Literal["current", "changed", "missing"]
CURRENT: Status = "current"
CHANGED: Status = "changed"
MISSING: Status = "missing"


class Source(TypedDict):
    id: str
    hash: str


class CitationStatus(TypedDict, total=False):
    id: str
    status: Status
    # The page's id today, when it was renamed since the answer (resolved through `aliases:`).
    now: str


def _public_page(page_id: str) -> Path | None:
    """The public wiki page with this stem; None if absent, private or the stem is not unique."""
    if not _PAGE_ID_RE.fullmatch(page_id):
        return None
    matches = [p for p in corpus.WIKI_DIR.rglob(f"{page_id}.md") if not corpus.is_private(p)]
    return matches[0] if len(matches) == 1 else None


def _renamed_to(page_id: str) -> Path | None:
    """The one public page that lists `page_id` among its aliases. Reads every page, so only
    after a stem miss."""
    slug = slugify(page_id)
    matches = [
        page
        for page in corpus.wiki_pages()
        if any(slugify(alias) == slug for alias in text_aliases(_text(page)))
    ]
    return matches[0] if len(matches) == 1 else None


def _text(page: Path) -> str:
    return page.read_text(encoding="utf-8", errors="replace")


def _digest(page: Path) -> str:
    """Hash of the whole file, frontmatter included: `read_page` serves the whole file."""
    return hashlib.sha256(page.read_bytes()).hexdigest()[:HASH_CHARS]


def fingerprint(page_id: str) -> str | None:
    """Content hash of the public page `page_id`; None when there is no such page."""
    page = _public_page(page_id)
    try:
        return _digest(page) if page else None
    except OSError:
        return None


def sources(page_ids: list[str]) -> list[Source]:
    """`{id, hash}` for each id that names a public page, in the order given. An id with no
    page (a made-up citation) is left out: there is nothing to go stale."""
    found: list[Source] = []
    for page_id in page_ids:
        digest = fingerprint(page_id)
        if digest is not None:
            found.append({"id": page_id, "hash": digest})
    return found


def check(page_id: str, digest: str) -> CitationStatus:
    """Compare one stored citation with the wiki as it is now.

    `current`: same content. `changed`: the page exists with other content, under its own id or,
    after a rename, under the id in `now`. `missing`: no public page answers to the id.
    """
    page = _public_page(page_id)
    renamed = False
    if page is None and _PAGE_ID_RE.fullmatch(page_id):
        page = _renamed_to(page_id)
        renamed = page is not None
    if page is None:
        return {"id": page_id, "status": MISSING}
    try:
        same = _digest(page) == digest
    except OSError:
        return {"id": page_id, "status": MISSING}
    status: CitationStatus = {"id": page_id, "status": CURRENT if same else CHANGED}
    if renamed:
        status["now"] = page.stem
    return status
