---
title: System Design Scored Behaviors
tags: [interview, reference]
summary: "The in-room behaviours a system design round actually scores, beyond the diagram: scope aggressively, turn requirements into APIs and numbers, justify every box causally, design from access patterns, evolve from the simplest working system, split services only for different scaling, name your own bottlenecks and forgotten durability, and show depth on one technology rather than adding boxes."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--interview-heuristics.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--interview-heuristics.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--interview-patterns.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--interview-patterns.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--interviewer-personas.md
---

# System Design Scored Behaviors

[[System Design Interview Study Guide]] is the five-step method. This page lists the
behaviours graders reward *inside* those steps. They are interview performance, not
architecture knowledge ([[Durable vs Performative Knowledge Split]]). They were extracted
from two recorded walkthroughs (a messaging app; a staff-level live-auction design), so
treat them as medium-confidence. Choosing *which option* at a component is covered by
[[Situation-Indexed Decision Tree]].

## Framing the problem

- **Scope aggressively, out loud.** "X has many features. To build a solid MVP in interview
  time I'll focus on one-to-one text messaging." Finishing a complete small design beats
  leaving half of a huge one. Interviewers reward the cut.
- **Functional requirements as a flow, then as APIs.** Send → receive → read becomes
  `POST /messages`, `GET /messages`, `POST /messages/read`. For an AI system:
  `POST /chat`, `POST /feedback`, `GET /conversation`. APIs are concrete and gradable.
- **Product metric → infrastructure metric.** 10B messages/day → ~100k rps average → ~500k
  peak → server count → storage. Precision doesn't matter. Letting the numbers drive the
  architecture does.
- **State the non-functionals as a list** (availability, latency, consistency, scalability,
  durability, fault tolerance, security), then tie each component back to one:
  consistency → ACID transaction, latency → SSE, durability → stream retention.

## Building the design

- **Every component gets a causal chain.** Don't say "we need a load balancer". Say
  "traffic grows → horizontal scaling → multiple API servers → load balancer".
- **Problem → options → trade-offs → choice → why it wins.** For example: "Updates flow only
  server→client. Polling wastes load, WebSockets are bidirectional, so SSE." The
  decision process is graded more than the final architecture.
- **Data model before algorithms, and access patterns before tables.** Ask "what queries
  must be fast?" first. "Unread must be O(1)" means a separate unread index. Letting
  architecture follow the queries is named as the biggest junior/senior difference.
- **Model entities as state machines** (undelivered → delivered → read). This fits orders,
  payments, AI jobs and agent workflows alike.
- **Start with API → service → DB, then evolve.** Each optimization answers a named problem:
  cron job → need lower latency → delayed queue message → need dynamic deadlines → workflow
  engine. Don't open with Kafka/Redis/Cassandra.
- **Abstractions before vendors.** Say "notification service" and "blob storage" first, and
  drill into a vendor only when asked.
- **Separate the read and write paths** even without CQRS. Write: validate → persist →
  publish event. Read: streaming service → pub/sub → SSE.
- **Split services only when their scaling profiles differ.** Thousands of held-open SSE
  connections justify a separate streaming service. "Microservices" does not.
- **Prefer managed services** ("engineers are expensive, can migrate later"). This is a
  maturity signal.
- **Move slow work to background workers**: persist → queue → worker → update state →
  notify. For AI: request → queue → LLM → eval → store → notify.

## The questions you will get

- **Duplicated state draws "how do you keep these consistent?"** Have answers ready:
  transaction, optimistic locking / compare-and-swap, serializable isolation, single writer.
- **Know when caching doesn't help.** "Bids change continuously, so a cache buys nothing"
  scores well. Cache only for many reads, few writes, and repeated access.
- **Spot scheduled work** (reminders, expiries, auction end, payment retries) and reach for
  delayed queues, schedulers or workflow engines.
- **Durability is the non-functional people most often forget.** "What if the server crashes
  after accepting the bid?" Without a durable stream between API and workers, the bid is lost.

## Closing and depth

- **Find your own bottleneck before the interviewer does**: current design → future scale →
  where it breaks → mitigation.
- **Admit hand-waving** ("I'm glossing over locking here"). It beats bluffing.
- **Keep it simple, then end with improvements**: caching, replication, partitioning,
  observability, failure recovery. Add operational metrics (p95/p99, error rate, queue
  depth, replication lag) alongside business ones.
- **Depth over boxes.** Senior and staff diagrams barely differ. Staff candidates explain
  *why* components behave as they do: Redis single-threading and Lua atomicity, Kafka
  partitions and ordering, Postgres MVCC and isolation levels. Reasonable confidence is
  enough ("this broker supports scheduled delivery, so I'd pick one with that capability").
  Perfect product recall isn't needed.

Staff-level order: clarify → estimate → simple architecture → walk request flows →
bottlenecks → optimize each → non-functionals → follow-ups → technology deep dives.

## See Also
- [[System Design Interview Study Guide]] — extends (behaviours inside the five steps)
- [[Situation-Indexed Decision Tree]] — prerequisite-for (which option to pick at each node)
- [[LLM System Bottleneck Table]] — prerequisite-for (the "find your own bottleneck" inventory)
- [[Durable vs Performative Knowledge Split]] — instance-of
- [[Technical Breadth Round Playbook]] — alternative-to (the verbal breadth round vs the design round)
- [[AI System Design Interviewer Rubric]] — extends (the same behaviours as rubric dimensions, plus the five phrases that always draw a probe)
