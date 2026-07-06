# Librarian

A compiled knowledge base for AI engineering — following the [Karpathy LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Raw sources (docs, sessions, meetings, papers, books) go into `raw/` (append-only). Claude compiles them into `wiki/` — structured, interlinked, contradiction-flagged. A local MCP server exposes the wiki to any agent at runtime.

**Mental model:** `raw/` = source code. Claude = compiler. `wiki/` = executable output.

---

## Why

Agent engineering accumulates a lot of hard-won knowledge: which framework to use and when, what thresholds actually work in production, which patterns look good in docs but fail at runtime. Without a system, you re-derive these decisions from scratch on every project.

Librarian captures that knowledge once, structures it for retrieval, and surfaces it before you start — via slash commands in Claude Code, MCP tools in running agents, or a graph UI for exploration.

---

## Architecture

```
Sessions ──────────────────────────────► raw/sessions/    ─┐
Docs (.claude/skills/, CLAUDE.md) ─────► raw/claude-docs/  │
Repo scraper (etl/scrape_repos.py) ─────► raw/repos/        │
Google Drive ──MCP──────────────────────► raw/gdrive/        ├──► /ingest ──► wiki/
Notion ────────MCP──────────────────────► raw/notion/        │
Meetings, PDFs, web, books, articles ──► raw/*/            ─┘

                                            wiki/
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                    MCP server           /adk-context       graph UI
                  (search_wiki,        (agent builder     (React + Cytoscape
                   read_page,            briefing)         + chat agent)
                   get_domain_briefing)
                          │
                          ▼
               Claude Code · custom agents · any MCP client
```

**Key invariants:**
- `raw/` is append-only — never edit after drop
- `wiki/` is Claude-maintained — humans correct factual errors only
- Conflicts are flagged, never silently overwritten
- `wiki/private/` is gitignored — company-specific pages live here locally

---

## Use Cases

| Use case | How |
|---|---|
| **Pre-build briefing** | `/adk-context` or `get_domain_briefing("langgraph")` — load accumulated patterns before starting a new agent |
| **Grounded Q&A** | `/query "what's our approach to agent memory?"` — answers from your own compiled experience, not generic docs |
| **Decision records** | Ingest an ADR or meeting note → wiki auto-creates a `type: decision` page with tradeoffs and cross-links |
| **Runtime agent knowledge** | Wire `search_wiki` + `read_page` as MCP tools in any agent — they self-brief from the KB at query time |
| **Research synthesis** | Drop papers, book quotes, article captures into `raw/` → ingest compiles contradictions, cross-links, and concept pages |
| **Team knowledge base** | Shared wiki with multi-user ingest; MCP server as team-wide retrieval API |
| **Codebase onboarding** | Scrape a new repo's CLAUDE.md + docs → ingest → instant grounded answers about architecture decisions |

---

## Quick Start

```bash
# 1. Install
uv sync                  # core deps
make install-api         # FastAPI + sentence-transformers + Gemini client
make install-ui          # npm install for React UI

# 2. Configure
cp .env.example .env
# Fill in:
#   ANTHROPIC_API_KEY   — required for /ingest, /query, /lint slash commands
#   GOOGLE_API_KEY      — required for graph UI chat agent (free at aistudio.google.com)
#   NOTION_API_KEY      — optional, for Notion connector
#   LINEAR_API_KEY      — optional, for Linear connector

# 3. Open in Claude Code
code .                   # CLAUDE.md loads automatically; MCP server auto-starts
```

**First run — seed from your existing docs:**

```
/ingest raw/claude-docs/     # compile any existing .claude/ docs
/ingest raw/sessions/        # compile Claude Code session history (batches of 20)
```

**Then query:**

```
/query "what's the right approach for agent memory with LangGraph?"
/adk-context    # curated briefing before any ADK or LangGraph build session
```

---

## Recommended Workflow

### Daily (30 seconds)

Drop any new raw source and ingest it immediately:

```bash
# Example: paste a meeting transcript
# raw/meetings/2026-07-05-architecture-review.md

/ingest raw/meetings/2026-07-05-architecture-review.md
```

### Weekly (5–10 minutes)

Full sync — pull new Notion/Drive content, scrape sessions, compile everything new:

```
/ingest          # full pipeline: Notion + GDrive + sessions + repos → wiki
/lint            # health check: orphans, stale pages, dead links, unresolved conflicts
```

Optionally scrape repos you're actively working on:

```bash
# Add repos to raw/repos/repos.txt, then:
uv run python etl/scrape_repos.py
/ingest raw/repos/
```

### Before any agent build session

```
/adk-context                      # briefing: decisions + patterns + concepts for your domain
# or
get_domain_briefing("langgraph")  # via MCP in the agent itself
```

### When you hit a conflict

```
/ingest resolve   # guided conflict resolution: read both claims, pick correct, mark resolved
/lint             # confirm all conflicts closed
```

### Architecture governance (PRs)

```
/sanyi review     # check if the diff violates the SANYI change contract
/code-review      # correctness + simplification pass
```

---

## Components

| Component | What it does |
|---|---|
| `raw/` | Append-only input drop zone — sessions, docs, meetings, PDFs, books, articles, repo scrapes |
| `wiki/` | LLM-compiled knowledge — one `.md` per concept, pattern, or decision; structured frontmatter, wikilinks |
| `wiki/private/` | Company-specific pages, gitignored — same format, local only |
| `CLAUDE.md` | Compiler contract — schema rules, ingest checklist, conflict policy, domain taxonomy |
| `etl/` | Scrapers: `scrape_sessions.py` (Claude/Codex), `scrape_claude_docs.py` (workspace docs), `scrape_repos.py` (repos) |
| `app/mcp_server/` | FastMCP server: `search_wiki` (hybrid FTS + semantic + backlink rank), `read_page`, `list_domain`, `get_domain_briefing` |
| `app/backend/` | FastAPI — wiki graph API, DuckDB-cached embeddings + UMAP layout, streaming Gemini chat agent |
| `app/ui/` | React + Vite graph UI — Cytoscape.js force-directed graph, chat panel, live wiki watch |
| `.claude/skills/` | `/ingest`, `/query`, `/lint`, `/adk-context`, `/seed-kb`, `/sanyi` — Claude Code slash commands |

---

## MCP Server

Pre-configured in `.claude/settings.json` — available to Claude Code and any MCP client automatically.

```bash
uv run python app/mcp_server/server.py
```

**Tools:**

| Tool | Description |
|---|---|
| `search_wiki(query, domain, limit)` | Hybrid search: FTS + cosine similarity + backlink rank |
| `read_page(path_or_title)` | Read a page by path or fuzzy title match |
| `list_domain(domain)` | All pages in a domain, sorted by backlink count |
| `list_pages(tag, directory)` | Filter pages by tag or directory |
| `get_domain_briefing(domain)` | All pages in a domain concatenated — decisions first, then patterns, concepts |

**Hybrid search** blends three signals: text match relevance (FTS), semantic similarity (sentence-transformers, if installed), and inbound backlink count. Falls back to FTS-only if sentence-transformers is absent.

---

## Graph UI

```bash
make api   # FastAPI backend on :8000 (wiki graph + semantic edges + UMAP + chat)
make ui    # Vite dev server on :5173
```

The backend caches embeddings and UMAP layout in DuckDB — only recomputed when wiki pages change.

---

## Wiki Invariants

1. **One page per concept** — find the existing page or create one; never scatter knowledge
2. **Conflicts are flagged, not overwritten** — contradictions go to `wiki/_conflicts.md` for human review
3. **Every page has at least one backlink** — orphan pages are a lint error
4. **`updated:` is set on every write** — stale pages (>60 days) are surfaced by `/lint`
5. **Sources are cited** — every wiki page lists the `raw/` files it was compiled from
6. **Private stays private** — company-specific pages go to `wiki/private/` (gitignored), not `wiki/projects/`

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
| `deep-agents` | Deep Agents harness — middleware, StateBackend, StoreBackend |
| `context-management` | Prefix caching, session compaction, history pruning |

---

## Raw Source Types

| Directory | Source | Scraper |
|---|---|---|
| `raw/sessions/` | Claude Code + Codex session JSONL | `etl/scrape_sessions.py` |
| `raw/claude-docs/` | `.claude/` docs from workspace projects | `etl/scrape_claude_docs.py` |
| `raw/repos/` | CLAUDE.md, skills, docs from configured repos | `etl/scrape_repos.py` + `repos.txt` |
| `raw/notion/` | Notion pages | MCP connector |
| `raw/gdrive/` | Google Drive docs | MCP connector |
| `raw/linear/` | Linear issues + projects | `etl/ingest_linear.py` |
| `raw/pdfs/` | PDF text extracts | `etl/ingest_pdf.py` |
| `raw/meetings/` | Meeting transcripts | Manual drop |
| `raw/web/` | Web article captures | Manual drop or URL mode |
| `raw/books/` | Book quotes + notes | Manual drop (see `CLAUDE.md` for format) |
| `raw/articles/` | Article highlights + notes | Manual drop or URL mode |

---

## Slash Commands

| Command | What it does |
|---|---|
| `/ingest [path \| url \| resolve]` | Compile raw sources → wiki; `resolve` mode for conflict resolution |
| `/query <question>` | Grounded answer from compiled wiki; optionally files answer as new page |
| `/lint` | Health check — orphans, dead links, stale pages, unresolved conflicts |
| `/adk-context [domain]` | Curated briefing for a build session |
| `/seed-kb` | Scrape sessions + docs then prompt to ingest |
| `/sanyi [init \| review \| audit]` | Change-contract governance — detect cross-layer violations |

---

## Architecture Governance (SANYI)

The repo includes the [SANYI change-contract system](wiki/meta/sanyi-change-contract-system.md) for detecting architectural decay across PRs.

Layers for this repo:
- **Bianyi** (ever-changing): wiki page content, ingest prompts, domain taxonomy config
- **Jianyi** (bounded): MCP tool schemas, wiki frontmatter spec, manifest format
- **Buyi** (invariant): source attribution (never serve without grounded source), manifest dedup, conflict flagging, MCP read-only constraint

```
/sanyi init     # create SANYI.md contract
/sanyi review   # check a diff against the contract
/sanyi audit    # full repo health check
```

---

## Related

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — original compiled-wiki pattern
