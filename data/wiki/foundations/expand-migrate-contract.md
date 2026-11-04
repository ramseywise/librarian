---
title: "Expand, Migrate, Contract"
tags: [foundations, pattern]
summary: "A rename, split or type change cannot be one statement because old and new code run together during a rollout; add the new shape, dual write, backfill, verify, move readers, and drop the old shape last, since contract is the one step with no rollback."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Expand, Migrate, Contract

During a rollout old and new code run at once, so a rename means one of them is always wrong. Also known as parallel change. The contract between teams (diffing versions, major-version breaks) is in [[Breaking Schema Changes and Expand-Contract]]; this page is the live-table rollout.

## Measured

A naive rename under a running old application gave 403 `UndefinedColumn` errors in half a second. The staged version gave 0 errors in every step (old app 395 queries, worst stall 9 ms; new app through contract 534 queries, worst stall 7 ms), with 0 rows differing between old and new columns before readers moved.

## Steps

1. **Expand:** add the new column, nullable.
2. **Dual write:** a trigger (or application code, which keeps logic visible but needs a deploy first) keeps both columns current.
3. **Backfill** in batches ([[Batched Rerunnable Data Backfills]]).
4. **Verify:** compare columns, not just job success.
5. **Deploy new code** reading the new column.
6. Stop writing the old column, then **contract** later.

Large-scale versions add a comparison of old and new reads on real traffic before the switch.

## Rollback per phase

| After | To roll back | Data at risk |
|---|---|---|
| Expand | Drop the new column | None; nothing reads it |
| Backfill and verify | Same | None |
| Code reads new | Redeploy old code; trigger keeps both current | None |
| Code stops writing old | Turn old writes back on and re-sync | Only what you fail to re-sync |
| Contract | **No rollback.** Restore from backup | Everything in the dropped column |

Wait as long as you can afford before contract: a nightly job or monthly report may be the last reader. [[Lineage for Blast Radius and Rebuild Lists]] says who to ask. A migration correct when it finishes is still wrong for old code running through the deploy; test old code against the new schema.

## Migration tools

A tool such as Alembic stores a version in a table, finds the gap to the scripts and runs what is missing; Flyway does the same from SQL files with versioned and repeatable migrations. Notes: `CONCURRENTLY` needs `autocommit_block`, and the transaction before it is committed, so use a transaction per migration and `IF NOT EXISTS`; autogenerate does not understand a rename and writes an add plus a drop that empties the column, so read every generated script; a downgrade restores shape, not data (1,000 rows, 0 values after drop and re-add), so treat contract as forward-only with a tested restore as the real rollback; offline mode emits SQL for review. A tool decides when a statement runs, not which are safe.

## See Also
- [[Breaking Schema Changes and Expand-Contract]] — related
- [[Lock Queue and lock_timeout for Live DDL]] — prerequisite-for
- [[Safe DDL Recipes for Defaults, NOT NULL and Indexes]] — prerequisite-for
- [[Parallel Run and Reconcile at the Grain People Read]] — related
- [[Re-embedding a Vector Store with a Second Index]] — related
