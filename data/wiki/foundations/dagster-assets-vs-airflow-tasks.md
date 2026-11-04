---
title: "Dagster Assets vs Airflow Tasks"
tags: [foundations, comparison]
summary: "Dagster's nodes are tables that should exist and Airflow's are work to run, so Dagster can answer which partitions are missing while Airflow reports which runs happened; both leave the checked table already written."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--05-dagster-and-airflow.md
---

# Dagster Assets vs Airflow Tasks

At 09:00 after an outage the question is not "did the job run" but "which days of which tables are wrong". An edge in an Airflow graph says run this after that; an edge in a Dagster graph says this table is computed from that one.

| | Dagster | Airflow |
|---|---|---|
| Node | asset: table, file or model that should exist | task in a Dag |
| Logical date | partition key, one of a declared set | `ds` / logical date from a timetable |
| What is missing | ask the instance which partitions exist | infer from Dag runs and states |
| Failed quality rule | blocking asset check | a task that raises |
| Backfill | select partitions, one run each by default | `airflow backfill create` over a range |
| dbt | models become assets, tests become checks | Cosmos turns a project into a Dag |

## Dagster behaviours
- Partitions are declared once and shared, so a schedule derives from them; a 03:00 run on the 14th builds the 13th, the last complete day.
- An asset check does not stop downstream assets by default; blocking must be requested. With it non-blocking, a poisoned day gave a green run while the report total fell from 315,233 to 257,445, a loss of 57,788 in fares.
- With blocking, the report never ran, but the checked table was already written; the idempotent task made repair a plain rerun.
- Partitioning an asset that rebuilds from all days (a report) records more than it means; make it unpartitioned downstream of the partitioned one.
- Passing data between assets pickles to local disk by default: fine for a list, wrong for a warehouse table.

## Airflow behaviours
- New Dags start paused. A check is just a task; Airflow does not know it tests a table, and a failed task leaves its successor "upstream failed".
- Backfill is a request stored in the metadata database and carried out by the scheduler, with a dry run and a reprocess behaviour; the range is a range of run dates (15th to 18th gave three runs).
- Two backfill runs at once failed on a DuckDB file lock because one process may write at a time; run serially or use a concurrent-writer warehouse.
- Runs are not tables: a manual delete leaves every run green. Dagster shares the blind spot but keeps its record per table and day.
- Since 3.0 an `@asset` is a one-task Dag whose completion schedules consumers, with no edge or sensor; it has no per-partition state and its runs have no logical date, so idempotency rules are yours to enforce.
- Avoid heavy imports at Dag top level and large XCom values; use absolute paths or connections on real workers.

## dbt in the graph
`dbt build` inside one task is a single opaque box. `dagster-dbt` read two models as two assets and two tests as two checks; ingest, dbt and ML training can then share one graph.

## Choosing
Neither fixes a non-idempotent task, a run without a logical date or an unchecked report. Choose the tool the organisation runs; for a new dbt-heavy platform where lineage matters, Dagster.

## See Also
- [[Airflow 3 Cron Timetables and the Logical Date]] — extends
- [[Orchestrator Design Rules and Tool Choice]] — extends
- [[Orchestrator Core Loop, Logical Dates and Retries]] — prerequisite-for
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — related
