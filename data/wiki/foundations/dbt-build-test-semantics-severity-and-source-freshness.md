---
title: "dbt Build Test Semantics, Severity and Source Freshness"
tags: [foundations, concept]
summary: "A dbt test is a query returning the rows that break a rule; in dbt build a failing error-severity test skips downstream models but the tested model is already rebuilt, and only freshness notices data that never arrived."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--01-transform.md
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--03-dbt-tests-snapshots-incremental.md
---

# dbt Build Test Semantics, Severity and Source Freshness

## What a test is
A test is a query that returns the failing rows; zero rows passes. The four built-ins each catch a failure already met:
| Test | Catches |
|---|---|
| unique | dedupe failed, surrogate key collides |
| not_null | required field arrived empty |
| relationships | foreign key with no parent |
| accepted_values | a new code the logic does not know |

## What build protects, and what it does not
`dbt build` walks the DAG building and testing together. A failure at `error` severity skips the models downstream, so the dashboard keeps yesterday's correct numbers. But a test queries the built table, so the tested model was rebuilt before it ran and its bad rows are already there for anyone querying it directly. The default protects the layer below the failing test, never the model under test. Write-audit-publish ([[Write-Audit-Publish and Atomic Visibility]]) closes that gap.

Read a failure count as "how many rows this query returned". In one run 200 bad source rows carrying a new payment code produced one failing row, because `accepted_values` returns each wrong value once.

## Severity and thresholds
- Decide per test: keys at `error`, descriptive columns at `warn`. Setting everything to warn means the first unread warning teaches the team to read none.
- `warn_if` and `error_if` put thresholds on the failing-row count so one test can warn low and fail high. With warn above 0 and error above 50, 12 negative fares warned and the build continued; 51 would have stopped it. A threshold is a decision about tolerable known dirt and should be written down with a reason; a long-run "usually around 12" belongs in a monitor that watches the trend.
- `store_failures` writes failing rows to a table so the person on call can inspect them without rerunning.

## Source freshness: the test that needs no data
Row tests pass forever on yesterday's clean rows if ingest has quietly stopped. Freshness compares the newest timestamp in a column with the clock, with `warn_after` and `error_after` thresholds (for example 6 and 24 hours). Point `loaded_at_field` at when the row arrived, not when the event happened: an event timestamp conflates a late batch with a quiet night. It is the first ingest monitor; richer monitors are a later stage.

## See Also
- [[dbt Layers, Materialisations and the ref Graph]] — prerequisite-for
- [[dbt Singular, Generic and Unit Tests with Reconciliation]] — extends
- [[Write-Audit-Publish and Atomic Visibility]] — extends
- [[Dagster Assets vs Airflow Tasks]] — related (blocking asset checks make the same trade)
