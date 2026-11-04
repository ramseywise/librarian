---
title: "Safe DDL Recipes for Defaults, NOT NULL and Indexes"
tags: [foundations, pattern]
summary: "Split the slow proof from the strong lock: constant defaults avoid a rewrite, NOT NULL goes through NOT VALID then VALIDATE, and indexes use CONCURRENTLY, which leaves an INVALID index if it fails."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Safe DDL Recipes for Defaults, NOT NULL and Indexes

Each recipe separates the slow work (a scan, a rewrite, a build) from the strong lock. Measurements: Postgres 16.2, 2,000,000-row table, probe writing by key. Wrap each in a [[Lock Queue and lock_timeout for Live DDL]] guard.

## Defaults: constant versus volatile

Two `ADD COLUMN ... DEFAULT` statements look alike. A non-volatile default is stored in the catalog and returned for old rows, so it is fast at any size (0.00 s, worst stall 1 ms). A volatile default such as `clock_timestamp()` must be computed per row, so the whole table and its indexes are rewritten under ACCESS EXCLUSIVE (1.47 s, worst stall 1461 ms). Proof: the table's filenode changed. The same rewrite happens for stored generated columns, identity columns and most type changes unless the types are binary coercible. A rewrite can need twice the table's disk space, which fails on a nearly full disk.

## NOT NULL in three steps

`SET NOT NULL` scans the table under ACCESS EXCLUSIVE. Instead:

1. `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID`: applies to new writes, skips the scan.
2. `VALIDATE CONSTRAINT`: scans under a lock that leaves reads and writes alone.
3. `SET NOT NULL`: skips the scan because a valid constraint already proves it; then drop the check.

Naive: 0.16 s, worst stall 157 ms. Safe: the scan took 0.09 s with worst stall 1 ms, and the other two steps 1 ms. Newer Postgres versions accept `NOT VALID` on NOT NULL directly. Foreign keys split the same way: `ADD ... NOT VALID`, then `VALIDATE` later.

## Indexes

A plain `CREATE INDEX` blocks writes for the whole build (0.32 s, worst stall 314 ms). `CREATE INDEX CONCURRENTLY` does two table scans and waits for existing transactions, so it is slower (0.52 s) but cost writers 3 ms. Conditions: it cannot run in a transaction; only one concurrent build per table; partitioned tables need it per partition. A failure (a unique build over duplicate rows) leaves an index marked `INVALID`: it serves no queries yet is maintained on every write. Query `indisvalid` after any failure, then drop and retry or `REINDEX INDEX CONCURRENTLY`.

## Other levers

Other DDL on large tables should be checked the same way (which lock, does it rewrite). MySQL's alternative to in-place change copies rows to a ghost table, follows the binlog and delays cut-over; that was read, not run.

## See Also
- [[Lock Queue and lock_timeout for Live DDL]] — prerequisite-for
- [[Expand, Migrate, Contract]] — related
- [[SQL Indexes and Query Plans]] — related
