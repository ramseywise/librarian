---
name: lint
description: "Health check the wiki. Finds orphan pages, dead wikilinks, stale pages, missing frontmatter, unresolved conflicts, and uncovered raw sources. Read-only — reports issues, does not fix them."
allowed-tools: Read Glob Grep Bash
---

You are running a health check on the wiki. This is a **read-only** operation — do not modify any wiki pages. Report issues only.

## Input

`$ARGUMENTS`:
- Empty → full lint
- `--quick` → only check pages modified in the last ingest session
- `--fix` → read-only is lifted; you may fix WARN and NOTE issues automatically (never fix BLOCKER without asking)

## Checks (run all, unless --quick)

### BLOCKER — must fix before trusting the wiki

- **Unresolved conflicts** — pages tagged `conflict` in frontmatter; also check `wiki/_conflicts.md` for open entries
- **Dead wikilinks** — `[[Page Name]]` references that don't match any file in `wiki/`
- **Missing frontmatter fields** — any page missing `title`, `tags`, `summary`, or `updated`

### WARN — degrades wiki quality

- **Orphan pages** — pages with no incoming `[[wikilinks]]` from any other wiki page
- **Stale pages** — `updated` date older than 60 days
- **Missing domain tag** — no domain tag from the canonical list in CLAUDE.md
- **Uncovered raw files** — files in `raw/` that have no coverage in any wiki page `sources:` list

### NOTE — good to fix when time allows

- **Missing See Also section** — pages with no cross-references at all
- **Short summaries** — `summary:` field is fewer than 8 words
- **Empty sections** — wiki sections with only a comment placeholder

## Output format

Group by severity. For each issue:
```
[BLOCKER] wiki/concepts/foo.md — dead wikilink: [[Bar Baz]] (no matching file)
[WARN]    wiki/agents/my-page.md — orphan (no incoming backlinks)
[NOTE]    wiki/concepts/bar.md — summary too short (4 words)
```

End with a summary count: `N blockers, N warnings, N notes`.

If `--fix` was passed, list what you fixed and what you skipped (with reason).
