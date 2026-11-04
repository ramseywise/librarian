---
title: "Write-Audit-Publish and Atomic Visibility"
tags: [foundations, pattern]
summary: "Idempotency repairs a crash on rerun but not what readers see meanwhile; write beside and swap so readers never see half a write, audit the staged copy before publishing so a failed test protects the tested table too, and expose only what passes: an honest gap instead of a wrong number, and a containment tool during an incident."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--04-idempotency-and-backfills.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--01-quality-dimensions-and-tests.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--03-incident-playbooks.md
---

# Write-Audit-Publish and Atomic Visibility

## Readers must never see half a write
A rerun repairs a crash, but between crash and repair readers see whatever is on disk. Writing in place and crashing halfway left readers 500 of 1,000 rows in a file that looked valid; writing to a temp file and renaming left the old complete file until the new one was ready, 1,000 rows. The rename is atomic only within one POSIX filesystem. Object stores have no directory rename, which is a main reason table formats exist: they commit a new metadata snapshot atomically so a half-written set of files is invisible. The same holds for batch jobs generally: build a new output and switch to it, rather than writing partial results to an external system from inside the job.

## Write, audit, publish
A test run after publication measures the damage; one run before it prevents it. The gap between written and visible is where tests run. Build a staging copy with the period replaced, run the audit on it, and swap into production in one transaction only if it passes.
- It closes the hole that a failing test in a build only protects what is downstream ([[dbt Build Test Semantics, Severity and Source Freshness]]).
- Example: a truncated re-landing shrank one day to 40 trips; an audit requiring at least 500 refused it, production kept 1,130 trips, and re-landing the correct file fixed it.
- Copying the whole table is for clarity; on a warehouse use a zero-copy clone or a table format's branches so the audit is cheap.

## A gate over days

One implementation is two small tables and a view: a `published_days` table, a `quarantine` table with a reason, and a `trips_published` view that joins raw data to published days only. The audit runs the row-level rules (no rows, duplicate keys, null share above 1%, median outside an expected band). A passing day is inserted into published days; a failing day goes to quarantine and is removed from published. Table formats can do the same with an audit branch; in dbt, tests upstream of the published model.

Over a 91-day synthetic quarter the gate published 80 days and quarantined 11: three single-day faults plus all eight unit-change days. Readers saw a gap; a gap is visible and honest, while a wrong number gets used.

## Where it sits

Each stage covers what the last cannot: a model contract cannot see a null spike, a row test cannot see a missing day, and monitors see those only after publication and only against history. Block when wrong data costs more than late data.

## Design traps

- Audit the layer that will be published. Auditing raw after a deduplicating repair keeps failing, so the gate would never release the repaired day; decide this before an incident.
- Without a gate, containment is cruder: pause the downstream DAG, restore the previous table version if the format supports it, or put a warning on the dashboard. For a model, rolling back the learned model is an ML-specific option, useless if the inputs are what is wrong.
- The same swap-a-pointer idea gives data deploys a rollback (see [[Parallel Run and Reconcile at the Grain People Read]]).

## See Also
- [[Idempotent Batch Loads and Partition Overwrite]] — prerequisite-for
- [[dbt Build Test Semantics, Severity and Source Freshness]] — related
- [[Dagster Assets vs Airflow Tasks]] — related (both leave the checked table already written)
- [[Data Quality Dimensions and Tests as Failing-Row Queries]] — prerequisite-for
- [[Data Incident Playbook: Contain Before Diagnosing]] — related
- [[Rollback Restores Code Only]] — related
