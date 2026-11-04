---
title: "Data Systems Foundations Reading Map"
tags: [foundations, reference]
summary: "Map and rules of thumb for the storage-and-compute layer under data engineering: what a system promises, encoding and layout, concurrent writers, partitioning and replication, failure, consensus, distributed compute, durability and choosing a store."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--README.md
---

# Data Systems Foundations Reading Map

Almost every debate in the field reduces to one of these mechanisms: a slow query comes down to layout and pruning, a count that dropped to replication lag, a wrong balance to isolation, "is exactly-once real?" to what a timeout can tell you, "do we need Spark?" to how much one query actually reads. The layer starts with one machine and adds trouble a step at a time.

## Reading order
1. What you promise and how to measure it: [[Latency Percentiles, Tail Amplification and Coordinated Omission]], [[Faults, Load Parameters and Systems of Record]], [[Relational, Document and Graph Models and Schema on Read]].
2. What a file promises its reader: [[Encoding Compatibility and Schema Evolution]], [[Parquet Row Groups, Pruning and Sort Order]].
3. Layout for OLTP and OLAP: [[Row Stores vs Column Stores]], [[B-Trees vs LSM-Trees]].
4. When two writers meet: [[Transaction Isolation Levels and Anomalies]], [[MVCC Row Versions and Snapshots]], [[Three Ways to Be Serializable]].
5. Where rows live and what a reader sees: [[Partitioning Strategies and Hot Spots]], [[Data Lake Partitioning and the Small Files Problem]], [[Replication Lag, Failover and Read Anomalies]], [[Quorums, Version Vectors and Last-Write-Wins]].
6. What a node can know: [[Unreliable Networks, Clocks and Process Pauses]], [[Fencing Tokens and Zombie Writers]], [[Idempotent Retries and Request IDs]].
7. How machines agree: [[Linearizability, Ordering and Quorum Reads]], [[Lamport Timestamps and Total Order Broadcast]], [[Atomic Commit and Why Two-Phase Commit Blocks]], [[Consensus and Coordination Services]].
8. Computing across a cluster: [[MapReduce, the Shuffle and Spark Lineage]], [[Shuffle Skew and Salting]], [[Distributed Compute Cost and the Single-Machine Threshold]].
9. What "saved" means: [[Write-Ahead Logs, fsync and the Durability Ladder]], [[Replication, Backups and the Durability Ladder Above the Disk]], [[Cache vs Source of Truth: Write-Through and Write-Behind]].
10. Choosing a store: [[Choosing a Store from the Access Pattern]], [[How Far Plain Postgres Stretches]].

## Rules of thumb
| Situation | Rule | Why |
|---|---|---|
| Stating a performance goal | percentiles measured from the client, merge histograms | means hide the tail; percentiles cannot be averaged |
| A CSV arrives | state the schema on first read | inference destroys zip codes and big IDs silently |
| Data at rest | Parquet, sorted by the main filter column | pruning and pushdown need physical order |
| Data between engines | Arrow | exchange without copying |
| Records in a stream | Avro or Protobuf, with a registry | evolution is checked, not hoped for |
| Slow warehouse query | read the plan before adding anything | most of the fix is pruning and join strategy |
| Read, decide, then write | serializable isolation or lock explicitly, retry aborts | snapshot isolation allows write skew |
| A retry that has effects | reuse one request ID from the client to the store | a timeout does not say whether the write applied |
| Ordering events across machines | no wall clocks; fence stale lock holders | skew loses writes, and pauses outlive leases |
| Reading from a replica | assume it is behind | async replication lags and can lose writes |
| A quorum store | do not assume `w + r > n` is linearizable | reads can still go backwards |
| Needing agreement | a coordination service or a database, not your own protocol | consensus is easy to get wrong in ways tests rarely show |
| Choosing a lake layout | partition by what you backfill, sort by what you filter | fine partitions create small files |
| Considering a cluster | measure what one query reads after pruning | one machine often suffices |

## See Also
- [[SQL Indexes and Query Plans]] — related
- [[SQL Schema Design and DDL]] — related
