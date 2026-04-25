# ObsidianKB — Implementation Plan

**Date:** 2026-04-24
**Author:** ramsey.wise
**Scope:** New GitHub repo (`ramseywise/obsidian-kb`) — a Karpathy-pattern personal KB wired into Notion, Linear, Gmail, and the Claude Code agent toolkit. Implemented in VS Code with Claude Code.
**Research:** [`research.md`](./research.md)

---

## Goal

A single self-contained GitHub repo that:

1. Maintains a **compiled wiki** of research knowledge as plain markdown (Karpathy pattern)
2. **Ingests** from Notion, Linear, Gmail transcripts, existing playground docs, and PDFs
3. **Outputs** to Linear (tickets) and Notion (documentation)
4. Is **queryable** via Claude Code in VS Code and (later) via a local MCP server
5. Serves as **agent-builder context** — the grounded knowledge layer for ADK / LangGraph work in playground

---

## Repo Structure

```
obsidian-kb/
├── CLAUDE.md               ← Wiki schema + ingest rules (the most important file)
├── AGENTS.md               ← Agent-specific rules for multi-step operations
├── README.md
├── .gitignore              ← Exclude raw/ large files, .env
├── .env.example
│
├── raw/                    ← Immutable input drop zone (append-only)
│   ├── notion/             ← Notion page exports (YYYY-MM-DD subdirs)
│   ├── linear/             ← Linear issue dumps
│   ├── meetings/           ← Gmail / meeting transcripts (YYYY-MM-DD)
│   ├── playground-docs/    ← Seeded from playground/.claude/docs/
│   ├── pdfs/               ← Extracted text from Dropbox PDFs
│   ├── web/                ← Saved web research
│   └── repos/              ← README / architecture dumps from key repos
│
├── wiki/                   ← LLM-compiled knowledge (Claude writes here)
│   ├── _index.md           ← Auto-generated table of contents
│   ├── _conflicts.md       ← Flagged contradictions between sources
│   ├── concepts/           ← Technology and architecture concepts
│   ├── agents/             ← Agent patterns, frameworks, decisions
│   ├── projects/           ← Per-project knowledge pages
│   ├── people/             ← Key people / authors (optional)
│   └── decisions/          ← Architecture decision records (ADRs)
│
├── scripts/
│   ├── ingest_pdf.py       ← Extract text from Dropbox PDFs → raw/pdfs/
│   ├── ingest_notion.py    ← Pull Notion pages via MCP → raw/notion/
│   ├── ingest_linear.py    ← Dump Linear issues via MCP → raw/linear/
│   ├── export_to_notion.py ← Push stable wiki pages → Notion
│   └── export_to_linear.py ← Push action items → Linear tickets
│
├── .claude/
│   ├── skills/
│   │   ├── ingest.md       ← /ingest slash command
│   │   ├── query.md        ← /query slash command
│   │   ├── lint.md         ← /lint slash command
│   │   └── adk-context.md  ← /adk-context — curated briefing for agent builds
│   └── hooks/
│       └── post-write-lint.sh  ← Auto-lint after wiki writes
│
└── mcp_server/             ← Local MCP server exposing wiki tools
    ├── server.py           ← FastMCP server
    ├── tools/
    │   ├── search.py       ← FTS search over wiki/
    │   ├── read_page.py    ← Read a specific wiki page
    │   ├── list_pages.py   ← List pages by tag or directory
    │   └── ingest.py       ← Trigger ingest from MCP client
    └── pyproject.toml
```

---

## CLAUDE.md Schema (Draft)

This is the most critical file. It defines the contract Claude Code uses when maintaining the wiki. To be expanded iteratively.

```markdown
# ObsidianKB — Wiki Schema

## Directory Rules
- `raw/` is IMMUTABLE. Never edit or delete files here.
- `wiki/` is LLM-maintained. Only Claude writes here (no manual edits except corrections).
- When ingesting a new raw source, update all relevant wiki pages — do not create one-off summary files.

## Page Naming
- Use kebab-case: `google-adk-overview.md`, `langgraph-state-management.md`
- One page per entity/concept. If a concept grows large, split with `[[See also: ...]]` links.
- Entity pages (agents, tools, frameworks) go in `wiki/agents/` or `wiki/concepts/`.
- Project pages go in `wiki/projects/`.
- Architecture decisions go in `wiki/decisions/` with date prefix: `2026-04-24-adk-vs-langgraph.md`.

## Frontmatter (required on every wiki page)
---
title: Human-readable title
tags: [tag1, tag2]          # from: adk, langgraph, rag, memory, mcp, voice, eval, infra
summary: One sentence — what this page is about
updated: YYYY-MM-DD
sources: [raw/path/to/source.md]
---

## Wikilinks
- Always cross-reference related pages with [[Page Title]] syntax.
- After ingesting a source, scan existing pages and add backlinks where relevant.

## Contradiction Handling
- If a new source contradicts an existing wiki claim, DO NOT silently overwrite.
- Add the conflict to `wiki/_conflicts.md` with both claims and source citations.
- Mark the affected page with tag: `conflict`.

## Ingest Checklist (run for every new raw source)
1. Read the source fully before writing anything.
2. Identify all entities, concepts, and decisions mentioned.
3. For each: find the existing wiki page or create a new one.
4. Update summaries, add new facts, note contradictions.
5. Update `wiki/_index.md` if a new page was created.
6. Check for orphan pages (no backlinks) and link appropriately.

## Domains (first-class tags)
- `adk` — Google Agent Development Kit patterns and APIs
- `langgraph` — LangGraph state machines, CRAG, checkpointers
- `rag` — Retrieval-augmented generation, embedders, rerankers
- `memory` — Agent memory patterns (short-term, long-term, episodic, semantic)
- `mcp` — Model Context Protocol, MCP servers, tool design
- `voice` — Voice agent patterns, BIDI streaming, session management
- `eval` — Evaluation harnesses, LLM judges, golden sets
- `infra` — Deployment, CI/CD, observability, caching
- `notion` — Sourced from Notion
- `linear` — Sourced from Linear
```

---

## Claude Code Skills (Slash Commands)

### `/ingest <path-or-url>`
Triggered manually or by dropping a file in `raw/`. Claude reads the source, identifies affected wiki pages, updates them per the `CLAUDE.md` ingest checklist, and reports what changed.

### `/query <question>`
Ask a question against the compiled wiki. Claude reads relevant pages (via filename + tag matching) and gives a grounded answer. Optionally files the answer back as a new wiki page.

### `/lint`
Health check. Finds orphan pages, stale `updated` dates, missing frontmatter, pages with `conflict` tag that need resolution, and cross-references that could be added. Outputs a prioritised list of fixes.

### `/adk-context`
Purpose-built for agent building sessions. Reads the `adk`, `langgraph`, `memory`, and `mcp` tagged wiki pages and outputs a structured briefing: key patterns, current decisions, open questions, relevant code pointers. Inject this at the start of a playground Claude Code session.

---

## Integration Architecture

### Input Pipeline

```
Notion ──MCP──► ingest_notion.py ──► raw/notion/YYYY-MM-DD/ ──┐
Linear ──MCP──► ingest_linear.py ──► raw/linear/              ──┤
Gmail ──────────► paste transcript ──► raw/meetings/YYYY-MM-DD/ ┤──► /ingest ──► wiki/
Playground docs ► one-time seed  ──► raw/playground-docs/    ──┤
Dropbox PDFs ──► ingest_pdf.py   ──► raw/pdfs/               ──┤
Web / bookmarks ► /save command  ──► raw/web/                ──┘
```

### Output Pipeline

```
wiki/ ──► /lint finds action item ──► export_to_linear.py ──MCP──► Linear ticket
wiki/ ──► page reaches stable     ──► export_to_notion.py ──MCP──► Notion page
wiki/ ──► /adk-context            ──► Claude Code context injection (playground)
wiki/ ──► mcp_server search tool  ──► any MCP client (Claude.ai, agent runtime)
```

---

## VS Code + Claude Code Setup

### Step 1 — Open the repo in VS Code

```bash
git clone git@github.com:ramseywise/obsidian-kb.git
cd obsidian-kb
code .
```

### Step 2 — Point Obsidian at the repo

Open Obsidian → Open folder as vault → select `obsidian-kb/` (or just `wiki/` if you prefer a cleaner vault). Install plugins: Dataview, Templater, Graph Analysis.

### Step 3 — Configure Claude Code

The `CLAUDE.md` at the repo root is automatically loaded by Claude Code when you open the repo. No additional setup needed — Claude Code will behave as a wiki maintainer when you open this repo.

### Step 4 — Add MCP connections (Notion + Linear)

In your VS Code Claude Code settings (`.claude/settings.json` or `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" }
    },
    "linear": {
      "command": "npx",
      "args": ["-y", "linear-mcp-server"],
      "env": { "LINEAR_API_KEY": "${LINEAR_API_KEY}" }
    },
    "obsidian-kb": {
      "command": "uv",
      "args": ["run", "python", "mcp_server/server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Store keys in `.env` (gitignored). Source via `direnv` or `dotenv`.

### Step 5 — Install Claude Code skills

Copy `.claude/skills/` into place. The skills are already in the repo — Claude Code will discover them via the skills directory. They appear as `/ingest`, `/query`, `/lint`, `/adk-context` in Claude Code's command palette.

---

## Phased Rollout

### Phase 1 — Core Structure (Week 1)

Objective: Repo exists, CLAUDE.md works, first wiki pages compiled from existing docs.

- [ ] Create `ramseywise/obsidian-kb` on GitHub (private)
- [ ] Write `CLAUDE.md` schema (start from draft above, refine)
- [ ] Set up `raw/`, `wiki/` directory structure
- [ ] Seed `raw/playground-docs/` from `playground/.claude/docs/` (copy all existing research + plans)
- [ ] Run first `/ingest` over seeded docs — validate Claude follows the schema correctly
- [ ] Point Obsidian vault at `obsidian-kb/`
- [ ] Verify `[[wikilinks]]` and backlinks render in Obsidian graph view

**Success:** 10+ wiki pages compiled from existing docs. Obsidian graph view shows meaningful connections. Claude Code `/query` gives grounded answers about agent architecture decisions.

### Phase 2 — Input Connectors (Week 2)

Objective: Live feeds from Notion and Linear into `raw/`.

- [ ] Configure Notion MCP in Claude Code settings; test page pull
- [ ] Write `scripts/ingest_notion.py` — pulls a Notion page by URL → `raw/notion/`
- [ ] Configure Linear MCP; test issue dump
- [ ] Write `scripts/ingest_linear.py` — dumps open issues for a project → `raw/linear/`
- [ ] Write `scripts/ingest_pdf.py` — reads from Dropbox path, extracts text → `raw/pdfs/`
- [ ] Establish meeting transcript convention: paste → `raw/meetings/YYYY-MM-DD-topic.md` → `/ingest`
- [ ] Run `/lint` — fix any orphan pages or frontmatter issues from Phase 1

**Success:** Can pull a Notion page and a Linear project dump, ingest them, and see new wiki pages or updates appear within one `/ingest` run.

### Phase 3 — Output Connectors + MCP Server (Week 3)

Objective: Wiki can push to Linear and Notion; wiki is queryable via MCP.

- [ ] Write `scripts/export_to_linear.py` — takes a wiki action item → creates Linear ticket via MCP
- [ ] Write `scripts/export_to_notion.py` — takes a stable wiki page → pushes to Notion as a page
- [ ] Build `mcp_server/server.py` (FastMCP) with tools: `search_wiki`, `read_page`, `list_pages`
- [ ] Add `mcp_server` to Claude Code MCP config
- [ ] Write `/adk-context` skill and test it at the start of a playground session
- [ ] Add `post-write-lint.sh` hook — runs `/lint --quick` after any Claude wiki write

**Success:** Can export a research summary to Notion with one command. Linear ticket created from a wiki action item. `/adk-context` produces a useful briefing before an ADK build session.

### Phase 4 — RAG Search Layer (Week 4+)

Objective: Wiki is searchable by agents at runtime.

- [ ] Add DuckDB FTS index over `wiki/` to `mcp_server` — `search_wiki` tool does keyword + tag filtering
- [ ] Optionally: add lightweight embedding layer (MiniLM — already in playground) for semantic search
- [ ] Expose `search_wiki` to playground agents — test injecting wiki context into librarian queries
- [ ] Write `/query` skill that uses the MCP search tool rather than raw file reads
- [ ] Evaluate: does wiki-grounded context improve ADK agent builds? Qualitative review.

**Success:** A playground agent (ADK or LangGraph) can call `search_wiki("voice session state management")` and get a grounded, curated answer from the compiled wiki — not a raw vector chunk.

### Phase 5 — Fine-Tuning Prep (Future)

- [ ] Write a script that generates synthetic QA pairs from wiki pages
- [ ] Evaluate fine-tuning a small model (Haiku or local) on the KB
- [ ] Explore using wiki as a CLAUDE.md bootstrap for new agent repos

---

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.12+ | Matches playground stack |
| Package manager | uv | Matches playground |
| MCP server | FastMCP | Already used in `mcp_prototype/` |
| FTS search | DuckDB | Already used in playground (librarian) |
| Semantic search (optional) | MiniLM (in-process) | Already in librarian; no infra |
| Notion connector | `@notionhq/notion-mcp-server` | Official MCP server |
| Linear connector | `linear-mcp-server` | Community MCP server |
| PDF extraction | `pdfplumber` or `pypdf` | Lightweight, no ML needed for text extraction |
| VS Code integration | Claude Code skills + MCP | Native Claude Code pattern |
| Obsidian frontend | Obsidian desktop + Dataview | Local vault, no lock-in |
| Sync | Git | Simple, works with VS Code |

---

## Constraints

- Raw PDFs (1GB Dropbox) stay in Dropbox — not committed to git. `scripts/ingest_pdf.py` reads from the Dropbox path via `.env: DROPBOX_PDF_PATH`.
- No vector DB infra in Phase 1-3. DuckDB FTS first; embedding only if FTS quality is insufficient.
- `wiki/` is Claude-maintained. Avoid manual edits except corrections — manual edits break the "compiled from raw" guarantee.
- Repo stays private initially. Can selectively publish `wiki/concepts/` later if useful.
- No continuous sync with Notion/Linear — pull on demand. Continuous sync creates too much noise.

---

## Open Questions to Resolve in Phase 1

1. **Wiki MCP server — read-only or read-write?** Start read-only. Adds write tools behind confirmation later.
2. **Obsidian vault root** — point at `obsidian-kb/` root or just `wiki/`? Recommend `wiki/` for a cleaner vault; `raw/` doesn't need to render in Obsidian.
3. **Conflict resolution policy** — flag in `_conflicts.md` and tag the page? Yes — do not silently overwrite. Resolve manually during `/lint` runs.
4. **`ingest` granularity** — whole Notion database or individual pages? Start with individual pages on demand.

---

## Immediate Next Steps

1. **Create the repo** — `gh repo create ramseywise/obsidian-kb --private`
2. **Write `CLAUDE.md`** — expand the draft above, validate with a test ingest of `playground/.claude/docs/components.md`
3. **Seed `raw/playground-docs/`** — copy all existing `.claude/docs/` files
4. **First `/ingest` run** — let Claude compile the first wiki pages, review quality
5. **Refine `CLAUDE.md`** based on what Claude does vs. what you expected
6. **Phase 2** — add Notion MCP config and test a live pull

The `CLAUDE.md` is the highest-leverage investment. Iterate on it aggressively in the first week before building connectors.
