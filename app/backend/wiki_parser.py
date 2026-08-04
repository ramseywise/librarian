from __future__ import annotations

from pathlib import Path

import frontmatter

from core.wiki_common import TYPED_LINK_RE, WIKILINK_RE

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


def _slug(title: str) -> str:
    return title.lower().strip().replace(" ", "-")


def parse_wiki() -> dict:
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
        page_slugs[_slug(title)] = title

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
                    "summary": post.get("summary") or "",
                    "updated": str(post.get("updated") or ""),
                    "path": str(md_file.relative_to(WIKI_DIR)),
                    "dimmed": False,
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
            link_target = _slug(match.group(1).strip())
            typed_links[link_target] = match.group(2)

        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            target_id = _slug(raw) if _slug(raw) in node_ids else raw.lower().replace(" ", "-")
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

    # Tag-shared edges: cross-domain pages sharing ≥1 frontmatter domain tag.
    # Skip same-directory pairs — intra-domain proximity is already captured by UMAP clustering.
    tag_map: dict[str, set[str]] = {}
    dir_map: dict[str, str] = {}
    domain_tags = _domain_tag_set()
    for n in nodes:
        tag_map[n["id"]] = {t for t in n["data"]["tags"] if t in domain_tags}
        dir_map[n["id"]] = n["data"]["domain"][0]

    node_list = list(node_ids)
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            a, b = node_list[i], node_list[j]
            if dir_map.get(a) == dir_map.get(b):
                continue
            shared = tag_map.get(a, set()) & tag_map.get(b, set())
            if len(shared) >= 1:
                edges.append(
                    {
                        "id": f"ts:{a}->{b}",
                        "source": a,
                        "target": b,
                        "data": {"edgeType": "tag-shared", "sharedTags": list(shared)},
                    }
                )

    return {"nodes": nodes, "edges": edges}
