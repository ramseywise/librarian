# React Flow Wiki Graph Explorer — Plan

**Date:** 2026-04-24  
**Updated:** 2026-04-25  
**Status:** Ready to implement. Obsidian evaluation complete — gap is clear.  
**Effort:** ~3-4 days MVP (graph + multi-edge + UMAP), ~6-8 days full (agent chat + write-back)

---

## What We're Building

A local dev React app with two panels:
- **Left**: interactive knowledge graph (React Flow) — nodes = wiki pages, multiple configurable edge types, styled by frontmatter tags, layout switcher including UMAP semantic positioning
- **Right**: agent chat panel — ask a question, agent reads wiki, highlights relevant subgraph, proposes new wikilinks

The agent chat drives the visualization — query results highlight nodes, write-back adds wikilinks to markdown files on disk.

**Why not Obsidian:** Juggl evaluation confirmed it cannot do multi-dimensional edge toggling, embedding-based spatial layout, or agent-driven highlighting. That gap is exactly what this build covers.

---

## Stack (confirmed)

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | Vite + React + TypeScript | Fast dev, standard |
| Graph rendering | React Flow | Custom nodes by tag, `hidden` filtering, 200 nodes no problem |
| Layout: hierarchical | `dagre` | Top-down, good for project → concept → pattern hierarchy |
| Layout: organic | `d3-force` | Physics sim, nodes repel — good for exploration |
| Layout: semantic | `umap-js` + MiniLM embeddings | Position by semantic distance; clusters emerge without explicit edges |
| Frontmatter parser | `gray-matter` | Used by Gatsby/Astro, dead simple |
| Wikilink extractor | regex `\[\[([^\]]+)\]\]` | Sufficient at this scale, zero deps |
| File watcher | `chokidar` | Industry standard, Vite uses it internally |
| Embeddings | `all-MiniLM-L6-v2` (384-dim) via FastAPI | Already in stack; lightweight, fast |
| UMAP reduction | `umap-js` (browser) or `umap-learn` (Python, precomputed) | Precompute on backend, serve as node positions |
| Agent backend | FastAPI + LangGraph | Python matches existing stack |
| Agent streaming | SSE (Server-Sent Events) | Unidirectional streaming, simpler than WebSocket |
| Write-back | FastAPI POST → `fs.write` → chokidar | Backend writes, chokidar detects, WebSocket refreshes graph |
| Deployment | Local only (`vite dev`) | No infra needed |

---

## Architecture

```
wiki/*.md ──► chokidar watcher ──► parse (gray-matter + regex)
                                         │
                              ┌──────────┴──────────┐
                              │                     │
                         wikilink edges        FastAPI: embed all pages
                              │                MiniLM → UMAP → {x,y} coords
                              │                     │
                              └──────────┬──────────┘
                                         │
                              nodes[] + edges[] JSON
                              (with positions + edge types)
                                         │
                                    WebSocket push
                                         │
                                         ▼
React app ◄──────────────── React Flow graph (left panel)
    │                              │
    │ user query                   │ highlight subgraph
    ▼                              ▲
FastAPI /chat/stream ──SSE──► token events + highlight events
    │
LangGraph agent
    │ search_wiki, read_page
    ▼
wiki/*.md


Write-back flow:
Agent proposes [[NewLink]] → React shows diff preview → user approves
→ POST /api/writeback → FastAPI writes to .md file
→ chokidar detects → re-parses → WebSocket pushes updated graph
```

---

## Multi-Dimensional Edge Types

The key feature beyond Obsidian. Three edge types, each togglable independently:

| Edge Type | Source | Color | Default |
|---|---|---|---|
| `wikilink` | Explicit `[[...]]` in markdown | White/light | On |
| `semantic` | Cosine similarity > 0.65 threshold (MiniLM) | Blue, opacity by score | Off |
| `tag-shared` | Pages sharing ≥2 domain tags | Orange | Off |

Toggle panel (top-left): three checkboxes. Checking `semantic` adds soft blue edges between conceptually related pages even without wikilinks — surfaces implicit relationships. This is the "layer between" that Obsidian cannot provide.

---

## Layout Modes

Switcher in UI (dropdown or button group):

| Mode | Algorithm | Best For |
|---|---|---|
| `dagre` | Hierarchical top-down | Seeing project → decision → concept hierarchy |
| `d3-force` | Physics repulsion | Organic exploration, clusters emerge from link density |
| `umap-semantic` | MiniLM embeddings → UMAP → 2D | Position encodes semantic distance; no edges needed to see clusters |

**UMAP implementation:** precomputed on FastAPI backend (`POST /api/layout/umap`), returns `{page_id: {x, y}}` map. React Flow applies positions. Recompute when wiki changes (chokidar triggers). ~2-3 seconds for 50 pages.

---

## Agent SSE Event Schema

Three event types on the same stream:

```json
{ "type": "token", "content": "The CRAG retry loop..." }
{ "type": "highlight", "pages": ["CRAG Retry Logic", "RAG Reranking", "LangGraph CRAG Pipeline"] }
{ "type": "edge_suggest", "from": "RAG Reranking", "to": "CRAG Retry Logic", "reason": "..." }
```

- `token` → append to chat message
- `highlight` → `setNodes()` dims non-relevant nodes to `opacity: 0.2`
- `edge_suggest` → shows proposed new wikilink as dashed edge in graph (write-back candidate)

---

## MVP Phases

### Phase A — Graph + Multi-Edge + Layout Switcher (3-4 days)
- [ ] Scaffold: `npm create vite@latest librarian-ui -- --template react-ts`
- [ ] Data layer: `gray-matter` parser + wikilink regex → `{nodes, edges}` JSON
- [ ] React Flow: render nodes with zoom/pan/minimap
- [ ] Custom node component: color by domain tag, shape by type tag, title + summary on hover
- [ ] Layout: dagre for initial positions; d3-force switcher
- [ ] Tag filter panel: multiselect → toggle `hidden` on nodes/edges
- [ ] chokidar watcher: Express backend → WebSocket → hot-reload graph on wiki file change
- [ ] **Multi-edge toggle panel**: wikilink / semantic / tag-shared checkboxes
- [ ] **Semantic edges**: FastAPI endpoint embeds all pages with MiniLM, returns cosine sim matrix, React draws edges above threshold
- [ ] **UMAP layout**: FastAPI `/api/layout/umap` → node positions → React Flow applies

### Phase B — Agent chat (2-3 days)
- [ ] FastAPI backend: `/chat/stream` endpoint with SSE
- [ ] LangGraph agent: `search_wiki` + `read_page` tools reading from `wiki/`
- [ ] React chat panel: SSE consumer, token streaming display
- [ ] Graph highlighting: `type: highlight` events → `setNodes` dims non-relevant nodes
- [ ] "Why highlighted?" sidebar: click a highlighted node → agent explains the connection
- [ ] `edge_suggest` events → dashed proposed-link overlay in graph

### Phase C — Write-back (1-2 days)
- [ ] FastAPI: `POST /api/writeback` handler → insert wikilink in `## See Also` section
- [ ] React: diff preview modal before write (HITL gate)
- [ ] chokidar picks up change → graph updates automatically

---

## Reference

- `nashsu/llm_wiki` — closest prior art (React + sigma.js, not React Flow, but data model worth studying)
- React Flow hidden nodes: `reactflow.dev/examples/nodes/hidden`
- React Flow dagre: `reactflow.dev/examples/layout/dagre`
- LangGraph SSE: `softgrade.org/sse-with-fastapi-react-langgraph`
- umap-js: `github.com/PAIR-code/umap-js`
- umap-learn Python: `umap-learn.readthedocs.io`

---

## What React Flow Cannot Do Out of the Box

- **Continuous physics simulation while dragging** — d3-force needs explicit integration; static layout on load is fine for MVP
- **Automatic layout** — external library required (dagre or d3-force). Not a blocker.
- **UMAP** — external computation required; we precompute on backend and inject positions
