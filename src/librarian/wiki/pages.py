"""Reading the wiki: every page parsed once, and the link index over them.

Shared by the stats, the leak check, the gaps list, lint, the graph and rename.
Private pages are loaded here so callers can match against them, never to print them.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import frontmatter
import yaml

from librarian.config import get_settings
from librarian.wiki.common import (
    LinkEntry,
    LinkIndex,
    fm,
    link_name,
    page_aliases,
    page_tags,
    resolve_link,
)

REPO_ROOT = get_settings().root
WIKI_DIR = get_settings().wiki_dir
TELEMETRY_DIR = get_settings().telemetry_dir
COURSES_DIR = get_settings().courses_dir
RETRIEVAL_LOG = get_settings().retrieval_log
_FM_TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
_FM_BLOCK_RE = re.compile(r"\A---\n.*?\n---\n?", re.DOTALL)


@dataclass
class Page:
    path: Path
    rel: str  # posix path relative to the wiki dir
    stem: str
    title: str
    tags: list[str]
    updated: date | None
    body: str
    parsed: bool  # False: broken YAML, so tags and date are unknown
    aliases: tuple[str, ...] = ()

    @property
    def domain(self) -> str:
        parts = self.rel.split("/")
        return parts[0] if len(parts) > 1 else "(root)"

    @property
    def scored(self) -> bool:
        return "tombstone" not in self.tags and not self.stem.startswith("_")


def _to_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _load_page(path: Path, wiki_dir: Path) -> Page:
    text = path.read_text(errors="replace")
    rel = path.relative_to(wiki_dir).as_posix()
    try:
        post = frontmatter.loads(text)
    except (yaml.YAMLError, ValueError):
        # The graph and index drop such a page; a leak check must still see its title.
        match = _FM_TITLE_RE.search(text)
        title = match.group(1).strip().strip("\"'") if match else path.stem
        body = _FM_BLOCK_RE.sub("", text, count=1)
        return Page(path, rel, path.stem, title, [], None, body, parsed=False)
    tags = page_tags(fm(post))
    title = str(fm(post).get("title") or path.stem)
    updated = _to_date(fm(post).get("updated"))
    aliases = tuple(page_aliases(post.metadata))
    return Page(path, rel, path.stem, title, tags, updated, post.content, True, aliases)


def _public_files(wiki_dir: Path) -> list[Path]:
    return sorted(
        f for f in wiki_dir.rglob("*.md") if f.relative_to(wiki_dir).parts[0] != "private"
    )


def _private_pages(wiki_dir: Path) -> list[Page]:
    # Searched from its own root: in a worktree private/ is a symlink, which rglob from
    # the wiki dir would not descend into.
    root = wiki_dir / "private"
    if not root.is_dir():
        return []
    return [_load_page(f, wiki_dir) for f in sorted(root.rglob("*.md"))]


def _public_pages(wiki_dir: Path) -> list[Page]:
    return [_load_page(f, wiki_dir) for f in _public_files(wiki_dir)]


class PageLinks:
    """`LinkIndex` over `Page`s: the one way health stats, lint, gaps, graph and rename resolve a link."""

    def __init__(self, pages: Iterable[Page]) -> None:
        self.by_rel = {p.rel: p for p in pages}
        self.index = LinkIndex(
            LinkEntry(
                key=p.rel,
                path=p.rel,
                stem=p.stem,
                title=p.title,
                aliases=p.aliases,
                tombstone="tombstone" in p.tags,
                private=p.rel.split("/", 1)[0] == "private",
            )
            for p in self.by_rel.values()
        )

    def resolve(self, raw: str, **options: bool) -> Page | None:
        """The page `[[raw]]` names (see `resolve_link` for the options), or None."""
        key = resolve_link(raw, self.index, **options)
        return None if key is None else self.by_rel[key]


def _link_index(pages: Iterable[Page]) -> PageLinks:
    return PageLinks(pages)


def _via_private_path(raw: str) -> bool:
    """Whether a link spells out a path through private/ (`private/some-page`)."""
    target = link_name(raw)
    return "/" in target and "private" in target.split("/")[:-1]


def _links_to_private(raw: str, public: PageLinks, private: PageLinks) -> bool:
    """Whether `[[raw]]` in a public file resolves to a private page.

    `private` holds only private pages. A name that a public page also answers to is that
    page's link, unless the link spells out the private/ path.
    """
    if private.resolve(raw, only_private=True) is None:
        return False
    return _via_private_path(raw) or public.resolve(raw, include_tombstones=True) is None
