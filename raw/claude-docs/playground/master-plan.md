# Librarian KB — Master Plan

> **ARCHIVED 2026-04-25** — Canonical page is now `wiki/projects/librarian-kb-plan.md`. Do not update this file.

**Updated:** 2026-04-25 (Phase 5 complete, Phase 6 active)  
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

### ✅ Phase 5 — Obsidian Plugins
- Juggl installed — custom node styling per tag, hierarchical/concentric layouts, live filtering
- Graph Analysis installed — cosine-similarity semantic edges between pages
- Evaluation: Juggl covers the core visualization needs; Phase 8 (React Flow) deprioritized

### 🔄 Phase 6 — Input Connectors (current)

Scope expanded to cover **personal + work** sources. All claude.ai MCP integrations are available without separate OAuth setup.

#### Done
- [x] Linear: MCP connector active (work)
- [x] Google Drive: 3 priority decks ingested (`langgraph_yan`, `adk-overview`, `poc-architecture`)
- [x] Work Notion: 4 priority pages ingested (RAG Pipeline, Support Knowledge Agent, Copilot, AGT-09)
- [x] Gmail: **removed** — Gemini meeting transcripts live in Google Drive (already covered by Drive connector)

#### Available via claude.ai MCP (no extra auth needed)
- [ ] **Google Drive** (ongoing): search for additional shared AI/agent decks as needed → `raw/gdrive/`
- [ ] **Notion** (personal): `ramsey.wise@gmail.com` account — researcher PDF notes, personal agent design notes. Requires separate auth session.
- [ ] **Guru** (work KB): `mcp__claude_ai_Guru` — company knowledge base articles relevant to agent stack
- [ ] **Google Calendar**: deprioritized — meeting context for decision provenance
- [ ] **Slack**: deprioritized

#### Scripts (local)
- [ ] **PDFs**: `scripts/ingest_pdf.py` reads from `DROPBOX_PDF_PATH` — configure `.env`. Personal reading list + work research papers.
- [ ] **Web research**: manual save to `raw/web/YYYY-MM-DD-topic.md` → `/ingest`. Consider auto-save hook.

#### Agent integration
- [ ] **researcher** agent: once Phase 12 wiring is done, PDFs from personal Dropbox + work shared drives both route through it
- [ ] Pull order: Drive (ongoing) → Personal Notion → PDFs. Guru/Calendar/Slack deprioritized.

### ⬜ Phase 7 — Plan Merge & Wiki Canonical Page
- [ ] Ingest `raw/claude-docs/playground/docs/archived/obsidian-kb-plan.md` into wiki
- [ ] Create `wiki/projects/librarian-kb-plan.md` as the canonical single-source plan page
- [ ] Archive this master-plan.md once wiki page is live

### 🔄 Phase 8 — React Flow UI (in progress)
**Plan doc:** `.claude/docs/plans/react-flow-ui.md`  
**Status:** Phase 8A + 8B complete (2026-04-25). 8C pending. Code lives in `app/`.

#### ✅ Phase 8A — Graph
- `app/ui/` — Vite + React + TypeScript + `@xyflow/react`
- `app/backend/` — FastAPI + WebSocket hot-reload + `watchfiles`
- Multi-edge types: wikilink / semantic (MiniLM cosine sim) / tag-shared (≥2 domain tags)
- Edge toggle panel, layout switcher (dagre ↔ UMAP-semantic), tag filter panel
- WebSocket pushes graph updates on any `wiki/` file change
- **Run:** `make api` (port 8000) + `make ui` (port 5173)

#### ✅ Phase 8B — Agent chat
- `app/backend/agent.py` — Anthropic tool-use loop: `search_wiki` + `read_page`, streams tokens
- `POST /api/chat/stream` SSE endpoint: `{type: token}`, `{type: highlight}`, `{type: done}`
- `useChatStream` hook: SSE consumer, calls `onHighlight(pages)` to dim non-relevant nodes
- `ChatPanel` component: token streaming display, Enter-to-send
- `NodeDetailPanel` component: node summary + "Referenced in last query" badge on click
- Agent highlights take precedence over tag-filter dimming

#### ⬜ Phase 8C — Write-back
- `POST /api/writeback` → insert wikilink in `## See Also`
- HITL diff preview modal before write
- `watchfiles` detects change → WebSocket refreshes graph

#### ⬜ Phase 8C — Write-back
- `POST /api/writeback` → insert wikilink in `## See Also`
- HITL diff preview modal before write
- `watchfiles` detects change → WebSocket refreshes graph

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

## Agent Integration Phases

> **Prerequisite:** Phases 5 (Obsidian plugins) and 8 (React Flow UI) must complete before starting these. The four agents live in `agents/`: `researcher`, `adk-agent-pocs`, `presenter`, `cartographer`.

### ⬜ Phase 12 — Researcher Integration

The `researcher` agent currently does PDF → Obsidian notes. Wire it into the librarian ingest pipeline.

- [ ] Add config path: `settings.readings_dir` → `raw/pdfs/`, output → `raw/pdfs-processed/` (intermediate)
- [ ] Researcher output format: emit wiki-compatible frontmatter (title, tags, summary, updated, sources) instead of Obsidian note format
- [ ] Add `uv run researcher <pdf>` → runs ingest protocol, creates/updates `wiki/` pages automatically
- [ ] Update `/ingest` skill to detect PDFs and delegate to researcher agent (vs. plain markdown copy)
- [ ] Prompt tuning: researcher prompts must know the domain tag taxonomy (`adk`, `rag`, `langgraph`, etc.) and atomic concept extraction rule

### ⬜ Phase 13 — ADK POC Knowledge Extraction

`agents/adk-agent-pocs/` contains live reference implementations (a2ui_mcp, SKILL.md multi-agent, MCP tool schemas). Use these to fill wiki gaps.

- [ ] Audit `adk-agent-pocs/` sub-projects: identify patterns not yet covered in wiki
- [ ] Create `wiki/skills/` subdirectory for POC-derived skill patterns (separate from `wiki/concepts/`)
- [ ] Priority pages to create from POCs:
  - `wiki/skills/a2ui-mcp-pattern.md` — agent-to-UI via MCP with structured schema
  - `wiki/skills/skill-md-multi-agent.md` — SKILL.md format in a multi-agent system
  - `wiki/skills/mcp-tool-schema-design.md` — tool schema patterns from POC impls
- [ ] Wire new `wiki/skills/` pages into `wiki/_index.md` and add backlinks from relevant concept pages
- [ ] Evaluate: after extraction, do the POCs reveal any new domain tags needed?

### ⬜ Phase 14 — Presenter Output Agent

`agents/presenter/` is a deck-authoring agent (intake → outline → slides → PPTX). Expand output targets.

- [ ] **PPT (current):** verify end-to-end flow works against the librarian wiki as source material
- [ ] **Linear:** export structured wiki action items → Linear tickets via MCP (complements Phase 10)
- [ ] **Notion:** export stable wiki pages → Notion pages via MCP (complements Phase 10)
- [ ] **Google Docs/Slides:** OAuth integration for sharing with collaborators
- [ ] Intake source: allow presenter to pull from wiki KB (via MCP `search_wiki`) rather than manual text input
- [ ] `/present` skill: Claude Code entry point to kick off a deck from a wiki query

### ⬜ Phase 15 — Cartographer Automation (Later)

`agents/cartographer/` parses Claude Code session JSONL + session notes, generates HTML reports and friction analysis. Automate the ingest pipeline.

- [ ] Explore: can cartographer trigger `/ingest` automatically after each session?
- [ ] Cron mode (`--cron`): daily friction analysis → `raw/sessions/YYYY-MM-DD-friction.md` → auto-ingest
- [ ] Session insights → wiki: does cartographer output meet the quality bar for wiki pages? Define criteria.
- [ ] Evaluate: does the `/seed-kb` skill become redundant once cartographer cron is running?
- [ ] Gate: do not automate until the ingest pipeline (Phase 12) is stable and signal quality from sessions is proven

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
| Agent integration | Phases 12-15 deferred until Phases 5+8 complete | 2026-04-25 |
| Researcher output | Wiki-compatible frontmatter (not Obsidian notes) | 2026-04-25 |
| POC extraction | `wiki/skills/` as dedicated directory for POC-derived patterns | 2026-04-25 |
| Presenter first target | PPT → expand to Linear/Notion/Google Docs in Phase 14 | 2026-04-25 |
| Cartographer | Deferred: automate ingest only after Phase 12 pipeline is stable | 2026-04-25 |
| Phase 8 (React Flow) | Active — 8A scaffolded; multi-edge + UMAP layout + tag filter built | 2026-04-25 |
| Input scope | Personal + work sources both in scope for Phase 6 | 2026-04-25 |
| MCP auth | claude.ai MCPs (Notion, Drive, Guru) used — no separate OAuth setup | 2026-04-25 |
| Pull order | Linear → Drive → Work Notion → PDFs; Gmail removed (transcripts in Drive); Slack deprioritized | 2026-04-25 |
