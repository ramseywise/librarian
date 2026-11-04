---
title: "Restore Drill with an Invariant"
tags: [foundations, pattern]
summary: "Only a restore proves a backup: schedule the restore on separate hardware, check a data invariant rather than an exit code, record the time taken, and alert on missing success; a replica is not a backup."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--05-operating-data-stores.md
---

# Restore Drill with an Invariant

A published postmortem of a wiped primary shows nearly every backup layer failing at once: a dump job that failed on every run because of a client and server version mismatch, whose failure emails were rejected by the receiver; snapshots enabled for other servers, not the database; a replica already wiped for a re-sync. The general point: nobody wants backups, they want restores. Replication and redundancy are not recoverability: a bad `DELETE` reached a standby in 34 ms (see [[Replication Lag, Failover and Read Anomalies]]).

## The drill

Make the restore the scheduled job, and let its success be the alert. `pg_dump` takes a consistent snapshot without blocking normal reads and writes. In the bench, transfers moved money between accounts while the dump ran (0.32 s, 2.3 MB). Each account starts at 1,000 and each transfer balances, so after restore the sum must be 1,000,000,000: that shows one consistent moment despite the writes.

| Candidate | Result |
|---|---|
| Real dump | ok in 0.40 s, invariant = 1,000,000,000 |
| Empty file from a job that wrote nothing | FAILED: input file is too short |

An exit code of zero or an existing file proves neither. Add three things: run it on a schedule on other hardware, record how long it took (that is your measured recovery time, not an estimate), and fire the alert on **missing success**, so a job that stops running looks like a failure.

## Backup kinds

| Method | Can do | Cannot do |
|---|---|---|
| SQL dump | Move between major versions; restore one table | Anything after the dump; dump alone omits roles and tablespaces |
| File system backup | Copy a whole cluster | Cross major versions; restore one table; needs server stopped or an atomic snapshot |
| Base backup plus archived WAL | Restore to any moment ([[Point-in-Time Recovery from Base Backup and WAL]]) | Cross major versions |

Restoring one table with `pg_restore -t` restored 1,000,000 rows with the primary key not kept, so recreate indexes and constraints or restore to a scratch database and copy rows.

## Defence in depth

Soft deletion first, since application bugs cause most data loss; regular validation third, because low-grade corruption can go unnoticed for weeks. Retention must reach back before the problem started, since the hardest recoveries were those discovered long after they began. Alerts must not depend on something that can silently fail, and destructive runbook steps need the host made obvious and a second reader.

## See Also
- [[Point-in-Time Recovery from Base Backup and WAL]] — extends
- [[Restore Drill: Rebuild-from-Migrations Visibility Probe]] — related
- [[Replication Lag, Failover and Read Anomalies]] — related
