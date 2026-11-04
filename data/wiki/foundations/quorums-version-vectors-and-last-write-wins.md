---
title: "Quorums, Version Vectors and Last-Write-Wins"
tags: [foundations, concept]
summary: "Leaderless replication reads and writes several replicas with w + r > n so sets overlap; concurrent writes are resolved by version vectors that keep siblings, or by last-write-wins that silently drops acknowledged writes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--05-partitioning-and-replication.md
---

# Quorums, Version Vectors and Last-Write-Wins

Dynamo-style stores aimed at an "always writeable" system, where rejecting an update was the worse outcome. A client writes to several replicas in parallel with no leader and reads from several. With `n` replicas, `w` write acknowledgements and `r` reads, if `w + r > n` the sets overlap so at least one reader sees the latest write.

| n | w | r | always overlap | tolerates down (write / read) |
|---|---|---|---|---|
| 3 | 2 | 2 | yes | 1 / 1 |
| 3 | 1 | 1 | no | 2 / 2 |
| 3 | 3 | 1 | yes | 0 / 2 |
| 5 | 3 | 3 | yes | 2 / 2 |
| 5 | 2 | 2 | no | 3 / 3 |

For n=7 the smallest overlapping w = r is 4, tolerating 3 failures. Latency follows the slowest member of each quorum, so r and w are usually below n. Despite its name, DynamoDB uses a single leader per partition; "Dynamo-style" describes Riak, Cassandra and Voldemort.

**A quorum is not linearizable.** Exceptions: sloppy quorums (writes accepted on any reachable node and handed over later, assuring only that data is somewhere), concurrent writes settled by last-write-wins losing data under clock skew, and partial write failures. In a simulation with n=3, w=3, r=2, 22% of histories were not linearizable (see [[Linearizability, Ordering and Quorum Reads]]). Stale replicas catch up through read repair and a background anti-entropy process; without the latter, rarely read data can stay under-replicated.

## Concurrent writes
"Concurrent" has nothing to do with the clock: two operations are concurrent if neither knew about the other. A **version vector** (a counter per client or replica for each key) records what each write had seen, so the store distinguishes an overwrite from a conflict and keeps conflicting values as **siblings** for the application to merge. In a cart example, a write replaced only what its author had read; an unseen write stayed as a sibling until a client read both and merged. Merging by union can resurrect removed items.

**Last write wins** keeps the highest timestamp and discards a write the client was told succeeded, with no error. It is safe only when a key is written once and never changed, such as a UUID per event; an append-only event table has that shape (see [[Unreliable Networks, Clocks and Process Pauses]] for how much skew loses).

## See Also
- [[Replication Lag, Failover and Read Anomalies]] — related
- [[Linearizability, Ordering and Quorum Reads]] — extends
- [[Unreliable Networks, Clocks and Process Pauses]] — related
