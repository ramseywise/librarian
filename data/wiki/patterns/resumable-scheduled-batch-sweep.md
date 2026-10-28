---
title: Resumable Scheduled Batch Sweep
tags: [infra, llm, pattern]
summary: "Drain a model-enrichment backlog with an unattended job where one run per vertical either resolves the single open batch job (poll it, collect it) or submits one bounded slice — never both concurrently, never auto-retrying failures without a lineage cap, and with every recovery branch folding its submit result into the run's one log line so it can say whether money was spent."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis271-scheduled-sweep.md
---

# Resumable Scheduled Batch Sweep

An event catalogue (repo akira, 2026-09) enriched content through a provider batch API with a
hard-coded 24-hour completion window. The manual CLI already had submit, poll, collect and
retry-failed modes. The task was to run it unattended. Because of the 24-hour window, one
invocation cannot submit and collect the same job, so the job's state has to carry across runs.

## One run, one decision

`runScheduledSweep` handles one vertical per call and adds **no lifecycle logic of its own**.
Every stage delegates to the same exported function the manual CLI calls; the new code only
sequences "given this job's state, what happens this run":

1. Read the **single most recent** job for the vertical (`started_at DESC`, `limit 1`).
2. `submitted` / `in_progress` → poll it (which also strands a dead job's items).
3. `completed` (finished at the provider, not yet collected) → collect and reconcile.
4. `failed` / `expired` / `reconcile_failed` / `preparing` → logged, **not open**, so they do not
   block a new slice.
5. Nothing open → select a bounded `--limit` slice and submit. Zero candidates is a normal,
   logged outcome, not an error.

A daily cadence fits the 24-hour window. By the next run the previous job has usually resolved,
so one run can collect yesterday's slice and submit today's.

## Decisions with a tradeoff named

- **No auto-retry without a lineage cap.** Retrying failed items creates a *new* job. That job
  is found as open next run, collected, and if the content always fails (a prompt that always
  errors, content the model always refuses), the same rule retries it again forever. No column
  marks "this is a retry of a retry", and adding one is a schema change. So the sweep logs
  `failed_count > 0` at `warn` and leaves retry as a manual operator command. A source-grep test
  asserts the retry function is never imported. The scope cut was named as an open question,
  not made silently.
- **A stuck job blocks its vertical.** A job stuck `in_progress` for days stops new submits for
  that vertical. The alternative, submitting regardless, risks unbounded concurrent spend, which
  is worse. An operator can still poll the stuck job by hand.
- **Most recent wins.** A manual submit racing the scheduled one leaves two open jobs. Only the
  newest is acted on, and the older drains a run later. Content-level double billing is already
  prevented by excluding rows held by any pending batch item, whichever job row is inspected.
- **`--limit` is the lever; the token ceiling is the backstop.** The per-run token ceiling
  refuses outright and is not the operating control. Literal per-vertical limits in the workflow
  YAML (25/15/15, which drains a measured 418-row backlog in about three weeks) are the
  operating control. They are a cost/pace decision for the operator, not a new env var.
- **Separate spend ledgers for chained stages.** When QC was later chained onto the rows a
  collect just wrote, it got its own ledger against the same per-run ceiling, not the
  enrichment ledger. Sharing one would let whichever ran first starve the other depending on
  call order. The QC candidate list is exactly the ids the collect reports as written. Reusing
  the backlog-sweep function would have meant ignoring its selector or re-querying state the
  caller already had.
- **A new workflow file, not a step in the crawl workflow.** A crawl failure and a stuck batch
  job are independently schedulable and independently failable. The arming convention is
  "cron commented out", because the risk is spend ([[Arm Unattended Writers by Risk Type]]).

## The defect class review caught: the recovery branch that hides its spend

Round 1 found the same bug twice. On both recovery paths (a dead job, a stale `preparing` job)
the sweep called `submitSlice()`, **threw the result away**, and returned
`{ action: 'observed_dead', jobId: <the dead job's id> }`. The workflow prints that JSON as the
run's only record. An operator could not tell whether a fresh batch had been submitted (money
spent, new job id unknown) or the backlog was empty and still stranded. One branch even logged
"proceeding to submit a fresh slice" and never confirmed it.

The fix added a `resubmit: { action: 'submitted' | 'no_candidates', jobId?, candidateCount? }`
field to both the result and the warn log. The top-level `jobId` kept its meaning (the old job
observed). Four tests cover both branches × both outcomes, and they were verified RED against the
restored pre-fix code, so they test the discarded result itself. The rule: **for an unattended
job, the one log line must answer "did this run spend, on what, and if not, why not" without a
second query.**

A recorded nit from the same review: the production-write guard is injected as `() => void`, so
a future second caller could pass a no-op. It was left as is, because injection is the
established pattern and the only caller passes the real guard. It was written down so a second
caller becomes a deliberate decision.

## See Also
- [[Batch Path Through the Synchronous Chain]] — extends (the batch lifecycle this sweep schedules)
- [[Spend Gate Before the Model Call]] — related (the per-row skip that bounds what a slice spends)
- [[Arm Unattended Writers by Risk Type]] — related (why the cron ships commented out)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (another outcome that reads as success in the log)
