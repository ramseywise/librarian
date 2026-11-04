---
title: "Replication Lag, Failover and Read Anomalies"
tags: [foundations, concept]
summary: "Leader-based replication, why logical row logs power change data capture, how asynchronous replication loses acknowledged writes and reuses IDs on failover, and the read anomalies lag produces on replica-fed dashboards."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--05-partitioning-and-replication.md
---

# Replication Lag, Failover and Read Anomalies

Replication keeps the same data on several machines for availability, latency, read scale and disconnected use. In **leader-based replication** (PostgreSQL, MySQL, MongoDB, Kafka) writes go to the leader, which ships a log of changes that followers apply in order.

## What the log contains
Replaying a statement diverged at once because `random()` differs per machine (`NOW()` and autoincrement likewise); shipping the resulting rows matched. Options: statement-based, write-ahead log shipping (exact but tied to one storage version) and logical row-based logs (decoupled from the engine and easy for other programs to parse), which is what **change data capture** reads to feed warehouses. Adding a follower follows one recipe: take a consistent snapshot, note its exact log position, copy it, replay the log from there; CDC and `CREATE INDEX` start the same way.

## Sync, async, and what failover loses
A synchronous follower is current but a stalled one blocks writes; semi-synchronous makes one follower synchronous and the rest asynchronous. In an asynchronous model with a client acknowledged before replication: the acknowledged fourth receipt was lost when a follower that had applied only 3 was promoted, a lagging follower served stale data without error, and the new leader's counter reused ID 4. If a cache or warehouse stored the first ID 4, rows collide. A real incident had the same shape, with a stale follower promoted and reused autoincrement keys. Further failover hazards: split brain (two nodes both believe they lead) and choosing a timeout (30 seconds is one example) that neither fires needlessly nor leaves a long outage. Making one follower synchronous means failover loses nothing, at the price of waiting for it on every write.

## Anomalies from lag
Lag is usually under a second but can reach minutes. The anomalies match what replica-fed dashboards show:
- **Read-your-writes** fails when a user reads a stale replica after saving. Fixes: read possibly-changed data from the leader, read everything from the leader for a short period after an update, or have the client remember its last write's log position and read only from a replica past it.
- **Monotonic reads** fails when successive reads hit replicas with different lag (nine comments, then seven). Pin each user to one replica by hash of user ID.
- **Consistent prefix** fails when causally related writes on different partitions arrive out of order, common when two warehouse tables load at different times.

Measure lag as leader log position minus follower position and alert on it. Multi-leader setups (multiple data centres, offline clients) permit write conflicts; avoid them without that exact need. Conflicts hide: two room bookings on different leaders each pass the availability check, the shape of write skew (see [[Transaction Isolation Levels and Anomalies]]).

## In a pipeline

| What you see | Mechanism | What to do |
|---|---|---|
| Counts drop briefly after a load | Replica lag, monotonic reads | Read one replica or the primary for load checks |
| Extract misses recent rows | Replication lag | Extract to a watermark below the lag, not to now |
| Duplicate IDs after failover | Lost writes, reused keys | Key on source, timestamp and log position |
| Fact row without dimension row | Consistent prefix | Load in dependency order, test orphans |
| A value reverts after a write you saw succeed | Last write wins | Immutable keys, or keep siblings |

Do not treat asynchronous replication as durable; know each source's mode before claiming exactly-once.

## See Also
- [[Quorums, Version Vectors and Last-Write-Wins]] — related
- [[Partitioning Strategies and Hot Spots]] — related
- [[Unreliable Networks, Clocks and Process Pauses]] — extends (why failure detection is never reliable)
- [[Idempotent Retries and Request IDs]] — related
