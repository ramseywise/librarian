---
title: "Point-in-Time Recovery from Base Backup and WAL"
tags: [foundations, pattern]
summary: "A base backup plus every archived WAL segment recovers a database to a chosen moment just before a bad delete, on a new timeline, which a nightly dump and a replica cannot do."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--05-operating-data-stores.md
---

# Point-in-Time Recovery from Base Backup and WAL

A nightly dump loses a day of data, and a replica replays a mistake. With a base backup and archived write-ahead log you recover to a moment of your choice.

## Drill (Postgres 16.2)

5,000 orders arrive after the base backup (106 MB); a bad `DELETE` leaves 1000. Copy the base backup, add a `recovery.signal` file, and configure a `restore_command` that copies segments from the archive, a `recovery_target_time` just before the delete, and promote on completion. Result: 13 WAL segments archived; restore took 0.17 s and orders = 5000; the log shows recovery stopping before the commit of the bad transaction. The nightly dump, taken before those orders existed, has none of them.

## Details

- Without a target, recovery replays all WAL and faithfully replays the mistake (1,000 orders came back), so the target is what makes it point-in-time.
- The recovered server starts a **new timeline**, so its WAL cannot be confused with the original's. The original remains, so good rows can be copied out and what was written after the mistake kept; that manual merge is usually the hard part.
- Recovering on a different server leaves the damaged one for investigation.
- `archive_command` must return zero only on success and refuse to overwrite an existing file; a broken one is silent until a restore needs it, so watch `pg_stat_archiver`.
- Recovery time grows with the WAL to replay, so frequent base backups shorten it.

Run it as a drill ([[Restore Drill with an Invariant]]).

## See Also
- [[Restore Drill with an Invariant]] — prerequisite-for
- [[Replica Lag and Replication Slots Retain WAL]] — related
