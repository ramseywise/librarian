---
title: Librarian KB — Build Plan
tags: [llm, infra, mcp, langgraph, project]
summary: Phased plan for the Librarian KB — through Phase 3 complete, next is Streamlit viz, then Chainlit + LangGraph agent and MCP connectors.
updated: 2026-04-24
sources:
  - raw/playground-docs/obsidian-kb-plan.md
  - raw/playground-docs/obsidian-kb-research.md
---

# Librarian KB — Build Plan

Current state: Phases 1–3 complete. 26 wiki pages, manifest at 167 entries, all core ingest done. Next: Streamlit viz (Phase 2b), then Phase 4 agent.

See [[Karpathy LLM Wiki Pattern]] for the foundational model this follows.

---

## Architecture Overview

```
raw/          ← immutable inputs (append-only, selectively git-tracked)
  ├── manifest.jsonl    ← ingest state: hash + date + wiki pages per file
  claude-docs/          ← scraped from all workspace .claude/ dirs
  playground-docs/      ← seeded playground research/plans
  web/                  ← saved web research
  sessions/             ← session transcripts (git-ignored)
  pdfs/                 ← extracted text (git-ignored)

wiki/         ← LLM-compiled knowledge (Claude writes here)

scripts/
  visualize.py          ← Streamlit wiki graph + coverage panel
  seed_kb.py            ← scraper (already exists as /seed-kb skill)

.claude/
  skills/               ← /ingest /query /lint /adk-context /seed-kb
```

---

## Phase 1 — Core Structure ✅ Complete

- Repo, CLAUDE.md schema, `raw/` + `wiki/` directory contract
- `raw/` seeded from playground docs and `.claude/` scraper
- 21 wiki pages compiled across concepts, agents, projects, decisions
- Skills: `/ingest`, `/query`, `/lint`, `/adk-context`, `/seed-kb`
- `.claude/` cleaned to: agents, commands, hooks, memory, skills, settings

---

## Phase 2 — Manifest + Dedup + Streamlit

**Goal:** ingest is idempotent; coverage is visible.

### 2a — Ingest Manifest ✅ Complete

`raw/manifest.jsonl` — one line per ingested file:
```jsonl
{"path": "raw/web/2026-04-24-anthropic-agents.md", "hash": "sha256:...", "ingested_at": "2026-04-24", "wiki_pages": ["wiki/agents/plan-and-execute-pattern.md"]}
```

- `/ingest` checks hash before processing — skip if unchanged, re-ingest if modified
- On completion, appends/updates the manifest entry
- Eliminates re-ingestion of `raw/playground-docs/` content already compiled
- `raw/sessions/`, `raw/pdfs/` remain git-ignored; manifest tracks everything else

### 2b — Streamlit Wiki Graph ← next

`scripts/visualize.py`:

```
Nodes    wiki pages (colored by domain tag)
Edges    [[wikilinks]] between pages
Panel    click node → summary + source files
Filter   by tag (adk / rag / langgraph / mcp / memory...)
Coverage manifest panel — which raw/ files have no wiki coverage yet
```

Stack: `streamlit` + `networkx` + `pyvis` (interactive graph) + `python-frontmatter` for parsing.

---

## Phase 3 — Focused Ingest ✅ Complete

| Source | Output |
|---|---|
| `raw/web/` | [[MCP Protocol]], [[Plan and Execute Pattern]], [[Agentic Workflow Patterns]], [[Production Hardening Patterns]] updated |
| `raw/claude-docs/listen-wiseer/` | [[Listen-Wiseer Project]], [[RAG Evaluation]], [[Agent Memory Types]] updated |
| `raw/claude-docs/playground/docs/plans/va-agent-*` | [[VA Agent Project]] created |
| `raw/linear/` | [[PII Masking Approaches]], [[HITL Annotation Pipeline]], [[Evaluation & Improvement Project (VIR)]] created |
| `raw/claude-docs/playground/agents/` + `skills/a2ui-workspace/` | [[ADK Context Engineering]] updated with SKILL.md eval framework |

Skipped: `raw/sessions/` (54 transcripts, token stats only — no wiki value), `raw/claude-docs/playground/skills/` (operational stubs, low priority).

---

## Phase 4 — Conversational Agent (Chainlit + LangGraph)

**Goal:** an agent that can explore the wiki, do deep research across clusters, and generate structured outputs.

### Architecture

```
Chainlit UI
  └── LangGraph StateGraph
        ├── Planner node   — identifies relevant wiki pages from query
        ├── Research node  — reads pages, builds context, flags gaps
        ├── Generator node — produces output (brief / tickets / deck outline)
        └── HITL gate      — confirm before any external write
```

**Why LangGraph:** Plan-and-Execute pattern is already in [[Plan and Execute Pattern]]. Already in the stack (librarian, listen-wiseer). Works natively with Chainlit streaming.

**Why not ADK here:** ADK's strength is hierarchical multi-agent delegation with clearly bounded sub-agents. The KB agent is a single-domain reasoning loop — better fit for LangGraph. ADK could replace the Generator node later when output targets (Linear, Notion, decks) become distinct specialized agents.

**Why not Cloudflare:** JS/TS only — breaks the Python stack. Revisit for hosting/edge deployment after the agent is working locally.

### Use Cases

| Query | Agent behaviour |
|---|---|
| "What do we know about voice agents?" | Research node reads `memory`, `mcp`, `adk` tagged pages; synthesises briefing |
| "Create tickets for the next phase of listen-wiseer" | Research → Generator → Linear MCP (with HITL confirmation) |
| "Prepare a deck on RAG architecture decisions" | Research → Generator → markdown outline → Notion export |

### Free Tier Reality

| Layer | Cost |
|---|---|
| LangGraph library | Free |
| LangGraph Cloud (optional) | Free tier: 1 deployment, limited traces |
| Chainlit | Free (open source) |
| Claude API | ~$0.003/1k input tokens (Haiku) — negligible for personal use |
| LangSmith (optional observability) | Free tier: 10k traces/month |

---

## Phase 5 — MCP Server + Input Connectors (deferred)

Originally Phase 2–3. Deferred because the agent works fine reading `wiki/` directly over filesystem. MCP becomes valuable when:
- Other agents (in playground, ADK builds) need to query the KB at runtime
- You want Claude.ai (browser) to access the wiki without opening VS Code

### MCP Server (`mcp_server/server.py` — FastMCP)

Tools: `search_wiki`, `read_page`, `list_pages_by_tag`. Read-only initially.

### Source Registry (portable MCP config)

`.claude/settings.json` already configures API-key-based MCP servers — no OAuth, works on any machine:

| Source | MCP server | Key in `.env` | Auth type |
|---|---|---|---|
| Personal Notion | `@notionhq/notion-mcp-server` | `NOTION_API_KEY` | API key — portable |
| Work Notion | claude.ai MCP (OAuth) | — | Session OAuth — machine-specific |
| Linear | `linear-mcp-server` | `LINEAR_API_KEY` | API key — portable |
| Librarian KB | `mcp_server/server.py` | `ANTHROPIC_API_KEY` | Local — portable |

**Pattern:** API-key servers activate automatically from `.env`; claude.ai OAuth overlay for work accounts when on the right machine. New machine = copy repo + add `.env` keys.

**Future:** per-project ingest design doc in `wiki/projects/` capturing which sources exist, which are ingested, what wiki pages they produce, and what's pending. Enables automated ingest config generation from the registry.

### Input Connectors (on-demand, not continuous sync)

| Source | Tool | Script |
|---|---|---|
| Personal Notion | `@notionhq/notion-mcp-server` (env) or `scripts/ingest_notion.py` | `NOTION_API_KEY` |
| Work Notion | claude.ai MCP OAuth | `/mcp` auth flow |
| Linear | `linear-mcp-server` (env) or `scripts/ingest_linear.py` | `LINEAR_API_KEY` |
| Gmail transcripts | Manual paste → `raw/meetings/` | — |
| Dropbox PDFs | `scripts/ingest_pdf.py` reads `DROPBOX_PDF_PATH` | — |

---

## Phase 6 — RAG Search + Fine-Tuning (future)

- DuckDB FTS index over `wiki/` for the Streamlit app and MCP search tool
- Lightweight embedding layer (MiniLM, already in librarian) for semantic search
- Synthetic QA pairs from wiki pages → fine-tune Haiku on KB content

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Ingest state | `manifest.jsonl` (file-based) | Git-trackable, no infra, Claude-readable |
| Visualization | Streamlit (Stage 1), Chainlit (Stage 2) | Different jobs: analytics vs. conversational |
| Agent framework | LangGraph + Chainlit | Already in stack; Plan-and-Execute is the right pattern |
| Output agents | ADK sub-agents (future) | Better fit when Linear/Notion/decks are distinct agents |
| Hosting | Local dev first; Cloudflare Workers later | Cloudflare free tier is best; requires JS port |
| Connectors | Deferred to Phase 5 | Not blocking; filesystem access is sufficient for Phases 2–4 |
| raw/ git strategy | Selective: include claude-docs/, web/, playground-docs/; ignore sessions/, pdfs/ | Keeps repo lean; preserves source traceability |

## See Also
- [[Karpathy LLM Wiki Pattern]]
- [[Plan and Execute Pattern]]
- [[Librarian Project]]
- [[MCP Protocol]]
