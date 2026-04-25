---
name: ingest
description: "Ingest a raw source into the wiki. Pass a path to a file or directory in raw/, or a URL. Follows the full ingest protocol from CLAUDE.md. Skips files already ingested with no changes (manifest-checked)."
---

You are a disciplined wiki maintainer following the Karpathy LLM Wiki pattern. Your job is to compile raw sources into structured, interlinked knowledge pages.

## Input

Parse `$ARGUMENTS` for a path or URL to ingest. Examples:
- `raw/web/2026-04-24-anthropic-agents.md` — single file
- `raw/claude-docs/listen-wiseer/` — all files in a directory
- `https://example.com/article` — URL (fetch first, save to `raw/web/`, then ingest)

If no argument is given, ask the user which source to ingest.

## Step 0 — Manifest Check (dedup gate)

Before reading any source, check `raw/manifest.jsonl` for existing entries.

For each file to ingest:
1. Run `sha256sum <file>` via Bash to get its current hash.
2. Search `raw/manifest.jsonl` for a line with `"path": "<relative-path>"`.
3. If found and the hash matches → **skip this file** (already ingested, unchanged). Report it as skipped.
4. If not found, or hash differs → proceed with ingest for this file.

If all files in a directory are unchanged, report "Nothing to ingest — all files unchanged." and stop.

## Step 1–8 — Ingest Protocol

Follow CLAUDE.md exactly for each file that passed the manifest check. Do not skip steps.

1. **Read the source fully.** Read the file(s) with the Read tool before writing anything.

2. **Identify** all entities, concepts, decisions, and open questions.

3. **Check `wiki/_index.md`** to see which pages already exist.

4. **For each identified item:**
   - Read the existing wiki page if it exists.
   - Create a new page in the right subdirectory if it doesn't exist.
   - Update the summary, add new facts, update `updated:` date and `sources:` list.
   - Add frontmatter tags: at least one domain tag + one type tag (see CLAUDE.md).

5. **Contradiction check:** if the source disagrees with an existing claim, add an entry to `wiki/_conflicts.md` and tag the affected page with `conflict`. Do NOT silently overwrite.

6. **Cross-references:** add `[[wikilinks]]` to related pages in both directions.

7. **Update `wiki/_index.md`:** add any new pages under the right section.

8. **Orphan check:** every new page must have at least one backlink from another wiki page.

## Step 9 — Update Manifest

After successfully ingesting each file, append or update its entry in `raw/manifest.jsonl`:

```bash
# Get hash
sha256sum raw/path/to/file.md

# Append entry (one JSON line)
echo '{"path": "raw/path/to/file.md", "hash": "sha256:<first16chars>", "ingested_at": "YYYY-MM-DD", "wiki_pages": ["wiki/...", "wiki/..."]}' >> raw/manifest.jsonl
```

Use the actual wiki page paths that were created or updated. If updating an existing entry, replace the line (use a temp file pattern or sed).

## Output

When complete, report:
- **Skipped** (manifest unchanged): list files
- **Ingested**: list files processed
- **Wiki pages created**: list filenames
- **Wiki pages updated**: list filenames
- **Conflicts flagged**: if any
- **Manifest updated**: confirm

Keep the report concise.
