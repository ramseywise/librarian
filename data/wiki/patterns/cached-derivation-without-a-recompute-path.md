---
title: Cached Derivation Without a Recompute Path
tags: [patterns, infra, pattern]
summary: A column that stores a function of another column with no code path to recompute it becomes a false fact the moment its input changes — and the trap is invisible because the stored value still looks authoritative.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/akira/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/akira/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/playground/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/playground/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/playground/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-LIB-110-restructure-shared-extraction.md
---

# Cached Derivation Without a Recompute Path

Found in a catalogue census (akira): 16 of 22 disabled ingestion sources were disabled for
a reason that was no longer true.

## The mechanism

`sources.enabled` was set by a sync job from a planning tool, derived from an
"ingestion approach" field: approach X → enabled, otherwise disabled with
`last_error = 'Not an automatic import candidate'`. Two things then happened:

1. The approach values were widened in the application code, so sources that had been
   rejected now qualified.
2. The sync job was deleted. Nothing in the repo could write `enabled` any more.

The column kept its last value. It looked like a decision ("this source is off") and was
actually a cache of a function that no longer existed, computed over inputs that had since
changed. The cheapest coverage gain on the board — re-enabling sixteen sources — needed no
new code, only noticing that the flag was stale.

## Variants of the same trap

- **The status column no query filters on** (see [[Data Clusters by Writer and Trust]]) —
  stored state with no reader *and* no writer.
- **The null that means "always"**: an enrichment gate skipped rows whose `content_hash`
  matched; a side path wrote `content_hash: null`, which the gate treated as "never seen",
  so those rows were re-enriched on every run — a 3× cost multiple hiding in a cache key.
  The mechanism is `existing?.hash && existing.hash === newHash`. A null short-circuits
  the `&&` to "changed" **on every pass, forever**. A wrong non-null value mismatches at
  most once, because the next real pass writes the true hash. A remediation run that
  wrote rows outside ingest could not reconstruct the real hash offline: the hash covers
  the raw scrape envelope, the canonical row does not keep it, and most source pages were
  gone. So it backfilled a **deterministic, traceable sentinel**,
  `sha256('<issue>-remediation:' + rowId)`, on exactly the rows it wrote. That bounds the
  cost to one more re-enrichment, the same as any content change. A best-effort
  "reconstruction" was rejected: it was no more likely to match, and more likely to be
  mistaken for authoritative provenance later.
- **Intake metadata nobody reads**: of 14 columns synced from the planning tool into the
  source registry, 6 were load-bearing in code. The other 8 were derived, cached, and
  unread — and each one was a future "why does this say X?" investigation.

## Rules

- A derived column needs a named recompute path (trigger, job, or view) or it should be a
  view. If the derivation's inputs can change and nothing recomputes, the column is a lie
  with a timestamp.
- When deleting a writer, grep for every column it wrote and decide each one: recompute,
  freeze with a comment, or drop.
- Prefer deriving the truth at read time from the authoritative input (here: the approach
  field) until volume forces a cache.

## The null-hash variant: a gate that re-derives forever

The opposite failure appeared in a batch-enrichment plan (akira, 2026-09). A
skip-if-unchanged gate written as `existing?.content_hash && existing.content_hash === hash`
treats a row with a null hash as "changed" every time, so legacy rows with no hash were
re-enriched — and paid for — on every run. A null in a cache column is ambiguous: "never
computed" and "computed but not recorded" read the same. The fix wrote a sentinel hash plus a
`content_hash_authoritative = false` flag, so the batch path never writes a bare null and the
gate can tell "known stale" from "unknown". See [[Batch Path Through the Synchronous Chain]].

## A parser fix is a derivation change (librarian, 2026-08)

Fixing a frontmatter parser bug (block-list `tags:` were read as empty) changes how
**unmodified** pages parse. The search index rebuilt only pages whose mtime changed, so
the fix would never reach existing rows. The plan bumped `SCHEMA_VERSION` (4 to 5) in the
same change to force a full rebuild. Rule: any change to the derivation function, not just
to inputs, must invalidate the cache.

## See Also
- [[Data Clusters by Writer and Trust]] — extends
- [[Write-Only Fields and the Reader Map]] — complements (the reader-side audit that finds these)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (a reader keyed to a value that quietly stopped being written)
- [[Hide-Unknown Display Contract]] — complements (display labels resolver-derived at read time, never stored)
- [[Batch Path Through the Synchronous Chain]] — related (the sentinel-hash fix for null cache keys)
- [[Per-Row Content Hash Misses Cross-Row State]] — extends (incremental indexes must recompute derivations that depend on other rows)
