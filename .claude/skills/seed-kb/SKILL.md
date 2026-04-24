---
name: seed-kb
description: "Seed the KB by scraping Claude Code sessions, Codex sessions, and web bookmarks from the local machine, then ingest any newly captured sources into the wiki."
allowed-tools: Read Write Edit Bash Glob Grep
---

You are seeding the librarian KB with raw material from this machine. Run the scrapers, report what was captured, then ingest any new sources.

## Steps

### 1 — Scrape Claude Code + Codex sessions

```bash
uv run python scripts/scrape_sessions.py
```

This reads `~/.claude/projects/**/*.jsonl` and `~/.codex/sessions/` + `~/.codex/archived_sessions/` and writes session markdown files to `raw/sessions/`. Already-captured sessions are skipped (idempotent).

Pass `--source claude` or `--source codex` to run only one. Pass `--dry-run` first if you want to preview.

### 2 — Scrape web bookmarks

```bash
uv run python scripts/scrape_bookmarks.py
```

Reads `raw/web/bookmarks.txt` (one URL per line, `#` comments ignored) and writes captured pages to `raw/web/`. Already-captured URLs are skipped.

To add a one-off URL without editing bookmarks.txt:
```bash
uv run python scripts/scrape_bookmarks.py --url https://example.com/article
```

### 3 — Report what's new

After the scrapers finish, check what was written:
- Count new files in `raw/sessions/` since last ingest
- Count new files in `raw/web/` since last ingest

Report: "Scraped X sessions (Y Claude, Z Codex), W web pages."

### 4 — Ingest new sources (optional)

If `$ARGUMENTS` includes `--ingest` or the user says to ingest, run the `/ingest` skill on the new directories:

```
/ingest raw/sessions/
/ingest raw/web/
```

Otherwise, remind the user they can run `/ingest raw/sessions/` and `/ingest raw/web/` when ready.

## Arguments

- `--sessions-only` — skip bookmark scraping
- `--bookmarks-only` — skip session scraping  
- `--ingest` — automatically ingest new sources after scraping
- `--dry-run` — preview what would be written, don't write anything
- no args — run both scrapers, report, prompt before ingesting
