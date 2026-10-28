---
title: The Run Record Belongs to the Process
tags: [infra, pattern]
summary: "A scheduled job's run row should be inserted by the process itself, which gets the id back, holds it in memory and closes the row on every exit path, including a SIGTERM before a hard kill. An id passed in from the scheduler, and an UPDATE that silently matches zero rows, leave run history showing 'running' forever or record nothing at all."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis72-importer-checkpointing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis72-importer-checkpointing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis72-importer-checkpointing.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis72-importer-checkpointing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis72-importer-checkpointing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis72-importer-checkpointing.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis72-importer-checkpointing.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
---

# The Run Record Belongs to the Process

When an ingestion importer in akira moved to an unattended daily schedule, its run-history
table (`content_pipeline_runs`) became the only place to see whether last night's run
worked. Two rounds of review found that the table could not be trusted as written, for
three separate reasons. None of them caused a visible error.

## Failure 1: the scheduler supplied the id and nobody created the row

The workflow passed `PIPELINE_RUN_ID: <run_id>-<attempt>` (for example `123456789-1`) into
the process. The child table's foreign key is `uuid NOT NULL REFERENCES
content_pipeline_runs(id)`. That broke in two independent ways:

1. The value is not a uuid, so the first child insert would fail on the cast.
2. Nothing in the codebase ever **INSERTed** a run row. The run-log module only ever
   UPDATEd one. A valid uuid would still have hit the foreign key.

Config validation checked that the variable was *present*, never that it was a uuid or
that it pointed at a row. So the cron could not have succeeded even with every secret
set.

**Fix:** the process calls `startPipelineRun()` once, before any work. That function
INSERTs the row, lets Postgres generate the id (`DEFAULT gen_random_uuid()`), and returns
it. The scheduler's run id is still written to the job log for correlation, with a comment
explaining why it cannot be the primary key. An explicit id override is still allowed, but
it is validated as a uuid, and a test pins the exact scheduler-shaped value as rejected.

## Failure 2: an UPDATE that matches nothing succeeds

`finishPipelineRun` and the interrupt handler both ran `UPDATE ... WHERE id = ...`.
PostgREST does not treat a zero-row update as an error. With the id bug above, every
"close the run" call would have returned success and written nothing. Both functions now
add `.select('id')`, check that the returned array is non-empty, and throw with the id
when it is empty. This is the run-log version of
[[Audit the Class, Not the Instance]]'s rule that a zero-row response is not an error, so
the error branch never fires.

## Failure 3: a hard kill leaves the row "running" forever

`timeout-minutes: 30` kills the job before the normal completion call runs. The row stays
at `status: running` with `finished_at: null`, and the dashboard renders it as
"running…" indefinitely. That is a dead run that looks like it is still alive.

- **Catch the warning signal.** The runner sends SIGTERM, then SIGKILL about 10 seconds
  later. A SIGTERM/SIGINT handler writes `status: 'canceled'`, a value the status check
  constraint already allowed, so no migration was needed. The write races a **7-second
  budget**, so the process can still exit by itself before SIGKILL. The handler is
  unit-tested with injected dependencies across six cases: normal write, SIGINT exit
  code, no id known, write throws, write hangs past the budget, and client construction
  throws. It is not tested by signalling the real CLI, because a test that imports the
  CLI and runs its side effects has caused problems in this repo before.
- **Keep the id in memory, not the environment.** Fixing failure 1 removed the
  environment variable that the signal handler had been reading. Without a matching
  change, the interrupt handler would have stopped working on every scheduled run, which
  is the one case it exists for. The fix was an `activePipelineRun` singleton that
  `startPipelineRun` sets and the handler reads first. One fix silently disabled a
  different fix. That is why each fix gets its own review round.
- **Assume the handler can still lose.** SIGKILL cannot be caught. The dashboard's
  last-run classifier labels a row **stale** when `finished_at` is null and the row is
  older than the job timeout plus 5 minutes (35 minutes). It sorts the latest run into
  one of: clean, spend-capped, partial, stale, failed, or still running inside its window.

## Choosing the scheduler

The job ran on a GitHub Actions `schedule` trigger rather than a serverless cron. A
serverless cron fires one HTTP request, so the whole crawl-and-enrich run has to finish
inside one invocation's time limit. A scheduled CI job has no wall-clock limit. It runs
the same `npm run import` the developer runs, and it reuses the existing CI secrets. A
serverless cron suits quick API-triggered jobs, not ETL. The cost of the CI job is the
shell behaviour described in [[Verify CI Steps by Extraction, Not Retyping]].

## The general rule

Whoever creates the record owns the id. The process that does the work should create its
own run record, hold the id, close it on every exit path it can catch, and assert that
the close actually matched a row. The reader then needs a time-based fallback for the
exit path the process cannot catch. A run row left `running` and an empty history both
look like "nothing went wrong."

## Resuming a crashed run from the same records

A follow-up plan (repo akira, 2026-09-10) used these run records as checkpoints. When a
run died partway through, the next invocation should skip the sources that had already
finished instead of re-fetching all of them. No new table was needed: the per-source run
row (`UNIQUE (pipeline_run_id, content_source_id)`, with status and `finished_at`) was
already the checkpoint, and the start function already upserted on that key, so
re-processing a source needed no new code. The only new decision was **which sources to
skip**. Four rules came out of it:

- **Skip only a status that means one thing.** The stored `partial` value was a collapse
  of three different outcomes: genuinely mixed, honestly empty, and skipped. Nothing on
  the row tells them apart. Only `success AND finished_at IS NOT NULL` is skipped; every
  other status is retried. Retrying is cheap, because the per-item content-hash gate makes
  unchanged items a no-op. Auditing which states were reachable also found that two
  allowed values (`pending`, and `canceled` on this table) had no writer at all. See
  [[Map Every State to Its Writer]].
- **The crash signature comes from the exit path.** A row left at `running` with
  `finished_at IS NULL` is exactly what a hard kill leaves behind (Failure 3 above), and
  it is treated as must-retry.
- **Resume names its run explicitly. It never auto-detects.** A `RESUME_PIPELINE_RUN_ID`
  env var picks the run. "Most recent unfinished run" is ambiguous (a stuck row from days
  ago), and a wrong guess silently resumes the wrong run. Resuming is a deliberate
  operator step the next morning, kept out of the scheduled workflow, because an automatic
  resume right after a crash would hammer a source that had just returned 429.
- **Reuse the original run id so totals describe the whole logical run.** Totals are the
  banked counts of skipped rows plus this pass's in-memory counts. The one accepted loss,
  named up front: a per-content-type breakdown in a diagnostic log line, which the row
  doesn't store.

The checkpoint sits one layer above the content-hash gate. The hash gate skips the
model call for an unchanged item. The checkpoint skips fetching and parsing a whole
source, along with its robots checks and rate-limit exposure. The plan was written before
its trigger fired (≥500 items in one run, or the first observed crash), so it was held at
REFINED with a production query as the blocking open question. See
[[Named-Trigger Deferral]].

## See Also
- [[Map Every State to Its Writer]] — related (status values with no writer, found while choosing the resume skip-set)
- [[Layered Ingestion Failure Posture]] — extends (run-level observability for the same pipeline)
- [[Audit the Class, Not the Instance]] — instance-of (zero-row PostgREST responses that never reach the error branch)
- [[Silence Reads as Clean]] — instance-of (a "running" row and a no-op UPDATE both read as healthy)
- [[Verify CI Steps by Extraction, Not Retyping]] — prerequisite-for (the exit-code mapping on the same scheduled job)
- [[Silent Failure Catalogue]] — related (removing the run-id env var would have disabled the SIGTERM handler that read it)
