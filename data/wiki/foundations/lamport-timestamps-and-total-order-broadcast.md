---
title: "Lamport Timestamps and Total Order Broadcast"
tags: [foundations, concept]
summary: "A counter-plus-node-ID gives a total order consistent with causality but only after the fact; total order broadcast, in practice a replicated log, fixes the order at delivery and so can implement uniqueness checks and compare-and-set."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--07-consistency-and-consensus.md
---

# Lamport Timestamps and Total Order Broadcast

## Lamport timestamps
Without a leader to hand out sequence numbers, a node keeps a counter and stamps events `(counter, node ID)`. The rule: on receiving a message, set your counter to the larger of yours and the sender's, then add one. Sorting by `(counter, node)` puts every effect after its cause with no wall clock, avoiding the inversions in [[Unreliable Networks, Clocks and Process Pauses]]. Unrelated events land in an arbitrary but consistent place, which is fine since nothing depended on them.

**Limit: the order exists only after the fact.** Two nodes can each accept a claim on the same username at once, both stamping `(1, node)`; a winner emerges only after they exchange stamps, so the loser's success was premature. To reject a duplicate at request time a node must know no other node is concurrently claiming it, and it can settle only after hearing from everyone, which never happens if any node is down. To decide now, the order must be final when you act.

## Total order broadcast
Requires reliable delivery (if one node gets a message all do) and totally ordered delivery (same order everywhere), with the order fixed at delivery. That is a **log**, and it is what a replication log and state machine replication use: apply the same sequence in order on every replica and they end in the same state.

It can implement things that look unrelated. A uniqueness check or linearizable compare-and-set needs only a log: append a tentative claim, read the log up to your own message, and you hold the key if yours came first. Every replica replaying the log reaches the same answer with no further coordination. A linearizable compare-and-set and total order broadcast can implement each other, and both are equivalent to consensus ([[Consensus and Coordination Services]]).

**Where it appears in a data stack:**
- A Kafka partition is a totally ordered log, so replaying gives the same answer (what makes reprocessing possible); order is total per partition, not across a topic.
- A table format's commit log is the same for a table: each metadata change replaces the version it was based on through an atomic operation, producing a linear history of table versions, and compare-and-set forms that order.
- Change data capture reads a database's replication log, whose order is already consistent with causality, so applying it in order to a warehouse is sound.

## See Also
- [[Linearizability, Ordering and Quorum Reads]] — prerequisite-for
- [[Consensus and Coordination Services]] — related
- [[Quorums, Version Vectors and Last-Write-Wins]] — alternative-to (version vectors track causality in full at higher cost)
