---
title: "Atomic Commit and Why Two-Phase Commit Blocks"
tags: [foundations, concept]
summary: "Two-phase commit gets all-or-nothing across nodes with a coordinator, but a participant that voted yes is stuck holding locks if the coordinator dies; it is acceptable inside one system and a poor fit across heterogeneous ones."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--07-consistency-and-consensus.md
---

# Atomic Commit and Why Two-Phase Commit Blocks

A transaction touching several nodes must commit on all or none. On one node, atomic commit comes down to one moment, the disk finishing a commit record. Across nodes you cannot simply send commit to each: some may fail while others succeed, and a committed transaction cannot be taken back because others may have read its data.

## Two-phase commit (2PC)
Unrelated to two-phase locking. A **coordinator** sends *prepare*; each participant votes. A yes vote is a promise: it can commit even after a crash, and it gives up its right to abort. The coordinator writes its decision to its own log (the commit point, itself an ordinary single-node atomic commit) and delivers it, retrying until delivered.

**The gap:** a participant that voted yes can neither commit nor abort alone. It is **in doubt** until it hears the decision.

| Scenario | Outcome |
|---|---|
| All vote yes | all committed |
| One votes no | all aborted |
| Coordinator dies before deciding | all prepared, all holding locks |
| Coordinator dies mid-commit | one committed; the others prepared and still holding locks |

In the last two the participants cannot safely ask each other: the coordinator may have decided either way (an abort after a timeout, or a commit already delivered to a participant now cut off), so any choice might contradict it.

## A real database shows the same behaviour
PostgreSQL exposes the participant side as `PREPARE TRANSACTION`. After a client prepared an update and disconnected, the transaction stayed listed in `pg_prepared_xacts`, other writers to that row hit a lock timeout, and it survived a database restart, because durability is the promise it made. Only `COMMIT PREPARED` or `ROLLBACK PREPARED` resolves it. This is why the feature is off by default (`max_prepared_transactions` is 0), and why a stuck prepared transaction should be monitored, not treated as harmless.

## Cost at scale
Locks can be held as long as the coordinator is down (20 minutes or more); orphaned transactions can need an administrator; XA, the standard API, is a lowest common denominator; and the coordinator becomes a database in its own right, a single point of failure inside what looked like a stateless application server. Distributed transactions in one MySQL setup were reported over 10 times slower than single-node ones.

**Internal vs heterogeneous:** distributed transactions where all participants run the same software can be efficient; those across different technologies are the problem. So a stream processor's exactly-once guarantee is usually internal, and Kafka transactions hold only inside Kafka. Across systems, prefer a log plus idempotent consumers, as change data capture gives, to a distributed commit ([[Idempotent Retries and Request IDs]]).

## How consensus improves on it
2PC needs every participant and blocks if its coordinator dies; a consensus algorithm accepts a majority and can terminate ([[Consensus and Coordination Services]]).

## See Also
- [[Consensus and Coordination Services]] — alternative-to
- [[Transaction Isolation Levels and Anomalies]] — prerequisite-for
- [[Idempotent Retries and Request IDs]] — related
- [[Lamport Timestamps and Total Order Broadcast]] — related
