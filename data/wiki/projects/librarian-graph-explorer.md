---
title: Librarian Graph Explorer
tags: [rag, langgraph, infra, project]
summary: Local React Flow wiki graph explorer — multi-dimensional edge types (wikilink/semantic/tag-shared), UMAP semantic layout, and agent chat with graph highlighting and wikilink write-back. Addresses the gap where Obsidian cannot do multi-edge toggling or embedding-based spatial layout.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/react-flow-ui.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-28-chat-agent-improvements.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-30-frontend-audit-fixes.md
  - data/raw/repos/librarian/README.md
---

# Librarian Graph Explorer

A local React app for interactive exploration of the `wiki/` knowledge graph. Two panels: a React Flow graph (left) and an agent chat (right). The agent reads wiki pages, highlights relevant nodes in the graph, and proposes new wikilinks that can be written back to disk.

**Status (original plan):** Plan complete. Ready to implement. Effort: ~3-4 days MVP (graph + multi-edge + UMAP), ~6-8 days full (agent chat + write-back). The graph and chat phases shipped; see *State as of 2026-10* below for what changed since the plan.

**Why not Obsidian:** Juggl evaluation confirmed it cannot do multi-dimensional edge toggling, embedding-based spatial layout (UMAP), or agent-driven highlighting. This build covers that gap.

---

## State as of 2026-10

The UI now has three tabs: the graph, **Courses** (lessons over `data/courses/`, linked to
wiki pages) and **Practice** (drills). The chat agent is a plain Anthropic tool-use loop,
not LangGraph: `search_wiki` and `read_page`, up to 8 turns, streamed over SSE from
`POST /api/chat/stream`.

### Chat agent hardening (plan of 2026-10-28, executed)

- **Multi-turn, text only.** The request carries a bounded `history` of prior
  user/assistant text turns; tool blocks never cross the wire. The agent trims to the last
  10 messages and 24k characters and drops a leading assistant turn. Pydantic enforces
  strict alternation ending on `assistant`. The client sends only completed pairs, so an
  errored reply drops out of history by construction.
- **Grounding is computed, not trusted.** Answers cite `[page:<id>]`; after the loop the
  agent emits a `grounding` SSE event with `cited`, `pages_read` and
  `ungrounded = cited − pages_read`. Cited ids are never added to `highlight`, so a
  hallucinated id cannot light up a node. Mechanism: [[Cited-Minus-Read Grounding Check]].
- **Answer telemetry.** One line per answer in `logs/agent.jsonl` (turns, tool calls,
  pages read, cited, ungrounded, latency, stop reason, `source` = chat or eval), written by
  a never-raising logger that mirrors the retrieval log.
- **Answer eval.** `run_eval.py --agent` drives the same streaming path the UI uses.
  A deterministic grader scores read-recall and cited-recall against expected source
  pages and whether the answer is grounded. An opt-in, billable LLM judge scores against
  `expected_answer`; unparseable verdicts are excluded rather than scored 0. No gating
  floor until a baseline exists.
- **Injectable client.** The streaming function takes a `client`, so tests drive the full
  loop with a fake and nothing in the test suite calls the API.

### Frontend audit (plan of 2026-10-30, planned)

The audit found:

- the graph payload had grown to **10.5 MB**, mostly 42k tag-shared edges, and was re-sent
  on every wiki change;
- domain lists were hardcoded in four places, missing five newer directories;
- the lesson markdown renderer rebuilt its component types every render
  ([[Render-Scoped Component Types Remount Their Subtree]]);
- the courses catalog was refetched on every tab mount, and progress state was split
  between two tabs;
- there were nested interactive elements and a hardcoded WebSocket URL.

Decisions D1–D7, all on their defaults:

- private pages stay in the local graph with a badge;
- chat renders `[page:id]` as clickable chips, reversing the earlier "no inline markers"
  choice;
- tag-shared edges are derived client-side for the visible subgraph only;
- sanitised raw HTML is allowed in lessons;
- embedding-based lesson-to-concept links are cached (threshold 0.55, top 6);
- the practice timer is client-only;
- the responsive styling pass runs last, alone.

The graph payload contract becomes wikilink edges, a disk-derived `domains` list and a
`private` flag per node. Target: under 1.5 MB.

Execution runs as [[File-Disjoint Agent Waves in One Working Tree]].

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Vite + React + TypeScript | Fast dev, standard |
| Graph rendering | React Flow | Custom nodes by tag, `hidden` filtering, 200 nodes performant |
| Layout: hierarchical | `dagre` | Top-down, good for project → concept → pattern hierarchy |
| Layout: organic | `d3-force` | Physics sim, nodes repel — exploration |
| Layout: semantic | `umap-js` + MiniLM embeddings | Position by semantic distance; clusters emerge without explicit edges |
| Frontmatter parser | `gray-matter` | Dead simple, standard |
| Wikilink extractor | regex `\[\[([^\]]+)\]\]` | Zero deps at this scale |
| File watcher | `chokidar` | Industry standard, hot-reload |
| Embeddings | `all-MiniLM-L6-v2` (384-dim) via FastAPI | Already in stack; fast |
| Agent backend | FastAPI + LangGraph | Python matches existing stack |
| Agent streaming | SSE | Unidirectional, simpler than WebSocket |
| Write-back | FastAPI POST → `fs.write` → chokidar | Backend writes, chokidar detects, WebSocket refreshes graph |

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
                                         │
                                    WebSocket push
                                         │
                                         ▼
React app ◄──────────────── React Flow graph (left panel)
    │                              │
    │ user query                   │ highlight subgraph
    ▼                              ▲
FastAPI /chat/stream ──SSE──► token + highlight + edge_suggest events
    │
LangGraph agent (search_wiki, read_page tools)
```

---

## Multi-Dimensional Edge Types

The key feature beyond Obsidian:

| Edge Type | Source | Color | Default |
|---|---|---|---|
| `wikilink` | Explicit double-bracket link syntax in markdown | White/light | On |
| `semantic` | Cosine similarity > 0.65 (MiniLM) | Blue, opacity by score | Off |
| `tag-shared` | Pages sharing ≥2 domain tags | Orange | Off |

Toggle panel: three checkboxes. Checking `semantic` adds soft blue edges between conceptually related pages even without wikilinks — surfaces implicit relationships.

---

## Layout Modes

| Mode | Algorithm | Best For |
|---|---|---|
| `dagre` | Hierarchical top-down | Project → decision → concept hierarchy |
| `d3-force` | Physics repulsion | Organic exploration |
| `umap-semantic` | MiniLM embeddings → UMAP → 2D | Semantic distance in positions; no edges needed to see clusters |

**UMAP:** precomputed on FastAPI backend (`POST /api/layout/umap`), returns `{page_id: {x, y}}`. Recomputes when wiki changes (~2-3s for 50 pages).

---

## Agent SSE Event Schema

```json
{ "type": "token", "content": "The CRAG retry loop..." }
{ "type": "highlight", "pages": ["CRAG Retry Logic", "RAG Reranking"] }
{ "type": "edge_suggest", "from": "RAG Reranking", "to": "CRAG Retry Logic", "reason": "..." }
```

- `token` → append to chat message
- `highlight` → dims non-relevant nodes to `opacity: 0.2`
- `edge_suggest` → shows proposed new wikilink as dashed edge (write-back candidate)

---

## Write-Back Flow

Agent proposes a new wikilink (e.g. a page named `NewLink`) → React shows diff preview → user approves → `POST /api/writeback` → FastAPI writes to `.md` file → chokidar detects → re-parses → WebSocket pushes updated graph.

HITL gate on write-back: user must approve every wikilink insertion before it lands in `wiki/*.md`.

---

## MVP Phases

| Phase | Scope | Effort |
|---|---|---|
| A — Graph + Multi-Edge + Layout | React Flow, dagre, d3-force, multi-edge toggles, semantic edges, UMAP | 3-4 days |
| B — Agent Chat | FastAPI `/chat/stream`, LangGraph `search_wiki` + `read_page`, SSE consumer, graph highlighting | 2-3 days |
| C — Write-Back | `POST /api/writeback`, diff preview modal, chokidar auto-refresh | 1-2 days |

---

## See Also
- [[Librarian KB — Build Plan]] <!-- auto-linked -->
- [[Librarian Project]]
- [[Librarian RAG Architecture]]
- [[LangGraph CRAG Pipeline]]
- [[Karpathy LLM Wiki Pattern]]
- [[MCP Protocol]]
- [[Cited-Minus-Read Grounding Check]]
- [[File-Disjoint Agent Waves in One Working Tree]]
- [[Render-Scoped Component Types Remount Their Subtree]]
