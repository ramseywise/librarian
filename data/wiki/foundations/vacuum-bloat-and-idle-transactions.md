---
title: "Vacuum, Bloat and Idle Transactions"
tags: [foundations, concept]
summary: "Updates leave dead row versions that VACUUM only frees for reuse, VACUUM FULL returns space under an exclusive lock, and one forgotten idle transaction stops cleanup entirely; transaction-ID wraparound is the failure to know by name."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--05-operating-data-stores.md
---

# Vacuum, Bloat and Idle Transactions

Postgres updates create a new row version and leave the old one for transactions that may still see it. Dead versions occupy space until VACUUM removes them. Bench: autovacuum off for determinism (never in production).

| State | Size | Dead rows |
|---|---|---|
| Fresh table | 16.9 MB | 0 |
| 3 full updates, no vacuum | 67.6 MB | 600,000 |
| VACUUM | 67.6 MB | 0 |
| 1 more update reuses the space | 67.6 MB | 200,000 |
| VACUUM FULL (0.34 s, exclusive) | 16.9 MB | 0 |

- Three updates made the table four times the size with the same data.
- Plain `VACUUM` frees space for reuse, not for the OS; the goal is a steady state, not a minimal table.
- `VACUUM FULL` rewrites the table under ACCESS EXCLUSIVE and needs disk for the copy, so it stops the application like a rewriting DDL ([[Safe DDL Recipes for Defaults, NOT NULL and Indexes]]). Routine vacuuming aims to avoid ever needing it.
- **A forgotten session stops cleanup.** One idle transaction holding a snapshot kept 200,000 dead rows that `VACUUM` could not remove, until the session ended. Find it in `pg_stat_activity`; `idle_in_transaction_session_timeout` is the guard (the client sees a terminated-connection error, which applications should handle). Old replication slots and standby feedback block cleanup the same way.

Autovacuum does this in production; tune it per table instead of switching it off. For big periodic deletes prefer `TRUNCATE`, or dropping a partition for time-based data.

## Wraparound

Transaction IDs are finite: the limit is about 2 billion transactions since a table's last aggressive vacuum. If autovacuum cannot keep up, the server warns near the limit and eventually stops assigning new transaction IDs. Recovery starts with ending long transactions and dropping old slots. Alert on `age(datfrozenxid)` early; the run printed 1182.

## See Also
- [[Replica Lag and Replication Slots Retain WAL]] — related
- [[Connection Pooling Turns Failure into Waiting]] — related
- [[Lock Queue and lock_timeout for Live DDL]] — related
