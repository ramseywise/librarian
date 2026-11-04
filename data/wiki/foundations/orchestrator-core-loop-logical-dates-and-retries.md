---
title: "Orchestrator Core Loop, Logical Dates and Retries"
tags: [foundations, concept]
summary: "Every orchestrator is a loop that orders tasks by dependency, skips what depends on a failure, retries with backoff and records runs against a logical date that is not the clock; scheduling is the set of expected runs minus the successful ones."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--02-orchestrate.md
---

# Orchestrator Core Loop, Logical Dates and Retries

A cron line that runs a script leaves out the decisions an orchestrator makes explicit: what depends on what, how many retries, which date a run is for, and what stops on failure. The core is small enough to write in about fifty lines: topologically sort the tasks, run each unless something it needs failed, retry within a limit, record the outcome against a logical date.

| Capability | Cron plus script | Orchestrator |
|---|---|---|
| Dependencies | order in a script | DAG; downstream waits on upstream success |
| Parameters | argv | typed run parameters (date, model run id) |
| Retries | manual rerun | per-task retry with backoff |
| Backfill | a for-loop written once | same pipeline over a date range, each run isolated |
| Observability | log files | run history, task state, alerts |
| Triggers | none | schedule, sensor, API call, upstream success |

## Failure propagation
When retries are exhausted the task is failed and everything downstream is skipped, so a publish step never puts yesterday's numbers out under today's date. A test task belongs in the graph: the orchestrator knows tasks finished, only a test knows the numbers were right. In the toy, a failing test leaves its bad output in the lake because the test ran after the write.

## Retries are for transient failures
Retry with backoff so a struggling service is not hit harder. A retry is safe only when the task is idempotent; retrying a broken SQL statement wastes attempts, and retrying an insert that timed out after succeeding writes rows twice (see [[Idempotent Batch Loads and Partition Overwrite]]). Use a small limit, and alert after it: none pages someone for every blip, unlimited hides an outage. An orchestrator declares failure from a missing heartbeat or timeout and cannot tell a dead worker from a partitioned one, so the old attempt may still be writing while the retry runs.

## The logical date
A run has a date that is not the clock. Tuesday's run may execute on Thursday and should process Tuesday. A task reading `now()` or `date.today()` can only ever process today, so a failed partition cannot be re-run. Take the logical date as a parameter, read only from what upstream wrote, and write to a path derived from that date.

## Scheduling is computing what is missing
A scheduler is a clock plus a comparison: runs the schedule says should exist minus runs that succeeded. Catch-up, backfill and recovery from an outage are the same operation on different ranges (Airflow calls it catchup, Dagster missing partitions, Mage a backfill). That comparison must live in durable state shared by everyone asking, so orchestrator state is a small database problem.

## Sensors
A schedule assumes data arrives on time; a sensor is a task that polls for evidence that it has. Give it a timeout, or a source that stops sending leaves it waiting forever with nobody told.

## See Also
- [[Orchestrator Design Rules and Tool Choice]] — extends
- [[Idempotent Batch Loads and Partition Overwrite]] — prerequisite-for
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — extends
- [[Airflow 3 Cron Timetables and the Logical Date]] — instance-of
- [[dbt Layers, Materialisations and the ref Graph]] — related
