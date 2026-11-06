from __future__ import annotations

from pathlib import Path

import frontmatter
import yaml

from librarian.config import get_settings
from librarian.log_config import get_logger
from librarian.wiki.common import (
    CANONICAL_LINK_TYPES,
    TYPED_LINK_RE,
    WIKILINK_RE,
    fm,
    page_aliases,
    slugify,
)

log = get_logger(__name__)

WIKI_DIR = get_settings().wiki_dir
RELATIONSHIP_TYPES = CANONICAL_LINK_TYPES

TYPE_TAGS = {"concept", "pattern", "decision", "project", "comparison", "reference", "conflict"}


def _domain_tag_set() -> set[str]:
    """Domain tags derived from disk: directories under data/wiki/, minus private/.

    Same derivation as the MCP server's _domains() — replaces a hardcoded set that
    had drifted (phantom deep-agents entry). Read at call time so tests can repoint
    WIKI_DIR.
    """
    if not WIKI_DIR.is_dir():
        return set()
    return {d.name for d in WIKI_DIR.iterdir() if d.is_dir() and d.name != "private"}


def _public_pages() -> list[Path]:
    """Wiki pages the graph UI may show: not `_`-prefixed, not under data/wiki/private/."""
    return sorted(
        f
        for f in WIKI_DIR.rglob("*.md")
        if not f.name.startswith("_") and f.relative_to(WIKI_DIR).parts[0] != "private"
    )


def public_page_ids() -> set[str]:
    """Node ids parse_wiki() emits. Semantic edges and UMAP positions are computed over
    every page (private and tombstoned included, see librarian/retrieval/embeddings.py), so their endpoints
    filter to this set before anything reaches the browser."""
    return {n["id"] for n in parse_wiki()["nodes"]}


def public_page_domains() -> dict[str, str]:
    """Node id → its directory, the same `data.domain[0]` parse_wiki() emits."""
    return {n["id"]: n["data"]["domain"][0] for n in parse_wiki()["nodes"]}


# Last parse and the file signature it was built from. Every page load asks twice (/api/graph
# and /ws), and during the catalog warmup a parse competes for the GIL and takes seconds.
_parsed: tuple[tuple, dict] | None = None


def parse_wiki() -> dict:
    """parse_wiki_uncached(), reused while no page has changed. Callers get their own top-level
    dict, so swapping `edges` is safe, but nodes and edges are shared: don't mutate them."""
    global _parsed
    signature = tuple((str(f), *_stat_key(f)) for f in _public_pages())
    if _parsed is None or _parsed[0] != signature:
        _parsed = (signature, parse_wiki_uncached())
    return dict(_parsed[1])


def _stat_key(f: Path) -> tuple[int, int]:
    st = f.stat()
    return st.st_mtime_ns, st.st_size


def parse_wiki_uncached() -> dict:
    """Graph payload for /ws `graph_update` and GET /api/graph: {nodes, edges, domains}.

    `edges` are wikilink edges only. Tag-shared edges (~42k pairs, ~10 MB of JSON on the
    real wiki) are derived client-side by apps/web/src/utils/tagEdges.ts from each
    node's `data.tags` and `domains`; tag_shared_edges() below is the same rule, used by
    `/api/graph?edges=all`. `domains` is the disk-derived domain list, sorted, without
    `private`.

    Private pages (data/wiki/private/) are excluded — neither nodes nor wikilink sources.
    This reverses decision D1 (2026-10-30), which showed them with a badge: client and
    company pages must not appear in the graph UI at all, matching the courses API and
    MCP search. Tombstones are excluded too, as they are from search.
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    page_slugs: dict[str, str] = {}  # slug -> title
    aliases_to_id: dict[str, str] = {}  # slug of a former name -> current page id

    # First pass: collect all pages
    pages = _public_pages()
    for md_file in pages:
        # One bad page must not take the graph down: this runs in the /ws watcher too, and an
        # exception there ends live updates until restart.
        try:
            post = frontmatter.load(md_file)
        except yaml.YAMLError as e:
            log.error("wiki_page_skipped", page=md_file.name, error=str(e).splitlines()[0])
            continue
        title = fm(post).get("title") or md_file.stem
        page_id = md_file.stem
        tags = fm(post).get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        # Retired pages stay on disk so inbound links resolve, but aren't part of the map.
        if "tombstone" in tags:
            continue

        page_slugs[page_id] = title
        # also register by title slug so wikilinks resolve
        page_slugs[slugify(title)] = title
        aliases_to_id.update({slugify(alias): page_id for alias in page_aliases(post.metadata)})

        domain = [md_file.parent.name]
        type_tag = next((t for t in tags if t in TYPE_TAGS), "concept")

        nodes.append(
            {
                "id": page_id,
                "type": "wikiNode",
                "data": {
                    "title": title,
                    "tags": tags,
                    "domain": domain,
                    "typeTag": type_tag,
                    "summary": fm(post).get("summary") or "",
                    "updated": str(fm(post).get("updated") or ""),
                    "path": str(md_file.relative_to(WIKI_DIR)),
                    "dimmed": False,
                },
                "position": {"x": 0, "y": 0},
            }
        )

    node_ids = {n["id"] for n in nodes}

    # Second pass: extract wikilinks → edges (with optional relationship types)
    seen_edges: set[tuple[str, str]] = set()
    for md_file in pages:
        source_id = md_file.stem
        if source_id not in node_ids:
            continue
        content = md_file.read_text()

        # Extract typed relationships from See Also sections
        typed_links: dict[str, str] = {}
        for match in TYPED_LINK_RE.finditer(content):
            link_target = slugify(match.group(1).strip())
            typed_links[link_target] = match.group(2)

        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            target_slug = slugify(raw)
            target_id = target_slug if target_slug in node_ids else aliases_to_id.get(target_slug)
            if target_id is None or target_id not in node_ids or target_id == source_id:
                continue
            key = (source_id, target_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edge_data: dict = {"edgeType": "wikilink"}
            if target_slug in typed_links:
                edge_data["relationship"] = typed_links[target_slug]
            edges.append(
                {
                    "id": f"wl:{source_id}->{target_id}",
                    "source": source_id,
                    "target": target_id,
                    "data": edge_data,
                }
            )

    return {"nodes": nodes, "edges": edges, "domains": sorted(_domain_tag_set())}


def tag_shared_edges(nodes: list[dict], domains: list[str] | set[str]) -> list[dict]:
    """Edges between pages in different directories that share >= 1 domain tag.

    Mirrors apps/web/src/utils/tagEdges.ts exactly (keep the two in agreement): the
    directory is `data.domain[0]`, only tags in `domains` count, ids are `ts:<a>-><b>`
    with a < b, `sharedTags` is sorted. Same-directory pairs are skipped — intra-domain
    proximity is already captured by UMAP clustering. Grouped by tag, so the cost is the
    sum of squared tag-group sizes rather than every node pair.
    """
    domain_set = set(domains)
    dir_of: dict[str, str] = {}
    tags_of: dict[str, set[str]] = {}
    by_tag: dict[str, list[str]] = {}
    for n in nodes:
        nid = n["id"]
        dir_of[nid] = (n["data"].get("domain") or [""])[0]
        tags = {t for t in n["data"].get("tags") or [] if t in domain_set}
        tags_of[nid] = tags
        for t in tags:
            by_tag.setdefault(t, []).append(nid)

    seen: set[str] = set()
    edges: list[dict] = []
    for ids in by_tag.values():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = sorted((ids[i], ids[j]))
                if dir_of[a] == dir_of[b]:
                    continue
                eid = f"ts:{a}->{b}"
                if eid in seen:
                    continue
                seen.add(eid)
                edges.append(
                    {
                        "id": eid,
                        "source": a,
                        "target": b,
                        "data": {
                            "edgeType": "tag-shared",
                            "sharedTags": sorted(tags_of[a] & tags_of[b]),
                        },
                    }
                )
    return edges
