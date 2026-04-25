# Librarian

Personal agent design reference — a compiled knowledge base that captures everything
learned about agent architecture, stack decisions, and system design patterns. Before
starting a new agent build, load the KB to get grounded recommendations from accumulated
experience, not from scratch.

---

## Architecture

```
Notion ──MCP──► ingest_notion.py ──►  raw/notion/          ─┐
Linear ──MCP──► ingest_linear.py ──►  raw/linear/           │
Meetings ───────────────────────────► raw/meetings/          ├──► /ingest ──► wiki/
Playground docs ────────────────────► raw/playground-docs/   │
PDFs ──────────► ingest_pdf.py ─────► raw/pdfs/             ─┘
Web / bookmarks ────────────────────► raw/web/

                                            wiki/
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                    MCP server           /adk-context       export scripts
                  (search_wiki,        (agent builder     (→ Notion pages,
                   read_page,            briefing)         → Linear tickets)
                   list_pages)
                          │
                          ▼
               Claude Code · playground agents · Claude.ai
```

**Key invariant:** `raw/` is append-only. `wiki/` is Claude-maintained.
`CLAUDE.md` is the compiler contract — the most important file in the repo.

---

## Components

| Component | What it does |
|---|---|
| `raw/` | Immutable input drop zone. Notion exports, Linear dumps, meeting transcripts, PDF text, web captures. Never edited after drop. |
| `wiki/` | LLM-compiled knowledge. One `.md` file per concept, project, or decision. Structured frontmatter, wikilinks, cross-references. Claude writes; humans correct factual errors. |
| `CLAUDE.md` | The compiler contract — schema rules, ingest checklist, conflict policy, domain taxonomy. Defines how Claude maintains the wiki. |
| `scripts/` | Connectors for pulling from Notion and Linear, extracting PDF text, and pushing stable pages back to Notion or as Linear tickets. Pull on demand, not continuous sync. |
| `app/backend/` | FastAPI server — wiki graph API, semantic edges (sentence-transformers), UMAP layout, and a streaming chat agent backed by a local Ollama model. |
| `app/ui/` | React + Vite graph UI. Visualises the wiki as a force-directed graph; chat panel queries the agent. |
| `mcp_server/` | FastMCP server exposing `search_wiki`, `read_page`, `list_pages` over the DuckDB FTS index. Read-only. Configured in `.claude/settings.json`. |
| `.claude/skills/` | `/ingest`, `/query`, `/lint`, `/adk-context` — Claude Code slash commands for all wiki operations. |

---

## Wiki Invariants

1. **One page per concept** — find the existing page or create one; never scatter knowledge.
2. **Conflicts are flagged, not overwritten** — contradictions go to `wiki/_conflicts.md` for human review.
3. **Every page has at least one backlink** — orphan pages are a lint error.
4. **`updated:` is set on every write** — stale pages (>60 days) are surfaced by `/lint`.
5. **Sources are cited** — every wiki page lists the `raw/` files it was compiled from.

---

## Domain Tags

| Tag | Covers |
|---|---|
| `adk` | Google Agent Development Kit — patterns, APIs, deployment |
| `langgraph` | LangGraph state machines, CRAG, checkpointers, edges |
| `rag` | Retrieval-augmented generation, embedders, rerankers, chunking |
| `memory` | Agent memory patterns — short-term, long-term, episodic, semantic |
| `mcp` | Model Context Protocol, MCP server design, tool schemas |
| `voice` | Voice agent patterns, BIDI streaming, session management |
| `eval` | Evaluation harnesses, LLM judges, golden sets, metrics |
| `infra` | Deployment, CI/CD, observability, caching |
| `llm` | LLM API patterns, prompt engineering, context management |

---

## Quick Start

```bash
# 1. Install Ollama (system service — required for the graph UI chat agent)
brew install ollama
ollama serve   # or open Ollama.app; runs as a menu bar service

# 2. Install dependencies
uv sync                  # core deps
make install-api         # api extras (FastAPI, sentence-transformers, ollama client)
make install-ui          # npm install for the React UI
make setup-ollama        # pull the model (default: llama3.2; set OLLAMA_MODEL to override)

# 3. Configure
cp .env.example .env     # fill in ANTHROPIC_API_KEY, NOTION_API_KEY, LINEAR_API_KEY
                         # OLLAMA_MODEL and OLLAMA_HOST are optional (see .env.example)

# 4. Open in Claude Code
code .                   # CLAUDE.md loads automatically
```

Run the graph UI:

```bash
make api   # FastAPI backend on :8000
make ui    # Vite dev server on :5173
```

Seed from existing playground research and plan docs (first run only):

```
/ingest raw/playground-docs/
```

Then query or start an agent build session:

```
/query "what's our approach to agent memory in LangGraph?"
/adk-context    # curated briefing before an ADK or LangGraph build session
```

Ongoing workflow — drop a source, ingest it:

```bash
# paste a meeting transcript to raw/meetings/2026-04-24-topic.md
/ingest raw/meetings/2026-04-24-topic.md
```

---

## Slash Commands

| Command | What it does |
|---|---|
| `/ingest <path>` | Compile a raw source into wiki pages following the full ingest checklist |
| `/query <question>` | Grounded answer from compiled wiki; optionally files the answer as a new page |
| `/lint` | Health check — orphans, dead wikilinks, stale pages, unresolved conflicts |
| `/adk-context` | Curated briefing from `adk`, `langgraph`, `memory`, `mcp` pages — inject at the start of a build session |

---

## MCP Server

```bash
uv run python mcp_server/server.py
```

Tools: `search_wiki(query, tag, limit)` · `read_page(path_or_title)` · `list_pages(tag, directory)`

Pre-configured in `.claude/settings.json` — available to Claude Code and any MCP client automatically.

---

## Related

- [`ramseywise/playground`](https://github.com/ramseywise/playground) — Agent dev repo; consumes this KB via `/adk-context` and `search_wiki`
- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Original compiled-wiki pattern
