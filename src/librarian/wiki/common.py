"""Shared wiki-markup patterns — the single definition site (LIB-110 Phase B).

WIKILINK_RE, TYPED_LINK_RE, and slugify were previously defined per-module in
wiki_parser, the MCP server, relinker, and graph_expansion; they must stay
identical or link resolution diverges between the index and the UI.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

import frontmatter
import yaml

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
