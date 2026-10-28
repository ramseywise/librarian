---
title: Offline Prompt Experiment Runner
tags: [eval, prompting, pattern, conflict]
summary: "Try a prompt change on a frozen, stratified sample of real rows before shipping it: keep a typed variant registry of same-shaped template functions with production auto-registered as control, call the model gateway and the pure pipeline directly with the write-back half removed, prove it is read-only with a client Proxy that throws on any write, and resume from append-only JSONL that tolerates (and self-heals) a truncated final line."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis272-enrichment-prompt-experiments.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis272-prompt-experiment-runner.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis272-prompt-experiment-runner.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis272-prompt-experiment-runner.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis272-prompt-experiment-runner.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis272-prompt-experiment-runner.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
---

# Offline Prompt Experiment Runner

From akira's enrichment-prompt experiment plan (DIS-272). Two downstream pieces of work
needed it. A prompt and output rewrite needed a way to try a prompt before shipping it.
Human labels needed a stable prompt identity to key against. The runner was built in two
phases with a review boundary between them: first prompt identity, then the runner.

## Phase 1: stamp prompt identity on every row

Three nullable `text` columns on each enrichment table: `model`, `prompt_version`, and
`prompt_hash`. The names copy the adjacent QC table's convention rather than inventing a
second one.

- **`prompt_hash` hashes the template, not the row.** SHA-256 of the template function
  rendered with empty placeholders, `template('', '')`. It is invariant across rows and
  changes only when the instruction text changes, including per-vertical vocabulary lists
  interpolated into it. Row content already has its own `content_hash`. Mixing the two
  would make the prompt hash change on every row. The function is generic over the
  template function, so experiment variants hash through the same path as production.
- **A human-bumped version plus an automatic hash backstop.** `PROMPT_VERSION` is bumped by
  hand when the production prompt text changes on purpose. It is deliberately a separate
  axis from the output-contract version. The hash catches the case where someone forgets
  to bump it. A golden-hash test pins the per-vertical hashes, so prompt drift without a
  bump fails CI.
- **Computed once, at the shared entry point.** The default identity is computed in the
  single function both the sync and batch paths already call. Neither caller changed. This
  was a lesson learned on an earlier content-hash extraction, applied up front this time.
- **History stays NULL.** No sentinel and no fabricated backfill. A row either was produced
  after the migration and has a real value, or it wasn't.
- **The column must accept any provider's model string.** No CHECK constraint or enum, so a
  future provider adapter needs no coordination.
- **An unpushed migration breaks every insert.** The writeback had no column allowlist, so
  new keys reach the DB automatically. That also means a missing migration fails *every*
  enrichment insert. The drift check was extended to probe the new column. See
  [[Migration Done Means Pushed and Probed]].

## Phase 2: the runner

- **Frozen, stratified sample.** Rows are picked by vertical × completeness bucket with a
  seeded Fisher–Yates shuffle (a bare sort by id would have made the seed a dead parameter).
  The sample is frozen to a manifest file. Row content is re-read live at run time.
- **Variant registry of same-shaped functions.** A variant has exactly the shape of the
  production template, `(summary, payload) => string`. It is reviewable as a code diff and
  hashes through the same path, with no new config format or DSL. `production` is
  registered automatically from the real templates, so every run includes the live prompt
  as its control arm. This is the registry [[Build the Knobs, Not the Choice]] later mirrored
  for scoring.
- **Bypass the production call, keep the pure chain.** The production enrich call is
  hardcoded to the production template, so the runner calls the model gateway directly. It
  then runs the result through the same pure validate/sanitize/review-gate pipeline,
  stamped with the variant's identity, and the write-back half is never assembled. The
  comparison reports the signals the heuristic graders protect (validation errors and
  warnings, sanitizations applied, review-gate status) straight from the pipeline result.
  The fixture-comparison harness doesn't fit, because a live row has no hand-authored
  expected value.
- **Read-only proven structurally.** Tests wrap the DB client in a `Proxy` that throws on
  `insert`/`update`/`upsert`/`delete`/`rpc`. That is a test, not a comment saying "this
  never writes".
- **Cost is explicit.** Token counts come from `usage`, so they are exact. The dollar figure
  uses CLI-overridable per-1k rates whose default is a labelled constant, never a pricing
  table that silently goes stale. Calls are synchronous under the existing spend ceiling
  and sized for tens of rows × a few variants. Provider batch mode is out of scope.
- **No job table.** State lives in one append-only JSONL output. Resume means "skip pairs
  already in the file". A DB-backed job table is justified only when a real provider job
  needs crash-safe state across processes. This is one local process that can simply be
  re-run.
- **Guarded `main()`.** Logic lives in importable functions, so importing the module in a
  test doesn't launch the CLI. A `--help` flag let one real subprocess test run without
  credentials or live model calls.

## The resume bug review caught

The first resume implementation `JSON.parse`d every line with no guard. A run that died
mid-append (crash or full disk) left a truncated last line, and from then on *every*
`--resume` threw before running a single pair. The fix has three parts:

1. tolerate an unparseable line **only if it is the final line**, warn, and re-run that
   pair; corruption anywhere else still throws;
2. **truncate the garbage tail from the file**, not just skip it in memory. Otherwise the
   next append lands after the fragment, the fragment stops being the final line, and the
   run *after* that throws again;
3. when appending, add a leading newline if the file doesn't already end in one, so a
   retried line is never glued onto a fragment.

A companion pinning test showed that a model error mid-run rejects the promise, leaves
exactly the completed pairs on disk, and resumes with no duplicates. It was proved non-vacuous
by temporarily patching the runner to swallow per-pair errors. See
[[Append-Only Log Writer Invariants]].

### The heal itself nearly destroyed the ledger (review rounds 2–3)

The first self-heal dropped the garbage tail by **rewriting the whole ledger** with
`writeFileSync`. That truncates the file before it writes, so a crash in the middle of a heal
could wipe every completed, paid-for result. It was replaced with `fs.truncateSync` at a byte
offset, which can only ever shorten the file. The orchestrator then found that the offset had
been computed from the blank-line-filtered lines. With blank lines earlier in the file it came
out too small and cut into the last good record. A script reproduced this against the staged
code. The offset now comes from the raw file (`trimEnd`, `lastIndexOf('\n')`,
`Buffer.byteLength`). Tests use a multi-byte record (`ü`), which a character-count offset fails,
and a final pass confirmed CRLF, a trailing newline, a file holding only a partial line, and a
corrupt non-final line. Both defects came from the orchestrator's own reading, not from a
reporter. **A recovery path that rewrites the thing it recovers has to be at least as
crash-safe as the write it repairs.**

### Does the golden-hash test enforce the version bump? (flagged)

The section above says prompt drift without a bump fails CI. The Phase 1 review says otherwise.
The test pins both the template hashes and the `PROMPT_VERSION` literal, so a developer who
edits the prompt can re-pin only the hash literals and pass, leaving the version stale. The
code comment was corrected to say the test makes the bump a *visible review obligation*, not
an enforced one, and that `prompt_hash` stays truthful either way. See `_conflicts.md`.

## See Also
- [[Frozen Version Stamps on Logged Results]] — extends (prompt identity is one of the stamps)
- [[Build the Knobs, Not the Choice]] — related (the same variant-registry shape for scoring)
- [[Frozen Ranking Baseline from a Pure Ranker]] — related (copies this runner's manifest → run → JSONL → report skeleton)
- [[Batch Path Through the Synchronous Chain]] — related (the production paths that inherit the identity stamp)
- [[Append-Only Log Writer Invariants]] — related (truncated-tail handling)
- [[Write-Only Fields and the Reader Map]] — prerequisite-for (the prompt/schema slices wait for this runner)
- [[Paired Input-Perturbation Eval]] — extends (same harness, pairs are input perturbations)
