---
title: Evidence-Driven Wiki Compaction
tags: [meta, pattern]
summary: "The recompile stage of an LLM-compiled wiki: a manual, roughly monthly ritual. It gathers age, size, similarity and retrieval-telemetry evidence, proposes merge, retire and compress moves as a dry-run report, and applies only the moves a human approves. Removed pages become tombstones, so no inbound link breaks."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--skills--compact-wiki--SKILL.md
  - data/raw/repos/librarian/CLAUDE.md
---

# Evidence-Driven Wiki Compaction

Ingest only ever adds. Without a recompile step, an LLM-compiled wiki gathers
near-duplicate pages, oversized accumulator pages and stale reference dumps. librarian's
`/compact-wiki` skill is that recompile step. It is deliberately **manual, triggered by
the owner, and never model-invoked** (`disable-model-invocation: true`). It runs about
monthly, or after about five ingests.

## Invariants

- Raw sources are never touched. Compaction edits the compiled layer only.
- **Every removed page leaves a tombstone.** It keeps the same filename, gains a
  `tombstone` tag, and its body shrinks to one line: `[[Successor]] — supersedes`. Inbound
  wikilinks stay valid. The search index excludes tombstones, but `read_page` can still
  open them, and they are exempt from orphan rules.
- `sources:` lists are never dropped. A merge unions them into the successor.
- On a merge, the successor must contain everything true that the merged page contained.
  Provenance is preserved, not just prose.
- Conflicts are flagged, never resolved, during compaction.

## Phases

1. **Gather signals (mechanical, read-only).** Age (>60 days since `updated:`), size
   (>~300 lines), similarity (relinker suggestions; its auto-tier pairs are the strongest
   merge evidence), retrieval telemetry (per-page counts, plus co-retrieval pairs that
   appear together in a result set ≥3 times), and inbound links (≤1 for retire
   candidates).
2. **Dry-run report.** Propose moves grouped as merge, retire or compress. Every move cites
   its evidence. A **"left alone" section records near-misses**, for example a stale page
   that was retrieved 14 times. Staleness is not disuse.
3. **Stop for approval.** The owner approves each move. No approval means no writes.
4. **Apply approved moves only.** Then rebuild the index, rerun the relinker, rotate the
   telemetry log (summarise the window, then truncate), and record the run.

## Why each choice

- **Evidence, not taste.** A move without an evidence line does not appear in the report.
  Retrieval telemetry turns "this page seems redundant" into a measured claim. That claim
  is only as good as the telemetry: test traffic in the retrieval log contaminated it
  until the log was isolated ([[Typed-Graph Retrieval Ablation]]).
- **Tombstones over deletes.** A delete breaks every inbound link. A tombstone moves
  readers to the successor.
- **Human gate over automation.** Same reason the relinker is suggest-only. Concept drift
  (three pages describing one concept) builds up for a month between passes. That cost
  was accepted on purpose. Automated entity merging is what graph-native stores do
  ([[Compiled-Prose KB vs Graph-Native Store]]).
- **Accumulator ceiling as the primary mechanism, compaction as the backstop.** Ingest
  already rolls per-session rows older than about the last 30 into month summaries.
  Compaction catches what slipped through.

## Known gap

A tombstone records *that* a page was superseded, not *what claim changed*. A parity
review suggested a cheap partial fix: when a page is tombstoned, also record the claim
delta. That gives a rough temporal model at markdown cost.

## See Also
- [[Karpathy LLM Wiki Pattern]] — extends (the recompile stage of the compile pipeline)
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends (relinker evidence feeds merge candidates)
- [[Signal Without a Consumer]] — instance-of (telemetry made useful by a ritual that reads it)
- [[Compiled-Prose KB vs Graph-Native Store]] — alternative-to (automated dedup/entity resolution)
- [[Knowledge Base Recompile Stage]] — instance-of
