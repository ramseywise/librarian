---
name: ingest
description: "Unified wiki pipeline. No args = full sync (pull Notion + GDrive via MCP + scrape local sources + compile all changed files into wiki). With a path = compile just that data/raw/ dir. With a URL = fetch → save → compile. With 'figma:<url>' = pull a specific Figma/FigJam file → save → compile. Use when raw sources need compiling into the wiki: a full sync, a data/raw/ path, a URL to capture, a Figma file, or `/ingest resolve` for open conflicts. Do NOT use for answering questions from the wiki (/query), health checks (/lint), merging or retiring pages (/compact-wiki), or working the reading queue (/learn)."
---

You are a disciplined wiki maintainer following the Karpathy LLM Wiki pattern. Your job is to compile raw sources into structured, interlinked knowledge pages.

## Core rule

Every source is read in full and compiled into linked pages, with no new page left without an inbound link and no contradiction silently overwritten.

## Workflow

### Input Parsing

Parse `$ARGUMENTS`:
- **No argument** → **Full pipeline mode** (Phase 1a + 1b + 2 + 3 below)
- `data/raw/path/` or single file → **Targeted compile mode** (Phase 3 only, scoped to that path)
- `https://...` → **URL mode**: WebFetch → save to `data/raw/web/YYYY-MM-DD-<slug>.md` → compile that file
- `figma:<figma-url>` → **Figma mode**: pull that specific Figma/FigJam file → save to `data/raw/figma/` → compile
- `resolve` → **Conflict resolution mode**: guide through unresolved entries in `data/wiki/_conflicts.md`
- `--no-review` → combines with any compile mode; skips the `ingest-reviewer` call at close-out

---

### Full Pipeline Mode (no args)

#### Phase 1a — Pull Notion

Use the `mcp__claude_ai_Notion__notion-search`, `mcp__claude_ai_Notion__notion-fetch`, and `mcp__claude_ai_Notion__notion-query-meeting-notes` tools.

**Step 1 — Search for recent content** (run the searches in parallel). Read the search terms, one query per line, from `.claude/skills/ingest/queries.local.txt` (gitignored, personal). If it does not exist, copy `queries.example.txt` to it and tell the user to edit it before continuing. For each line:
- `notion-search(query="<line>", filters={created_date_range: {start_date: 90 days ago}}, page_size=10, max_highlight_length=0)`

**Step 2 — Fetch recent meeting notes**:
- `notion-query-meeting-notes` with a `created_time` filter for the last 30 days
- For each result, call `notion-fetch(id=<id>, include_transcript=false)` to get full content

**Step 3 — Fetch full content** for each search result:
- Call `notion-fetch(id=<page-id>)` for each unique result
- Deduplicate by page ID across all search results before fetching

**Step 4 — Save to data/raw/notion/**:
- Derive filename from page title: `data/raw/notion/YYYY-MM-DD-<title-slugified>.md` using the page's `last_edited_time` date
- If a file with that name already exists and content is identical → skip
- Otherwise write the fetched markdown content to the file

---

#### Phase 1b — Pull Google Drive

Use the `mcp__claude_ai_Google_Drive__*` tools.

1. Call `mcp__claude_ai_Google_Drive__list_recent_files(pageSize=25, orderBy="lastModified")`
2. For each file where `mimeType` contains `google-apps.document` or `google-apps.presentation`:
   - Call `mcp__claude_ai_Google_Drive__read_file_content(fileId=<id>)`
   - Save to `data/raw/gdrive/YYYY-MM-DD-<title-slugified>.md` using the file's modifiedTime date
   - If file exists with identical content → skip
3. Report: N files written, N skipped

---

#### Phase 2 — Scrape local sources

Run both scrapers from the librarian directory:

```bash
# Scrape Claude Code docs + session notes from all workspace projects
make scrape   # run from the repo root

# Scrape CLAUDE.md, README, skill files, and docs from configured repos
uv run librarian scrape repos
```

`make scrape` pulls:
- Claude Code docs from all workspace projects (`.claude/docs/`, `.claude/skills/`, `docs/`, `.agents/`)
- Claude Code + Codex session notes → `data/raw/sessions/`

`librarian/ingest/scrape_repos.py` pulls:
- CLAUDE.md, README.md, SANYI.md, `.claude/skills/**/*.md`, `docs/**/*.md` from repos listed in `data/raw/repos/repos.txt`
- Saves to `data/raw/repos/<repo-name>/`

---

#### Phase 3 — Compile all changed data/raw/ into wiki

Process every `data/raw/` subdirectory below, in priority order. For each, run the **Triage** gate then **Ingest Protocol**.

1. `data/raw/claude-docs/` — workspace project docs (highest signal)
2. `data/raw/repos/` — scraped repo CLAUDE.md, skills, and docs
3. `data/raw/notion/` — pages just pulled + any previously saved
4. `data/raw/gdrive/` — Drive docs just pulled
5. `data/raw/figma/` — any previously saved Figma content (skip if dir is empty)
6. `data/raw/sessions/` — compile all new files; report count processed and remaining
7. `data/raw/meetings/` — meeting transcripts
8. `data/raw/books/` — book quotes and notes
9. `data/raw/articles/` — article captures with highlights
10. `data/raw/web/` — saved web research
11. `data/raw/pdfs/` — PDF extracts
12. `data/raw/linear/` — Linear project dumps

Skip any subdirectory where all files match the manifest (nothing changed).

##### Session resume pointer

The manifest IS the resume pointer: `data/raw/manifest.jsonl` records every ingested file by hash. Already-ingested sessions are skipped automatically on every run. If the context window fills before all sessions are processed, stop and report how many remain — the next `/ingest data/raw/sessions/` picks up from the unprocessed remainder.

---

### Figma Mode (`figma:<url>`)

For a user-provided Figma URL:

- **FigJam board** (URL path `/board/`): extract `fileKey` from URL, then call `mcp__claude_ai_Figma__get_figjam(fileKey=..., nodeId="0:1")` for the root board
- **Design file** (URL path `/design/`): call `mcp__claude_ai_Figma__get_metadata(fileKey=...)` to list pages, then `mcp__claude_ai_Figma__get_design_context(fileKey=..., nodeId=<page-id>)` for relevant pages

Save extracted content to `data/raw/figma/YYYY-MM-DD-<file-slug>.md`, then compile that file into wiki.

> Figma files are **not auto-discovered** in full pipeline mode — they must be passed explicitly as `figma:<url>`. This is intentional: design files need targeted extraction, not bulk scraping.

---

### Conflict Resolution Mode (`resolve`)

When invoked as `/ingest resolve`:

1. Read `data/wiki/_conflicts.md` in full.
2. List all **Unresolved** conflicts (Status: Unresolved).
3. For each conflict in turn:
   a. Display both claims with their source citations.
   b. Read the affected wiki page and both raw source files.
   c. Ask: *Which claim is correct, or should both be preserved with context?*
   d. On human answer:
      - Update the affected wiki page with the resolution (correct claim + context from both sources if needed).
      - Mark the conflict entry resolved in `_conflicts.md` with today's date and a one-sentence explanation.
      - Remove the `conflict` tag from the page frontmatter.
   e. Continue to the next conflict.
4. Run `/lint` to confirm all conflicts are resolved.

---

### Bulk Mode (an archive, or more than about 20 sources)

Adapted from second-brain-os (MIT). Later sources should update the pages earlier ones created, so:

1. Triage first (Step 0b), then sort what is left by date, **oldest first**. Newest first makes every old source look like a contradiction.
2. Over about 200 sources, propose a filter before starting.
3. Ingest **ten sources per batch**, then report the batch range and counts, stage it, and stop for a go-ahead.
4. Read every page the first batch produced. A flaw that passes in batch one is in every later batch too.
5. Run `/lint` at the end. Large imports leave orphans and duplicates.

### Transcript Cleaning (auto-captions, subtitle files, unpunctuated meeting text)

Adapted from second-brain-os (MIT). Do this before Step 1, because pages compiled from caption dumps are noticeably worse.

Clean, never summarise: nothing is cut. Add punctuation and paragraphs, label speakers, fix mangled technical terms, keep a timestamp every few minutes, and propose split points when the recording covers separate topics. Keep filler that carries meaning, such as hedging or a speaker correcting themselves. List anything you could not resolve rather than guessing. If it is too garbled to clean reliably, say so and do not produce a plausible reconstruction.

Write the cleaned copy as a **new** dated file in the same `data/raw/` subdirectory and leave the original alone. Compile the cleaned file.

### Step 0a — Filename Lint (pre-ingest gate)

Before touching the manifest, run:

```bash
uv run librarian ingest lint-raw   # run from the repo root
```

If any **ERRORS** are reported → stop and tell the user which files need renaming before ingesting. WARNINGs are advisory only; do not block on them.

---

### Step 0b — Triage (duplicate and sensitivity gate)

Before reading any source file, run:

```bash
uv run librarian ingest triage <files or dirs>
```

Then act on each file's **status**:

| Status | Do this |
|---|---|
| `unchanged` | Skip it and report it as skipped. |
| `duplicate` | Same content under another path. Don't recompile: add this path to the `sources:` of the listed pages and record it in the manifest with the same `wiki_pages`. Say so in the report. |
| `changed` | Read it and update the listed pages. Create a page only for a concept they don't cover. |
| `new` | Normal ingest. |

And on its **route** (`new` and `changed` only):

| Route | Do this |
|---|---|
| `stop` | A live-looking secret. Exit code 1. Compile nothing from this file, tell the user the file and line, and don't print the value. It continues only after they've dealt with it. |
| `decide` | A listed term or a private page's name. Go to the routing rule below. |
| `strip` | Contact details. Leave them out of every page, then compile as public. Refer to people by role. |
| `clear` | Nothing matched. Still apply the routing rule while reading. The scan only knows patterns and the listed terms. |

**Routing rule.** A wiki page is public as soon as it's pushed, and the raw source never is, so this decision is made on the page's content:

- Would the learning survive with every organisation, person and project detail removed? Generalise it ("at <client> we found…" becomes the pattern itself) and write it public.
- Does it only make sense with that context (a client's data, an internal roadmap, an interview process, personal history)? Write it to `data/wiki/private/`. It stays queryable locally, and never goes in `_index.md` or a lesson.
- Not sure? Use `private/` and list the page in the report. Moving a page out later is easy; a pushed name stays in git history.

Public pages must not expose a source through its path either. If a raw file name carries a sensitive name (the `path` finding), write its directory in `sources:` and note the name is withheld.

Public vendors and authors a page is about aren't sensitive. The test is whether the name came from private context.

When a run has clients or colleagues the terms list doesn't have, add them to `data/wiki/private/_sensitive-terms.txt` (gitignored). `terms: NONE LISTED` in the output means names were not checked at all, so say that in the report.

After writing, `librarian wiki check` blocks on secrets, listed terms and private names in public pages. Resolve its BLOCKERs before updating the manifest.

---

### Steps 1–10 — Ingest Protocol

Follow `CLAUDE.md` exactly for each file triage did not skip.

1. **Read the source fully** before writing anything to `data/wiki/`.
2. **Identify** all entities, concepts, decisions, and open questions.
3. **Check `data/wiki/_index.md`** to see which pages already exist.
4. **For each identified item:**
   - Read the existing wiki page if it exists.
   - Create a new page in the right subdirectory if it doesn't exist.
   - Update the summary, add new facts, update `updated:` date and `sources:` list.
   - Tags: at least one domain tag + one type tag (see `CLAUDE.md`).
5. **Contradiction check:** if source disagrees with existing wiki claim → add entry to `data/wiki/_conflicts.md`, tag page with `conflict`. Do NOT silently overwrite. Consider source `confidence` level when evaluating contradictions (see `docs/wiki-templates.md` § Source Confidence).
6. **Cross-references (bidirectional):** add `[[wikilinks]]` to related pages in both directions. For each new page, identify 2–3 existing pages that should link TO it and add backlinks in their `## See Also` sections. Use typed relationships (`— extends`, `— prerequisite-for`, etc.) where the relationship type is clear.
7. **Update `data/wiki/_index.md`** with the verb, never by hand (it skips `private/` pages and keeps the count and the order):
    ```bash
    uv run librarian wiki index-add <new page paths>
    ```
8. **Orphan check (blocking):** run `uv run librarian wiki verify <new page paths>` after the backlinks of step 6. It prints `FAIL` and exits 1 for a page with no inbound link or no index line. If you cannot identify an existing page to backlink to the new page, STOP and report the issue. Do not mark the file as ingested in the manifest until `verify` passes.
9. **Update manifest** (see Step 9 below).
10. **Relink pass:** after all files in this cycle are ingested, run the relinker to discover additional semantic links:
    ```bash
    uv run librarian wiki relink
    ```
    The relinker is **suggest-only** — it never modifies a wiki page. It writes
    `data/wiki/_relink_suggestions.md` (auto-tier, mid-tier, and orphan-backfill
    candidates) and `data/wiki/_bridge_suggestions.md`. Scan the suggestions for
    high-value links and add them manually with typed relationships; dismiss the rest
    by deleting the entry. Use `--dry-run` to report to stdout without writing the
    suggestion files.

#### Book and article source handling

For `data/raw/books/` and `data/raw/articles/` sources, apply the same ingest protocol with these additions:
- Treat each quoted passage as a potential concept seed — if the quote names a technique or pattern, check if it deserves its own wiki page.
- Add a `source_type: quote` attribution in the page's `sources:` frontmatter when knowledge comes primarily from a book/article quote.
- Cross-reference with existing wiki pages that the quote validates or challenges.

---

### Step 9 — Update Manifest

After `verify` passes, for each raw file (or several files that produced the same pages):

```bash
uv run librarian ingest mark data/raw/path/to/file.md --pages data/wiki/a/x.md data/wiki/b/y.md
```

It hashes the file and replaces any earlier entry for that path. `uv run librarian ingest status` shows what is still pending.

---

### Close-out (once per run)

Run this once, after the last file, not once per file. Skip it if triage skipped every file: a run that changed nothing has nothing to report on.

1. **Print the report** (see Output format).
2. **Log the run**, in one command:
   ```bash
   uv run librarian wiki log ingest "data/raw/web/x.md -> 2 new, 3 updated, 9 links, 0 conflicts"
   ```
   `data/telemetry/operations.jsonl` is committed and `data/raw/` is not, so the detail is the source and the four counts, nothing else. Never name a private page. If the run wrote to `data/wiki/private/`, or the filename carries an organisation or person name, log the directory (`data/raw/notion/`) instead of the file.
3. **Accumulator ceiling:** if the run appended a row to a per-session accumulator page (such as `meta/session-log.md`), keep its last ~30 rows in full and roll older ones into month-range summary rows. (`operations.jsonl` is rolled by `wiki log` itself.)
4. **Call the `ingest-reviewer` agent once**, unless `--no-review` was passed. Give it the raw source path (or paths) and the list of pages written, new and updated. It returns PASS or a numbered defect list. Print the verdict as it came. Do not fix the defects in the same run: they are for the human.

## Output format

Print this once per run. For a run over several files, `Source:` is the directory or `data/raw/` with a file count (`data/raw/web/ (12 files)`), and the counts are totals.

```
Source:          data/raw/<path>
New pages:       <n>  [[A]], [[B]]
Updated pages:   <n>  [[C]]
Links added:     <n>  (<typed>/<untyped>)
Contradictions:  <n>  -> _conflicts.md
Not ingested:    <what was left out and why>
```

`Links added` counts backlinks too. `Not ingested` says `nothing` when nothing was left out; a concept merged into its parent as a stub goes here, and so does a file held back by the orphan check.

Then the reviewer's verdict, on its own:

```
Review: <PASS | numbered defect list | skipped (--no-review) | not run (<reason>)>
```

Above the report, print the lines for whatever this run actually did (the phase lines only in full pipeline mode):

```
Phase 1a (Notion):    N pages pulled, N skipped (identical)
Phase 1b (GDrive):    N files pulled, N skipped
Phase 2  (scrape):    N files written to data/raw/ (sessions + repos)
Triage:               N unchanged, N duplicate, N new/changed (N clear, N strip, N decide, N stop)
Routed private:       N pages (names withheld)
Ingested:             N files
Conflicts flagged:    [list or none]
Sessions remaining:   N files not yet ingested (run /ingest data/raw/sessions/ to continue)
Repos remaining:      N repos with no changes scraped since last run
Manifest updated:     ✓
```

`/ingest resolve` prints this instead, and logs `resolve -> <n> resolved, <n> left` with `librarian wiki log ingest`. It does not call the reviewer, which checks pages against a raw source.

```
Conflicts resolved:  <n>  [[A]]
Conflicts left:      <n>
```

## Calibration

1–3 new pages for a typical source. Zero means concepts were buried in a coarser page; more than five means stubs. A new page under 200 words is a stub: merge it into its parent.

These numbers describe a typical source and do not replace `CLAUDE.md` step 3: anything with a name and a non-obvious mechanism still gets its own page. So a dense source (a survey, a book chapter, a long design doc) may rightly produce more than five, and zero is right when every concept already has a page and `Updated pages` shows the new facts landed. The check is on stubs under 200 body words, not on the count. Past five, reread each new page: keep the ones that explain their mechanism, and merge the ones that only restate a sentence of the source. If the source cannot fill 200 words on a concept, this source does not yet support a page on it.

Buried concepts never become graph nodes; stubs become nodes that answer nothing.
