---
title: Persist Paid Work Per Chunk
tags: [rag, infra, pattern]
summary: "A paid backfill (embeddings, enrichment) that calls the model for every item before writing any of them loses all the paid results and its failure list on the first database error; embed one chunk, upsert that chunk atomically against the unique key, record a chunk's write failure instead of throwing, skip already-done rows by input hash, and exit non-zero when any item failed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis386-retrieval-foundation.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis386-retrieval-foundation.md
---

# Persist Paid Work Per Chunk

## The defect

akira's first embedding backfill (venue descriptors into a pgvector side table) had a
`--write` path that:

1. embedded **every** planned item first,
2. then wrote row by row, each as a separate DELETE and a separate INSERT,
3. and `throw`-ed on either error.

Review traced three failures from that shape:

- **Paid work discarded.** If the insert for row *k* failed (a transient 5xx), the throw
  dropped rows *k+1..N*, whose embeddings had already been paid for, and the `failed` list
  never reached the CLI.
- **Non-atomic replace.** A reporter had called delete-then-insert "atomic". It was two HTTP
  requests. A failed insert after a successful delete left that owner with **no** row.
- **Inert knob.** `chunkSize` changed nothing, because writes were per-row regardless.

The CLI also exited 0 when items had failed, so a scheduled run would record success.

## The shape that fixed it

- **Embed chunk → upsert chunk.** Each chunk is embedded (spend ledger checked before each
  call), then written in **one** `upsert(rows, { onConflict: <full unique key> })`. The
  key here was content kind, content id, embedding model and input-recipe version. One
  statement per chunk is atomic, and a mid-run failure keeps every earlier chunk.
- **Record, don't throw.** A chunk's write error goes into `failed`, per content id, and
  the run continues and returns its result.
- **Idempotent re-run.** An `input_text_hash` skip-check means a re-run after a partial
  failure skips already-embedded rows instead of paying again.
- **Exit code tells the truth.** `if (failed.length) process.exitCode = 1`.
- **Dry-run by default.** `--write` is opt-in. The tests mock the embedding call and
  cover ledger spend on success, ledger exhaustion mid-plan (later items count as
  `spendLimitReached`), an empty plan, and a failed chunk.

## Related decisions from the same foundation slice

- **The embedding model is a schema decision.** A `vector(1536)` column fixes the dimension,
  so changing model means a new migration plus a new input-recipe version, not a config
  swap. The recipe version is part of the unique key for that reason.
- **Build plumbing before any reader.** Storage, gateway purpose and backfill shipped with
  no query wired into ranking. The retrieval metric that would justify wiring it had zero
  labelled rows to run on. A reviewer checked the diff's file list against the feed
  entrypoints, and that check was the guard.
- **Re-measure a pilot statistic before sizing on it.** A distinctness ratio from a
  40-row, one-district pilot was re-run per venue kind against the real table before the
  dimension choice was treated as final.

## See Also
- [[Resumable Scheduled Batch Sweep]] — related (the batch-API version: every branch reports whether money was spent)
- [[A Capped Run Is Not a Clean Run]] — related (a run that stopped early must not read as complete)
- [[PGVector Migration Pattern]] — extends (the backfill half of a pgvector rollout)
- [[Silent Failure Catalogue]] — instance-of (exit 0 on partial failure)
