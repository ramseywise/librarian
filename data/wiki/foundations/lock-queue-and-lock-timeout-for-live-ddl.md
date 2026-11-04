---
title: "Lock Queue and lock_timeout for Live DDL"
tags: [foundations, concept]
summary: "A one-millisecond ALTER can stall every read because it queues for an ACCESS EXCLUSIVE lock behind a long reader while new queries queue behind it; a per-session lock_timeout with retry turns the stall into a short delay."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Lock Queue and lock_timeout for Live DDL

A migration changes a live system: old and new code read the table and neither stops. Measurements here come from Postgres 16.2 on a 2,000,000-row, 208 MB table with a probe application reading or writing by primary key every couple of milliseconds. A migration is safe if the probe does not notice it. Absolute times grow with table size; the shape holds.

## Which lock a statement takes

Read it from `pg_locks` rather than guessing:

| Lock | Blocks | Taken by |
|---|---|---|
| `AccessExclusiveLock` | Everything, reads included | Most `ALTER TABLE`: add, drop, rename, change type |
| `ShareLock` | Writes, not reads | Plain `CREATE INDEX` |
| `ShareRowExclusiveLock` | Writes, not reads | `ADD FOREIGN KEY`, on both tables |
| `ShareUpdateExclusiveLock` | Other schema changes and `VACUUM`, not reads or writes | `VALIDATE CONSTRAINT`, `CREATE INDEX CONCURRENTLY` |

Only an ACCESS EXCLUSIVE lock blocks a plain `SELECT`. The craft of online DDL is spending very little time holding it and doing the slow part under weaker locks ([[Safe DDL Recipes for Defaults, NOT NULL and Indexes]]).

## The queue

`ADD COLUMN` with no default only changes the catalog, so it takes a millisecond once it has the lock. Getting the lock is the problem. A report that holds a weak lock conflicts with ACCESS EXCLUSIVE, so the `ALTER` waits, and every new query on the table, even plain reads that do not conflict with the report, waits behind the `ALTER`. A slow reader plus a fast schema change gives an outage neither would cause alone.

| lock_timeout | ALTER | Read probe |
|---|---|---|
| off | finished after 2.00 s | 114 queries, worst stall 2003 ms |
| 100ms | gave up after 0.10 s | 1,596 queries, worst stall 101 ms |

## Use

Set `lock_timeout` in the migration's session, not in the server configuration, where it would apply to every session. The price is that the statement did not happen, so the migration must retry; pause between attempts longer than the timeout, since each failed attempt costs the application up to one timeout. In a lab run the retry loop took 4 attempts with worst read stall 101 ms against 2,003 ms with no timeout. Some teams ship the loop as a framework feature that retries with varying timeouts.

A related trap: a `CONCURRENTLY` index build waits for existing transactions, so an idle-in-transaction session holds it open; `idle_in_transaction_session_timeout` limits that.

## See Also
- [[Safe DDL Recipes for Defaults, NOT NULL and Indexes]] — extends
- [[Expand, Migrate, Contract]] — related
- [[Batched Rerunnable Data Backfills]] — related
- [[Vacuum, Bloat and Idle Transactions]] — related
