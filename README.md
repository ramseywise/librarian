# Librarian

A compiled knowledge base for AI engineering — following the [Karpathy LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Raw sources (docs, sessions, meetings, papers, books) go into `data/raw/` (append-only). Claude compiles them into `data/wiki/` — structured, interlinked, contradiction-flagged. A local MCP server exposes the wiki to any agent at runtime.

**Mental model:** `data/raw/` = source code. Claude = compiler. `data/wiki/` = executable output.

---

## Why

Agent engineering accumulates a lot of hard-won knowledge: which framework to use and when, what thresholds actually work in production, which patterns look good in docs but fail at runtime. Without a system, you re-derive these decisions from scratch on every project.

Librarian captures that knowledge once, structures it for retrieval, and surfaces it before you start — via slash commands in Claude Code, MCP tools in running agents, or a graph UI for exploration.

---

## Architecture

```
Sessions ──────────────────────────────► data/raw/sessions/    ─┐
Docs (.claude/skills/, CLAUDE.md) ─────► data/raw/claude-docs/  │
Repo scraper (src/librarian/ingest/scrape_repos.py) ─────► data/raw/repos/        │
Google Drive ──MCP──────────────────────► data/raw/gdrive/        ├──► /ingest ──► data/wiki/
Notion ────────MCP──────────────────────► data/raw/notion/        │
Meetings, PDFs, web, books, articles ──► data/raw/*/            ─┘

                                            data/wiki/
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                    MCP server           /adk-context       graph UI
                  (search_wiki,        (agent builder     (React Flow graph
                   read_page,            briefing)         + chat agent)
                   get_domain_briefing)
                          │
                          ▼
               Claude Code · custom agents · any MCP client
```

**Key invariants:**
- `data/raw/` is append-only — never edit after drop
- `data/wiki/` is Claude-maintained — humans correct factual errors only
- Conflicts are flagged, never silently overwritten
- `data/wiki/private/` is gitignored — company-specific pages live here locally

---

## Use Cases

| Use case | How |
|---|---|
| **Pre-build briefing** | `/adk-context` or `get_domain_briefing("langgraph")` — load accumulated patterns before starting a new agent |
| **Grounded Q&A** | `/query "what's our approach to agent memory?"` — answers from your own compiled experience, not generic docs |
| **Decision records** | Ingest an ADR or meeting note → wiki auto-creates a `type: decision` page with tradeoffs and cross-links |
| **Runtime agent knowledge** | Wire `search_wiki` + `read_page` as MCP tools in any agent — they self-brief from the KB at query time |
| **Research synthesis** | Drop papers, book quotes, article captures into `data/raw/` → ingest compiles contradictions, cross-links, and concept pages |
| **Shared retrieval API** | One compiled wiki served over MCP and the HTTP API to every agent that needs it |
| **Codebase onboarding** | Scrape a new repo's CLAUDE.md + docs → ingest → instant grounded answers about architecture decisions |

---

## TL;DR — Run Ingestion

```
/ingest              # full pipeline: Notion + GDrive + sessions/docs scrape + repos → wiki
/lint                # health check after ingesting
```

That's it — this is the command people forget. Full pipeline mode pulls Notion + GDrive via
MCP, scrapes local sources (`make scrape` + `src/librarian/ingest/scrape_repos.py`), and compiles every changed
file into `data/wiki/` in one shot. Other variants:

```
/ingest data/raw/sessions/    # targeted compile of one data/raw/ dir
/ingest resolve          # walk through flagged conflicts in data/wiki/_conflicts.md
/seed-kb --ingest        # scrape this machine's sessions/docs/bookmarks, then ingest
```

---

## Quick Start

```bash
# 1. Install
uv sync                  # core deps
make install-api         # FastAPI + sentence-transformers + Anthropic client
make install-ui          # npm install for React UI

# 2. Configure
cp .env.example .env
# Fill in:
#   ANTHROPIC_API_KEY   — required for /ingest, /query, /lint slash commands
#                         and for the graph UI chat agent (#96)
#   NOTION_API_KEY      — optional, for Notion connector
#   LINEAR_API_KEY      — optional, for Linear connector

# 3. Open in Claude Code
code .                   # CLAUDE.md loads automatically; MCP server auto-starts
```

**First run — seed from your existing docs:**

```
/ingest data/raw/claude-docs/     # compile any existing .claude/ docs
/ingest data/raw/sessions/        # compile Claude Code session history (batches of 20)
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
# data/raw/meetings/2026-07-05-architecture-review.md

/ingest data/raw/meetings/2026-07-05-architecture-review.md
```

### Weekly (5–10 minutes)

Full sync — pull new Notion/Drive content, scrape sessions, compile everything new:

```
/ingest          # full pipeline: Notion + GDrive + sessions + repos → wiki
/lint            # health check: orphans, stale pages, dead links, unresolved conflicts
```

Optionally scrape repos you're actively working on:

```bash
# Add repos to data/raw/repos/repos.txt, then:
uv run librarian scrape repos
/ingest data/raw/repos/
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
/code-review      # correctness + simplification pass
```

The `contracts` review dimension (via `uv run --project ~/workspace/guacamayo review-cli run`) checks the diff against `SANYI.md` automatically.

---

## Components

| Component | What it does |
|---|---|
| `data/raw/` | Append-only input drop zone — sessions, docs, meetings, PDFs, books, articles, repo scrapes |
| `data/wiki/` | LLM-compiled knowledge — one `.md` per concept, pattern, or decision; structured frontmatter, wikilinks |
| `data/wiki/private/` | Company-specific pages, gitignored — same format, local only |
| `CLAUDE.md` | Compiler contract — schema rules, ingest checklist, conflict policy, domain taxonomy |
| `src/librarian/` | The Python package behind the `librarian` CLI: `wiki/` (parser, telemetry, graph, rename, relinker), `ingest/` (scrapers, gate, raw lint), `courses/` (catalog, curriculum), `retrieval/` (embeddings), `config.py` (paths and settings, `LIBRARIAN_ROOT`). Run `uv run librarian --help` |
| `src/librarian/mcp/` | FastMCP wrappers over `librarian.retrieval`: `search_wiki`, `read_page`, `list_domain`, `list_pages`, `get_domain_briefing`, plus the codemap tools |
| `src/librarian/api/` | FastAPI — wiki graph API, DuckDB-cached embeddings + UMAP layout, streaming Anthropic chat agent |
| `app/` | React + Vite graph UI — React Flow (`@xyflow/react`) force-directed graph, chat panel, live wiki watch |
| `.claude/skills/` | `/ingest`, `/query`, `/lint`, `/adk-context`, `/seed-kb` — Claude Code slash commands |

---

## MCP Server

Pre-configured in `.claude/settings.json` — available to Claude Code and any MCP client automatically.

```bash
uv run librarian mcp
```

**Tools:**

| Tool | Description |
|---|---|
| `search_wiki(query, domain, limit, expand)` | Hybrid search: FTS + cosine similarity + backlink rank. `domain` matches directory **or** domain tag. `expand=True` also returns pages one typed relationship hop away (spike) |
| `read_page(path_or_title)` | Read a page by path or fuzzy title match |
| `list_domain(domain)` | All pages in a domain, sorted by backlink count |
| `list_pages(tag, directory)` | Filter pages by tag or directory |
| `get_domain_briefing(domain)` | All pages in a domain concatenated — decisions first, then patterns, concepts |

**Hybrid search** blends three signals: text match relevance (FTS), semantic similarity (sentence-transformers, if installed), and inbound backlink count. Falls back to FTS-only if sentence-transformers is absent.

**Graph-aware retrieval** — `expand=True` walks the *typed* relationship subgraph
(`prerequisite-for` / `extends`) one hop out from the results to answer "what else do I need
to understand these hits?" It deliberately ignores untyped wikilinks: those run ~24 per page
and would drown a context window, while typed edges are sparse and author-asserted. The
rationale, measurements, and rejected alternatives are in
[Wiki Graph Engineering](data/wiki/meta/wiki-graph-engineering.md).

---

## Graph UI

```bash
make api   # FastAPI backend on :8000 (wiki graph + semantic edges + UMAP + chat)
make ui    # Vite dev server on :5173
```

The backend caches embeddings and UMAP layout in DuckDB — only recomputed when wiki pages change.

### Deploy (one image, one port)

```bash
docker compose up --build   # API + built UI on :8000; reads .env if present
```

`data/` is mounted read-only (the private wiki and course trees are masked with empty tmpfs mounts);
indexes, caches, logs and flashcard results go to the `librarian-var` volume (`LIBRARIAN_STATE_DIR`).
Set `LIBRARIAN_API_TOKEN` in `.env`: every `/api` route and `/ws` then need `Authorization: Bearer <token>`,
and the web UI asks for the token once and keeps it in localStorage. `/healthz` and `/readyz` stay open.
Chat is limited per process (`LIBRARIAN_CHAT_RATE_LIMIT`, `LIBRARIAN_CHAT_DAILY_BUDGET_USD`); see `.env.example`.

### Run with Docker

```bash
echo 'LIBRARIAN_API_TOKEN=<a long random string>' >> .env
make app            # creates the empty private mountpoints, then `docker compose up`
make app-build      # same, rebuilding the image
```

- `LIBRARIAN_API_TOKEN` is required. The container binds `0.0.0.0`, and `librarian api` refuses to
  bind a non-loopback host without a token unless you pass `--insecure` (serves unauthenticated).
- The image sets `LIBRARIAN_PUBLIC=true`, so `private/` wiki and course trees are never read,
  indexed or served, whatever is on disk (the compose tmpfs masks are a second lock).

### Courses

The **Courses** tab (`#/courses`) is a learning UI over `data/courses/`: a course catalog,
module/lesson sidebar with progress, rendered lessons (GFM, KaTeX math, images, copyable
code), on-page TOC, and lesson search. Lessons are linked to wiki pages — explicit
`wiki: [page-id]` frontmatter, inline `[[wikilinks]]`, and verbatim mentions of multi-word
wiki titles — so "Concepts in the graph" jumps to the node in the graph, and a graph
node's detail panel lists the lessons that cover it. Progress is per-browser (localStorage).

Content is plain markdown, laid out `<course>/<module>/[section dirs/]<lesson>.md` with
`_course.md` / `_module.md` frontmatter (`title`, `summary`, `order`). Lessons are authored
here, directly in `data/courses/`.

Lecture decks for every course are built here from `data/courses/<course>/<module>/slides/deck.yaml`
and the module's `assets/`: `make slides PILLAR=<course>/<module> [PREVIEW=1] [PDF=1]`, or
`make slides-all`. Built files are gitignored. See `.claude/skills/slides/SKILL.md`.

Each `slides/deck.yaml` in a source module also becomes flashcards: one card per slide with a
takeaway (front = `recall` or `title`, back = `takeaway`), attached to the lesson its
`source:` names. Study them from a module or lesson with "Study N flashcards" (flip, next,
shuffle). There is no scheduling.

---

## Wiki Invariants

1. **One page per concept** — find the existing page or create one; never scatter knowledge
2. **Conflicts are flagged, not overwritten** — contradictions go to `data/wiki/_conflicts.md` for human review
3. **Every page has at least one backlink** — orphan pages are a lint error
4. **`updated:` is set on every write** — stale pages (>60 days) are surfaced by `/lint`
5. **Sources are cited** — every wiki page lists the `data/raw/` files it was compiled from
6. **Private stays private** — company-specific pages go to `data/wiki/private/` (gitignored), not `data/wiki/projects/`

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
| `data/raw/sessions/` | Claude Code + Codex session JSONL | `src/librarian/ingest/scrape_sessions.py` |
| `data/raw/claude-docs/` | `.claude/` docs from workspace projects | `src/librarian/ingest/scrape_claude_docs.py` |
| `data/raw/repos/` | CLAUDE.md, skills, docs from configured repos | `src/librarian/ingest/scrape_repos.py` + `repos.txt` |
| `data/raw/notion/` | Notion pages | MCP connector |
| `data/raw/gdrive/` | Google Drive docs | MCP connector |
| `data/raw/linear/` | Linear issues + projects | `src/librarian/ingest/ingest_linear.py` |
| `data/raw/pdfs/` | PDF text extracts | `src/librarian/ingest/ingest_pdf.py` |
| `data/raw/meetings/` | Meeting transcripts | Manual drop |
| `data/raw/web/` | Web article captures | Manual drop or URL mode |
| `data/raw/books/` | Book quotes + notes | Manual drop (see `CLAUDE.md` for format) |
| `data/raw/articles/` | Article highlights + notes | Manual drop or URL mode |

---

## Slash Commands

| Command | What it does |
|---|---|
| `/ingest [path \| url \| resolve]` | Compile raw sources → wiki; `resolve` mode for conflict resolution |
| `/query <question>` | Grounded answer from compiled wiki; optionally files answer as new page |
| `/lint` | Health check — orphans, dead links, stale pages, unresolved conflicts |
| `/adk-context [domain]` | Curated briefing for a build session |
| `/seed-kb` | Scrape sessions + docs then prompt to ingest |

---

## Architecture Governance (SANYI)

The repo includes the [SANYI change-contract system](data/wiki/meta/sanyi-change-contract.md) for detecting architectural decay across PRs.

Layers for this repo:
- **Bianyi** (ever-changing): wiki page content, ingest prompts, domain taxonomy config
- **Jianyi** (bounded): MCP tool schemas, wiki frontmatter spec, manifest format
- **Buyi** (invariant): source attribution (never serve without grounded source), manifest dedup, conflict flagging, MCP read-only constraint

SANYI.md is the hand-maintained contract; `CLAUDE.md` carries the ingest checklist and conflict policy. The `contracts` review dimension reads `SANYI.md` and enforces all three layers automatically on every diff.

---

## Related

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — original compiled-wiki pattern
