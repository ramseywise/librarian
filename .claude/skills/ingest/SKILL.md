---
name: ingest
description: "Unified wiki pipeline. No args = full sync (pull Notion + GDrive via MCP + scrape local sources + compile all changed files into wiki). With a path = compile just that raw/ dir. With a URL = fetch → save → compile. With 'figma:<url>' = pull a specific Figma/FigJam file → save → compile."
---

You are a disciplined wiki maintainer following the Karpathy LLM Wiki pattern. Your job is to compile raw sources into structured, interlinked knowledge pages.

## Input Parsing

Parse `$ARGUMENTS`:
- **No argument** → **Full pipeline mode** (Phase 1a + 1b + 2 + 3 below)
- `raw/path/` or single file → **Targeted compile mode** (Phase 3 only, scoped to that path)
- `https://...` → **URL mode**: WebFetch → save to `raw/web/YYYY-MM-DD-<slug>.md` → compile that file
- `figma:<figma-url>` → **Figma mode**: pull that specific Figma/FigJam file → save to `raw/figma/` → compile
- `resolve` → **Conflict resolution mode**: guide through unresolved entries in `wiki/_conflicts.md`

---

## Full Pipeline Mode (no args)

### Phase 1a — Pull Notion

Use the `mcp__claude_ai_Notion__notion-search`, `mcp__claude_ai_Notion__notion-fetch`, and `mcp__claude_ai_Notion__notion-query-meeting-notes` tools.

**Step 1 — Search for recent AI/agent content** (run these searches in parallel):
- `notion-search(query="agent AI LangGraph eval", filters={created_date_range: {start_date: 90 days ago}}, page_size=10, max_highlight_length=0)`
- `notion-search(query="RAG evaluation grounding pipeline", filters={created_date_range: {start_date: 90 days ago}}, page_size=10, max_highlight_length=0)`

**Step 2 — Fetch recent meeting notes**:
- `notion-query-meeting-notes` with a `created_time` filter for the last 30 days
- For each result, call `notion-fetch(id=<id>, include_transcript=false)` to get full content

**Step 3 — Fetch full content** for each search result:
- Call `notion-fetch(id=<page-id>)` for each unique result
- Deduplicate by page ID across all search results before fetching

**Step 4 — Save to raw/notion/**:
- Derive filename from page title: `raw/notion/YYYY-MM-DD-<title-slugified>.md` using the page's `last_edited_time` date
- If a file with that name already exists and content is identical → skip
- Otherwise write the fetched markdown content to the file

---

### Phase 1b — Pull Google Drive

Use the `mcp__claude_ai_Google_Drive__*` tools.

1. Call `mcp__claude_ai_Google_Drive__list_recent_files(pageSize=25, orderBy="lastModified")`
2. For each file where `mimeType` contains `google-apps.document` or `google-apps.presentation`:
   - Call `mcp__claude_ai_Google_Drive__read_file_content(fileId=<id>)`
   - Save to `raw/gdrive/YYYY-MM-DD-<title-slugified>.md` using the file's modifiedTime date
   - If file exists with identical content → skip
3. Report: N files written, N skipped

---

### Phase 2 — Scrape local sources

Run both scrapers from the librarian directory:

```bash
# Scrape Claude Code docs + session notes from all workspace projects
cd /path/to/librarian && make scrape

# Scrape CLAUDE.md, README, skill files, and docs from configured repos
uv run python etl/scrape_repos.py
```

`make scrape` pulls:
- Claude Code docs from all workspace projects (`.claude/docs/`, `.claude/skills/`, `docs/`, `.agents/`)
- Claude Code + Codex session notes → `raw/sessions/`

`etl/scrape_repos.py` pulls:
- CLAUDE.md, README.md, SANYI.md, `.claude/skills/**/*.md`, `docs/**/*.md` from repos listed in `raw/repos/repos.txt`
- Saves to `raw/repos/<repo-name>/`

---

### Phase 3 — Compile all changed raw/ into wiki

Process every `raw/` subdirectory below, in priority order. For each, run the **Manifest Check** then **Ingest Protocol**.

1. `raw/claude-docs/` — workspace project docs (highest signal)
2. `raw/repos/` — scraped repo CLAUDE.md, skills, and docs
3. `raw/notion/` — pages just pulled + any previously saved
4. `raw/gdrive/` — Drive docs just pulled
5. `raw/figma/` — any previously saved Figma content (skip if dir is empty)
6. `raw/sessions/` — compile all new files; report count processed and remaining
7. `raw/meetings/` — meeting transcripts
8. `raw/books/` — book quotes and notes
9. `raw/articles/` — article captures with highlights
10. `raw/web/` — saved web research
11. `raw/pdfs/` — PDF extracts
12. `raw/linear/` — Linear project dumps

Skip any subdirectory where all files match the manifest (nothing changed).

#### Session resume pointer

The manifest IS the resume pointer: `raw/manifest.jsonl` records every ingested file by hash. Already-ingested sessions are skipped automatically on every run. If the context window fills before all sessions are processed, stop and report how many remain — the next `/ingest raw/sessions/` picks up from the unprocessed remainder.

---

## Figma Mode (`figma:<url>`)

For a user-provided Figma URL:

- **FigJam board** (URL path `/board/`): extract `fileKey` from URL, then call `mcp__claude_ai_Figma__get_figjam(fileKey=..., nodeId="0:1")` for the root board
- **Design file** (URL path `/design/`): call `mcp__claude_ai_Figma__get_metadata(fileKey=...)` to list pages, then `mcp__claude_ai_Figma__get_design_context(fileKey=..., nodeId=<page-id>)` for relevant pages

Save extracted content to `raw/figma/YYYY-MM-DD-<file-slug>.md`, then compile that file into wiki.

> Figma files are **not auto-discovered** in full pipeline mode — they must be passed explicitly as `figma:<url>`. This is intentional: design files need targeted extraction, not bulk scraping.

---

## Conflict Resolution Mode (`resolve`)

When invoked as `/ingest resolve`:

1. Read `wiki/_conflicts.md` in full.
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

## Step 0a — Filename Lint (pre-ingest gate)

Before touching the manifest, run:

```bash
cd /Users/ramsey.wise/Workspace/librarian && uv run python etl/lint_raw.py
```

If any **ERRORS** are reported → stop and tell the user which files need renaming before ingesting. WARNINGs are advisory only; do not block on them.

---

## Step 0b — Manifest Check (dedup gate)

Before reading any source file, check `raw/manifest.jsonl`.

For each candidate file:
1. Run `sha256sum <file>` to get current hash.
2. Search manifest for `"path": "<relative-path>"`.
3. Hash matches → **skip** (unchanged). Report as skipped.
4. Not found or hash differs → proceed with ingest.

If all files in a directory are unchanged → report "Nothing to ingest — all files unchanged." and move to next directory.

---

## Steps 1–8 — Ingest Protocol

Follow `CLAUDE.md` exactly for each file that passed the manifest check.

1. **Read the source fully** before writing anything to `wiki/`.
2. **Identify** all entities, concepts, decisions, and open questions.
3. **Check `wiki/_index.md`** to see which pages already exist.
4. **For each identified item:**
   - Read the existing wiki page if it exists.
   - Create a new page in the right subdirectory if it doesn't exist.
   - Update the summary, add new facts, update `updated:` date and `sources:` list.
   - Tags: at least one domain tag + one type tag (see `CLAUDE.md`).
5. **Contradiction check:** if source disagrees with existing wiki claim → add entry to `wiki/_conflicts.md`, tag page with `conflict`. Do NOT silently overwrite.
6. **Cross-references:** add `[[wikilinks]]` to related pages in both directions.
7. **Update `wiki/_index.md`:** add any new pages under the right section. Do NOT add `wiki/private/` pages to `_index.md`.
8. **Orphan check:** every new page must have at least one backlink from another page.

### Book and article source handling

For `raw/books/` and `raw/articles/` sources, apply the same ingest protocol with these additions:
- Treat each quoted passage as a potential concept seed — if the quote names a technique or pattern, check if it deserves its own wiki page.
- Add a `source_type: quote` attribution in the page's `sources:` frontmatter when knowledge comes primarily from a book/article quote.
- Cross-reference with existing wiki pages that the quote validates or challenges.

---

## Step 9 — Update Manifest

After ingesting each file:

```bash
sha256sum raw/path/to/file.md
echo '{"path": "raw/path/to/file.md", "hash": "sha256:<first16chars>", "ingested_at": "YYYY-MM-DD", "wiki_pages": ["wiki/...", "wiki/..."]}' >> raw/manifest.jsonl
```

If updating an existing entry, replace the line (sed or temp file pattern).

---

## Output Report

```
Phase 1a (Notion):    N pages pulled, N skipped (identical)
Phase 1b (GDrive):    N files pulled, N skipped
Phase 2  (scrape):    N files written to raw/ (sessions + repos)
Manifest check:       N unchanged (skipped), N new/changed
Ingested:             N files
Wiki pages created:   [list]
Wiki pages updated:   [list]
Conflicts flagged:    [list or none]
Sessions remaining:   N files not yet ingested (run /ingest raw/sessions/ to continue)
Repos remaining:      N repos with no changes scraped since last run
Manifest updated:     ✓
```
