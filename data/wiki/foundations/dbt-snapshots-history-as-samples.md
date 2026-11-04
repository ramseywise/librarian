---
title: "dbt Snapshots: History as Samples"
tags: [foundations, concept]
summary: "A snapshot is a Type 2 history built by comparing a mutable source with what it holds on each run, so it samples rather than records: changes between runs are lost and a missed run cannot be rebuilt."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--03-dbt-tests-snapshots-incremental.md
---

# dbt Snapshots: History as Samples

A source that updates in place destroys its own history. A snapshot is the hand-built Type 2 dimension as a feature: each run compares the source with what it holds, closes rows that changed and inserts new versions with `dbt_valid_from` and `dbt_valid_to`. Setting the open end to a far-future date keeps range joins free of `coalesce`. Join facts on the natural key and the fact's date falling inside the range to get history as it was.

## It samples
A snapshot records the source's state at each run. When a row changed twice between runs the middle state is gone: a zone that spent one day in a second borough before moving to a third left no trace, and the first version ran straight into the third. Nothing fails and nothing can recover it. Remedies: snapshot at least as often as the source changes, or capture every change at the source with CDC. Unlike a model, a snapshot cannot be rebuilt from anything, so a missed run is an incident, and snapshots ignore `--full-refresh` by design.

## Timestamp or check
| | timestamp | check |
|---|---|---|
| Change detected by | `updated_at` moved | listed columns differ |
| `dbt_valid_from` | source's `updated_at` | the run's time |
| Misses | updates that do not bump the column (common with hand-run fixes) | changes outside the listed columns |

Prefer timestamp when the column is trustworthy, since it records when the change happened, not when it was noticed. In one test a rename of a zone added a row to the timestamp snapshot but none to a check snapshot watching only the borough column.

## Hard deletes
Rows that vanish from the source are ignored by default, so a deleted row stays current forever. `hard_deletes: invalidate` closes it; `new_record` adds a row flagged deleted.

## Rules
- Snapshot sources directly and keep logic out, or a transform bug is baked into permanent history.
- Verify the source really bumps `updated_at`, including on manual fixes.
- Declared in YAML since dbt 1.9.

## See Also
- [[dbt Incremental Models: Watermarks, Lookback and Strategies]] — related
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — related (a dated dimension keeps a backfill honest)
- [[dbt Layers, Materialisations and the ref Graph]] — related
