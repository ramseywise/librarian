from __future__ import annotations

import re
from pathlib import Path

import frontmatter

WIKI_DIR = Path(__file__).parent.parent.parent / "wiki"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")

DOMAIN_TAGS = {
    "langgraph", "rag", "adk", "mcp", "memory", "voice",
    "eval", "infra", "llm", "deep-agents", "context-management",
}
TYPE_TAGS = {"concept", "pattern", "decision", "project", "comparison", "reference", "conflict"}


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

        domain = [t for t in tags if t in DOMAIN_TAGS]
        type_tag = next((t for t in tags if t in TYPE_TAGS), "concept")

        nodes.append({
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
        })

    node_ids = {n["id"] for n in nodes}

    # Second pass: extract wikilinks → edges
    seen_edges: set[tuple[str, str]] = set()
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        source_id = md_file.stem
        content = md_file.read_text()
        for match in WIKILINK_RE.finditer(content):
            raw = match.group(1).strip()
            target_id = _slug(raw) if _slug(raw) in node_ids else raw.lower().replace(" ", "-")
            if target_id not in node_ids or target_id == source_id:
                continue
            key = (source_id, target_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({
                "id": f"wl:{source_id}->{target_id}",
                "source": source_id,
                "target": target_id,
                "data": {"edgeType": "wikilink"},
            })

    # Tag-shared edges: pages sharing ≥2 domain tags
    tag_map: dict[str, set[str]] = {}
    for n in nodes:
        tag_map[n["id"]] = set(n["data"]["domain"])

    node_list = list(node_ids)
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            a, b = node_list[i], node_list[j]
            shared = tag_map.get(a, set()) & tag_map.get(b, set())
            if len(shared) >= 2:
                edges.append({
                    "id": f"ts:{a}->{b}",
                    "source": a,
                    "target": b,
                    "data": {"edgeType": "tag-shared", "sharedTags": list(shared)},
                })

    return {"nodes": nodes, "edges": edges}
