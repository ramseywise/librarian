---
title: "Replica Lag and Replication Slots Retain WAL"
tags: [foundations, concept]
summary: "Reads from a standby are stale even on an idle pair, long standby queries get cancelled by replay conflicts, an unread replication slot holds WAL until the disk fills, and capacity forecasts must include operations that need a table's size again."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--05-operating-data-stores.md
---

# Replica Lag and Replication Slots Retain WAL

Reading from a standby is the first scaling step for many teams, and its cost is stale reads. Theory is in [[Replication Lag, Failover and Read Anomalies]]; these are measurements on a real primary and standby.

## Staleness

Even on an idle pair on one machine, a read straight after a write was stale 194 times in 200: the lag was tiny but the read was faster. During bulk writes 199 of 200 were stale, peak replay gap 17.2 MB, replay_lag 0.137 s. Never route a read-your-own-write through a replica without a check. Alert on `pg_stat_replication` (byte gap from LSNs, and the lag times), whichever matches what you promise readers, and use it as the brake on backfills ([[Batched Rerunnable Data Backfills]]).

## Replay conflicts

On a hot standby, applying WAL can conflict with a running query (for example vacuum removed rows it can still see). After `max_standby_streaming_delay` the server cancels the query or ends the session, so long reports get a random error. Options all cost: a higher delay means more lag; `hot_standby_feedback` moved the cost to bloat on the primary (200,000 dead rows left, 169 MB) ([[Vacuum, Bloat and Idle Transactions]]); a dedicated reporting replica means hardware.

## WAL and slots

- **WAL is bigger than the data:** updating 1,000,000 rows wrote 278 MB of WAL for a 73 MB table. Backfills fill the WAL disk and the archive and push replicas behind.
- **A slot with nobody reading holds WAL forever.** Three more full updates left 460, 724 and 978 MB held. If the consumer dies, a full disk stops the primary. Alert on retained WAL and consider `max_slot_wal_keep_size`.
- **Plan headroom for operations:** 410 GB used of 1 TB growing 3 GB a day gave 130 days to an 80% alarm; with a 300 GB rewrite planned, 30 days. `VACUUM FULL`, a type change and a concurrent reindex all need that room. The inputs were made up; the gap is the point.

Graph and alert on the trend: disk and days left, WAL per hour, connections against the limit, replication lag, oldest transaction age, dead rows per table, `age(datfrozenxid)`, archiver failures, and time of the last successful restore drill.

## Upgrades

Minor releases only swap binaries. Major ones: dump and restore (longest downtime), `pg_upgrade` (minutes, in place, so back up first), or logical replication (seconds at the switch, most moving parts, rollback while the old side lives). None was run; the procedure is [[Expand, Migrate, Contract]]. Check the version of every tool that talks to the server, the backup job above all.

## See Also
- [[Replication Lag, Failover and Read Anomalies]] — related
- [[Point-in-Time Recovery from Base Backup and WAL]] — related
- [[Connection Pooling Turns Failure into Waiting]] — related
