---
title: Backend Scaling Fundamentals
tags: [infra, reference]
summary: The generic backend substrate every LLM system design assumes — single server first, then load balancing, stateless app servers, caching with TTL vs invalidation and stampede mitigation, replication (≠ backup), sharding with consistent hashing — reasoned as an iterative loop where every scaling fix introduces the next problem.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--01-distributed-systems.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--01-distributed-systems.md
---

# Backend Scaling Fundamentals

The component vocabulary underneath the LLM-flavoured design round. Source is a cleaned
video-transcript walkthrough (medium confidence) using a photo-sharing app as the running
example; the claims are standard backend knowledge.

## The core loop

> Every scaling solution introduces a new problem.

1. Gather requirements. 2. Sketch the simplest architecture. 3. Find the first bottleneck.
4. Add the smallest component that solves it. 5. Name the trade-off that component introduces.
6. Repeat. Throughout, application logic never changes — **scaling changes where work happens,
not what the work is.**

Start with **one server** (app + database + files). It is the correct starting point for most
new systems, not a straw man.

## Five questions before designing

Users now and later · read-heavy or write-heavy · what data can never be lost (uploads) vs what
can be stale (like counts) · latency per operation (feed <200 ms, upload 2–3 s) · budget.
Non-functional requirements matter more to interviewers than features.

## Components, each with the problem it creates

| Failure | Fix | New problem |
|---|---|---|
| CPU/RAM exhausted | more app servers | which server gets the request → **load balancer** |
| Hot reads on the DB | **cache** | staleness |
| Single machine dies | replication + external object storage | replication lag |
| Storage exceeds one DB | **sharding** | hot shards, resharding |

- **Load balancer** — reverse proxy doing distribution, health checks, dead-server removal;
  round robin, least connections, weighted.
- **Stateless servers** — sessions in app memory log users out when the next request lands on
  another server. Move sessions to shared storage (typically Redis). Sticky sessions work but
  balance poorly and lose sessions on failure. Golden rule: keep app servers stateless.
- **Vertical before horizontal** — a bigger box is simple but capped and still a single point
  of failure; horizontal needs a balancer, shared state, distributed data.
- **Monolith before microservices** — microservices buy independent scaling and deploys at the
  cost of network failures, debugging complexity, operations. Split only when justified.

## Data

- **Access patterns define the schema.** Don't start with "which database?"; start with "what
  questions must the system answer?"
- **SQL** for structured, relational, transactional data; **NoSQL** for flexible schema,
  document/event data, extreme scale. Real systems use both.
- **Indexes** speed reads and slow writes — measure, then index.
- **Caching:** TTL (simple, eventually consistent) vs active invalidation on write (more work,
  always fresh). **Cache stampede** — many entries expiring together — is mitigated with
  randomised TTLs, request coalescing, background refresh.
- **Replication:** writes to primary, reads from replicas; replicas lag, so read-your-own-writes
  goes to the primary. Failover promotes a replica. **Replication is not backup** — it copies
  mistakes too.
- **Sharding** solves storage scale (replication solves read scale). Pick the shard key
  (usually user id) to avoid hot shards; modulo partitioning moves almost everything on reshard,
  **consistent hashing** moves only a small slice.

## See Also
- [[API Design Fundamentals]] — complements (the interface layer on the same substrate)
- [[System Design Interview Study Guide]] — prerequisite-for (the method that operates on this vocabulary)
- [[LLM System Bottleneck Table]] — extends (the LLM-specific bottlenecks on top)
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — extends
