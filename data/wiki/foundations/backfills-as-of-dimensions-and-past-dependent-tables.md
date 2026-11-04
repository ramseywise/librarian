---
title: "Backfills, As-Of Dimensions and Past-Dependent Tables"
tags: [foundations, pattern]
summary: "With idempotent per-period tasks a backfill is a rerunnable, parallelisable loop; the hard parts are which dimension version old periods should use, tables that read the previous partition, late data restatement, and reconciling afterwards."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--04-idempotency-and-backfills.md
---

# Backfills, As-Of Dimensions and Past-Dependent Tables

## Late data and restatement
A day is never finished. If rows for an old day turn up, land them and run that day again: 50 extra trips moved one partition (1,140 to 1,190 trips) and the other ten days did not change. Assign a row to its period by event time, and record when it was learned in the landing path or a load date; keeping both answers what the numbers said on a given date.

## Dimensions: today's truth or that day's truth
A backfill joined to a current-state dimension applies today's attributes to old periods and rewrites history without touching fact logic. After one zone moved borough on the 15th, rerunning the 10th against the current dimension moved 137 trips and cut that borough's total from 550 to 413, though nothing happened on the 10th. Totals stayed equal, so a total-level reconciliation cannot catch it. Restating in current territories can be a legitimate report; the error is doing it by accident, because a nightly job on a Type 1 dimension and a backfill then give different answers for the same day. Join to a dated dimension, or snapshot the dimension per day ([[dbt Snapshots: History as Samples]]).

## Dependencies on the past
A daily table depends only on its own day, so partitions rebuild in any order. A cumulative table reading yesterday's result cannot: built backwards it reported 1,200 where the true total was 12,700, with no error, since each day found no previous row and started from zero. Restating one old day stales every later partition, in order (restating January 14 stales 7 partitions through January 20). This is what `depends_on_past` and partition mappings declare. Prefer a window function over the daily table, which makes the cumulative figure a pure function of its input. A cheap test: the step between consecutive cumulative days must equal that day's trips.

## Running it
Because each day is independent and idempotent, a backfill can stop part-way, rerun over the whole range, and run in parallel, all ending in the same place: one worker or four gave the same result hash.
- Limit concurrency; a backfill competes with the daily run, and parallel runs against a single-writer store or a shared output collide.
- Choose a reprocess rule: skip existing, redo failures, or redo everything.
- Run a dry run and one old day first and compare with expectation.
- Cost it: a three-year daily backfill is more than 1,000 runs.
- Tell consumers numbers will change.
- Reconcile every partition against source afterwards; a green run says only that tasks finished.
- Restating a day and stopping stales everything downstream; work out the closure first.

## See Also
- [[Idempotent Batch Loads and Partition Overwrite]] — prerequisite-for
- [[Orchestrator Core Loop, Logical Dates and Retries]] — prerequisite-for
- [[Dagster Assets vs Airflow Tasks]] — related
- [[Airflow 3 Cron Timetables and the Logical Date]] — related
- [[SQL Window Functions]] — related
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — prerequisite-for
