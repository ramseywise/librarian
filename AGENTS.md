# AGENTS.md — Multi-Step Agent Rules

> Rules for agentic / multi-step operations in this repo. Read alongside CLAUDE.md.

---

## Ingest Agent

When running a batch ingest (multiple raw sources at once):

- Process sources one at a time, in chronological order (oldest first).
- After each source, update `wiki/_index.md` before moving to the next.
- Do not batch wiki page writes — each ingest is atomic per source.
- If a source fails to parse (corrupt, empty, unreadable), log it in `wiki/_conflicts.md` under "Ingest Errors" and continue.
- After all sources are processed, run lint automatically.

## Lint Agent

- Lint is read-only. Do not modify wiki pages during a lint run.
- Output all issues to stdout — do not write a lint report file unless explicitly asked.
- Prioritise: BLOCKER > WARN > NOTE.
- When running after an ingest, only lint the pages touched during that ingest session.

## Export Agent (Notion / Linear)

- Before exporting, confirm with the user which pages to export.
- Notion export: push to the workspace defined in `NOTION_TARGET_PAGE_ID` env var.
- Linear export: create tickets under the project defined in `LINEAR_PROJECT_ID` env var.
- After export, add an `exported:` field to the page frontmatter with the destination and date.
- Never export pages tagged `conflict` — resolve conflicts before exporting.

## Tool Use Discipline

- Prefer reading `wiki/_index.md` before reading individual pages — it's faster.
- When writing wiki pages, always write frontmatter first, then content.
- Use Bash only for: running scripts in `scripts/`, file operations not covered by file tools.
- Do not make web requests during ingest unless the source is a URL (use WebFetch).
