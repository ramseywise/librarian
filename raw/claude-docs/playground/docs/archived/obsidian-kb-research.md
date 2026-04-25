# ObsidianKB — Research

**Date:** 2026-04-24
**Author:** ramsey.wise
**Purpose:** Ground truth for the obsidian-kb GitHub repo plan — a Karpathy-pattern personal knowledge base wired into Notion, Linear, and the Claude Code agent toolkit.
**Related plan:** [`plan.md`](./plan.md)

---

## 1. Karpathy's LLM Wiki Pattern

### Origin

Andrej Karpathy published a [GitHub gist titled `llm-wiki`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) in early 2026. The idea is simple: treat your personal knowledge like a software build system. Raw sources go in. An LLM compiles them into a structured wiki. The wiki is what you query.

### The Compiler Analogy

| Build system | LLM Wiki |
|---|---|
| Source code | `raw/` — immutable inputs |
| Compiler | LLM agent (Claude Code) |
| Executable | `wiki/` — compiled markdown |
| Tests | `lint` — health checks |
| Runtime | `query` — ask questions |

### Three-Layer Architecture

**`raw/`** — Immutable input drop zone. PDFs, meeting transcripts, Notion exports, Linear dumps, repo snapshots, research papers, bookmarks. Never edit files here directly. This is the append-only source of truth.

**`wiki/`** — LLM-generated, continuously updated. One `.md` file per entity, concept, or topic. Interlinked with `[[wikilinks]]`. Each page has a frontmatter summary line + tags. When a new raw source is ingested, Claude touches 10–15 wiki pages — updating summaries, adding cross-refs, flagging contradictions with existing knowledge.

**`CLAUDE.md` / `AGENTS.md`** — The schema. Tells Claude exactly how to behave as a wiki maintainer: directory layout, naming conventions, frontmatter schema, when to create new pages vs. update existing ones, what counts as a contradiction. This file is what turns a generic LLM into a disciplined knowledge worker.

### Three Core Operations

**`ingest`** — Drop a source in `raw/`. Claude reads it, writes or updates the relevant wiki pages, and flags anything that contradicts existing knowledge. A single ingest may touch many wiki pages. Knowledge is synthesised *once* at ingest time, not re-derived per query.

**`query`** — Ask questions against the compiled wiki. Answers are grounded in your accumulated structured understanding, not raw chunk retrieval. Good answers can be filed back as new wiki pages — compounding over time.

**`lint`** — Health checks. Find orphan pages (no backlinks), stale claims, internal contradictions, missing cross-references. Claude also surfaces new questions to investigate and source gaps to fill.

### Why It Beats RAG for a Personal / Team KB

Traditional RAG requires infra (vector DB, embedding pipeline, chunking strategy) and re-derives knowledge on every query from raw chunks. The wiki pattern:

- No infra — plain markdown files
- Synthesises once at ingest, not per query
- Answers are grounded in structured, interlinked understanding rather than chunk similarity
- Genuinely compounds — every ingest makes the entire wiki richer
- Works well at thousands of pages; for millions, vector search wins

The "70x cheaper than RAG" claim circulating comes from comparing embedding + vector retrieval costs vs. Claude reasoning directly over a structured markdown context. The real gain is compounding quality, not just cost.

### Future Direction (Karpathy's Hint)

Use the wiki to generate synthetic training data → fine-tune a model so it "knows" your KB in its weights. The long arc: external wiki → RAG → fine-tuned weights. Your personal knowledge base becomes your personalised model.

---

## 2. Obsidian as the Frontend

Obsidian is recommended as the "IDE" for this knowledge base, not because it's required (it's all `.md` files), but because:

- **Graph view** — visual map of how concepts interconnect via backlinks
- **`[[wikilinks]]`** — native syntax, automatically generates backlinks
- **Local-first** — the vault is just a folder on disk; Claude Code reads/writes it directly
- **Dataview plugin** — SQL-like queries over frontmatter for dashboards
- **Canvas** — visual composition of wiki nodes for planning
- **No lock-in** — if Obsidian goes away, you still have plain markdown

Obsidian is used as a **read-mostly UI**, not as the write path. Claude Code is the primary writer.

---

## 3. Community Implementations (April 2026)

A strong ecosystem has emerged around the pattern. Key repos to study before implementation:

| Repo | What it adds | Relevance |
|---|---|---|
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | Slash commands `/wiki /save /autoresearch`, persistent vault | Good UX model for Claude Code skills |
| [Pratiyush/llm-wiki](https://github.com/Pratiyush/llm-wiki) | MCP server with 12 tools (query, search, lint, sync, export), works with any MCP client | Best starting point for our MCP layer |
| [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | Local MCP server with semantic search (QMD) | Semantic search layer reference |
| [jonathanprocter/llm-wiki-notion](https://github.com/jonathanprocter/llm-wiki-notion) | Notion backend instead of Obsidian | Notion integration reference |
| [lucasastorian/llmwiki](https://github.com/lucasastorian/llmwiki) | Hosted MCP server Claude.ai connects to directly | If we want a hosted option later |
| [NicholasSpisak/second-brain](https://github.com/NicholasSpisak/second-brain) | LLM-maintained Obsidian KB with Claude Code hooks | Closest to our use case |
| [ScrapingArt/Karpathy-LLM-Wiki-Stack](https://github.com/ScrapingArt/Karpathy-LLM-Wiki-Stack) | Comprehensive Obsidian + Claude Code reference | Good architecture overview |
| [LLM Wiki v2 gist](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) | Extends pattern with agent memory lessons | Worth reading for schema design |

**Recommendation:** Start from `Pratiyush/llm-wiki` for the MCP server skeleton, use `AgriciDaniel/claude-obsidian` for the Claude Code skill/command patterns.

---

## 4. Mapping to the Current Playground Stack

### What We Already Have

The playground already has pieces of this system:

| Existing piece | Role in obsidian-kb |
|---|---|
| `librarian/` — LangGraph CRAG RAG agent | Could serve as the `query` backend for the wiki; or be retired in favour of the simpler wiki pattern for research queries |
| `playground/.claude/docs/` — existing research + plan docs | Seed content for `raw/` on day one |
| `playground/.claude/memory/` — user + project profiles | Input to `CLAUDE.md` schema |
| `adk-agent-pocs/`, `va-google-adk/`, `va-langgraph/` | Primary knowledge domains to document in the wiki |
| Obsidian vault (Dropbox, `~1GB raw PDFs`) | Already a `raw/`-like corpus — migrate into the new structure |
| `mcp_prototype/` — FastMCP MCP server | Pattern reference for our wiki MCP server |

### What's Missing / New

- A **dedicated `obsidian-kb` repo** — separate from playground (research infra, not product code)
- **Ingestion connectors** — Notion MCP, Gmail transcript parser, Linear MCP dump
- **`CLAUDE.md` schema** — tailored to our research domains (agent frameworks, ADK, LangGraph, voice, memory, RAG, MCP)
- **Output connectors** — push compiled wiki knowledge back to Linear (tickets) and Notion (docs)
- **VS Code + Claude Code wiring** — skills, hooks, and MCP config for the new repo
- **RAG search layer** — optional DuckDB FTS or lightweight embedding over the wiki for the agent builder context injection

### Key Architectural Decision: Separate Repo vs. Subfolder of Playground

**Separate repo (`obsidian-kb`)** is the right call because:
- The KB is infrastructure that *all* projects will consume — it shouldn't live inside any one project
- Obsidian needs to point its vault at a single directory; a separate repo is cleaner
- Claude Code's `CLAUDE.md` needs to be scoped to KB maintenance behaviour, not playground agent dev behaviour
- Makes it easier to selectively make the KB public or share parts of it later

---

## 5. Integration Surface

### Inputs

| Source | Mechanism | Format into `raw/` |
|---|---|---|
| Notion | Notion MCP (`notion-mcp`) | Export pages as `.md` into `raw/notion/YYYY-MM-DD/` |
| Linear | Linear MCP | Dump issues + comments as structured `.md` into `raw/linear/` |
| Gmail / meeting transcripts | Gmail MCP or manual paste | `.md` transcript files into `raw/meetings/YYYY-MM-DD/` |
| Existing `.claude/docs/` | Copy on init | Seed into `raw/playground-docs/` |
| Obsidian vault (Dropbox PDFs) | CLI script or manual | PDFs → text → `raw/pdfs/` |
| GitHub repos (playground, adk samples) | `git archive` or README dump | `raw/repos/` |
| Web research / bookmarks | Claude Code `/save` command | `raw/web/` |

### Outputs

| Target | Mechanism | Trigger |
|---|---|---|
| Linear | Linear MCP `save_issue` | `lint` surfaces an action item → Claude creates ticket |
| Notion | Notion MCP `create_page` | Wiki page reaches "stable" state → push as Notion doc |
| Agent context injection | Read wiki pages as Claude Code context | Before building a new ADK/LangGraph agent |
| RAG search (future) | DuckDB FTS or lightweight embedder over `wiki/` | `librarian` query interface |

---

## 6. VS Code + Claude Code Integration

Claude Code is the runtime. The KB lives on disk. The integration works as follows:

- **`CLAUDE.md`** in the repo root — wiki schema, domain glossary, ingest rules
- **`AGENTS.md`** (optional, Claude Code reads both) — agent-specific rules for multi-step ingest
- **Claude Code skills** — `/ingest`, `/query`, `/lint` as custom slash commands
- **MCP server** — exposes wiki tools to any MCP client (Claude.ai, other agents)
- **Hooks** — `post-tool-use` hook to auto-lint after any write to `wiki/`

This means you open the `obsidian-kb` repo in VS Code, run Claude Code, and use slash commands to drive the KB from your editor — the same UX you already use in playground.

---

## 7. Agent Builder Context (Google ADK / LangGraph)

The long-term goal: when building a new agent in playground, inject relevant wiki pages as context. Patterns:

1. **Manual**: open relevant wiki pages in VS Code, they become Claude Code file context
2. **Skill-based**: an `/adk-context` Claude Code skill that reads the wiki and injects a curated briefing before you start building
3. **MCP-based**: the wiki MCP server exposes a `search_wiki` tool that playground agents can call at runtime for self-directed knowledge retrieval
4. **Fine-tuning (future)**: use wiki content to generate synthetic QA pairs, fine-tune a model — KB becomes weights

The wiki is particularly valuable for capturing the ADK vs. LangGraph decision surface (already partially documented in `components.md` and the ADK samples analysis) — so Claude Code has grounded context on architectural tradeoffs rather than re-deriving them from general knowledge each session.

---

## 8. Open Questions / Spikes

| Question | Impact | Suggested spike |
|---|---|---|
| Should the wiki MCP server be read-only or read-write? | Security boundary for agent consumers | Start read-only; add write tools behind confirmation |
| Notion MCP vs. Notion export scripts? | Freshness vs. simplicity | Use Notion MCP for on-demand pulls; don't try to sync continuously |
| How to handle conflicting information across sources? | Wiki quality | CLAUDE.md rule: flag contradictions as a `[[conflict]]` tag, never silently overwrite |
| DuckDB FTS vs. lightweight embedding for wiki search? | Latency and cost | DuckDB FTS first (already used in playground); add embedding later |
| Obsidian vault sync (iCloud / git / Dropbox)? | Accessibility across machines | Git-based sync for the KB repo; Obsidian points at the working tree |
| Should raw PDFs (1GB Dropbox) be in the repo? | Repo size | No — keep in Dropbox, add a `scripts/ingest_pdf.py` that reads from the Dropbox path |

---

## Sources

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [LLM Wiki v2 gist (rohitg00)](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2)
- [VentureBeat — Karpathy's LLM Knowledge Base bypasses RAG](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an)
- [Beyond RAG — Level Up Coding](https://levelup.gitconnected.com/beyond-rag-how-andrej-karpathys-llm-wiki-pattern-builds-knowledge-that-actually-compounds-31a08528665e)
- [MindStudio — What Is Karpathy's LLM Wiki?](https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code)
- [Code With Seb — Claude Code + Obsidian](https://www.codewithseb.com/blog/claude-code-obsidian-second-brain-guide)
- [aimaker substack — Karpathy + Obsidian second brain](https://aimaker.substack.com/p/llm-wiki-obsidian-knowledge-base-andrej-karphaty)
- [Pratiyush/llm-wiki](https://github.com/Pratiyush/llm-wiki)
- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)
- [jonathanprocter/llm-wiki-notion](https://github.com/jonathanprocter/llm-wiki-notion)
- [ScrapingArt/Karpathy-LLM-Wiki-Stack](https://github.com/ScrapingArt/Karpathy-LLM-Wiki-Stack)
