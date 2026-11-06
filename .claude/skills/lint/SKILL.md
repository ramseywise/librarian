---
name: lint
description: "Health check the wiki. Finds orphan pages, dead wikilinks, stale pages, missing frontmatter, unresolved conflicts, private leaks, and uncovered raw sources, and reports the health rates. Read-only: reports issues, and fixes only mechanical ones when given --fix. Use when checking wiki health, before a compaction, or to confirm conflicts are resolved. Do NOT use for compiling new sources (/ingest), answering questions from the wiki (/query), merging or retiring pages (/compact-wiki), or auditing taxonomy drift (/wiki-sync)."
allowed-tools: Read Glob Grep Bash
---

You are running a health check on the wiki. This is a **read-only** operation — do not modify any wiki pages. Report issues only. The one exception is `--fix`, below.

## Core rule

Report everything, change nothing unless `--fix` was passed, and even then change only what needs no judgement about meaning.

## Workflow

### Input

`$ARGUMENTS`:
- Empty → full lint
- `--quick` → only check pages modified in the last ingest session
- `--fix` → read-only is lifted for mechanical WARN and NOTE issues only; you may fix those automatically (never fix BLOCKER without asking)

### Rates

Run this first, in every mode, and report the result:

```bash
uv run librarian wiki stats --json
```

Report what the script returns; never compute or estimate a rate yourself. If it fails, write `Rates: unavailable (<reason>)`.

### Checks (run all, unless --quick)

#### BLOCKER — must fix before trusting the wiki

- **Private leak** — run `uv run librarian wiki check`; a failure is a BLOCKER. Report the public file and line the script gives, never the private title
- **Unresolved conflicts** — pages tagged `conflict` in frontmatter; also check `data/wiki/_conflicts.md` for open entries
- **Dead wikilinks** — `[[Page Name]]` references that don't match any file in `data/wiki/`
- **Missing frontmatter fields** — any page missing `title`, `tags`, `summary`, or `updated`

#### WARN — degrades wiki quality

- **Orphan pages** — pages with no incoming `[[wikilinks]]` from any other wiki page
- **Stale pages** — `updated` date older than 60 days
- **Missing domain tag** — no domain tag from the canonical list in CLAUDE.md
- **Uncovered raw files** — files in `data/raw/` that have no coverage in any wiki page `sources:` list
- **Untyped links** — pages where >50% of `## See Also` entries lack a `— type` annotation

#### NOTE — good to fix when time allows

- **Missing See Also section** — pages with no cross-references at all
- **Short summaries** — `summary:` field is fewer than 8 words
- **Empty sections** — wiki sections with only a comment placeholder
- **Bridge gaps** — domain pairs with >5 pages each but <3 cross-domain wikilinks (check `data/wiki/_bridge_suggestions.md` if it exists)
- **Stale suggestions** — `data/wiki/_relink_suggestions.md` entries older than 14 days unreviewed

### Fixed or proposed

Every finding is one or the other.

**Mechanical** (the file alone determines the fix; `--fix` applies these, and sets `updated:` on each page it changes):
- Missing domain tag, when the page's directory under `data/wiki/` names the domain
- Empty sections: remove a section holding only a comment placeholder

**Semantic** (always proposed, with `--fix` too): everything else. Which page should link an orphan, what type a link has, whether a stale page is still true, how to word a summary and which raw file deserves a page all take judgement. Stale pages are flagged, never auto-updated: the flags feed `/compact-wiki`. A BLOCKER is never fixed without asking, however mechanical it looks.

## Output format

Group by severity. For each issue, one line as below. Without `--fix`, mechanical findings stay under `Proposed` with `(mechanical)` at the end of the line.

```
Rates: orphan <n>%, average degree <n>, main component <n>%, stale <n>%, typed links <n>%, stubs <n>%, open conflicts <n>

Fixed (mechanical, --fix only):
- data/wiki/concepts/baz.md — added domain tag `rag` from directory
(or: none)

Proposed (semantic):
[BLOCKER] data/wiki/concepts/foo.md — dead wikilink: [[Bar Baz]] (no matching file)
[BLOCKER] data/wiki/concepts/qux.md:12 — private leak (see wiki_telemetry.py check)
[WARN]    data/wiki/agents/my-page.md — orphan (no incoming backlinks)
[NOTE]    data/wiki/concepts/bar.md — summary too short (4 words)

Skipped (--fix only):
- data/wiki/concepts/quux.md — <what was skipped and why>

N blockers, N warnings, N notes
```

Omit `Skipped` without `--fix`. The summary count covers every finding, fixed or not.

## Calibration

An aggressive lint that applies semantic fixes on its own judgement destroys work: a link typed wrongly steers retrieval expansion, and an orphan linked from the nearest page looks healthy while meaning nothing. A timid lint that lists every finding with no split produces a report nobody acts on. The line is mechanical against semantic, and a short mechanical list is correct.

Read the rates against these thresholds. Mark a rate `(broken)` past its broken line; the rest are reported without comment.

| Rate | Healthy | Broken |
|---|---|---|
| Orphan rate | < 5% | > 15% |
| Average degree | 8–20 | < 4 |
| Main component | ≥ 80% | < 60% |
| Stale rate | report only | none |
| Typed-link rate | ≥ 50% | none |
| Stub rate | < 5% | none |

Page count is never a health number.
