# CLAUDE.md — Librarian Wiki Schema

> This is the most important file in this repo. It defines the contract for how Claude
> maintains the wiki. Read this fully before performing any operation.

---

## Refs (read before writing code here)

- `~/.claude/refs/python.md`, `logging.md`

## What This Repo Is

A personal agent design reference following Karpathy's LLM Wiki pattern. Raw sources
(Notion, Linear, meetings, PDFs, playground docs) go into `data/raw/` (append-only). Claude
compiles them into `data/wiki/` (structured, interlinked markdown). Obsidian is the read and
visualization UI. Claude Code is the write runtime. A local MCP server exposes the wiki
to other agents.

The core use case: before starting a new agent build, load the KB to get grounded
recommendations from accumulated design experience — your own hard-won patterns, not
generic documentation.

**Mental model:** `data/raw/` = source code. Claude = compiler. `data/wiki/` = executable output.

**Visualization:** Obsidian native graph view (wikilinks = edges). Install the Graph
Analysis community plugin for cosine-similarity edges between pages. Do NOT use the
Streamlit visualizer — it was deprecated and the script has since been removed.

**Agent layer:** `src/librarian/agent/` — `tools.py` is the one registry of read-only tools (typed
params, schema, implementation) that both the chat agent and the MCP server build from, and `loop.py`
is the Anthropic-based chat agent (#96) tool loop, streamed via SSE (`POST /api/chat/stream`) to the React graph UI's chat panel. No
write-back route or tool exists; the UI is read-only over the wiki.

**Feature notes:** the map filter panel, the atlas and glossary, the skill verbs, the retrieval eval
gate and the code index (`src/librarian/tools/codemap/`, MCP `find_symbol`/`repo_map`) are described in the wiki page
[Librarian Repo Feature Notes](data/wiki/projects/librarian-repo-feature-notes.md). Rules that survive from them:

- The graph UI's map panel is an overlay: `data/wiki/` directories stay the canonical domains for tags, MCP and `/lint`. Private pages never appear in it.
- Every wiki verb/skill (`/quiz`, `/gaps`, `/challenge`, `/wiki-weekly`, `/harness-audit`, `/evals-bootstrap`, `/wiki-graph`, `/write`) skips private pages. `/wiki-weekly` is the wiki's report; `/weekly` is the course's. `/wiki-rename` (`librarian.wiki.rename`) rewrites links in `private/` too, reporting those only as a count.
- A ranking change must clear all four `make eval-gate` arms (`sem`, `nofts`, `uniform`, `course`). Backlinks are deliberately not a ranking signal; never judge ranking on `sem` alone.

**Skills and unattended jobs:** skills live flat in `.claude/skills/<name>/SKILL.md` and are grouped by product in
`.claude/skills/README.md` (wiki, course, build). A skill keeps the judgement and the order; mechanical steps are
`librarian` verbs. Scheduled work runs headless with `librarian jobs run <name>` (Agent SDK, restricted tools, never
commits). See `.claude/skills/README.md`.

---

## Code Layout

- `src/librarian/` — the library, installed as the `librarian` package: `config.py` (every path and
  setting; `LIBRARIAN_ROOT` or a `pyproject.toml` above the package locates the repo), `log_config.py`,
  `cli.py`, `accounts/` (users, API keys; the API's `current_user` resolves them),
  `wiki/` (parser, health, telemetry, graph, rename, relinker, common), `retrieval/`
  (index, ranking, search/read API, embeddings), `courses/` (catalog, curriculum, leitner, glossary) and `ingest/`
  (scrapers, ingest gate, manifest, raw lint).
- Also inside the `librarian` package, in three layers (enforced by import-linter, `make lint-imports`):
  entry points `api/` (FastAPI, `librarian api`; routers in `api/routers/`, logic in the core) and `mcp/`
  (FastMCP, `librarian mcp`), independent of each other and using only the public names of
  `librarian.retrieval`; `agent/` (the tool registry and chat loop they share); `tools/` (`slides`, `presenter`, `codemap`, `cartographer`: what builds the media and content; they must not import api/mcp; `mcp`
  imports codemap's tools); and the core below (`courses`, `retrieval`, `wiki`, `ingest`, `accounts`, `db`), which imports none of them.
- `app/` — the React/Vite frontend only (`app/src/`, built to `app/dist/`, served by the API). The single
  `Dockerfile` at the repo root builds it and the API into one image.
- Cartographer (`src/librarian/tools/cartographer/`: session facts, dashboard, weekly sweep) runs as `uv run cartographer`.
- CLI: `librarian wiki stats|snapshot|check|gaps|log|ask|graph|rename|relink`,
  `librarian ingest triage|lint-raw|notion|linear|pdf`, `librarian scrape sessions|docs|repos|feeds|arxiv|bookmarks`,
  `librarian courses check|review`, `librarian users add|list`, `librarian keys create|list|revoke`,
  `librarian mcp [--rebuild]`, `librarian api`. Each is a thin dispatcher to the
  module's `main(argv)`, and `python -m librarian.<module>` works too.

---

## Directory Contract

### `data/raw/` — Immutable Input Zone

- **NEVER edit or delete files in `data/raw/`**. It is append-only.
- Subdirectories by source type:
  - `data/raw/notion/` — Notion page exports (use `YYYY-MM-DD-page-title.md`)
  - `data/raw/linear/` — Linear issue/project dumps
  - `data/raw/meetings/` — Meeting transcripts (use `YYYY-MM-DD-topic.md`)
  - `data/raw/playground-docs/` — Research + plan docs from playground repo and `.claude/docs/archived/`
  - `data/raw/pdfs/` — Extracted text from research PDFs
  - `data/raw/web/` — Saved web research, bookmarks, article captures
  - `data/raw/repos/` — CLAUDE.md, README, skill files, and docs scraped from active repos via `src/librarian/ingest/scrape_repos.py`; configure which repos to scrape in `data/raw/repos/repos.txt`
  - `data/raw/books/` — Curated quotes and notes from books (format below)
  - `data/raw/articles/` — Web article captures with highlighted quotes (format below)

#### Source Confidence

All raw sources may include an optional `confidence` field in frontmatter:

| Level | Sources | Treatment during ingest |
|-------|---------|------------------------|
| `high` | Own design docs, CLAUDE.md, verified decisions | Claims become wiki assertions |
| `medium` | Documentation, articles, meeting notes | Claims added with attribution (default if omitted) |
| `low` | Web scrapes, unverified transcripts | Claims marked provisional |

When a `low` confidence source contradicts a `high` confidence wiki claim, flag the conflict but note the disparity. When a `high` confidence source contradicts `medium`, update the wiki and note both sources. Default to `medium` if the field is absent.

**Self-reported claims:** when a source makes a claim about itself (a vendor about its product, an author about their own tool) and nothing independent confirms it, name the source and write "(self-reported)" inline straight after the claim. This holds whatever the source's confidence level.

#### Book source format (`data/raw/books/<author-title.md>`)

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

#### Article source format (`data/raw/articles/<YYYY-MM-DD-slug.md>`)

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

### `data/wiki/` — LLM-Compiled Knowledge

- Claude is the **only writer** here. Do not manually edit unless correcting a factual error.
- One `.md` file per entity, concept, project, or decision.
- **Directory = domain (primary retrieval axis). Type = tag (frontmatter only).**
- Subdirectories:
  - `data/wiki/rag/` — RAG, retrieval, chunking, embeddings, reranking, hybrid search
  - `data/wiki/langgraph/` — LangGraph state machines, CRAG, checkpointers, reducers, streaming
  - `data/wiki/adk/` — Google ADK, SKILL.md, VA patterns, voice, orchestration
  - `data/wiki/infra/` — Deployment, observability, caching, security, production hardening
  - `data/wiki/patterns/` — **Experiential knowledge: findings from your own build sessions.** Named, non-obvious mechanisms discovered while working (`silent-fallthrough-string-discovery`, `copier-re-entry-capability-path`), alongside the framework-agnostic classics (ReAct, CoT, ACI). This is the wiki's highest-value bucket and the core of the Karpathy use case — do not dilute it with textbook material. Externally-sourced concept knowledge belongs in a subject directory below.
  - `data/wiki/eval/` — Evaluation harnesses, LLM judges, annotation pipelines, preference alignment
  - `data/wiki/deep-agents/` — Deep Agents harness, middleware, state/store backends
  - `data/wiki/memory/` — Agent memory patterns (in-context, episodic, semantic, procedural)
  - `data/wiki/mcp/` — Model Context Protocol, tool schemas, A2A
  - `data/wiki/prompting/` — Prompt engineering as a discipline: prompt construction, injection defence, structured output, few-shot design
  - `data/wiki/context/` — Context engineering: assembly, compaction, window budgeting, retrieval-into-context (distinct from `context-management` runtime tactics in `infra/`)
  - `data/wiki/foundations/` — ML/DS/data-engineering fundamentals: classical ML, deep learning, NLP, data systems, MLOps
  - `data/wiki/interview/` — Coding-interview patterns (arrays/hashing, two pointers, sliding window, …), system design, prep references
  - `data/wiki/meta/` — Wiki-about-wiki: Karpathy pattern, Claude workflow system, session knowledge
  - `data/wiki/graph/` — Graph engineering and knowledge graphs: node, edge and state primitives, graph governance, entity resolution, text-to-Cypher, graph ML, graph retrieval, multi-agent topology and failure modes
  - `data/wiki/harness/` — Agent harness engineering: harness anatomy and maturity, execution boundaries and guardrails, retry and termination design, verification loops, tool design, deployment anti-patterns
  - `data/wiki/loop/` — Loop engineering: the cycle that re-prompts, checks and stops an agent unattended (autonomy ladder, termination design, state files, evolve loop, self-modification, where lessons are stored)
  - `data/wiki/projects/` — Per-project knowledge (generic, public — librarian, listen-wiseer, etc.)
  - `data/wiki/private/` — Company/project-specific pages; **gitignored, never committed**. Move pages here when they contain proprietary context, client names, or internal project details. Use the same page format — they are still compiled and queryable locally.
  - `data/wiki/_index.md` — Auto-generated TOC, updated after every ingest. Do not list `data/wiki/private/` entries here.
  - `data/wiki/_conflicts.md` — Flagged contradictions between sources
- **Source character decides the top-level split, then subject decides the directory.**
  Ask first: is this something *you* discovered while building (→ `patterns/`), textbook
  knowledge synthesized from an external source (→ a subject dir), or exam-performance
  technique that is only true while interviewing (→ `interview/`)? These three decay at
  different rates and serve different queries. Within the second bucket, route by subject.
- **ADRs live in their domain directory** — not a flat `decisions/` dir. Use `type: decision` tag.
- **Projects stay flat** in `data/wiki/projects/` until a project exceeds ~5 pages.

### `data/telemetry/` — Wiki Health Telemetry (generated)

Written by `librarian.wiki.telemetry`, never by hand. Outside `data/wiki/`, so the MCP index, relinker and graph don't see it.

- **Tracked:** `metrics.jsonl` (one row per day, at most 36, from `make wiki-snapshot`) and `operations.jsonl` (`log <op> "<detail>"`: last ~30 entries in full, older ones one row per month). This repo is public: `log` refuses text that names a private page.
- **Gitignored (query history):** `asked.jsonl` (`ask "<topic>"`) and `gaps.md` (`make wiki-gaps`).

### `data/courses/` — Coursework (authored, editable)

- Learning content served by the Courses tab of the graph UI (`src/librarian/courses/catalog.py`).
  It is **not** raw input and **not** compiled wiki: edit it directly, add lessons freely.
- Layout: `<course>/<module>/[section dirs/]<lesson>.md`; `_course.md` and `_module.md`
  hold `title` / `summary` / `order` frontmatter. Lesson frontmatter: `title`, `summary`,
  `order`, optional `section`, `kind` (`reading` | `notebook`), and `wiki: [page-id, …]`
  to link concepts explicitly. Inline `[[Wiki Page]]` links work too. Images go in the
  module's `assets/` and are referenced relatively.
- Lessons are authored here; the one-off import from `../learn-ai-engineering` ended 2026-11-06 and
  the importer is gone. Edit `data/courses/` directly. Drills are the `drills` module of the
  Programming course (`programming/drills`); the root `.gitignore` keeps local files out of it. Never copy
  from sisyphus (private; `jobs/` is personal PII).
  Drill files (frontmatter with a `track`, schema in `programming/drills/README.md`) are
  `kind: drill` with `track`/`topic`/`difficulty`/`timebox_min`/`units`, and their `concepts` become
  `wiki` links. They feed Practice mode: `GET /api/courses/practice` and the `#/practice` tab.
  Concepts with no wiki page show as plain `drill.tags`. Attempt counts come from sisyphus
  `drills/coding/drill-log.md`, read live at request time (`SISYPHUS_DIR`) and never written
  into `data/` — this repo is public and the log is personal history.
  `make flashcards` (`src/librarian/tools/slides/flashcards.py`) turns the local `slides/deck.yaml` and
  `slides/lectures/*.yaml` of each module into its `_flashcards.md`. The tool only deletes files carrying its own `generated_by` line. Frontmatter
  `cards: [{front, back, lesson?}, ...]`, served by `GET /api/courses/flashcards/<module or
  lesson id>`, studied at `#/flashcards/<id>`; self-grades go via `POST /api/courses/flashcard-results` to the attempts store, and `src/librarian/courses/leitner.py` computes due dates from it; it stores no schedule of its own.
  **Attempts store:** `var/attempts.sqlite3` in the state dir (gitignored; `src/librarian/courses/attempts.py`) holds every graded event: flashcards, quiz answers and drill runs (`POST /api/courses/drill-results`). An old `logs/flashcards.jsonl` is imported once and left alone; the sisyphus drill log is still read live and merged. **Quizzes:** `<module>/_quiz.md` (frontmatter `questions: [{prompt, options, answer, explanation?, lesson?, id?}]`), checked by `librarian courses check quiz`, served without answers by `GET /api/courses/quiz/<id>` and graded by `POST /api/courses/quiz-results`; a wrong answer is due tomorrow like a missed card. Never seed one from `private/`. **Slides viewer:** `#/slides/<module>[/<lecture>]`; `GET /api/courses/slides/<id>` rebuilds a stale deck in the background into `var/slides/` (images need `uv` and macOS Quick Look; without them the viewer shows the slide text). **Study home:** `#/study`, from `GET /api/courses/study`: cards and questions due, the next drill for the weakest track, the module's lecture.
- Private and tombstoned wiki pages are never linked from lessons.
- **`data/courses/private/`** (gitignored, mirrors the layout: `private/<course>/<module>/...`) holds
  what must not be public: solutions to site problems (`leetcode/`, `hackerrank/`), `coding/scratch/`,
  interview prep. It is the publication gate: anything there stays on this machine. The catalog serves
  it to the local UI as part of its course with `private: true`, but it never reaches the search index,
  MCP, the curriculum snapshot, the gap list or a public lesson's prev/next. Nothing public links into it.
  Two kinds of file live only in the mirror, maintained by hand, with the public lessons unchanged
  (`librarian.courses.overlay`): book and paper figures with no licence to share (all of `<module>/assets/sources/...`
  and named figures elsewhere in `assets/`; the asset route and deck builder fall back to the mirror, the UI hides a figure that is in neither tree) and each module's
  `readings:` list (`private/<course>/<module>/_module.md`, merged by the catalog; the public
  `_module.md` keeps `readings_count`). Lessons' `sources/` links
  are resolved at render time through `COURSE_SOURCES_DIR` (default `../learn-ai-engineering`) and
  served by `GET /api/courses/sources/<path>`, local only (`SERVE_COURSE_SOURCES=false` turns it off).
  The sibling supplies nothing else: only those `sources/` PDFs.
  `data/concept_homes.json` (hand-edited) lists the maths concepts and the lessons that teach them, for `courses check curriculum`.
- **Media is built here, for every course.** Deck specs are `<course>/<module>/slides/deck.yaml`
  or `slides/lectures/NN-slug.yaml`, images are in the module's `assets/`, and `src/librarian/tools/slides/`
  renders them: `make slides PILLAR=<course>/<module> [PREVIEW=1] [PDF=1]`, `make slides-all`,
  `make deck-check`, `make deck-graph`. Authoring steps are in the `/slides` skill. Built `.pptx`
  and `.pdf` files are gitignored. `src/librarian/tools/presenter/` is a
  separate LLM-driven tool for one-off talks, not course media.

---

## Page Format (required on every wiki page)

```markdown
---
title: Human-readable title
tags: [tag1, tag2]
summary: One sentence — what this page is about and why it matters
updated: YYYY-MM-DD
sources:
  - data/raw/path/to/source.md
---

# Title

Content...

## See Also
- [[Related Page]]
- [[Another Page]]
```

### Frontmatter Rules

- `aliases` (optional): former names. Links and `read_page` still resolve through them, after stems and titles, and Obsidian reads the same key. Written by `/wiki-rename`.
- `tags`: must include at least one domain tag (see Domains below) and one type tag
- `summary`: must fit on one line; should answer "what do I need to know about this?"
- `updated`: set to today's date whenever the page is modified
- `sources`: list all raw files this page was derived from

### Optional Sections

`## What argues against it` and `## Open questions` go before `## See Also`. Both are optional and recommended for `patterns/` pages. Write them only when a source supports them, never to fill the slot. Existing pages are not backfilled.

### Domain Tags (first-class — always include at least one)

> The canonical domain list is derived from disk: directories under `data/wiki/`
> (excluding `private/`). The table below is illustrative, not normative.

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

Run this checklist for **every** new raw source, without exception. Log one line per run: `uv run librarian wiki log ingest "<source> -> <n> new, <n> updated"`.

0. **Triage first:** `uv run librarian ingest triage <files>` reports whether each file is unchanged, a duplicate of compiled content, changed or new, and routes it: `clear`, `strip` (contact details), `decide` (a listed term or private page name: generalise, or compile to `data/wiki/private/`) or `stop` (a secret). When unsure, use `private/`. Terms live in `data/wiki/private/_sensitive-terms.txt`. The steps are in the ingest skill.
1. **Read the source fully** before writing anything to `data/wiki/`.
2. **Identify** all entities, concepts, decisions, and open questions mentioned.
3. **Extract atomic concepts** — this is the most important step for graph density. For every named technique, pattern, algorithm, or method mentioned in the source, ask: *does this deserve its own page?* Create a new page if yes. Examples of things that get their own page: `semantic caching`, `RRF fusion`, `inter-annotator agreement`, `prefix caching`, `CRAG retry loop`, `HistoryCondenser`. Do NOT bury these as bullets inside a coarser page — they become nodes in the graph only if they are pages. Rule of thumb: if it has a name and a non-obvious mechanism, it gets a page.
4. **For each identified item (both coarse topics and atomic concepts):**
   - Find the existing wiki page, or create a new one if it doesn't exist.
   - Update the summary if the source adds new understanding.
   - Add new facts as additional sections or bullets.
   - Update the `sources:` frontmatter list.
   - Update `updated:` to today's date.
5. **Scan for contradictions:** if the source disagrees with an existing wiki claim, do NOT silently overwrite. Go to step 6.
6. **Handle contradictions:** add an entry to `data/wiki/_conflicts.md`, tag the affected page with `conflict`, and note both claims with source citations. Do not resolve — flag for human review.
7. **Add cross-references (bidirectional):** after updating pages, scan for opportunities to add `[[wikilinks]]` to related pages. Prefer linking atomic concept pages from within broader topic pages — this is how graph edges form. Every atomic concept page should appear as an inline `[[wikilink]]` inside at least one coarser page. **Additionally:** for each new page, identify 2–3 existing pages that should link TO it and add backlinks in their `## See Also` sections. Use typed relationships where the type is clear.
8. **Update `data/wiki/_index.md`:** add any new pages to the appropriate section (`uv run librarian wiki index-add <pages>`).
9. **Check for orphans (blocking):** any new page MUST have at least one incoming backlink from another wiki page (`uv run librarian wiki verify <pages>` checks this and the index entry; exit 1 on failure). If you cannot identify an existing page to backlink to the new page, STOP and report the issue. Do not mark the file as ingested in the manifest until this is resolved.
10. **Relink pass:** after all pages are created/updated for this ingest cycle, run `uv run librarian wiki relink` to discover additional semantic links. The relinker is **suggest-only** — it never modifies a wiki page. Review `data/wiki/_relink_suggestions.md` and add the worthwhile candidates **manually, with typed relationships** (`- [[Page]] — extends`); delete the entries you dismiss. Adding untyped links is what the graph already has too many of (see `data/wiki/meta/wiki-graph-engineering.md`).
11. **Accumulator ceiling:** pages that receive per-session appended rows (e.g.
    `meta/session-log.md`) keep the last ~30 entries in full; when an append pushes
    past that, roll older entries into month-range summary rows at ingest time —
    same rule as index files. Compaction is the backstop, not the primary mechanism.

---

## Query Protocol

When answering a query against the wiki:

1. Check `data/wiki/_index.md` to identify relevant pages.
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
- **Orphan raw files** — files in `data/raw/` with no corresponding wiki coverage
- **Untyped links** — `## See Also` entries without a `— type` annotation (>50% untyped = WARN)
- **Unrecognized link types** — typed-syntax annotations whose type is not canonical (WARN)
- **Bridge gaps** — domain pairs with >5 pages each but <3 cross-domain links (NOTE)
- **Stale suggestions** — `data/wiki/_relink_suggestions.md` entries older than 14 days unreviewed
- **Private leak** — a page outside `private/` has a wikilink resolving into `private/` (`make wiki-check`, exit 1; a 3+ word private title in public text is a WARN). A lesson outside `data/courses/private/` that links, embeds or lists a lesson id into it, or names a private wiki page (`[[...]]` or `wiki:`), also blocks, and so does a git-tracked file under either `private/` tree (pre-commit runs `wiki check --tracked-only`). Reports name the public file and line, never the private page

Output a prioritised list: BLOCKER (conflicts, dead links, private leak) → WARN (orphans, stale, untyped) → NOTE (missing coverage, bridge gaps, stale suggestions).

### Health numbers (`make wiki-stats`)

Deterministic. Private pages, tombstones and underscore files are out of every rate; page count is printed but is not a health number. Between the bands reads `watch`. The bands are local heuristics, not research results: see [Wiki Health Metrics](data/wiki/meta/wiki-health-metrics.md) for where each comes from. Average degree counts both ends of a link, so it reads double a links-per-page figure.

| Number | Definition | Healthy | Broken |
|---|---|---|---|
| Orphan rate | pages with no inbound wikilink ÷ pages | < 5% | > 15% |
| Average degree | (inbound + outbound links) ÷ pages | 8–20 | < 4 |
| Main component | pages in the largest connected component ÷ pages | ≥ 80% | < 60% |
| Stale rate | pages with `updated` older than 60 days ÷ pages | report only | none |
| Typed-link rate | typed See Also entries ÷ See Also entries | ≥ 50% | none |
| Stub rate | pages under 200 body words ÷ pages | < 5% | none |

---

## Compaction Protocol

The recompile stage: `/compact-wiki`, run manually by Ramsey ~monthly (or after ~5
ingests). Evidence-driven — page age, size, relinker similarity, and retrieval
telemetry (`logs/retrieval.jsonl`, written by the MCP server) — with three moves:
**merge** (union sources, successor absorbs all true content, merged page becomes a
tombstone), **retire** (tombstone + `[[Successor]] — supersedes`), **compress**
(accumulator ceiling). Always a dry-run report first; only Ramsey-approved moves are
applied; data/raw/ is never touched. See `.claude/skills/compact-wiki/SKILL.md` and
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

**Direction:** the type describes the *linked* page relative to the page it is written
on. `- [[X]] — prerequisite-for` on page P reads "X is a prerequisite for P". Retrieval
expansion (`src/librarian/retrieval/graph_expansion.py`) depends on this reading, so write the link
on the page that X relates *to*.

| Type | `- [[X]] — type` on page P means |
|------|---------|
| `extends` | X builds on or refines P |
| `prerequisite-for` | Understand X before P |
| `alternative-to` | X is a competing approach to the same problem (symmetric) |
| `instance-of` | X is a concrete example of the general pattern P |
| `contradicts` | X disagrees with P (links to conflict entry) |
| `supersedes` | X replaces P (tombstones point at their successor this way) |
| `related` | Weak, undirected association; not walked by retrieval expansion |

Use `related` rather than inventing a type (`part-of`, `depends-on`, `complements`, …);
put the nuance in a parenthetical note: `- [[X]] — related (part of; the eval stage)`.
Canonical types are defined once in `src/librarian/wiki/common.py` (`CANONICAL_LINK_TYPES`).

Untyped links (`- [[Page]]`) are still valid — type gradually during future ingests.
The parser extracts relationship types into edge metadata for graph visualization.

---

## Conflict Handling

### Flagging (during ingest)

When a new source contradicts an existing wiki claim:

1. **Do not silently overwrite** the existing claim.
2. Add an entry to `data/wiki/_conflicts.md`:

```markdown
## Conflict: [Topic] — [YYYY-MM-DD]

**Claim A** (from `[[Existing Page]]`, sourced from `data/raw/...`):
> Exact quote or paraphrase of claim A

**Claim B** (from new source `data/raw/...`):
> Exact quote or paraphrase of claim B

**Status:** Unresolved — needs human review
**Impact:** [which projects or decisions does this affect?]
**Would settle it:** [the source, measurement or test that would decide between the claims]
```

3. Tag the affected page with `conflict` in frontmatter.
4. During lint, surface all unresolved conflicts.

### Resolution (human review step)

To resolve a conflict in `data/wiki/_conflicts.md`:

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

Use `data/wiki/_index.md` to find pages by domain. The index is maintained automatically during ingest.

When searching for a page, check:
1. `data/wiki/_index.md` for the canonical list
2. The domain subdirectory directly: `data/wiki/rag/`, `data/wiki/langgraph/`, `data/wiki/adk/`, etc.
3. `data/wiki/projects/` for project-level pages

---

## What NOT to Do

- **Do not** edit files in `data/raw/` — they are immutable inputs
- **Do not** create summary files outside the `data/wiki/` structure — all knowledge belongs in wiki pages
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
