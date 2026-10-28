---
title: Batch Path Through the Synchronous Chain
tags: [llm, infra, pattern]
summary: "When adding an async batch mode to an existing model-call pipeline, don't write a second sanitize-validate-review-write chain: give the synchronous function one optional precomputed-output field so a collected batch result runs through the identical code, and prove it with a differential test plus a spy asserting that function is the only writer — that is what makes a batched row not a lower-grade row by construction."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
---

# Batch Path Through the Synchronous Chain

From the akira batch-enrichment plan (an event catalogue moving its LLM enrichment backlog
to a provider Batch API for the ~50% discount).

## The problem

Provider batch APIs are submit-a-file / poll-a-job / collect-results, with up to a 24 h
completion window. None of that fits the synchronous gateway's `generate()` call, so a
second provider seam is genuinely needed for transport. The trap is letting that second
seam drag a second *processing* path along with it: a reconcile step that sanitizes,
validates, applies the review gate, flattens and writes the row on its own. Two chains
drift, and the one nobody exercises daily is the one that silently writes worse rows
(see [[The Untested Copy Wins]]).

## The mechanism

The synchronous runner already separated the model call from the deterministic chain
after it. The batch design adds exactly **one optional field** to the runner's options:

- `precomputedModelOutput?` — when present, skip the model call and use this
  already-obtained result: `enriched = options.precomputedModelOutput ?? await enrich(...)`.
- The batch reconcile step's only job, per collected item, is calling **the same runner**
  with that field set. It owns submit/poll/collect/job-state, never row semantics.

## Proving it, not promising it

Two test layers, both required:

1. **Differential (unit):** identical input and identical raw model text through (a) the
   default path with a mocked model call and (b) the precomputed path must produce a
   byte-identical result *and* an identical written row, field for field.
2. **Wiring (spy):** in the batch module's tests, assert the shared runner is the **only**
   function that turns a succeeded batch item into a written row. Without this, layer 1 is a
   true fact about the runner that may be irrelevant to the batch code.

Done-when includes breaking each on purpose — delete the precomputed branch, or add a
second write inside the batch module — and confirming at least one test goes red.

## What legitimately differs, named

- **Spend checks become estimates.** The synchronous path checks the ledger before each
  call and records actual usage after. A batch has no "before this call" moment, so the
  pre-submit check is an estimate (chars ÷ 4 × items against the run ceiling), and actual
  usage is recorded on collection with a logged warning when it diverges >25% — the
  approximation stays visible rather than trusted (see [[Spend Gate Before the Model Call]]).
- **The skip-key must still be real.** Items built at ingestion time hash the real raw
  envelope; backlog items whose raw input was never persisted get an explicit,
  non-authoritative sentinel hash with an `authoritative = false` flag — never a bare null
  (see [[Cached Derivation Without a Recompute Path]]).
- **Job state lives in tables, not memory.** A job row and per-item rows are written before
  submission, so a crash between submit and collect loses nothing; poll and collect are
  idempotent re-reads.

## Defect classes the review round found

A 10-dimension review of the first implementation returned 1 blocker and 15 important
findings. The recurring classes are worth checking in any batch orchestrator:

- **Selection ignored in-flight work** — the backlog query re-selected content already held
  by an outstanding batch (double charge). Fixing it naively created a worse bug; see
  [[Fixing an Accidentally Load-Bearing Bug]].
- **An external call and a DB write cannot be atomic.** Submit-then-record now retries, and
  on final failure logs the billed provider batch id with recovery SQL before throwing — an
  id that exists only in an exception message is spend you can lose.
- **Declared states nobody assigns.** A `reconcile_failed` status existed in the type and
  CHECK constraint but no code set it; a `skipped` counter was unreachable and printed a
  constant 0 as if measured.
- **Ledger wired only in tests.** `options.ledger?.record()` was a permanent no-op in
  production because the CLI never constructed a ledger — found independently by three
  review dimensions.
- **One malformed JSONL line aborted a whole batch**; per-item provider errors were reported
  `succeeded` with no text. Parse per line; classify per item.
- **The fake returned `data: null` from update-select**, unlike real PostgREST, which would
  silently zero any count derived from it ([[A Fake That Conforms to a Broken Seam]]).

## See Also
- [[The Untested Copy Wins]] — instance-of (the single-primitive fix applied to a batch mode)
- [[Differential Parity Testing Against the Original]] — extends (differential test between two paths of one codebase)
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — related (the batch seam is a second transport, not a second meaning)
- [[Spend Gate Before the Model Call]] — related (why batch spend checks degrade to estimates)
- [[Fixing an Accidentally Load-Bearing Bug]] — related (the blocker fix in the same review round)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — related (batch as the second cost lever)
- [[Resumable Scheduled Batch Sweep]] — extends (the scheduled, resumable form of the batch path)
