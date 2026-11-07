"""Shared wiki-markup patterns — the single definition site (LIB-110 Phase B).

WIKILINK_RE, TYPED_LINK_RE, slugify and `resolve_link` were previously defined per-module in
wiki_parser, retrieval, relinker, and graph_expansion; link resolution diverged between the
index and the UI until every consumer called `resolve_link`.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any

import frontmatter
import yaml

from librarian.log_config import get_logger

log = get_logger(__name__)


def fm(post: frontmatter.Post) -> dict[str, Any]:
    """A page's frontmatter as `dict[str, Any]`.

    python-frontmatter annotates `Post.get` and `Post.metadata` as `object`, which makes every
    `post.get("tags") or []` a type error. The values are whatever YAML held; callers validate.
    """
    return post.metadata


def page_tags(meta: Mapping[str, object]) -> list[str]:
    """`tags:` as a list of strings: absent or empty is `[]`, a bare string is one tag."""
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        return [tags]
    return [str(t) for t in tags]  # type: ignore[attr-defined]


def parse_frontmatter(text: str) -> dict[str, Any]:
    """A page's frontmatter in the shapes the index and listings rely on; `{}` if unparseable.

    The one text-to-metadata parser for wiki pages and lessons. `tags` is always a list of
    strings and every other value a string, because `updated` parses as `datetime.date` and
    would leak into a DuckDB insert. Callers that need the raw YAML values (graph, relinker,
    telemetry) read `frontmatter.load` themselves and share `page_tags`/`page_aliases` here.
    A hand-rolled line parser once dropped block-list tags (`tags:\\n  - rag`), indexing those
    pages with zero tags.
    """
    try:
        meta = dict(fm(frontmatter.loads(text)))
    except Exception as exc:
        # `{}` has no `tags` key, unlike a page with no frontmatter: callers that index can tell.
        log.warning("frontmatter_unparseable", error=str(exc))
        return {}
    meta["tags"] = page_tags(meta)
    for key, val in meta.items():
        if key != "tags" and not isinstance(val, str):
            meta[key] = "" if val is None else str(val)
    return meta


_FENCE_RE = re.compile(r"^[ \t]*(```|~~~).*?(?:^[ \t]*\1[^\n]*$|\Z)", re.MULTILINE | re.DOTALL)
_BARE_WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")


def _blank_fences(text: str) -> str:
    """`text` with fenced code blocks blanked to spaces; offsets and line numbers are unchanged."""
    return _FENCE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


class _WikilinkPattern:
    """`[[Page]]` links outside fenced code blocks and not `![[embeds]]`.

    Quacks like the compiled pattern for the two methods callers use (`finditer`, `search`);
    match offsets refer to the original text.
    """

    def finditer(self, text: str) -> Iterator[re.Match[str]]:
        return _BARE_WIKILINK_RE.finditer(
            _blank_fences(text) if "```" in text or "~~~" in text else text
        )

    def search(self, text: str) -> re.Match[str] | None:
        return next(self.finditer(text), None)


WIKILINK_RE = _WikilinkPattern()
# `- [[X]] — type` describes X relative to the page it is written on: "X is a
# prerequisite for this page", "X extends this page". `related` is the weak,
# undirected type: a real edge, but not one retrieval expansion walks.
CANONICAL_LINK_TYPES = frozenset(
    {
        "extends",
        "prerequisite-for",
        "alternative-to",
        "instance-of",
        "contradicts",
        "supersedes",
        "related",
    }
)
# Built from the set so the two cannot drift; the lookahead stops `related` from
# matching the start of a longer token.
TYPED_LINK_RE = re.compile(
    r"-\s*\[\[([^\]]+)\]\]\s*—\s*"
    r"(" + "|".join(sorted(CANONICAL_LINK_TYPES)) + r")(?![\w-])"
)
# Open type capture — matches the same anchored syntax with *any* type token, so
# annotations whose type is not canonical can be censused instead of silently
# dropped (they render identically in Obsidian either way).
ANY_TYPED_LINK_RE = re.compile(r"-\s*\[\[([^\]]+)\]\]\s*—\s*([a-z][a-z0-9-]*)")

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Normalise a title, wikilink target, or filename stem to a comparable slug.

    Any run of non-alphanumerics collapses to a single hyphen, so punctuated
    titles and their kebab-case file stems land on the same key. Non-ASCII
    letters are dropped, not transliterated — "Café" → "caf".
    """
    return _SLUG_RE.sub("-", text.lower()).strip("-")


def page_aliases(meta: Mapping[str, object]) -> list[str]:
    """Former names from a page's `aliases:` frontmatter, the key Obsidian also reads.

    Every resolver registers these last, after stems and titles, so a page's current name
    always beats another page's old one.
    """
    aliases = meta.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]
    return [str(a) for a in aliases] if isinstance(aliases, list) else []


def text_aliases(text: str) -> list[str]:
    """`page_aliases` for callers holding a page's raw text. Almost no page has any, so skip YAML."""
    if "aliases:" not in text:
        return []
    try:
        return page_aliases(frontmatter.loads(text).metadata)
    except (yaml.YAMLError, ValueError):
        return []


# ── Wikilink resolution ──────────────────────────────────────────────────────
# The one place a `[[Target]]` becomes a page. The graph UI, the search index's link table,
# graph expansion, the relinker, health stats, lint, rename and the course catalog all call
# `resolve_link`, so they count the same edges.

_SEE_ALSO_PREFIX_RE = re.compile(r"^see also:\s*", re.IGNORECASE)


def link_name(raw: str) -> str:
    """The page name a link spells: no `See also:` prefix, `|display` or `#heading`."""
    name = _SEE_ALSO_PREFIX_RE.sub("", raw.strip())
    return name.split("|", 1)[0].split("#", 1)[0].strip()


@dataclass(frozen=True)
class LinkEntry:
    """One page as the resolver sees it. `key` is whatever the caller wants back (a path, a
    relative path, a stem); `path` only fixes the order collisions are settled in."""

    key: str
    path: str
    stem: str
    title: str
    aliases: tuple[str, ...] = ()
    tombstone: bool = False
    private: bool = False


@dataclass(frozen=True)
class LinkCollision:
    """Two or more pages claiming one link name at the same rank. `keys[0]` is who wins."""

    kind: str  # "stem" | "title" | "alias"
    slug: str
    keys: tuple[str, ...]
    scope: str = "live"  # "live" | "tombstone" | "private": collisions never cross scopes


class _Group:
    """Name tables for one class of pages. Within a table the first page in path order wins."""

    def __init__(self) -> None:
        self.exact_stem: dict[str, str] = {}
        self.stem: dict[str, str] = {}
        self.title: dict[str, str] = {}
        self.alias: dict[str, str] = {}
        self.claims: dict[tuple[str, str], list[str]] = {}

    def add(self, entry: LinkEntry) -> None:
        self.exact_stem.setdefault(entry.stem, entry.key)
        self._claim("stem", self.stem, slugify(entry.stem), entry.key)
        self._claim("title", self.title, slugify(entry.title), entry.key)
        for alias in entry.aliases:
            self._claim("alias", self.alias, slugify(alias), entry.key)

    def _claim(self, kind: str, table: dict[str, str], slug: str, key: str) -> None:
        if not slug:
            return
        table.setdefault(slug, key)
        keys = self.claims.setdefault((kind, slug), [])
        if key not in keys:
            keys.append(key)

    def lookup(self, name: str, slug: str) -> str | None:
        # Rank: a page's current name beats another page's old one (aliases last).
        if (hit := self.exact_stem.get(name)) is not None:
            return hit
        for table in (self.stem, self.title, self.alias):
            if (hit := table.get(slug)) is not None:
                return hit
        return None


class LinkIndex:
    """Link names for a set of pages, built once.

    Rank, highest first: exact file stem, slugified stem, title, alias (case-insensitive,
    punctuation-insensitive through `slugify`). Pages are visited in sorted `path` order and the
    first to claim a name keeps it; every later claim at the same rank is recorded in
    `collisions` so lint can warn. Live public pages, then tombstones, then private pages are
    searched in that order, so a retired or private page never shadows a live one.
    """

    def __init__(self, entries: Iterable[LinkEntry]) -> None:
        self.entries: dict[str, LinkEntry] = {}
        self._live, self._tombstones, self._private = _Group(), _Group(), _Group()
        for entry in sorted(entries, key=lambda e: (e.path, e.key)):
            if entry.stem.startswith("_"):
                continue  # _index.md and friends are not link targets
            self.entries[entry.key] = entry
            group = (
                self._private
                if entry.private
                else self._tombstones
                if entry.tombstone
                else self._live
            )
            group.add(entry)
        self.collisions: tuple[LinkCollision, ...] = tuple(
            LinkCollision(kind, slug, tuple(keys), scope)
            for scope, group in (
                ("live", self._live),
                ("tombstone", self._tombstones),
                ("private", self._private),
            )
            for (kind, slug), keys in sorted(group.claims.items())
            if len(keys) > 1
        )

    def groups(
        self,
        *,
        include_private: bool,
        include_tombstones: bool,
        private_first: bool,
        only_private: bool,
    ) -> list[_Group]:
        if only_private:
            return [self._private]
        order = [self._live]
        if include_tombstones:
            order.append(self._tombstones)
        if include_private:
            if private_first:
                order.insert(0, self._private)
            else:
                order.append(self._private)
        return order


def resolve_link(
    target: str,
    index: LinkIndex,
    *,
    include_private: bool = False,
    include_tombstones: bool = False,
    private_first: bool = False,
    only_private: bool = False,
) -> str | None:
    """The `key` of the page `[[target]]` names, or None.

    `|display` and `#heading` are ignored, so are a `See also:` prefix and a folder path
    (`rag/some-page.md`): the whole name is tried first, since titles may contain a slash
    ("Bayesian A/B Testing"), then its last segment. Public consumers (the default) never
    resolve into private pages; the leak check passes `include_private`, and a link from
    inside `private/` passes `private_first`. Tombstones resolve only on request: a link to
    one is not dead, but it is not an edge either.
    """
    name = link_name(target)
    if not name:
        return None
    groups = index.groups(
        include_private=include_private,
        include_tombstones=include_tombstones,
        private_first=private_first,
        only_private=only_private,
    )
    candidates = [name]
    if "/" in name:
        candidates.append(name.rsplit("/", 1)[1].removesuffix(".md").strip())
    for candidate in candidates:
        slug = slugify(candidate)
        if not slug:
            continue
        for group in groups:
            if (hit := group.lookup(candidate, slug)) is not None:
                return hit
    return None
