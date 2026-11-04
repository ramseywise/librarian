---
title: "Replication, Backups and the Durability Ladder Above the Disk"
tags: [foundations, decision]
summary: "A replica survives the machine but copies your mistakes in milliseconds; async replication loses the lag at failover, sync replication stalls commits when the standby stalls, and only a restored backup with archived WAL survives a bad deploy."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--09-persistence.md
---

# Replication, Backups and the Durability Ladder Above the Disk

Disks, replicas and backups each fail differently and should be used together: no single technique is absolute, faults correlate, SSDs can violate their guarantees on power loss, and 30 to 80% of SSDs develop at least one bad block in their first four years. Guidance on recovery planning says recovery should not cost more than the loss it prevents, so the decision is set by the cost of being wrong: a clickstream on async commit can be right, a payments ledger on the same setting is a serious mistake. Mechanics of the log below are in [[Write-Ahead Logs, fsync and the Durability Ladder]]; lag and anomalies are in [[Replication Lag, Failover and Read Anomalies]].

## Async vs sync failover
Real Postgres standbys, primary killed under load, standby promoted, acknowledged writes counted (one run per row, so a demonstration, not a rate):

| Replication | Acknowledged | During a 1 s standby stall | Lost after failover |
|---|---|---|---|
| asynchronous | 7,315 | 0 | 0 |
| asynchronous, standby stalled 1 s | 21,878 | 15,432 | 15,620 |
| synchronous | 4,059 | 0 | 0 |
| synchronous, standby stalled 1 s | 3,915 | 0 | 0 |

Async lost nothing on a healthy network, which makes it dangerous: most days it looks free. Once the standby stalled, the primary kept acknowledging, and the loss is proportional to replication delay at failover. Sync lost nothing, but during the stall the primary acknowledged nothing, because each commit waits for the standby: a replica problem became a primary outage. **RPO zero costs availability**; with one standby and no plan, a stalled standby stalls every commit. Promotion itself took about 0.1 s, which is not the RTO: failure detection and the decision to fail over usually dominate ([[Unreliable Networks, Clocks and Process Pauses]]).

## A replica is not a backup
A bad `DELETE` on the primary emptied the standby in about 34 ms. Replicas cover hardware; backups cover people. The copy that does is a base backup plus archived WAL, allowing point-in-time recovery to just before the mistake ([[Point-in-Time Recovery from Base Backup and WAL]]). RPO becomes the age of the newest archived WAL (only completed segments are archived, so `archive_timeout` caps it on a quiet server); RTO becomes restore time plus replay time, which is only known by doing it. A backup never restored is a hope, not a rung.

**Object stores.** A durability figure of eleven nines describes the provider losing an object, not you overwriting or deleting one; versioning and object lock cover that. It will preserve your bad `DELETE` perfectly.

## The ladder as a table
| Rung | Survives | Does not survive | RPO | RTO |
|---|---|---|---|---|
| Process memory | nothing | process crash | all unflushed (up to 512 records per crash in the test) | none needed |
| Page cache | process crash | OS crash, power cut | since last OS writeback (about 30 s on Linux per one store's docs) | reboot |
| `fsync` to device | power cut, if the device honours flushes | disk failure, lying drive | 0 if honest | restart |
| WAL, commit async | server crash, without corruption | last few hundred ms of commits | bounded at 3 x `wal_writer_delay` | 0.1 s to replay |
| WAL, commit sync | server crash | disk failure | 0 | grows with WAL (6 s for 2.1 GB) |
| Async replica | machine loss | your mistakes; loses the lag | replication lag | detection plus promotion |
| Sync replica | machine loss, no acknowledged loss | your mistakes; stalls if standby does | 0 | as above, plus outage during a stall |
| Object store with versioning | zone loss, overwrites, deletes | account compromise without object lock | upload interval | re-download |
| Tested backup with WAL archive | your own bad deploy | whatever you never restored | newest archived WAL | restore plus replay |

## Pitfalls
- Calling a replica a backup.
- Reading eleven nines as data safety.
- Sync replication with one standby and no plan for who is paged.

## See Also
- [[Cache vs Source of Truth: Write-Through and Write-Behind]] — related
- [[Replica Lag and Replication Slots Retain WAL]] — related
- [[Idempotent Retries and Request IDs]] — related (replaying after a crash must be harmless)
