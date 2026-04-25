# Librarian KB — Master Plan

**Updated:** 2026-04-24  
**Sources merged:** `raw/claude-docs/playground/docs/archived/obsidian-kb-plan.md`, memory/project_librarian.md, `.claude/docs/plans/react-flow-ui.md`

---

## North Star

A specialized agent-design KB — not a general second brain. Before starting any new agent build, load the KB to get grounded recommendations from your own accumulated design experience. Scope stays narrow: agent engineering, RAG, LangGraph, ADK, MCP, eval patterns.

**Mental model:** `raw/` = source code → Claude = compiler → `wiki/` = executable output → agent/viz = interface

---

## Architecture (3 Layers)

```
Layer 3: React Flow UI      ←  graph explorer + agent chat; highlights subgraph on query; write-back to wiki
              ↕ read/write
Layer 2: Obsidian           ←  interim viz; Juggl + Graph Analysis plugins (semantic edges)
              ↕ read
Layer 1: Wiki KB            ←  deterministic compiler: raw/ → wiki/ (atomic concepts as pages)
```

---

## Phase Status

### ✅ Phase 1 — Core Structure
- Repo initialized at `ramseywise/librarian`
- `CLAUDE.md` schema written with ingest protocol, page format, domain/type tags
- `raw/`, `wiki/` directory structure in place
- Claude Code skills: `/ingest`, `/query`, `/lint`, `/adk-context`, `/seed-kb`

### ✅ Phase 2 — Seed & First Ingest
- `raw/playground-docs/` seeded from `playground/.claude/docs/archived/`
- `raw/claude-docs/` seeded from all workspace `.claude/docs/`
- `raw/sessions/` seeded (54 session notes — low signal, skip ingest)
- First wiki pages compiled: 26 pages across concepts/agents/projects/decisions
- `raw/manifest.jsonl` tracking ingested files with SHA256 hashes

### ✅ Phase 3 — Atomic Concept Extraction
- Ingest protocol updated in `CLAUDE.md`: atomic concepts as own pages (not buried bullets)
- 10 new atomic pages: RRF, HistoryCondenser, LangGraph BaseStore, Prefix Caching, CRAG Retry Logic, Send API Fan-out, Summarization Node, ACI, Embedder Warmup, SKILL.md Pattern
- Wikilinks wired from parent pages into atomic pages
- Wiki now at 36 pages, 156+ wikilinks

### ✅ Phase 4 — Obsidian Vault
- Vault opened at `wiki/` (`.obsidian/` config in place)
- `make viz` and VS Code task configured (`open -a Obsidian`)
- Streamlit visualizer deprecated

### 🔄 Phase 5 — Obsidian Plugins (current)
- [ ] Install **Juggl** — advanced graph: custom node styling per tag, hierarchical/concentric layouts, live filtering
- [ ] Install **Graph Analysis** — cosine-similarity semantic edges between pages
- [ ] Evaluate: what can Juggl do that we need? What gap remains for React Flow?
- Install: `Cmd+,` → Community Plugins → Browse → search each → Install → Enable

### ⬜ Phase 6 — Input Connectors
- [x] Linear: done via MCP (Claude Desktop connector; no API key needed)
- [ ] Notion: `scripts/ingest_notion.py` exists; needs `NOTION_API_KEY` + target page IDs. Scope Notion content before ingesting.
- [ ] Gmail/meetings: Enterprise Google Workspace OAuth. High signal for decisions. Not set up.
- [ ] PDFs: `scripts/ingest_pdf.py` reads from `DROPBOX_PDF_PATH`. Configure `.env`.
- [ ] Web research: manual save to `raw/web/YYYY-MM-DD-topic.md` → `/ingest`. Consider auto-save hook for Claude web searches.

### ⬜ Phase 7 — Plan Merge & Wiki Canonical Page
- [ ] Ingest `raw/claude-docs/playground/docs/archived/obsidian-kb-plan.md` into wiki
- [ ] Create `wiki/projects/librarian-kb-plan.md` as the canonical single-source plan page
- [ ] Archive this master-plan.md once wiki page is live

### ⬜ Phase 8 — React Flow UI (plan written)
**Plan doc:** `.claude/docs/plans/react-flow-ui.md`  
**Do not start until Phase 5 evaluation complete.**

Stack confirmed:
- Vite + React + TypeScript + React Flow
- Layout: dagre (hierarchical) + d3-force (organic), runtime switcher
- Data layer: `gray-matter` + wikilink regex + `chokidar` watcher + WebSocket hot-reload
- Agent bridge: FastAPI + SSE (`{type: token}` for chat, `{type: highlight, pages:[]}` for graph)
- Write-back: POST to FastAPI → `fs.write` → chokidar → WebSocket refresh

Phases:
- Phase 8A (2-3 days): Graph only — render, custom nodes by tag, dagre layout, tag filter panel, hot-reload
- Phase 8B (2-3 days): Agent chat panel — SSE streaming, LangGraph agent with `search_wiki`/`read_page`, graph highlighting
- Phase 8C (1-2 days): Write-back — HITL diff preview modal, FastAPI write, auto-refresh

Reference: `nashsu/llm_wiki` on GitHub (closest prior art)

### ⬜ Phase 9 — MCP Server
- [ ] `mcp_server/server.py` (FastMCP) with tools: `search_wiki`, `read_page`, `list_pages`
- [ ] Add to Claude Code MCP config in `.claude/settings.json`
- [ ] DuckDB FTS index over `wiki/` for `search_wiki` tool
- [ ] Expose to playground agents — test injecting wiki context into ADK/LangGraph builds
- [ ] `/adk-context` skill uses MCP search rather than raw file reads

### ⬜ Phase 10 — Output Connectors
- [ ] `scripts/export_to_linear.py` — wiki action item → Linear ticket via MCP
- [ ] `scripts/export_to_notion.py` — stable wiki page → Notion page via MCP
- [ ] `/lint` findings → auto-create Linear tickets for orphan pages, dead links

### ⬜ Phase 11 — RAG Search Layer (Future)
- [ ] Semantic search over wiki via MiniLM embeddings (already in playground)
- [ ] `/query` skill uses embeddings rather than filename matching
- [ ] Evaluate: does wiki-grounded context improve ADK/LangGraph agent builds?

---

## Constraints (carry forward)

- `raw/` is immutable — append only, never edit or delete
- `wiki/` is Claude-maintained — no manual edits except factual corrections
- PDFs stay in Dropbox, not committed to git (`DROPBOX_PDF_PATH` in `.env`)
- No continuous sync with Notion/Linear — pull on demand
- No vector DB infra until DuckDB FTS quality is proven insufficient
- Repo stays private initially

---

## Key Decisions (locked)

| Decision | Choice | Date |
|---|---|---|
| Wiki pattern | Karpathy LLM Wiki (raw → compiled) | 2026-04-24 |
| Orchestration | LangGraph (not ADK) for agent layer | 2026-04-12 |
| Interim viz | Obsidian native + Juggl + Graph Analysis | 2026-04-24 |
| Target viz | React Flow (not Cytoscape, not sigma.js) | 2026-04-24 |
| Agent streaming | FastAPI + SSE (not WebSocket, not polling) | 2026-04-24 |
| Taxonomy | Bottom-up emergence preferred; top-down OK to start | 2026-04-24 |
| Scope | Agent engineering KB only (not general second brain) | 2026-04-24 |
