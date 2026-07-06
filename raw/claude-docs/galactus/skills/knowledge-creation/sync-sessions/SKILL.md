---
name: sync-sessions
description: "Sync all Claude sessions to librarian/raw/sessions/, enrich with cost data, and run weekly insights analysis. Run this from any project."
---

Run all three cartographer steps in sequence from the librarian directory. Use the Bash tool for each step and report results.

## Steps

**1. Migrate** — convert new JSONL sessions into session notes with cost data in frontmatter:
```bash
cd /Users/ramsey.wise/Workspace/librarian && uv run cartographer --migrate
```

**2. Enrich** — backfill cost + classification data into any notes that are missing it:
```bash
cd /Users/ramsey.wise/Workspace/librarian && uv run cartographer --enrich
```

**3. Sync + Analyze** — sync session notes to `raw/sessions/` and run Claude insights analysis:
```bash
cd /Users/ramsey.wise/Workspace/librarian && uv run cartographer --cron
```

> **Note on classification:** `--enrich` will classify `work_type`/`output_type`/`key_output` via Haiku only if `ANTHROPIC_API_KEY` is set in `librarian/.env`. Without it, cost + facet enrichment still runs; classification is skipped gracefully. To enable: add `ANTHROPIC_API_KEY=sk-ant-...` to `/Users/ramsey.wise/Workspace/librarian/.env`.

## Output

After all three complete, print a brief summary:
- How many new session notes were created (from migrate)
- How many files were enriched
- Where the insights report was saved (from --cron)
- Any errors worth flagging

Keep it to 5 lines or less.
