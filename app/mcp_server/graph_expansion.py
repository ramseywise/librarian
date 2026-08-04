"""One-hop retrieval expansion along typed wikilink relationships.

SPIKE — measures whether the wiki's typed `## See Also` annotations are dense
enough to be worth querying at retrieval time.

The wiki has two kinds of edge and they behave very differently:

    total wikilink edges   6887   (~24 per page — mentions, prose links, index rows)
    typed relationship     543    (7%; `— extends`, `— prerequisite-for`, ...)

Expanding along *all* edges would drown a context window: at 24 neighbours per
hit, a 10-result search becomes a 240-page neighbourhood. The typed subgraph is
the opposite shape — sparse, author-asserted, and still covering 189 of 281
pages at a median out-degree of 2. That is the layer worth traversing.

We expand along `prerequisite-for` and `extends` only (375 of the 543 typed
edges). Both are *directional dependencies*: they answer "what must I also know
to make sense of this hit?" `alternative-to` and `contradicts` are deliberately
excluded — they are genuinely useful to a reader but they pull in competing
approaches, which is noise when the caller asked about one thing.
"""

from __future__ import annotations

import re
from pathlib import Path

from core.wiki_common import TYPED_LINK_RE

# The two relationship types that express "you need this to understand that".
EXPANSION_RELATIONSHIPS = frozenset({"prerequisite-for", "extends"})

# How to describe an edge walked against its written direction. CLAUDE.md defines
# `prerequisite-for` as "must understand this before the target", so arriving at
# the *source* from the target means the source is what builds on the seed.
INVERSE_LABEL = {
    "prerequisite-for": "builds-on",
    "extends": "extended-by",
}


def _slug(text: str) -> str:
    """Normalise a title or filename stem to a comparable slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_typed_edges(pages: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Extract typed relationship edges from page bodies.

    Args:
        pages: (path, title, content) triples for every indexed page.

    Returns:
        (source_path, target_path, relationship) triples. Links that do not
        resolve to an indexed page are dropped — a dead wikilink is a lint
        error, not something retrieval should try to follow.
    """
    slug_to_path: dict[str, str] = {}
    for path, title, _ in pages:
        slug_to_path[_slug(title)] = path
        slug_to_path[_slug(Path(path).stem)] = path

    edges: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for path, _, content in pages:
        for match in TYPED_LINK_RE.finditer(content):
            target = slug_to_path.get(_slug(match.group(1).strip()))
            if not target or target == path:
                continue
            edge = (path, target, match.group(2))
            if edge not in seen:
                seen.add(edge)
                edges.append(edge)
    return edges


def expand_one_hop(
    seed_paths: list[str],
    edges: list[tuple[str, str, str]],
    max_expansions: int = 5,
) -> list[tuple[str, str, str]]:
    """Find pages one typed hop from the seeds.

    Traversal is bidirectional by design. `prerequisite-for` is written on the
    *dependent* page pointing back at its foundation ("[[Transformer
    Architecture]] — prerequisite-for"), so following it forward reaches
    foundations. But a seed that *is* a foundation should also surface the pages
    built on top of it, which means walking the same edge backwards. Both
    directions answer "what else does this hit depend on or get depended on by".

    Args:
        seed_paths:     Paths of the pages the primary search already returned.
        edges:          Typed edges from build_typed_edges().
        max_expansions: Cap on returned neighbours. Bounds the context cost —
                        without it a well-connected seed set can pull in dozens.

    Returns:
        (neighbour_path, relationship, seed_path) triples, ordered by how many
        distinct seeds reached each neighbour (descending). A page reached from
        several seeds is more likely to be genuinely central to the query than
        one reached from a single hit.
    """
    seeds = set(seed_paths)
    if not seeds:
        return []

    # neighbour -> (set of seeds that reached it, one representative edge)
    reached: dict[str, tuple[set[str], str, str]] = {}

    def record(neighbour: str, relationship: str, seed: str) -> None:
        if neighbour in seeds:
            return  # already returned by the primary search
        if neighbour in reached:
            reached[neighbour][0].add(seed)
        else:
            reached[neighbour] = ({seed}, relationship, seed)

    # Direction matters and the annotation is written from the *linking* page's
    # point of view. `[[RLHF Pipeline]] — prerequisite-for` on the LLM guide
    # means "RLHF Pipeline is a prerequisite for this page" — the edge points
    # source→target but the dependency runs target→source. Walking such an edge
    # backwards is still useful (a foundation should surface what builds on it),
    # but it must be *labelled* as the inverse or the caller reads the hierarchy
    # upside down.
    for source, target, relationship in edges:
        if relationship not in EXPANSION_RELATIONSHIPS:
            continue
        if source in seeds:
            record(target, relationship, source)
        if target in seeds:
            record(source, INVERSE_LABEL[relationship], target)

    ranked = sorted(reached.items(), key=lambda kv: (-len(kv[1][0]), kv[0]))
    return [(path, rel, seed) for path, (_, rel, seed) in ranked[:max_expansions]]
