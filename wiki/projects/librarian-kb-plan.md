---
title: Librarian KB — Build Plan
tags: [llm, infra, mcp, langgraph, rag, project]
summary: Phased build plan for the Librarian KB — Phases 1–5 complete, Phase 6 (connectors) active, Phase 8A+B (React Flow UI) done, Phases 9–15 future.
updated: 2026-04-25
sources:
  - raw/claude-docs/playground/docs/archived/obsidian-kb-plan.md
  - raw/claude-docs/playground/docs/archived/obsidian-kb-research.md
---

# Librarian KB — Build Plan

A specialized agent-design KB following the [[Karpathy LLM Wiki Pattern]] — not a general second brain. Before starting any new agent build, load the KB to get grounded recommendations from accumulated design experience. Scope stays narrow: agent engineering, RAG, LangGraph, ADK, MCP, eval patterns.

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
- Repo initialized; `CLAUDE.md` schema written with ingest protocol, page format, domain/type tags
- `raw/`, `wiki/` directory structure in place
- Claude Code skills: `/ingest`, `/query`, `/lint`, `/adk-context`, `/seed-kb`

### ✅ Phase 2 — Seed & First Ingest
- `raw/playground-docs/` seeded from `playground/.claude/docs/archived/`
- `raw/claude-docs/` seeded from all workspace `.claude/docs/`
- First wiki pages compiled: 26 pages across concepts/agents/projects/decisions
- `raw/manifest.jsonl` tracking ingested files with SHA256 hashes

### ✅ Phase 3 — Atomic Concept Extraction
- Ingest protocol updated: atomic concepts as own pages (not buried bullets)
- 10 new atomic pages: [[Reciprocal Rank Fusion]], [[HistoryCondenser]], [[LangGraph BaseStore]], [[Prefix Caching]], [[CRAG Retry Logic]], [[Send API Fan-out]], [[Summarization Node]], [[ACI (Agent-Computer Interface)]], [[Embedder Warmup]], [[SKILL.md Pattern]]
- Wiki at 36 pages, 156+ wikilinks

### ✅ Phase 4 — Obsidian Vault
- Vault opened at `wiki/` (`.obsidian/` config committed)
- `make viz` opens Obsidian at `wiki/`
- Streamlit visualizer deprecated

### ✅ Phase 5 — Obsidian Plugins
- Juggl installed — custom node styling per tag, hierarchical/concentric layouts, live filtering
- Graph Analysis installed — cosine-similarity semantic edges between pages
- Evaluation complete: Juggl covers core viz needs; React Flow (Phase 8) deprioritized but built anyway for multi-edge + agent chat

### 🔄 Phase 6 — Input Connectors (active)
Personal + work sources in scope. All claude.ai MCP integrations available without separate OAuth.

**Done:**
- Linear: MCP connector active (work)
- Google Drive: 3 priority decks ingested (`langgraph_yan`, `adk-overview`, `poc-architecture`)
- Work Notion: 4 priority pages ingested (RAG Pipeline, Support Knowledge Agent, Copilot, AGT-09)
- Gmail: removed — Gemini meeting transcripts live in Google Drive (already covered)

**Pending:**
- Google Drive (ongoing): search for additional shared AI/agent decks → `raw/gdrive/`
- Notion (personal): `ramsey.wise@gmail.com` account — researcher PDF notes, personal agent design notes
- Guru (work KB): company knowledge base articles relevant to agent stack
- PDFs: `scripts/ingest_pdf.py` reads from `DROPBOX_PDF_PATH`

### ✅ Phase 7 — Plan Merge & Wiki Canonical Page
- Source `raw/claude-docs/playground/docs/archived/obsidian-kb-plan.md` ingested (manifest confirmed)
- `wiki/projects/librarian-kb-plan.md` rewritten as canonical single-source plan page
- `.claude/docs/plans/master-plan.md` archived

### 🔄 Phase 8 — React Flow UI (Phase 8C pending)
**Code lives in `app/`. Run:** `make install-api && make install-ui`, then `make api` + `make ui`.

**✅ Phase 8A — Graph**
- `app/ui/` — Vite + React + TypeScript + `@xyflow/react`
- `app/backend/` — FastAPI + WebSocket hot-reload + `watchfiles`
- Multi-edge types: wikilink / semantic (MiniLM cosine sim) / tag-shared (≥2 domain tags)
- Edge toggle panel, layout switcher (dagre ↔ UMAP-semantic), tag filter panel

**✅ Phase 8B — Agent Chat**
- `app/backend/agent.py` — Anthropic tool-use loop: `search_wiki` + `read_page`, streams tokens
- SSE endpoint: `{type: token}`, `{type: highlight}`, `{type: done}`
- `ChatPanel` component with token streaming; `NodeDetailPanel` with highlight badge

**⬜ Phase 8C — Write-back**
- `POST /api/writeback` → insert wikilink in `## See Also` (endpoint exists, needs HITL UI)
- HITL diff preview modal before write
- `watchfiles` detects change → WebSocket refreshes graph

### ⬜ Phase 9 — MCP Server
- `mcp_server/server.py` (FastMCP): `search_wiki`, `read_page`, `list_pages` tools
- Add to Claude Code MCP config in `.claude/settings.json`
- DuckDB FTS index over `wiki/` for `search_wiki`
- Expose to playground agents — inject wiki context into ADK/LangGraph builds

### ⬜ Phase 10 — Output Connectors
- `scripts/export_to_linear.py` — wiki action item → Linear ticket via MCP
- `scripts/export_to_notion.py` — stable wiki page → Notion page via MCP
- `/lint` findings → auto-create Linear tickets for orphan pages, dead links

### ⬜ Phase 11 — RAG Search Layer
- Semantic search over wiki via MiniLM embeddings (already in `app/backend/embeddings.py`)
- `/query` skill uses embeddings rather than filename matching
- Evaluate: does wiki-grounded context improve agent builds?

---

## Agent Integration Phases

> **Prerequisite:** Phases 5 + 8 must complete before starting. The four agents live in `agents/`: `researcher`, `adk-agent-pocs`, `presenter`, `cartographer`.

### ⬜ Phase 12 — Researcher Integration
Wire `agents/researcher/` (PDF → Obsidian notes) into the librarian ingest pipeline.
- Researcher emits wiki-compatible frontmatter (title, tags, summary, updated, sources)
- `uv run researcher <pdf>` → runs ingest protocol, creates/updates `wiki/` pages
- `/ingest` skill detects PDFs and delegates to researcher

### ⬜ Phase 13 — ADK POC Knowledge Extraction
`agents/adk-agent-pocs/` contains live reference implementations. Use to fill wiki gaps.
- Audit sub-projects; create `wiki/skills/` for POC-derived patterns
- Priority: `a2ui-mcp-pattern`, `skill-md-multi-agent`, `mcp-tool-schema-design`

### ⬜ Phase 14 — Presenter Output Agent
`agents/presenter/` deck-authoring agent. Expand output targets.
- Verify PPT end-to-end against librarian wiki as source
- Linear + Notion + Google Docs/Slides export
- `/present` skill: Claude Code entry point to kick off a deck from a wiki query

### ⬜ Phase 15 — Cartographer Automation
`agents/cartographer/` parses session JSONL → HTML friction reports.
- Cron mode: daily friction analysis → `raw/sessions/` → auto-ingest
- Gate: do not automate until Phase 12 ingest pipeline is stable

---

## Key Decisions

| Decision | Choice | Date |
|---|---|---|
| Wiki pattern | Karpathy LLM Wiki (raw → compiled) | 2026-04-24 |
| Orchestration | LangGraph (not ADK) for agent layer | 2026-04-12 |
| Interim viz | Obsidian native + Juggl + Graph Analysis | 2026-04-24 |
| Target viz | React Flow (not Cytoscape, not sigma.js) | 2026-04-24 |
| Agent streaming | FastAPI + SSE (not WebSocket, not polling) | 2026-04-24 |
| Scope | Agent engineering KB only (not general second brain) | 2026-04-24 |
| Agent integration | Phases 12–15 deferred until Phases 5+8 complete | 2026-04-25 |
| Input scope | Personal + work sources both in scope for Phase 6 | 2026-04-25 |
| MCP auth | claude.ai MCPs (Notion, Drive, Guru) — no separate OAuth | 2026-04-25 |

## See Also
- [[Karpathy LLM Wiki Pattern]]
- [[Librarian Project]]
- [[ADK vs LangGraph Comparison]]
- [[MCP Protocol]]
- [[Plan and Execute Pattern]]
