---
title: "Batched Rerunnable Data Backfills"
tags: [foundations, pattern]
summary: "Fill a new column in small keyed batches whose predicate selects only unfilled rows so a dead job simply restarts; a backfill alone is wrong on a live table, so a trigger for new writes and a repair pass come first."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Batched Rerunnable Data Backfills

Filling a new column for old rows is a data change, so no DDL lock is involved, yet it can stop a site through row locks. Setup: 2,000,000-row Postgres 16.2 table with a probe writing by key.

## Why batches

A single `UPDATE` locked every row until commit: 5.24 s, with the probe's worst stall 5237 ms. Batches of 10,000 rows in short keyed transactions took the worst stall to 20 ms for the same work.

## Rerunnable

The predicate selects only rows still `NULL`, so the job is restartable. A run died after 800,000 rows with 1,200,000 missing; the rerun did the remaining 1,200,000 in 3.48 s. This is the [[Idempotent Backfills and Dated Corrections]] property applied to a live table. A predicate that assumes one column is a trap: if a trigger filled one new column on touched rows but not another, rows are skipped and the second column stays NULL. Keep a verify step that compares data against an independent truth, not one that checks the job finished.

## A backfill alone is wrong

About 1,900 rows (1932 measured) came out wrong because the application kept changing the source column after the batch passed each row. New writes must reach the new column **before** the backfill starts, via a trigger or application dual write. With a trigger plus a repair pass, 1,928 rows were repaired and wrong rows went to 0. Disabling the trigger gave no errors, since every statement succeeded; only a comparison finds it.

## Brakes

Real backfills tune batch size from recent jobs and pause on database health signals such as autovacuum activity and WAL rate. Replica lag is another brake: a fast backfill is a large WAL stream for standbys to apply ([[Replica Lag and Replication Slots Retain WAL]]).

## See Also
- [[Idempotent Backfills and Dated Corrections]] — related
- [[Expand, Migrate, Contract]] — prerequisite-for
- [[Lock Queue and lock_timeout for Live DDL]] — related
