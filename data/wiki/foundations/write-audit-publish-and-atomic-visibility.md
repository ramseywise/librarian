---
title: "Write-Audit-Publish and Atomic Visibility"
tags: [foundations, pattern]
summary: "Idempotency repairs a crash on rerun but not what readers see meanwhile; write beside and swap so readers never see half a write, and audit the staged copy before publishing so a failed test protects the tested table too."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--04-idempotency-and-backfills.md
---

# Write-Audit-Publish and Atomic Visibility

## Readers must never see half a write
A rerun repairs a crash, but between crash and repair readers see whatever is on disk. Writing in place and crashing halfway left readers 500 of 1,000 rows in a file that looked valid; writing to a temp file and renaming left the old complete file until the new one was ready, 1,000 rows. The rename is atomic only within one POSIX filesystem. Object stores have no directory rename, which is a main reason table formats exist: they commit a new metadata snapshot atomically so a half-written set of files is invisible. The same holds for batch jobs generally: build a new output and switch to it, rather than writing partial results to an external system from inside the job.

## Write, audit, publish
The gap between written and visible is where tests run. Build a staging copy with the period replaced, run the audit on it, and swap into production in one transaction only if it passes.
- It closes the hole that a failing test in a build only protects what is downstream ([[dbt Build Test Semantics, Severity and Source Freshness]]).
- Example: a truncated re-landing shrank one day to 40 trips; an audit requiring at least 500 refused it, production kept 1,130 trips, and re-landing the correct file fixed it.
- Copying the whole table is for clarity; on a warehouse use a zero-copy clone or a table format's branches so the audit is cheap.

## See Also
- [[Idempotent Batch Loads and Partition Overwrite]] — prerequisite-for
- [[dbt Build Test Semantics, Severity and Source Freshness]] — related
- [[Dagster Assets vs Airflow Tasks]] — related (both leave the checked table already written)
