---
name: compact-wiki
description: "Periodic wiki compaction ritual — the recompile stage of the Karpathy pattern. Gathers evidence (page age, size, relinker similarity, retrieval telemetry), proposes merge/retire/compress moves as a dry-run report, applies ONLY Ramsey-approved moves. Manual, ~monthly. Trigger on: /compact-wiki, 'compact the wiki', 'wiki maintenance', 'consolidate wiki pages'. Use when Ramsey runs the monthly compaction, or after ~5 ingests. Do NOT use for compiling new sources (/ingest), a health check with no merges (/lint), answering questions from the wiki (/query), or taxonomy drift (/wiki-sync)."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Edit Write
---

You are running the wiki compaction ritual. **Dry-run report first, always.** Nothing
is written in phase 1–2; apply (phase 4) touches only moves Ramsey explicitly approved.

Rationale and evidence base: `.claude/docs/plans/2026-07-17-knowledge-compaction.md`.

## Core rule

Every move cites its evidence in a dry-run report first, and only the moves Ramsey approved are applied.

## Workflow

### Invariants (from CLAUDE.md contract — never violate)

- `data/raw/` is immutable. Compaction touches `data/wiki/` only.
- Every removed page leaves a **tombstone** (same filename, `tombstone` tag, one-line
  body pointing to its successor: `[[Successor]] — supersedes`). Inbound wikilinks stay
  valid; tombstones are excluded from search ranking automatically.
- `sources:` lists are never dropped — merges union them into the successor.
- Conflicts are flagged (`_conflicts.md`), never silently resolved.
- Voice/content preservation on merges: the successor must contain everything true the
  merged page contained (same discipline as guacamayo's /synthesize, provenance instead
  of voice).

### Phase 1 — Gather signals (mechanical, read-only)

0. **Stats before**: `uv run librarian wiki stats --json`. Print the result;
   it is the "before" half of the final report.
1. **Age**: `grep -rh "^updated:" data/wiki --include="*.md"` → pages >60 days stale.
2. **Size**: `find data/wiki -name "*.md" -not -name "_*" -exec wc -l {} +` → pages over
   ~300 lines (reference dumps, accumulators).
3. **Similarity**: read `data/wiki/_relink_suggestions.md` if present; optionally run
   `uv run librarian wiki relink` first. High-similarity pairs = merge candidates.
   The relinker is suggest-only, so this file is now its *complete* output — the
   auto-tier pairs it used to write straight into pages appear here too, under
   `## Auto-Link Candidates`. That tier is the strongest merge evidence in the file.
4. **Retrieval** (if `logs/retrieval.jsonl` has data): per-page retrieval counts over
   the window; co-retrieval pairs = paths appearing together in one `search_wiki`
   result set ≥3 times. Aggregate with a short python snippet, don't read the file raw.
   Absent or sparse telemetry is fine — age/size/similarity carry the first runs.
5. **Inbound links**: backlink counts from lint or the index — retire candidates need
   ≤1 inbound link.
6. **Hubs**: `uv run librarian wiki graph --json` → `hubs`. A top hub with
   `clusters_spanned` ≤3 has many links into few topics, so it may be doing several pages'
   work. Split candidates are evidence for Ramsey only: split is not one of the three moves,
   so nothing in phase 4 acts on them. If `stability` is below 0.9 the clusters are not settled:
   say so under that heading and list none.

### Phase 2 — Dry-run report

Propose moves grouped by type, each with cited evidence. No move without evidence. Print
the dry-run template under Output format.

### Phase 3 — STOP for approval

Ramsey approves per move (approve all / subset / none). No approval, no writes.

### Phase 4 — Apply approved moves only

- **Merge**: integrate content into successor (union sources, preserve everything
  true), turn merged-away page into a tombstone, update `updated:` dates.
- **Retire**: replace body with tombstone format, add `tombstone` to tags, add
  `[[Successor]] — supersedes` line.
- **Compress**: apply the accumulator ceiling (last ~30 entries + month rollups).
- Then: update `data/wiki/_index.md`, run `uv run librarian wiki relink`, rotate telemetry
  (summarize the window's aggregate into the report; truncate `logs/retrieval.jsonl`),
  append a one-line run record to the plan doc's `## Review` section, and add a
  `guacamayo/.claude/docs/tooling-ledger.md` row (status `hypothesis`, verification: "next
  compaction's evidence quality / no lint regressions").
- Finish with `/lint` expectations: zero new dead links, zero new orphans (tombstones
  are exempt from orphan rules — they exist to be pointed at, not linked from).
- **Stats after**: `uv run librarian wiki stats --json`. Print the result.
- **Log the run**, once, counts only, never a page name:
  ```bash
  uv run librarian wiki log compact "4 merged, 2 retired, 1 compressed"
  ```
  If Ramsey approved nothing, nothing was written: no stats after, no log line.

### Cadence

Manual, Ramsey-triggered, ~monthly (or after ~5 ingests). Never scheduled, never
model-invoked.

## Output format

Phase 2, before any write:

```markdown
# Wiki Compaction Dry-Run — <date>

Stats before: orphan <n>%, average degree <n>, main component <n>%, stale <n>%, typed links <n>%, stubs <n>%

## Merge candidates
- [[A]] + [[B]] → [[A]] — evidence: similarity 0.87, co-retrieved 5×, B stale 84d, 2 shared sources

## Retire candidates
- [[C]] → tombstone (supersedes → [[D]]) — evidence: stale 120d, 0 retrievals in window, 1 inbound link

## Compress candidates
- [[session-log]] — 694 lines; keep last ~30 rows, roll older into month summaries

## Split candidates (not applied here)
- [[F]] — evidence: 47 links, spans 3 clusters, 410 lines

## Left alone (near-misses worth recording)
- [[E]] — stale but 14 retrievals; staleness is not disuse
```

Phase 4, after the approved moves:

```markdown
# Wiki Compaction Applied — <date>

Applied:      <n> merged, <n> retired, <n> compressed
Not approved: <n> moves
Stats before: orphan <n>%, average degree <n>, main component <n>%, stale <n>%, typed links <n>%, stubs <n>%
Stats after:  orphan <n>%, average degree <n>, main component <n>%, stale <n>%, typed links <n>%, stubs <n>%
Lint:         <n> new dead links, <n> new orphans
Telemetry:    <the window's retrieval aggregate, before truncation>
```

## Calibration

Over-compaction loses knowledge: a merge on similarity alone can collapse two pages that
answer different queries, and a retire on age alone removes a page people still use. A
stale page (>60 days) with retrievals is not a retire candidate, and a retire candidate has
≤1 inbound link. Under-compaction is a report with no candidates despite pages over ~300 lines or accumulators
past ~30 rows.

Co-retrieval counts as evidence at ≥3 shared result sets in the window. Absent or sparse
telemetry is fine: age, size and similarity carry the first runs. Success is zero new dead
links and zero new orphans, not the number of pages removed.
