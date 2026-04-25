"""Streamlit wiki graph visualizer — powered by Cytoscape.js via st-cytoscape.

Run: uv run streamlit run scripts/visualize.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import frontmatter
import streamlit as st
from st_cytoscape import cytoscape

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

DOMAIN_TAGS = [
    "adk", "langgraph", "rag", "memory", "mcp", "voice",
    "eval", "infra", "llm", "deep-agents", "context-management",
]

TAG_COLORS = {
    "adk": "#4285F4",
    "langgraph": "#34A853",
    "rag": "#EA4335",
    "memory": "#9C27B0",
    "mcp": "#FF6D00",
    "voice": "#00BCD4",
    "eval": "#F9A825",
    "infra": "#607D8B",
    "llm": "#795548",
    "deep-agents": "#E91E63",
    "context-management": "#009688",
    "other": "#9E9E9E",
}

CYTO_SHAPES = {
    "concept": "ellipse",
    "pattern": "diamond",
    "decision": "rectangle",
    "project": "star",
    "comparison": "triangle",
    "reference": "pentagon",
}

STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "data(color)",
            "shape": "data(shape)",
            "width": "data(size)",
            "height": "data(size)",
            "font-size": "11px",
            "color": "#ffffff",
            "text-valign": "center",
            "text-halign": "center",
            "text-wrap": "wrap",
            "text-max-width": "85px",
            "text-outline-color": "#111111",
            "text-outline-width": "1px",
        },
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#888888",
            "line-color": "#444444",
            "opacity": 0.5,
            "width": 1,
        },
    },
    {
        "selector": "node:selected",
        "style": {
            "border-width": "3px",
            "border-color": "#ffffff",
        },
    },
    {
        "selector": "edge:selected",
        "style": {"line-color": "#ffffff", "opacity": 1.0},
    },
]

LAYOUT = {
    "name": "cose",
    "animate": False,
    "randomize": False,
    "nodeRepulsion": 12000,
    "idealEdgeLength": 100,
    "gravity": 0.2,
    "numIter": 1000,
}


def load_wiki_pages() -> list[dict]:
    pages = []
    for f in WIKI_DIR.rglob("*.md"):
        if f.name.startswith("_"):
            continue
        post = frontmatter.load(f)
        tags = post.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        domain = next((t for t in tags if t in DOMAIN_TAGS), "other")
        page_type = next((t for t in tags if t in CYTO_SHAPES), "concept")
        wikilinks = re.findall(r"\[\[([^\]]+)\]\]", post.content)
        pages.append({
            "file": f,
            "rel": str(f.relative_to(WIKI_DIR)),
            "title": post.get("title", f.stem),
            "summary": post.get("summary", ""),
            "tags": tags,
            "domain": domain,
            "type": page_type,
            "updated": str(post.get("updated", "")),
            "sources": post.get("sources", []),
            "wikilinks": [w for w in wikilinks if not w.startswith("_")],
        })
    return pages


def load_manifest() -> dict[str, dict]:
    manifest_path = REPO_ROOT / "raw" / "manifest.jsonl"
    if not manifest_path.exists():
        return {}
    entries = {}
    for line in manifest_path.read_text().splitlines():
        line = line.strip()
        if line:
            e = json.loads(line)
            entries[e["path"]] = e
    return entries


def build_elements(
    pages: list[dict],
    selected_tags: list[str],
    selected_types: list[str],
) -> list[dict]:
    filtered = [
        p for p in pages
        if (not selected_tags or any(t in selected_tags for t in p["tags"]))
        and (not selected_types or p["type"] in selected_types)
    ]
    filtered_titles = {p["title"] for p in filtered}

    in_degree: dict[str, int] = {p["title"]: 0 for p in filtered}
    for p in filtered:
        for link in p["wikilinks"]:
            if link in in_degree:
                in_degree[link] += 1

    elements: list[dict] = []

    for p in filtered:
        degree = in_degree[p["title"]] + len([l for l in p["wikilinks"] if l in filtered_titles])
        size = max(25, min(75, 25 + degree * 5))
        elements.append({
            "data": {
                "id": p["title"],
                "label": p["title"],
                "color": TAG_COLORS.get(p["domain"], "#9E9E9E"),
                "shape": CYTO_SHAPES.get(p["type"], "ellipse"),
                "size": size,
                "summary": p["summary"],
                "tags": ", ".join(p["tags"]),
                "type": p["type"],
                "domain": p["domain"],
                "updated": p["updated"],
                "title": p["summary"] or p["title"],
            }
        })

    seen: set[str] = set()
    for p in filtered:
        for link in p["wikilinks"]:
            if link in filtered_titles and link != p["title"]:
                edge_id = f"{p['title']}||{link}"
                if edge_id not in seen:
                    elements.append({"data": {"source": p["title"], "target": link}})
                    seen.add(edge_id)

    return elements


def main() -> None:
    st.set_page_config(page_title="Librarian Wiki", page_icon="📚", layout="wide")
    st.title("📚 Librarian Wiki Graph")

    pages = load_wiki_pages()
    manifest = load_manifest()

    st.sidebar.header("Filters")
    all_domain_tags = sorted({t for p in pages for t in p["tags"] if t in DOMAIN_TAGS})
    selected_tags = st.sidebar.multiselect("Domain", all_domain_tags, default=[])
    all_types = sorted({p["type"] for p in pages})
    selected_types = st.sidebar.multiselect("Type", all_types, default=[])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Wiki pages", len(pages))
    col2.metric("Ingested sources", len(manifest))
    raw_files = list((REPO_ROOT / "raw").rglob("*.md"))
    pending = len([f for f in raw_files if str(f.relative_to(REPO_ROOT)) not in manifest])
    col3.metric("Pending ingest", pending)
    col4.metric("Wikilinks", sum(len(p["wikilinks"]) for p in pages))

    st.markdown("---")

    tab_graph, tab_pages, tab_coverage = st.tabs(["Graph", "Pages", "Coverage gaps"])

    with tab_graph:
        elements = build_elements(pages, selected_tags, selected_types)
        node_count = sum(1 for e in elements if "source" not in e["data"])

        if node_count == 0:
            st.info("No pages match the selected filters.")
        else:
            selected = cytoscape(elements, STYLESHEET, layout=LAYOUT, height="640px", key="wiki_graph")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    "**Domains:** " + "  ".join(
                        f'<span style="background:{TAG_COLORS[t]};padding:2px 6px;border-radius:3px;'
                        f'color:white;font-size:11px">{t}</span>'
                        for t in all_domain_tags if t in TAG_COLORS
                    ),
                    unsafe_allow_html=True,
                )
            with col_b:
                st.caption("Shapes: ● concept  ◆ pattern  ■ decision  ★ project  ▲ comparison")

            if selected and selected.get("nodes"):
                node_id = selected["nodes"][0]
                page = next((p for p in pages if p["title"] == node_id), None)
                if page:
                    st.markdown("---")
                    st.subheader(page["title"])
                    st.write(page["summary"])
                    st.caption(f"Tags: {', '.join(page['tags'])}  |  Updated: {page['updated']}")
                    if page["sources"]:
                        st.caption(f"Sources: {', '.join(page['sources'])}")
                    if page["wikilinks"]:
                        st.caption(f"Links to: {', '.join(page['wikilinks'])}")

    with tab_pages:
        search = st.text_input("Search pages", placeholder="rag, langgraph, pattern...")
        for p in sorted(pages, key=lambda x: x["title"]):
            if selected_tags and not any(t in selected_tags for t in p["tags"]):
                continue
            if selected_types and p["type"] not in selected_types:
                continue
            if search and search.lower() not in p["title"].lower() and search.lower() not in " ".join(p["tags"]):
                continue
            with st.expander(f"**{p['title']}** — {p['domain']} · {p['type']}"):
                st.write(p["summary"])
                st.caption(f"Tags: {', '.join(p['tags'])}  |  Updated: {p['updated']}")
                if p["sources"]:
                    st.caption(f"Sources: {', '.join(p['sources'])}")
                if p["wikilinks"]:
                    st.caption(f"Links to: {', '.join(p['wikilinks'])}")

    with tab_coverage:
        st.subheader("Raw files pending ingest")
        st.caption("Files in raw/ with no manifest entry. Grouped by directory.")

        raw_root = REPO_ROOT / "raw"
        pending_files = [
            f for f in sorted(raw_root.rglob("*.md"))
            if str(f.relative_to(REPO_ROOT)) not in manifest
        ]

        by_dir: dict[str, list] = {}
        for f in pending_files:
            parts = f.relative_to(raw_root).parts
            top = parts[0] if len(parts) > 1 else "root"
            by_dir.setdefault(top, []).append(f)

        skip_dirs = {"sessions"}
        for dir_name, files in sorted(by_dir.items()):
            label = f"~~{dir_name}~~ (skipped)" if dir_name in skip_dirs else dir_name
            with st.expander(f"{label}  ({len(files)} files)"):
                for f in files:
                    kb = round(f.stat().st_size / 1024, 1)
                    st.text(f"  {f.relative_to(raw_root)}  ({kb} KB)")

        if manifest:
            st.subheader("Ingested sources")
            for path, entry in sorted(manifest.items()):
                pages_touched = entry.get("wiki_pages", [])
                st.text(f"✓  {path}  →  {len(pages_touched)} wiki page(s)  [{entry['ingested_at']}]")


if __name__ == "__main__":
    main()
