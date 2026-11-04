---
title: "Latency Percentiles, Tail Amplification and Coordinated Omission"
tags: [foundations, concept]
summary: "Response time is a distribution: report percentiles, merge histograms rather than averaging percentiles, expect the tail to compound across backend calls, and measure with an open-loop load generator."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--01-data-systems-and-data-models.md
---

# Latency Percentiles, Tail Amplification and Coordinated Omission

Two measures matter and each belongs to a kind of system. A batch job cares about **throughput** (records per second). An online service cares about **response time** (how long a client waits). A batch job also takes longer than size divided by throughput, because of skew and because it waits for its slowest task.

## The mean describes nobody

The same request takes different times because of a garbage-collection pause, a page fault or a TCP retransmit. In a simulation of a million requests where 1.5% hit something slow, the mean was 55.2 ms, the median 40.3 ms, p99 366.6 ms and p99.9 2184.1 ms; 22.2% of requests were slower than the mean. Report p50, p95 and p99 and say over which window. A tail is worth paying for when the slowest users are the valuable ones, but optimising further out costs more than it returns.

## Percentiles cannot be averaged

Averaging per-server percentiles has no statistical meaning: it weighs a quiet server like a busy one. In a ten-server test where one slow server took 30% of traffic (sticky sessions), the average of the ten p99s was 476.8 ms, the true p99 of all requests 535.9 ms, and the p99 from merged histograms 524.0 ms. The small gap to the exact value is bucket width. Store histograms and add them. A dashboard built from pre-aggregated percentiles in a warehouse ships this bug.

## Tail latency amplification

When one request needs many backend calls the user waits for the slowest. The share of requests that hit a call slower than its p99 is `1 - 0.99^n`: 1.0% at 1 call, 9.6% at 10, 39.5% at 50 and 63.4% at 100. A query that fans out across partitions therefore costs more than the sum of its parts (see [[Partitioning Strategies and Hot Spots]]).

## Coordinated omission

A closed-loop load generator sends the next request only after the last reply, so it stops generating load during a stall and the stall vanishes from its results. In a 100-second test with one 2-second server stall:

| Client | p50 | p99 | max |
|---|---|---|---|
| Open loop (a request every 10 ms regardless) | 5.0 ms | 1505.1 ms | 2005.0 ms |
| Closed loop | 5.0 ms | 5.0 ms | 2005.0 ms |

The closed loop recorded one slow request. Real users would have queued behind the stall and waited while the backlog drained. The mechanism is **head-of-line blocking**: one slow request holds up those behind it. Requests must keep arriving independently of replies.

## See Also
- [[Faults, Load Parameters and Systems of Record]] — related (the load-parameter view of the same system)
- [[Distributed Compute Cost and the Single-Machine Threshold]] — related (skew makes a job wait for its slowest task)
- [[Data Systems Foundations Reading Map]] — related
