---
title: Karpathy LLM Wiki Pattern
tags: [llm, concept]
summary: The compiler analogy for personal knowledge bases — raw sources in, LLM compiles them into structured interlinked wiki pages, no vector infra needed.
updated: 2026-08-03
sources:
  - raw/playground-docs/obsidian-kb-research.md
---

# Karpathy LLM Wiki Pattern

Andrej Karpathy published the [llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) in early 2026. The core insight: treat personal knowledge like a software build system.

## The Compiler Analogy

| Build system | LLM Wiki |
|---|---|
| Source code | `raw/` — immutable inputs |
| Compiler | LLM agent (Claude Code) |
| Executable | `wiki/` — compiled markdown |
| Tests | `lint` — health checks |
| Runtime | `query` — ask questions |

## Three-Layer Architecture

**`raw/`** — Immutable input drop zone. PDFs, meeting transcripts, Notion exports, Linear dumps, repo snapshots. Never edit files here. Append-only source of truth.

**`wiki/`** — LLM-generated, continuously updated. One `.md` file per entity, concept, or topic. Interlinked with wikilinks. Each page has frontmatter summary + tags. A single ingest may touch 10–15 wiki pages.

**`CLAUDE.md`** — The schema. Tells the LLM exactly how to behave as wiki maintainer: directory layout, naming conventions, frontmatter schema, when to create vs. update pages, what counts as a contradiction.

## Three Core Operations

**`ingest`** — Drop a source in `raw/`. Claude reads it, writes/updates wiki pages, flags contradictions. Knowledge synthesised once at ingest time, not re-derived per query.

**`query`** — Ask questions against the compiled wiki. Answers grounded in accumulated structured understanding. Good answers can be filed as new wiki pages — compounding over time.

**`lint`** — Health checks. Find orphan pages, stale claims, internal contradictions, missing cross-references. Also surfaces new questions and source gaps.

## Why It Beats RAG for a Personal KB

Traditional RAG requires infra (vector DB, embedding pipeline, chunking strategy) and re-derives knowledge on every query from raw chunks. The wiki pattern:

- No infra — plain markdown files
- Synthesises once at ingest, not per query
- Answers grounded in structured, interlinked understanding rather than chunk similarity
- Genuinely compounds — every ingest makes the entire wiki richer
- Works well at thousands of pages; for millions, [[RAG Retrieval Strategies]] wins

The "70x cheaper than RAG" claim compares embedding + vector retrieval costs vs. Claude reasoning directly over structured markdown context. The real gain is compounding quality, not just cost.

## Obsidian as Frontend

Obsidian is the recommended read UI — not because it's required (all `.md` files), but for:
- **Graph view** — visual map of concept interconnections via backlinks
- **wikilinks** (`\[\[Page Title\]\]` syntax) — auto-generates backlinks
- **Local-first** — vault is just a folder; Claude Code reads/writes it directly
- **Dataview plugin** — SQL-like queries over frontmatter

Obsidian is read-mostly. Claude Code is the primary writer.

## Community Implementations (April 2026)

| Repo | What it adds |
|---|---|
| `Pratiyush/llm-wiki` | MCP server with 12 tools (query, search, lint, sync, export) |
| `AgriciDaniel/claude-obsidian` | Slash commands `/wiki /save /autoresearch`, persistent vault |
| `NicholasSpisak/second-brain` | LLM-maintained Obsidian KB with Claude Code hooks |

**Recommended starting points:** `Pratiyush/llm-wiki` for MCP server skeleton; `AgriciDaniel/claude-obsidian` for Claude Code skill patterns.

## Future Direction

Use the wiki to generate synthetic training data → fine-tune a model so it "knows" the KB in its weights. Long arc: external wiki → RAG → fine-tuned weights.

## Wiki Taxonomy Decisions

### Decisions live in domain directories, not a flat `decisions/` dir

**Decision:** architectural decision records (ADRs) live in the domain directory they belong to (`wiki/infra/`, `wiki/langgraph/`, etc.), tagged `type: decision`. A flat `wiki/decisions/` directory would break domain-scoped retrieval.

*Rationale:* When loading a domain briefing (`get_domain_briefing("infra")`), you want the observability decision in the same retrieval as the observability concept pages. A flat decisions dir requires two queries.

### Private content stays gitignored

Company-specific, client-identifying, or proprietary content goes in `wiki/private/` (gitignored), never in committed `wiki/` subdirectories. Private pages use the same format and are locally queryable — they just don't appear in the public repo.

### Raw sources documented as references

Every wiki page should list the `sources:` frontmatter field pointing back to the `raw/` files it was compiled from. This makes it possible to re-derive a page if the wiki is corrupted and to trace provenance of claims.

## See Also
- [[Librarian Project]]
- [[MCP Protocol]]
- [[RAG Retrieval Strategies]]
- [[Session Knowledge Capture Patterns]]
- [[Durable vs Performative Knowledge Split]] — complements (durable/performative axis alongside raw/compiled)
- [[AI Engineering Curriculum Structure]] — instance-of (a source corpus that pre-organises itself before compilation, and splits its own material by decay rate)
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends (what the compiled graph's edges are actually worth at retrieval time)
