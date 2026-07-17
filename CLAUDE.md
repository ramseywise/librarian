# CLAUDE.md — Librarian Wiki Schema

> This is the most important file in this repo. It defines the contract for how Claude
> maintains the wiki. Read this fully before performing any operation.

---

## Refs (read before writing code here)

- `~/.claude/refs/python.md`, `logging.md`

## What This Repo Is

A personal agent design reference following Karpathy's LLM Wiki pattern. Raw sources
(Notion, Linear, meetings, PDFs, playground docs) go into `raw/` (append-only). Claude
compiles them into `wiki/` (structured, interlinked markdown). Obsidian is the read and
visualization UI. Claude Code is the write runtime. A local MCP server exposes the wiki
to other agents.

The core use case: before starting a new agent build, load the KB to get grounded
recommendations from accumulated design experience — your own hard-won patterns, not
generic documentation.

**Mental model:** `raw/` = source code. Claude = compiler. `wiki/` = executable output.

**Visualization:** Obsidian native graph view (wikilinks = edges). Install the Graph
Analysis community plugin for cosine-similarity edges between pages. Do NOT use the
Streamlit visualizer (`etl/visualize.py`) — it is deprecated.

**Agent layer:** `app/backend/agent.py` — a Gemini-based chat agent with its own wiki-search
tool, streamed via SSE (`POST /api/chat/stream`) to the React graph UI's chat panel. No
write-back tool exists yet (`/api/writeback` mutates a page's `## See Also` section directly
from the UI, not via an agent tool call).

**Code index (2026-07):** `tools/codemap/` — tree-sitter-based structural index (symbols,
import edges) over source repos, separate from the wiki-compile pipeline. Exposed via MCP
tools (`find_symbol`, `repo_map`, `find_references`, etc.) alongside the wiki tools. See
`.claude/docs/plans/codemap-code-index.md`.

---

## Directory Contract

### `raw/` — Immutable Input Zone

- **NEVER edit or delete files in `raw/`**. It is append-only.
- Subdirectories by source type:
  - `raw/notion/` — Notion page exports (use `YYYY-MM-DD-page-title.md`)
  - `raw/linear/` — Linear issue/project dumps
  - `raw/meetings/` — Meeting transcripts (use `YYYY-MM-DD-topic.md`)
  - `raw/playground-docs/` — Research + plan docs from playground repo and `.claude/docs/archived/`
  - `raw/pdfs/` — Extracted text from research PDFs
  - `raw/web/` — Saved web research, bookmarks, article captures
  - `raw/repos/` — CLAUDE.md, README, skill files, and docs scraped from active repos via `etl/scrape_repos.py`; configure which repos to scrape in `raw/repos/repos.txt`
  - `raw/books/` — Curated quotes and notes from books (format below)
  - `raw/articles/` — Web article captures with highlighted quotes (format below)

#### Source Confidence

All raw sources may include an optional `confidence` field in frontmatter:

| Level | Sources | Treatment during ingest |
|-------|---------|------------------------|
| `high` | Own design docs, CLAUDE.md, verified decisions | Claims become wiki assertions |
| `medium` | Documentation, articles, meeting notes | Claims added with attribution (default if omitted) |
| `low` | Web scrapes, unverified transcripts | Claims marked provisional |

When a `low` confidence source contradicts a `high` confidence wiki claim, flag the conflict but note the disparity. When a `high` confidence source contradicts `medium`, update the wiki and note both sources. Default to `medium` if the field is absent.

#### Book source format (`raw/books/<author-title.md>`)

```markdown
---
source_type: book
title: "Title of the Book"
author: "Author Name"
year: YYYY
---

## Chapter N — Chapter Title

> "Exact quote that is relevant to agent design or engineering."

**Note:** Why this quote matters for your work — connect it to a pattern, decision, or technique.

> "Another relevant quote."

**Note:** Application or implication.
```

#### Article source format (`raw/articles/<YYYY-MM-DD-slug.md>`)

```markdown
---
source_type: article
title: "Article Title"
author: "Author Name"
url: https://...
published: YYYY-MM-DD
---

> "Key quote from the article."

**Note:** Why this is relevant.
```

### `wiki/` — LLM-Compiled Knowledge

- Claude is the **only writer** here. Do not manually edit unless correcting a factual error.
- One `.md` file per entity, concept, project, or decision.
- **Directory = domain (primary retrieval axis). Type = tag (frontmatter only).**
- Subdirectories:
  - `wiki/rag/` — RAG, retrieval, chunking, embeddings, reranking, hybrid search
  - `wiki/langgraph/` — LangGraph state machines, CRAG, checkpointers, reducers, streaming
  - `wiki/adk/` — Google ADK, SKILL.md, VA patterns, voice, orchestration
  - `wiki/infra/` — Deployment, observability, caching, security, production hardening
  - `wiki/patterns/` — Framework-agnostic agentic patterns (ReAct, CoT, ACI, workflow)
  - `wiki/eval/` — Evaluation harnesses, LLM judges, annotation pipelines, preference alignment
  - `wiki/deep-agents/` — Deep Agents harness, middleware, state/store backends
  - `wiki/memory/` — Agent memory patterns (in-context, episodic, semantic, procedural)
  - `wiki/mcp/` — Model Context Protocol, tool schemas, A2A
  - `wiki/foundations/` — ML/DS/data-engineering fundamentals: classical ML, deep learning, NLP, data systems, MLOps
  - `wiki/interview/` — Coding-interview patterns (arrays/hashing, two pointers, sliding window, …), system design, prep references
  - `wiki/meta/` — Wiki-about-wiki: Karpathy pattern, Claude workflow system, session knowledge
  - `wiki/projects/` — Per-project knowledge (generic, public — librarian, listen-wiseer, etc.)
  - `wiki/private/` — Company/project-specific pages; **gitignored, never committed**. Move pages here when they contain proprietary context, client names, or internal project details. Use the same page format — they are still compiled and queryable locally.
  - `wiki/_index.md` — Auto-generated TOC, updated after every ingest. Do not list `wiki/private/` entries here.
  - `wiki/_conflicts.md` — Flagged contradictions between sources
- **ADRs live in their domain directory** — not a flat `decisions/` dir. Use `type: decision` tag.
- **Projects stay flat** in `wiki/projects/` until a project exceeds ~5 pages.

---

## Page Format (required on every wiki page)

```markdown
---
title: Human-readable title
tags: [tag1, tag2]
summary: One sentence — what this page is about and why it matters
updated: YYYY-MM-DD
sources:
  - raw/path/to/source.md
---

# Title

Content...

## See Also
- [[Related Page]]
- [[Another Page]]
```

### Frontmatter Rules

- `tags`: must include at least one domain tag (see Domains below) and one type tag
- `summary`: must fit on one line; should answer "what do I need to know about this?"
- `updated`: set to today's date whenever the page is modified
- `sources`: list all raw files this page was derived from

### Domain Tags (first-class — always include at least one)

| Tag | Covers |
|---|---|
| `adk` | Google Agent Development Kit — patterns, APIs, deployment |
| `langgraph` | LangGraph state machines, CRAG, checkpointers, edges |
| `rag` | Retrieval-augmented generation, embedders, rerankers, chunking |
| `memory` | Agent memory patterns — short-term, long-term, episodic, semantic |
| `mcp` | Model Context Protocol, MCP server design, tool schemas |
| `voice` | Voice agent patterns, BIDI streaming, session management |
| `eval` | Evaluation harnesses, LLM judges, golden sets, metrics |
| `infra` | Deployment, CI/CD, observability (LangFuse/LangSmith/Cloud Trace), caching |
| `llm` | LLM API patterns, prompt engineering, context management |
| `deep-agents` | Deep Agents harness — middleware, StateBackend, StoreBackend, skill format |
| `context-management` | Prefix caching, session compaction, history pruning, context windows |
| `foundations` | ML/DS/data-engineering fundamentals — classical ML, deep learning, NLP, data systems, MLOps |
| `interview` | Coding-interview patterns, algorithms, system design, prep material |

### Type Tags (include exactly one)

| Tag | Use when |
|---|---|
| `concept` | Explaining a technology, framework, or idea |
| `pattern` | A reusable implementation pattern |
| `decision` | A documented architectural choice with tradeoffs |
| `project` | Project-level knowledge page |
| `comparison` | Comparing two or more technologies/approaches |
| `reference` | Quick-reference cheat sheet |
| `conflict` | Page has a flagged contradiction (see Conflicts section) |

---

### Tombstone Pages (retired/merged pages)

A page removed by compaction is never deleted — it becomes a **tombstone**: same
filename (inbound wikilinks stay valid), `tombstone` added to tags, body reduced to one
line pointing at its successor:

```markdown
---
title: Old Page Title
tags: [rag, tombstone]
summary: Retired — superseded by Successor Page.
updated: YYYY-MM-DD
sources: [...unchanged...]
---

# Old Page Title

Retired YYYY-MM-DD. See [[Successor Page]] — supersedes.
```

Tombstones are excluded from the search index (MCP server skips `tombstone`-tagged
pages at build time) but remain readable via `read_page`. They are exempt from orphan
rules. Only `/compact-wiki` creates tombstones.

## Ingest Protocol

Run this checklist for **every** new raw source, without exception.

1. **Read the source fully** before writing anything to `wiki/`.
2. **Identify** all entities, concepts, decisions, and open questions mentioned.
3. **Extract atomic concepts** — this is the most important step for graph density. For every named technique, pattern, algorithm, or method mentioned in the source, ask: *does this deserve its own page?* Create a new page if yes. Examples of things that get their own page: `semantic caching`, `RRF fusion`, `inter-annotator agreement`, `prefix caching`, `CRAG retry loop`, `HistoryCondenser`. Do NOT bury these as bullets inside a coarser page — they become nodes in the graph only if they are pages. Rule of thumb: if it has a name and a non-obvious mechanism, it gets a page.
4. **For each identified item (both coarse topics and atomic concepts):**
   - Find the existing wiki page, or create a new one if it doesn't exist.
   - Update the summary if the source adds new understanding.
   - Add new facts as additional sections or bullets.
   - Update the `sources:` frontmatter list.
   - Update `updated:` to today's date.
5. **Scan for contradictions:** if the source disagrees with an existing wiki claim, do NOT silently overwrite. Go to step 6.
6. **Handle contradictions:** add an entry to `wiki/_conflicts.md`, tag the affected page with `conflict`, and note both claims with source citations. Do not resolve — flag for human review.
7. **Add cross-references (bidirectional):** after updating pages, scan for opportunities to add `[[wikilinks]]` to related pages. Prefer linking atomic concept pages from within broader topic pages — this is how graph edges form. Every atomic concept page should appear as an inline `[[wikilink]]` inside at least one coarser page. **Additionally:** for each new page, identify 2–3 existing pages that should link TO it and add backlinks in their `## See Also` sections. Use typed relationships where the type is clear.
8. **Update `wiki/_index.md`:** add any new pages to the appropriate section.
9. **Check for orphans (blocking):** any new page MUST have at least one incoming backlink from another wiki page. If you cannot identify an existing page to backlink to the new page, STOP and report the issue. Do not mark the file as ingested in the manifest until this is resolved.
10. **Relink pass:** after all pages are created/updated for this ingest cycle, run `uv run python etl/relinker.py` to discover additional semantic links. Review `wiki/_relink_suggestions.md` if generated.
11. **Accumulator ceiling:** pages that receive per-session appended rows (e.g.
    `meta/session-log.md`) keep the last ~30 entries in full; when an append pushes
    past that, roll older entries into month-range summary rows at ingest time —
    same rule as index files. Compaction is the backstop, not the primary mechanism.

---

## Query Protocol

When answering a query against the wiki:

1. Check `wiki/_index.md` to identify relevant pages.
2. Read the relevant pages in full — do not skim.
3. Synthesise a grounded answer citing specific pages.
4. If the answer reveals new insight worth preserving, offer to file it as a new wiki page.
5. If the query exposes a gap (no wiki page covers it), flag it for future ingest.

---

## Lint Protocol

Run lint to find health issues. Check each of the following:

- **Orphan pages** — pages with no backlinks from any other wiki page
- **Missing frontmatter** — pages missing required frontmatter fields
- **Stale pages** — `updated` date older than 60 days (flag for review, don't auto-update; these flags feed `/compact-wiki` as retire/merge candidates)
- **Unresolved conflicts** — pages tagged `conflict` that haven't been resolved
- **Dead wikilinks** — `[[Page]]` references that don't correspond to an existing file
- **Missing summaries** — `summary:` field is empty or generic
- **Orphan raw files** — files in `raw/` with no corresponding wiki coverage
- **Untyped links** — `## See Also` entries without a `— type` annotation (>50% untyped = WARN)
- **Bridge gaps** — domain pairs with >5 pages each but <3 cross-domain links (NOTE)
- **Stale suggestions** — `wiki/_relink_suggestions.md` entries older than 14 days unreviewed

Output a prioritised list: BLOCKER (conflicts, dead links) → WARN (orphans, stale, untyped) → NOTE (missing coverage, bridge gaps, stale suggestions).

---

## Compaction Protocol

The recompile stage: `/compact-wiki`, run manually by Ramsey ~monthly (or after ~5
ingests). Evidence-driven — page age, size, relinker similarity, and retrieval
telemetry (`logs/retrieval.jsonl`, written by the MCP server) — with three moves:
**merge** (union sources, successor absorbs all true content, merged page becomes a
tombstone), **retire** (tombstone + `[[Successor]] — supersedes`), **compress**
(accumulator ceiling). Always a dry-run report first; only Ramsey-approved moves are
applied; raw/ is never touched. See `.claude/skills/compact-wiki/SKILL.md` and
`.claude/docs/plans/2026-07-17-knowledge-compaction.md`.

## Wikilinks

- Use `[[Page Title]]` syntax for all cross-references. Obsidian renders these as backlinks.
- Prefer linking to the concept page rather than the project page when both exist.
- When creating a new page, immediately add a backlink from at least one existing page.
- `[[See also: Page Title]]` in the See Also section is acceptable for non-inline references.

### Typed Relationships

In `## See Also` sections, annotate links with a relationship type using `— type` suffix:

```markdown
## See Also
- [[CRAG Retry Logic]] — extends
- [[RAG Evaluation]] — prerequisite-for
- [[LangGraph vs ADK]] — alternative-to
```

| Type | Meaning |
|------|---------|
| `extends` | Builds on or refines the target |
| `prerequisite-for` | Must understand this before the target |
| `alternative-to` | Competing approach to the same problem |
| `instance-of` | Concrete example of a general pattern |
| `contradicts` | Disagrees with (links to conflict entry) |
| `supersedes` | Replaces an older approach/decision |

Untyped links (`- [[Page]]`) are still valid — type gradually during future ingests.
The parser extracts relationship types into edge metadata for graph visualization.

---

## Conflict Handling

### Flagging (during ingest)

When a new source contradicts an existing wiki claim:

1. **Do not silently overwrite** the existing claim.
2. Add an entry to `wiki/_conflicts.md`:

```markdown
## Conflict: [Topic] — [YYYY-MM-DD]

**Claim A** (from `[[Existing Page]]`, sourced from `raw/...`):
> Exact quote or paraphrase of claim A

**Claim B** (from new source `raw/...`):
> Exact quote or paraphrase of claim B

**Status:** Unresolved — needs human review
**Impact:** [which projects or decisions does this affect?]
```

3. Tag the affected page with `conflict` in frontmatter.
4. During lint, surface all unresolved conflicts.

### Resolution (human review step)

To resolve a conflict in `wiki/_conflicts.md`:

1. Read both claims and their source files.
2. Determine which is correct — or synthesise both if both are partially right.
3. Update the affected wiki page with the correct/synthesised claim; cite both sources.
4. Mark the conflict entry resolved:

```markdown
**Status:** Resolved — [YYYY-MM-DD]
**Resolution:** Claim A was correct; Claim B referred to a different threshold (chunk-level vs. reranker-level). Updated [[Affected Page]] to distinguish both contexts.
```

5. Remove the `conflict` tag from the page frontmatter.
6. Run `/lint` to confirm no remaining unresolved conflicts.

---

## Naming Conventions

- **Files:** `kebab-case.md` — e.g., `google-adk-state-management.md`, `langgraph-vs-adk-comparison.md`
- **Decisions:** `YYYY-MM-DD-decision-slug.md` — e.g., `2026-04-24-adk-vs-langgraph.md`
- **Raw sources:** preserve the original name or use `YYYY-MM-DD-source-topic.md`
- **Page titles** (in frontmatter): Title Case — e.g., "Google ADK State Management"

---

## Domains Index

Use `wiki/_index.md` to find pages by domain. The index is maintained automatically during ingest.

When searching for a page, check:
1. `wiki/_index.md` for the canonical list
2. The domain subdirectory directly: `wiki/rag/`, `wiki/langgraph/`, `wiki/adk/`, etc.
3. `wiki/projects/` for project-level pages

---

## What NOT to Do

- **Do not** edit files in `raw/` — they are immutable inputs
- **Do not** create summary files outside the `wiki/` structure — all knowledge belongs in wiki pages
- **Do not** silently resolve conflicts — always flag them in `_conflicts.md`
- **Do not** leave new pages without at least one backlink
- **Do not** skip the ingest checklist for "small" sources — every source matters
- **Do not** write speculative content — wiki pages represent synthesised knowledge from sources, not inference

---

## Environment

```
ANTHROPIC_API_KEY=       # Required for MCP server and scripts
NOTION_API_KEY=          # Required for Notion ingestion
LINEAR_API_KEY=          # Required for Linear ingestion
DROPBOX_PDF_PATH=        # Path to local Dropbox PDF directory
```

Source from `.env` (gitignored). See `.env.example`.
