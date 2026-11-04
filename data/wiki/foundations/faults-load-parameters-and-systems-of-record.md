---
title: "Faults, Load Parameters and Systems of Record"
tags: [foundations, concept]
summary: "Design vocabulary for data systems: faults versus failures, why correlated software and human faults beat redundancy, choosing load parameters from the distribution not the mean, and separating systems of record from rebuildable derived data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--01-data-systems-and-data-models.md
---

# Faults, Load Parameters and Systems of Record

Applications that combine a database, a cache, a search index, a queue and a warehouse are data systems whatever the plan was. The API over them is a promise about behaviour (the cache is invalidated when a value changes; a search result never points at a deleted row), and the designer owns those promises. Three concerns organise the design: **reliability** (keeps working when things go wrong), **scalability** (a reasonable way to cope as load grows) and **maintainability** (many people can keep working on it over years).

## System of record vs derived data

A **system of record** holds the authoritative version of a fact. Everything else (cache, index, warehouse table) is **derived data**, which can be thrown away and rebuilt from the source. For any table ask which it is: a bad day on derived data means a rerun, on a system of record it means data loss. A table called derived whose source has expired has quietly become a system of record.

## Faults are not failures

A **fault** is one component deviating from spec; a **failure** is the whole system no longer serving users. Faults cannot be driven to zero, so the goal is to stop them becoming failures, including by injecting faults on purpose.

- **Hardware faults** are countable. With 10,000 disks and a mean time to failure of 10, 30 or 50 years, expect 2.74, 0.91 or 0.55 failed disks per day. At cluster scale a disk failure is routine.
- **Software faults** are correlated: the same bug on the same input on every node at once. Redundancy and retries do nothing. Process isolation, crash-and-restart and self-checks (a queue asserting messages in equals messages out) help.
- **Human faults** are the largest category: in one study of large services, operator configuration errors led outage causes and hardware accounted for only 10-25%. Defences are a sandbox, fast rollback and tools to recompute data, which is the mission statement of an idempotent pipeline.

## Describe load before asking if it scales

"Does it scale?" has no answer until you pick **load parameters**. In a social-timeline example, 4.6k posts per second on average and 12k at peak sit against 300k timeline reads per second. The hard part is fan-out: precomputing a timeline per follower at an average of 75 followers turns 4.6k posts into 345k writes per second, and an account with 30 million followers means 30 million writes for one post. Simulating a heavy-tailed follower distribution over a million users gave a mean of 53 but a median of 7; a few hundred accounts of a million (those at or above 10,000 followers) generated about 30% of the write load. The answer is a hybrid: fan out for most accounts, fetch the very large ones at read time. The distribution, not the mean, is the load parameter; with a thinner tail (Pareto shape 2.0) the mean drops to about 8 and the hybrid changes nothing.

The same shape appears as a hot partition and as a skewed shuffle. Scaling up (a bigger machine) and scaling out (shared-nothing across smaller ones) are mixed in practice, and a single large machine is often the simpler, cheaper answer. Stateless services scale out easily; stateful ones are hard. No generic scalable architecture exists: 100k requests per second at 1 kB each and 3 requests per minute at 2 GB each have the same data throughput and look nothing alike.

## See Also
- [[Latency Percentiles, Tail Amplification and Coordinated Omission]] — extends
- [[Partitioning Strategies and Hot Spots]] — related (hot partitions are the same skew)
- [[Relational, Document and Graph Models and Schema on Read]] — related
- [[Data Systems Foundations Reading Map]] — related
