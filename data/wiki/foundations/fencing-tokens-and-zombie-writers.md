---
title: "Fencing Tokens and Zombie Writers"
tags: [foundations, pattern]
summary: "A paused or deposed worker still believes it holds a lock; majority quorums settle truth inside a cluster, and a monotonically increasing fencing token checked at the resource stops stale writers, which is how zombie task attempts are neutralised."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--06-when-distributed-systems-fail.md
---

# Fencing Tokens and Zombie Writers

A node cannot trust its own judgement about being leader or lock holder, because a pause can outlive its lease (see [[Unreliable Networks, Clocks and Process Pauses]]). Truth is defined by a **quorum**: a majority decides, so no single node's belief matters.

## Majorities
| Nodes | Majority | Tolerates |
|---|---|---|
| 3 | 2 | 1 |
| 4 | 3 | 1 |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

Two majorities must overlap, so a split cluster cannot make two conflicting decisions; a 2|2 split of four halts rather than guesses. Even sizes add nothing (four tolerates one, like three), which is why coordination services run 3 or 5 nodes.

## The stale lease holder
Worker A takes a lease, pauses 15 s, and wakes after worker B was granted it. With no protection A's late write lands beside B's. **Fencing**: the lock service hands out a token that rises with each grant, and the storage refuses a write whose token is lower than one it has already seen. In the simulation A's token-1 write was rejected after storage saw token 2. The check must live in the **resource**, not the client, since a client verifying itself can pause in the same way. If A's stale write arrives before B's first write it is accepted, correctly: fencing proves only that no newer holder has written.

## Zombies in a pipeline
A task loses its heartbeat, the scheduler starts a second attempt, and the first wakes and finishes. Without fencing its output can overwrite the retry's.
- A batch engine's output committer lets only one attempt of a task win, so speculative or zombie attempts do not land in the final directory.
- Kafka transactions fence an old producer sharing a `transactional.id` with a newer one.
- A table-format commit is safe against a zombie: it succeeds only by compare-and-set on the current version.
- Bare files written to a known path have no commit step and nothing fences anything; a stale overwrite silently wins. Write to a temporary location, then swap, and name the attempt in the path.

## See Also
- [[Atomic Commit and Why Two-Phase Commit Blocks]] — related
- [[Consensus and Coordination Services]] — extends
- [[Idempotent Retries and Request IDs]] — related
