---
title: Knowledge Base Recompile Stage
tags: [meta, memory, pattern]
summary: "A compiled LLM wiki needs a recompile stage, not just a compile stage — a periodic, dry-run-first ritual that merges, retires (tombstone + supersedes) and compresses pages from age, size, similarity and retrieval-telemetry evidence, so precision does not decay as the KB grows."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-17-knowledge-compaction.md
  - data/raw/repos/librarian/.claude--docs--CHANGELOG.md
---

# Knowledge Base Recompile Stage

The [[Karpathy LLM Wiki Pattern]] as first implemented in librarian had a compile stage
(ingest creates and updates pages, adds links, flags conflicts) and no recompile stage:
no protocol step merged, retired or shrank anything. Growth was monotonic. A research pass
at ~117 pages found ~25% of pages untouched past the lint's own 60-day stale threshold,
the largest page an unbounded per-session accumulator (694 lines), and retrieval entirely
unmeasured.

## Why size is not the problem

Retrieval already solves the context-size cost of a big wiki. The real costs are:

- **Precision decay** — stale pages rank against fresh ones with no downranking or
  supersedes signal.
- **Maintenance surface** — near-duplicate pages that never conflict, so nothing flags them.

Both get worse with more writers, so consolidation is cheaper as a standing ritual than
as a later rescue.

## The schema already had the primitives

`supersedes` typed links, the conflicts file, and the 60-day stale lint all existed and
were all unused: zero pages used `supersedes`, and nothing acted on a stale flag. The
compaction work needed **a consumer for signals the schema already emitted**, not new
schema. See [[Signal Without a Consumer]].

## Instrument first, compact second

Relinker similarity finds *overlap*, not *value*: a never-read page and a load-bearing page
can be equally similar to a neighbour. So the first build step was retrieval telemetry,
one append-only JSONL line per MCP tool call (`search_wiki`, `read_page`, list/briefing
tools), wrapped so a logging failure can never break retrieval. JSONL was chosen over a
DuckDB table: it survives index rebuilds and carries no schema risk, and aggregation only
happens at compaction time, which is rare. Co-retrieval (two pages in the same result set
≥3 times) is the proxy for "these might be one page". The first dry run was allowed to go
ahead on age, size and similarity alone, without waiting for telemetry to build up.

Two lessons from running the telemetry:

- **Test traffic pollutes it.** Pytest runs called the real tools and wrote to the real log.
  43% of entries (201 of 464) came from test temp dirs before an autouse fixture redirected
  the log path for every test.
- Instrumentation that is only patched per-test leaks the moment a new test forgets the
  patch. Patching every test by default is what holds.

## The three moves

| Move | Trigger evidence | Mechanics |
|---|---|---|
| **Merge** | High similarity + co-retrieval | Union `sources:`; successor absorbs all true content; merged page becomes a tombstone |
| **Retire** | Stale + never retrieved + ≤1 inbound link | Tombstone with `[[Successor]] — supersedes` |
| **Compress** | Accumulator pages | Keep last ~30 rows, roll older into month summaries |

Invariants: raw sources untouched, every removed page leaves a tombstone, sources never
dropped, conflicts flagged and never resolved silently. Always a dry-run report first, with
a human approving each move.

## Tombstones over link rewriting

The alternative to a tombstone (rewrite every inbound link, delete the page) silently
erases provenance, which is the failure a provenance-first wiki exists to prevent. A
tombstone keeps its filename so inbound wikilinks stay valid, is excluded from the search
index at build time, and stays readable via direct page reads: you can follow it, but
search won't surface it. The objection "tombstones are growth by another name" fails
because they are one-line pointers that never rank.

## Fix accumulators upstream

The per-session log was the top compaction candidate, but the lasting fix was a rule in the
ingest protocol: pages that get appended rows keep the last ~30 entries and roll older
ones into month summaries *at ingest time*. Compaction is the backstop, not the primary
mechanism.

## See Also
- [[Karpathy LLM Wiki Pattern]] — extends (adds the missing recompile stage)
- [[Signal Without a Consumer]] — instance-of (supersedes links and stale lint had no reader)
- [[Wiki Graph Engineering — Edge Quality Over Edge Count]] — extends
- [[Single Writer, Offline Consolidation]] — alternative-to (consolidation off the critical path, applied to agent memory)
- [[Memory Lifecycle]] — extends
- [[Freshness Key Blind to Content Semantics]] — extends (the search index this ritual feeds)
