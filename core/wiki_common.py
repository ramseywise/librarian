"""Shared wiki-markup patterns — the single definition site (LIB-110 Phase B).

WIKILINK_RE and TYPED_LINK_RE were previously defined verbatim in wiki_parser,
the MCP server, relinker, and graph_expansion; they must stay identical or link
resolution diverges between the index and the UI.
"""

from __future__ import annotations

import re

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")
TYPED_LINK_RE = re.compile(
    r"-\s*\[\[([^\]]+)\]\]\s*—\s*"
    r"(extends|prerequisite-for|alternative-to|instance-of|contradicts|supersedes)"
)
