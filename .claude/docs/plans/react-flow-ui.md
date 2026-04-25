# React Flow Wiki Graph Explorer — Plan

**Date:** 2026-04-24  
**Status:** Planned — not started. Execute after Obsidian plugin evaluation (Phase 2).  
**Effort:** ~2-3 days MVP (graph only), ~5-7 days full (agent chat + write-back)

---

## What We're Building

A local dev React app with two panels:
- **Left**: interactive knowledge graph (React Flow) — nodes = wiki pages, edges = wikilinks, styled by frontmatter tags
- **Right**: agent chat panel — ask a question, agent reads wiki, highlights relevant subgraph, proposes new wikilinks

The agent chat drives the visualization — query results highlight nodes, write-back adds wikilinks to markdown files on disk.

---

## Stack (confirmed by research)

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | Vite + React + TypeScript | Fast dev, standard |
| Graph rendering | React Flow | Custom nodes by tag, `hidden` filtering, 200 nodes no problem |
| Layout algorithm | d3-force (default) + dagre (alt) | d3-force = organic feel; dagre = hierarchical; add switcher |
| Frontmatter parser | `gray-matter` | Used by Gatsby/Astro, dead simple |
| Wikilink extractor | regex `\[\[([^\]]+)\]\]` | Sufficient at this scale, zero deps |
| File watcher | `chokidar` | Industry standard, Vite uses it internally |
| Agent backend | FastAPI + LangGraph | Python matches existing stack |
| Agent streaming | SSE (Server-Sent Events) | Unidirectional streaming, simpler than WebSocket |
| Write-back | FastAPI POST → `fs.write` → chokidar | Backend writes, chokidar detects, WebSocket refreshes graph |
| Deployment | Local only (`vite dev`) | No infra needed; Cloudflare Pages later if wanted |

---

## Architecture

```
wiki/*.md ──► chokidar watcher ──► parse (gray-matter + regex)
                                         │
                                         ▼
                              nodes[] + edges[] JSON
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

## Agent SSE Event Schema

Two event types on the same stream:

```json
{ "type": "token", "content": "The CRAG retry loop..." }
{ "type": "highlight", "pages": ["CRAG Retry Logic", "RAG Reranking", "LangGraph CRAG Pipeline"] }
```

React handles each: `token` → append to chat message, `highlight` → `setNodes()` dims non-relevant nodes to `opacity: 0.2`.

---

## MVP Phases

### Phase A — Graph (2-3 days)
- [ ] Scaffold: `npm create vite@latest librarian-ui -- --template react-ts`
- [ ] Data layer: `gray-matter` parser + wikilink regex → `{nodes, edges}` JSON
- [ ] React Flow: render nodes with zoom/pan/minimap
- [ ] Custom node component: color by domain tag, shape by type tag, title + summary on hover
- [ ] Layout: integrate `dagre` for initial positions
- [ ] Tag filter panel: multiselect → toggle `hidden` on nodes/edges
- [ ] chokidar watcher: Express backend → WebSocket → hot-reload graph on wiki file change

### Phase B — Agent chat (2-3 days)
- [ ] FastAPI backend: `/chat/stream` endpoint with SSE
- [ ] LangGraph agent: `search_wiki` + `read_page` tools reading from `wiki/`
- [ ] React chat panel: SSE consumer, token streaming display
- [ ] Graph highlighting: `type: highlight` events → `setNodes` dims non-relevant nodes
- [ ] "Why highlighted?" sidebar: click a highlighted node → agent explains the connection

### Phase C — Write-back (1-2 days)
- [ ] FastAPI: `POST /api/writeback` handler → insert wikilink in `## See Also` section
- [ ] React: diff preview modal before write (HITL gate)
- [ ] chokidar picks up change → graph updates automatically

---

## Reference

- `nashsu/llm_wiki` — closest prior art (React + sigma.js, not React Flow, but data model worth studying)
- React Flow hidden nodes example: `reactflow.dev/examples/nodes/hidden`
- React Flow dagre example: `reactflow.dev/examples/layout/dagre`
- LangGraph SSE pattern: `softgrade.org/sse-with-fastapi-react-langgraph`

---

## What React Flow Cannot Do Out of the Box

- **Continuous physics simulation** (nodes repel each other as you drag) — needs d3-force integration, more complex. Static layout computed once on load is fine for MVP.
- **Automatic layout** — external library required (dagre or d3-force). Not a blocker.

---

## Do Not Start Until

Obsidian + Juggl + Graph Analysis evaluated. The gap between what Juggl can do and what we need is the exact scope of this build. Don't over-engineer before that evaluation.
