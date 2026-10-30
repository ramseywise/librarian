from __future__ import annotations

from pathlib import Path

import frontmatter

from core.wiki_common import TYPED_LINK_RE, WIKILINK_RE, slugify

WIKI_DIR = Path(__file__).parent.parent.parent / "data" / "wiki"
RELATIONSHIP_TYPES = {
    "extends",
    "prerequisite-for",
    "alternative-to",
    "instance-of",
    "contradicts",
    "supersedes",
}

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


def parse_wiki() -> dict:
    """Graph payload for /ws `graph_update` and GET /api/graph: {nodes, edges, domains}.

    `edges` are wikilink edges only. Tag-shared edges (~42k pairs, ~10 MB of JSON on the
    real wiki) are derived client-side by app/frontend/src/utils/tagEdges.ts from each
    node's `data.tags` and `domains`; tag_shared_edges() below is the same rule, used by
    `/api/graph?edges=all`. `domains` is the disk-derived domain list, sorted, without
    `private`.

    Private pages (data/wiki/private/) ARE included, flagged `data.private = True`:
    decision D1 (2026-10-30) keeps them visible in the local graph UI with a badge. The
    courses API and MCP search still exclude them.
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    page_slugs: dict[str, str] = {}  # slug -> title

    # First pass: collect all pages
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        post = frontmatter.load(md_file)
        title = post.get("title") or md_file.stem
        page_id = md_file.stem
        tags = post.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]

        page_slugs[page_id] = title
        # also register by title slug so wikilinks resolve
        page_slugs[slugify(title)] = title

        domain = [md_file.parent.name]
        is_private = md_file.relative_to(WIKI_DIR).parts[0] == "private"
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
                    "summary": post.get("summary") or "",
                    "updated": str(post.get("updated") or ""),
                    "path": str(md_file.relative_to(WIKI_DIR)),
                    "dimmed": False,
                    "private": is_private,
                },
                "position": {"x": 0, "y": 0},
            }
        )

    node_ids = {n["id"] for n in nodes}

    # Second pass: extract wikilinks → edges (with optional relationship types)
    seen_edges: set[tuple[str, str]] = set()
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        source_id = md_file.stem
        content = md_file.read_text()

        # Extract typed relationships from See Also sections
        typed_links: dict[str, str] = {}
        for match in TYPED_LINK_RE.finditer(content):
            link_target = slugify(match.group(1).strip())
            typed_links[link_target] = match.group(2)

        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            target_id = slugify(raw)
            if target_id not in node_ids or target_id == source_id:
                continue
            key = (source_id, target_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edge_data: dict = {"edgeType": "wikilink"}
            if target_id in typed_links:
                edge_data["relationship"] = typed_links[target_id]
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

    Mirrors app/frontend/src/utils/tagEdges.ts exactly (keep the two in agreement): the
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
