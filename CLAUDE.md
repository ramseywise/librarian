# CLAUDE.md — Librarian Wiki Schema

> The contract for how Claude maintains the wiki. Read this fully before any operation.
> Detail lives in `docs/` (linked per section). `SANYI.md` is the separate, hand-maintained change contract (immutable / simple / changeable invariants, migrations, debt); read it before changing anything it covers.

## Refs (read before writing code here)

- `~/.claude/refs/python.md`, `logging.md`

## What This Repo Is

A personal agent design reference following Karpathy's LLM Wiki pattern. Raw sources go into `data/raw/` (append-only). Claude compiles them into `data/wiki/` (structured, interlinked markdown). Obsidian reads, Claude Code writes, a local MCP server exposes the wiki to other agents. Core use case: before a new agent build, load the KB for grounded recommendations from your own accumulated patterns.

**Mental model:** `data/raw/` = source code. Claude = compiler. `data/wiki/` = executable output.

Rules that survive from the feature notes ([Librarian Repo Feature Notes](data/wiki/projects/librarian-repo-feature-notes.md)):

- The graph UI's map panel is an overlay: `data/wiki/` directories stay the canonical domains for tags, MCP and `/lint`. Private pages never appear in it.
- Every wiki verb/skill (`/quiz`, `/gaps`, `/challenge`, `/wiki-weekly`, `/harness-audit`, `/evals-bootstrap`, `/wiki-graph`, `/write`) skips private pages. `/wiki-weekly` is the wiki's report; `/weekly` is the course's. `/wiki-rename` (`librarian.wiki.rename`) rewrites links in `private/` too, reporting those only as a count.
- **Eval gate:** a ranking change must clear all six `make eval-gate` arms (`sem`, `nofts`, `uniform`, `course`, `graph`, `multihop`). Backlinks are deliberately not a ranking signal; never judge ranking on `sem` alone.
- **Migrations are expand-only within a release:** add columns nullable (or with a server default), never drop or rename one in the same release that stops using it; the drop or rename ships one release later. `./librarian upgrade` refuses without a backup younger than 15 minutes.
- Skills live flat in `.claude/skills/<name>/SKILL.md`, grouped by product in `.claude/skills/README.md`. Scheduled work runs headless with `librarian jobs run <name>` and never commits.

Detail docs:

- Visualization, agent layer, skills/jobs, package layout and import layers (`make lint-imports`): [docs/code-layout.md](docs/code-layout.md)
- Operations (`./librarian ...`), content releases, full CLI listing, environment keys: [docs/operations.md](docs/operations.md)
- `data/courses/` internals (lessons, drills, flashcards, quizzes, attempts store, private mirror, media): [docs/courses.md](docs/courses.md)
- Book and article source formats: [docs/raw-formats.md](docs/raw-formats.md)
- Wiki subdirectory list, domain tags, optional sections, domains index: [docs/wiki-schema.md](docs/wiki-schema.md)
- Telemetry, lint check list, health-number table (`make wiki-stats`): [docs/wiki-health.md](docs/wiki-health.md)
- Confidence table, tombstone, conflict and resolution templates, ingest examples: [docs/wiki-templates.md](docs/wiki-templates.md)
- What was actually verified and where: [docs/status.md](docs/status.md)

---

## Directory Contract

### `data/raw/` — Immutable Input Zone

- **NEVER edit or delete files in `data/raw/`**. It is append-only.
- Subdirectories by source type: `notion/` (`YYYY-MM-DD-page-title.md`), `linear/`, `meetings/` (`YYYY-MM-DD-topic.md`), `playground-docs/` (research + plan docs from playground repo and `.claude/docs/archived/`), `pdfs/` (extracted text), `web/` (saved research, bookmarks, captures), `repos/` (CLAUDE.md, README, skills, docs scraped via `src/librarian/ingest/scrape_repos.py`; repos configured in `data/raw/repos/repos.txt`), `books/` and `articles/` (formats: [docs/raw-formats.md](docs/raw-formats.md)).
- Optional `confidence` frontmatter (`high` / `medium` / `low`); default `medium`. `low` contradicting `high` is flagged as a conflict, not applied. Table: [docs/wiki-templates.md](docs/wiki-templates.md).
- **Self-reported claims:** when a source makes a claim about itself (a vendor about its product, an author about their own tool) and nothing independent confirms it, name the source and write "(self-reported)" inline straight after the claim, whatever the source's confidence.

### `data/wiki/` — LLM-Compiled Knowledge

- Claude is the **only writer** here. Do not manually edit unless correcting a factual error.
- One `.md` file per entity, concept, project, or decision.
- **Directory = domain (primary retrieval axis). Type = tag (frontmatter only).** Directory list: [docs/wiki-schema.md](docs/wiki-schema.md).
- **Routing:** did *you* discover it while building (→ `patterns/`: named, non-obvious mechanisms from your own sessions plus framework-agnostic classics; never dilute with textbook material), is it textbook knowledge from an external source (→ a subject dir, by subject), or exam technique only true while interviewing (→ `interview/`)?
- `data/wiki/private/` — company/project-specific pages (proprietary context, client names, internal details); **gitignored, never committed**. Same page format; still compiled and queryable locally.
- `data/wiki/_index.md` — auto-generated TOC, updated after every ingest; never lists `private/` entries. `data/wiki/_conflicts.md` — flagged contradictions.
- **ADRs live in their domain directory** (not a flat `decisions/`), tagged `type: decision`. **Projects stay flat** in `data/wiki/projects/` until a project exceeds ~5 pages.

### `data/telemetry/` and `data/courses/`

- `data/telemetry/` is generated by `librarian.wiki.telemetry`, never by hand; `log` refuses text naming a private page (public repo). Details: [docs/wiki-health.md](docs/wiki-health.md).
- `data/courses/` mirrors `../learn-ai-engineering` (`uv run librarian courses import`; author there, not here) and is editable (not raw, not compiled wiki). Internals: [docs/courses.md](docs/courses.md). Rules that bind:
  - `data/courses/private/` (gitignored) is the publication gate: it never reaches the search index, MCP, curriculum snapshot, gap list or a public lesson; nothing public links into it. Private and tombstoned wiki pages are never linked from lessons. Never seed a quiz from `private/`. Never copy from sisyphus (private; `jobs/` is personal PII).
  - The drill log is personal history: `librarian db import-drill-log [--user EMAIL]` brings it in locally (Date, QID, Aid, Score only, never the Note); the server never reads it and it is never written into `data/`.

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

- `aliases` (optional): former names; links and `read_page` resolve through them after stems and titles. Written by `/wiki-rename`.
- `tags`: at least one domain tag (derived from the directories on disk; [docs/wiki-schema.md](docs/wiki-schema.md)) and exactly one type tag.
- `summary`: one line; answers "what do I need to know about this?"
- `updated`: today's date whenever the page is modified. `sources`: every raw file the page was derived from.
- Optional `## What argues against it` and `## Open questions` go before `## See Also` ([docs/wiki-schema.md](docs/wiki-schema.md)); only when a source supports them.

### Type Tags (include exactly one)

| Tag | Use when |
|---|---|
| `concept` | Explaining a technology, framework, or idea |
| `pattern` | A reusable implementation pattern |
| `decision` | A documented architectural choice with tradeoffs |
| `project` | Project-level knowledge page |
| `comparison` | Comparing two or more technologies/approaches |
| `reference` | Quick-reference cheat sheet |
| `conflict` | Page has a flagged contradiction |

### Tombstones

Compaction never deletes a page: it keeps the filename, adds `tombstone` to tags and reduces the body to one line `[[Successor]] — supersedes`. Excluded from the search index, readable via `read_page`, exempt from orphan rules; only `/compact-wiki` creates them. Template: [docs/wiki-templates.md](docs/wiki-templates.md).

## Wikilinks and Typed Relationships

- `[[Page Title]]` for all cross-references; prefer the concept page over the project page; a new page gets a backlink from an existing page immediately. `[[See also: Page Title]]` is acceptable in See Also.
- In `## See Also`, annotate links `— type`. **Direction:** the type describes the *linked* page relative to the page it is written on: `- [[X]] — prerequisite-for` on page P reads "X is a prerequisite for P". Retrieval expansion (`src/librarian/retrieval/graph_expansion.py`) depends on this, so write the link on the page X relates *to*.

| Type | `- [[X]] — type` on page P means |
|------|---------|
| `extends` | X builds on or refines P |
| `prerequisite-for` | Understand X before P |
| `alternative-to` | X is a competing approach to the same problem (symmetric) |
| `instance-of` | X is a concrete example of the general pattern P |
| `contradicts` | X disagrees with P (links to conflict entry) |
| `supersedes` | X replaces P (tombstones point at their successor this way) |
| `related` | Weak, undirected association; not walked by retrieval expansion |

Use `related` rather than inventing a type (`part-of`, `depends-on`, `complements`, …); nuance goes in a parenthetical: `- [[X]] — related (part of; the eval stage)`. Canonical types: `CANONICAL_LINK_TYPES` in `src/librarian/wiki/common.py`. Untyped links remain valid; type them gradually.

---

## Ingest Protocol

Run for **every** new raw source, however small. Log one line per run: `uv run librarian wiki log ingest "<source> -> <n> new, <n> updated"`. Examples: [docs/wiki-templates.md](docs/wiki-templates.md).

0. **Triage:** `uv run librarian ingest triage <files>` routes each file: `clear`, `strip` (contact details), `decide` (listed term or private page name: generalise, or compile to `data/wiki/private/`) or `stop` (a secret). When unsure, use `private/`. Terms: `data/wiki/private/_sensitive-terms.txt`. Steps are in the ingest skill.
1. **Read the source fully** before writing to `data/wiki/`.
2. **Identify** all entities, concepts, decisions, open questions.
3. **Extract atomic concepts:** every named technique, pattern, algorithm or method with a non-obvious mechanism gets its own page; never bury it as a bullet in a coarser page.
4. **Per item:** find or create the page; update summary, facts, `sources:` and `updated:`.
5. **Scan for contradictions** with existing wiki claims; if any, go to 6 (never silently overwrite).
6. **Handle contradictions:** entry in `data/wiki/_conflicts.md`, tag the page `conflict`, cite both claims. Do not resolve; flag for human review.
7. **Cross-references (bidirectional):** add `[[wikilinks]]`, with atomic pages linked inline from at least one coarser page; for each new page add backlinks from 2–3 existing pages' `## See Also`, typed where clear.
8. **Index:** `uv run librarian wiki index-add <pages>` (updates `data/wiki/_index.md`).
9. **Orphan check (blocking):** every new page needs an incoming backlink; `uv run librarian wiki verify <pages>` checks this and the index entry (exit 1 on failure). If you cannot find a page to backlink from, STOP and report; do not mark the file ingested in the manifest.
10. **Relink pass:** `uv run librarian wiki relink` is suggest-only and never modifies a page. Review `data/wiki/_relink_suggestions.md`, add worthwhile candidates **manually, with typed relationships** (`- [[Page]] — extends`), delete dismissed entries (rationale: `data/wiki/meta/wiki-graph-engineering.md`).
11. **Accumulator ceiling:** pages with per-session appended rows (e.g. `meta/session-log.md`) keep the last ~30 entries in full; roll older ones into month-range summary rows at ingest time (same rule as index files). Compaction is the backstop.

## Query Protocol

1. Check `data/wiki/_index.md` (or the domain subdirectory, or `data/wiki/projects/`). 2. Read pages in full. 3. Synthesise a grounded answer citing pages. 4. Offer to file a worthwhile insight as a page. 5. Flag a gap for future ingest if no page covers it.

## Lint Protocol

Output order: BLOCKER (conflicts, dead links, private leak) → WARN (orphans, stale >60 days, untyped) → NOTE (missing coverage, bridge gaps, stale suggestions). Stale pages are flagged, not auto-updated. Full check list, ontology codes and health-number table: [docs/wiki-health.md](docs/wiki-health.md).

- **Private leak (blocks):** a page outside `private/` with a wikilink resolving into `private/` (`make wiki-check`, exit 1; a 3+ word private title in public text is a WARN). A lesson outside `data/courses/private/` that links, embeds or lists a lesson id into it, or names a private wiki page (`[[...]]` or `wiki:`), also blocks, as does a git-tracked file under either `private/` tree (pre-commit runs `wiki check --tracked-only`). Reports name the public file and line, never the private page.

## Compaction Protocol

`/compact-wiki`, run manually by Ramsey ~monthly (or after ~5 ingests), evidence-driven (page age, size, relinker similarity, `logs/retrieval.jsonl`). Moves: **merge** (union sources, successor absorbs all true content, merged page becomes a tombstone), **retire** (tombstone + `[[Successor]] — supersedes`), **compress** (accumulator ceiling). Dry-run report first; only Ramsey-approved moves are applied; `data/raw/` is never touched. See `.claude/skills/compact-wiki/SKILL.md` and `.claude/docs/plans/2026-07-17-knowledge-compaction.md`.

## Conflict Handling

Contradicting a wiki claim: do not silently overwrite; add an entry to `data/wiki/_conflicts.md`; tag the page `conflict`; lint surfaces unresolved ones. Resolution is a human review step: mark the entry resolved, remove the `conflict` tag, run `/lint`. Entry and resolution templates: [docs/wiki-templates.md](docs/wiki-templates.md).

## Naming Conventions

- **Files:** `kebab-case.md` (`google-adk-state-management.md`). **Decisions:** `YYYY-MM-DD-decision-slug.md`. **Raw sources:** original name or `YYYY-MM-DD-source-topic.md`. **Page titles:** Title Case ("Google ADK State Management").

## What NOT to Do

- **Do not** edit files in `data/raw/` — they are immutable inputs
- **Do not** create summary files outside the `data/wiki/` structure — all knowledge belongs in wiki pages
- **Do not** silently resolve conflicts — always flag them in `_conflicts.md`
- **Do not** leave new pages without at least one backlink
- **Do not** skip the ingest checklist for "small" sources — every source matters
- **Do not** write speculative content — wiki pages represent synthesised knowledge from sources, not inference
- **Do not** call something "deployed" because its suite passes, or "qualified" because its commit is pushed: `docs/status.md` records what was checked, and only a check on a host (date and host) or a restore drill moves a row past `tested in CI`
