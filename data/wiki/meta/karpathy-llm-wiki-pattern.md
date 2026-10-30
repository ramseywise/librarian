---
title: Karpathy LLM Wiki Pattern
tags: [llm, concept]
summary: The compiler analogy for personal knowledge bases — raw sources in, LLM compiles them into structured interlinked wiki pages, no vector infra needed.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/docs/archived/obsidian-kb-research.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-17-knowledge-compaction.md
  - data/raw/repos/librarian/.claude--docs--plans--wiki-taxonomy-refactor.md
  - data/raw/repos/librarian/.claude--docs--research--learning-repos-into-kb.md
  - data/raw/repos/librarian/.claude--docs--research--two-knowledge-eras-audit.md
  - data/raw/repos/librarian/.claude--skills--wiki-sync--SKILL.md
  - data/raw/repos/librarian/.claude--skills--ingest--SKILL.md
  - data/raw/repos/librarian/.claude--skills--lint--SKILL.md
  - data/raw/repos/librarian/.claude--skills--query--SKILL.md
  - data/raw/repos/librarian/CLAUDE.md
  - data/raw/repos/librarian/README.md
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

### Audit the raw sources before locking the structure

The taxonomy refactor (2026-04) deliberately deferred migration until a raw-source
coverage audit finished. The reasoning: "raw source coverage may reveal missing domains;
wrong to lock structure before audit." The audit confirmed that the old concepts/agents
split was broken. It also showed that a 97-file coverage gap was mostly archived plans,
so migration did not have to wait for ingest. The rule that came out of it was
**directory = domain (the primary retrieval axis), type = tag (frontmatter only)**. One
call was reversed during the refactor: "decisions stay flat" (2026-04-26) gave way to
ADRs living in their domain directory, for the domain-scoped retrieval reason above.

### Curate new eras of content; do not bulk-ingest

Two later audits asked whether older material (classical ML/DS notebooks, course repos,
textbook exercises) should enter the wiki. Both answered "curate". Bulk ingest of
operational or tutorial material had already failed once: 38 SKILL.md sources produced 4
pages. The classical-era audit found about seven page-worthy items across several repos,
all comparison or decision shaped (for example, which A/B significance test to use).
Most of what it reviewed was "how a for-loop works"-tier material. It recommended a
single, narrowly scoped fundamentals domain, kept **out of flagship agents' runtime
wiring** so that textbook content cannot dilute design recommendations. The immediate
decision was to wait. `foundations/` and `interview/` now exist, and the
source-character rule in CLAUDE.md (patterns vs subject knowledge vs interview
technique) is the outcome of that thinking.

### Hardcoded domain lists drift from disk

The frontend and backend each carried hardcoded domain lists that silently went stale
as directories were added. A read-only `/wiki-sync` audit compares them against
`data/wiki/` and reports missing domains and "ghost" entries (in code, not on disk). It
only applies mechanical fixes with `--fix`. The schema now treats disk as canonical: the
domain-tag table in CLAUDE.md is "illustrative, not normative".

As of 2026-10-30 no hand-maintained domain list remains in the graph pipeline. The
backend parser and the MCP server each derive the domain set from the directories at call
time (excluding `private/`), and the graph payload carries a sorted `domains` field.
The frontend maps a name to a colour only: fixed colours for established domains, a
deterministic palette hash for any other. Tag-shared edges are derived client-side with
the same rule as the server. A new wiki directory therefore needs no code change to be
filterable and coloured. `/wiki-sync` now audits that the derivations still derive, and
sweeps the frontend for a reintroduced literal list. That grep runs a **positive control**
first, against the one file that legitimately names domains; the control must match, so a
broken pattern cannot report "no drift".

## See Also
- [[Librarian Project]]
- [[MCP Protocol]]
- [[RAG Retrieval Strategies]]
- [[Session Knowledge Capture Patterns]]
- [[Durable vs Performative Knowledge Split]] — complements (durable/performative axis alongside raw/compiled)
- [[AI Engineering Curriculum Structure]] — instance-of (a source corpus that pre-organises itself before compilation, and splits its own material by decay rate)
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends (what the compiled graph's edges are actually worth at retrieval time)
- [[Automated Paper Discovery Pipeline]] — extends (an automated, gated feed of research papers into raw)
- [[Knowledge Base Recompile Stage]] — extends (the consolidation stage the compile/query/lint trio lacks)
- [[Evidence-Driven Wiki Compaction]] — extends (the recompile stage)
- [[Compiled-Prose KB vs Graph-Native Store]] — extends (the compiled-prose bet against graph-native stores)
