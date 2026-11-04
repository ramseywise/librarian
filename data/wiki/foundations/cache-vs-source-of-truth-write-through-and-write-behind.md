---
title: "Cache vs Source of Truth: Write-Through and Write-Behind"
tags: [foundations, pattern]
summary: "A system of record holds the authoritative data and derived data can be rebuilt from it; write-behind silently turns a cache into the source of truth for its flush window, and the test is to delete the cache and see what breaks."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--09-persistence.md
---

# Cache vs Source of Truth: Write-Through and Write-Behind

A **system of record** holds the authoritative version; **derived data** can be rebuilt from it, a cache being the classic case (see [[Faults, Load Parameters and Systems of Record]]). Losing derived data costs time; losing the system of record costs the data. Ask of every store: if this were deleted, could I rebuild it, and from what?

## Two write policies
- **Write-through:** write to the database and commit, then invalidate the cache entry. The database has the write before the client hears anything.
- **Write-behind:** acknowledge in the cache and write to the database later, flushing in batches.

With a real SQLite file underneath and an in-process dictionary cache that vanishes on restart, 1000 writes were acknowledged under each policy, flushing every 300 writes under write-behind. After a restart, write-through returned all 1000 and write-behind 900: the 100 acknowledged writes since the last flush were lost. Write-behind's RPO is its flush interval, and it has quietly made the cache the source of truth for that window.

## Same ladder in a cache server's configuration
Redis offers snapshots, which can lose the minutes since the last save, and an append-only file with three settings: `appendfsync always` (very slow, very safe), `everysec` (the default, can lose one second), `no` (leaves it to the OS). A cache needs none of this; a store holding the only copy of carts or sessions needs you to have chosen.

## The test
Delete the cache in staging. If the app rebuilds it and gets slower for a while, it is a cache. If someone has to explain to customers, it was your database all along.

## See Also
- [[Write-Ahead Logs, fsync and the Durability Ladder]] — prerequisite-for
- [[Replication, Backups and the Durability Ladder Above the Disk]] — related
- [[Choosing a Store from the Access Pattern]] — related
