"""Shared wiki-markup patterns — the single definition site (LIB-110 Phase B).

WIKILINK_RE, TYPED_LINK_RE, and slugify were previously defined per-module in
wiki_parser, retrieval, relinker, and graph_expansion; they must stay
identical or link resolution diverges between the index and the UI.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import frontmatter
import yaml


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
    except Exception:
        return {}
    meta["tags"] = page_tags(meta)
    for key, val in meta.items():
        if key != "tags" and not isinstance(val, str):
            meta[key] = "" if val is None else str(val)
    return meta


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")
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
