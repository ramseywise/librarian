---
name: compact-wiki
description: "Periodic wiki compaction ritual — the recompile stage of the Karpathy pattern. Gathers evidence (page age, size, relinker similarity, retrieval telemetry), proposes merge/retire/compress moves as a dry-run report, applies ONLY Ramsey-approved moves. Manual, ~monthly. Trigger on: /compact-wiki, 'compact the wiki', 'wiki maintenance', 'consolidate wiki pages'."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Edit Write
---

You are running the wiki compaction ritual. **Dry-run report first, always.** Nothing
is written in phase 1–2; apply (phase 4) touches only moves Ramsey explicitly approved.

Rationale and evidence base: `.claude/docs/plans/2026-07-17-knowledge-compaction.md`.

## Invariants (from CLAUDE.md contract — never violate)

- `raw/` is immutable. Compaction touches `wiki/` only.
- Every removed page leaves a **tombstone** (same filename, `tombstone` tag, one-line
  body pointing to its successor: `[[Successor]] — supersedes`). Inbound wikilinks stay
  valid; tombstones are excluded from search ranking automatically.
- `sources:` lists are never dropped — merges union them into the successor.
- Conflicts are flagged (`_conflicts.md`), never silently resolved.
- Voice/content preservation on merges: the successor must contain everything true the
  merged page contained (same discipline as guacamayo's /synthesize, provenance instead
  of voice).

## Phase 1 — Gather signals (mechanical, read-only)

1. **Age**: `grep -rh "^updated:" wiki --include="*.md"` → pages >60 days stale.
2. **Size**: `find wiki -name "*.md" -not -name "_*" -exec wc -l {} +` → pages over
   ~300 lines (reference dumps, accumulators).
3. **Similarity**: read `wiki/_relink_suggestions.md` if present; optionally run
   `uv run python core/relinker.py` first. High-similarity pairs = merge candidates.
4. **Retrieval** (if `logs/retrieval.jsonl` has data): per-page retrieval counts over
   the window; co-retrieval pairs = paths appearing together in one `search_wiki`
   result set ≥3 times. Aggregate with a short python snippet, don't read the file raw.
   Absent or sparse telemetry is fine — age/size/similarity carry the first runs.
5. **Inbound links**: backlink counts from lint or the index — retire candidates need
   ≤1 inbound link.

## Phase 2 — Dry-run report

Propose moves grouped by type, each with cited evidence. No move without evidence.

```markdown
# Wiki Compaction Dry-Run — <date>

## Merge candidates
- [[A]] + [[B]] → [[A]] — evidence: similarity 0.87, co-retrieved 5×, B stale 84d, 2 shared sources

## Retire candidates
- [[C]] → tombstone (supersedes → [[D]]) — evidence: stale 120d, 0 retrievals in window, 1 inbound link

## Compress candidates
- [[session-log]] — 694 lines; keep last ~30 rows, roll older into month summaries

## Left alone (near-misses worth recording)
- [[E]] — stale but 14 retrievals; staleness is not disuse
```

## Phase 3 — STOP for approval

Ramsey approves per move (approve all / subset / none). No approval, no writes.

## Phase 4 — Apply approved moves only

- **Merge**: integrate content into successor (union sources, preserve everything
  true), turn merged-away page into a tombstone, update `updated:` dates.
- **Retire**: replace body with tombstone format, add `tombstone` to tags, add
  `[[Successor]] — supersedes` line.
- **Compress**: apply the accumulator ceiling (last ~30 entries + month rollups).
- Then: update `wiki/_index.md`, run `uv run python core/relinker.py`, rotate telemetry
  (summarize the window's aggregate into the report; truncate `logs/retrieval.jsonl`),
  append a one-line run record to the plan doc's `## Review` section, and add a
  `guacamayo/.claude/docs/tooling-ledger.md` row (status `hypothesis`, verification: "next
  compaction's evidence quality / no lint regressions").
- Finish with `/lint` expectations: zero new dead links, zero new orphans (tombstones
  are exempt from orphan rules — they exist to be pointed at, not linked from).

## Cadence

Manual, Ramsey-triggered, ~monthly (or after ~5 ingests). Never scheduled, never
model-invoked.
