"""Shared wiki-markup patterns — the single definition site (LIB-110 Phase B).

WIKILINK_RE, TYPED_LINK_RE, and slugify were previously defined per-module in
wiki_parser, the MCP server, relinker, and graph_expansion; they must stay
identical or link resolution diverges between the index and the UI.
"""

from __future__ import annotations

import re

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")
TYPED_LINK_RE = re.compile(
    r"-\s*\[\[([^\]]+)\]\]\s*—\s*"
    r"(extends|prerequisite-for|alternative-to|instance-of|contradicts|supersedes)"
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Normalise a title, wikilink target, or filename stem to a comparable slug.

    Any run of non-alphanumerics collapses to a single hyphen, so punctuated
    titles and their kebab-case file stems land on the same key. Non-ASCII
    letters are dropped, not transliterated — "Café" → "caf".
    """
    return _SLUG_RE.sub("-", text.lower()).strip("-")
