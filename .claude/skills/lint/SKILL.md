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

The deterministic checks are one verb. Run it and report its lines under the severities it gives:

```bash
uv run librarian wiki lint            # --quick <page paths> limits it to those pages; --json for parsing
uv run librarian wiki check           # Private leak: a failure is a BLOCKER; report the public file and line, never the private title
```

`wiki lint` covers: BLOCKER dead wikilinks, missing `title`/`tags`/`summary`/`updated`, `conflict`-tagged pages; WARN orphans, stale pages (older than 60 days), no domain tag; NOTE short summaries (under 8 words), no See Also. It exits 1 on a blocker.

`wiki check` is the **Private leak** check (BLOCKER).

`wiki lint` also reports, with no flag: **open entries in `data/wiki/_conflicts.md`** (BLOCKER), empty placeholder sections (NOTE) and `_relink_suggestions.md` entries unreviewed for over 14 days (NOTE). Add `--raw-coverage` for **uncovered raw files** (WARN: files in `data/raw/` that no page lists in `sources:`, one line per directory).
What the verb does not cover is yours to check, with Read/Grep:
- **Untyped links** (WARN): pages where >50% of `## See Also` entries lack a `— type` annotation (the rate is in `wiki stats`)
- **Bridge gaps** (NOTE): domain pairs with >5 pages each but <3 cross-domain wikilinks (see `data/wiki/_bridge_suggestions.md`)

### Fixed or proposed

Every finding is one or the other.

**Mechanical** (the file alone determines the fix; `uv run librarian wiki lint --fix` applies these, prints a `[FIXED]` line per change and sets `updated:` on each page it changes; `--quick <pages>` limits it):
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
[BLOCKER] data/wiki/concepts/qux.md:12 — private leak (see librarian wiki check)
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
