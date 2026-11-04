---
title: "Event Time, Watermarks and Late Data"
tags: [foundations, concept]
summary: "Windows must be defined on event time, but a stream never says a window is complete; a watermark is a heuristic that fires windows, and allowed lateness trades lost late events against stale results."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--04-kafka-and-stream-semantics.md
---
# Event Time, Watermarks and Late Data

Delivery guarantees say whether a record arrives, not when. Event time is when something happened; processing time is when you heard about it. Windows on arrival time make a restart look like a spike or a quiet period that never occurred in the world, so windows are defined on event time and processing time is kept for operational rates.

## The skew in numbers

Simulation: 600 rides, one per second for ten minutes; delays mostly a few seconds, with 2% of events delayed an extra 120 to 400 s (a tunnel).

- 255 adjacent pairs were out of event-time order on arrival.
- First minute by event time 60, by processing time 53.

## Watermarks

A watermark is a running assertion that the stream has probably delivered everything up to event time T. A window fires when the watermark passes its end. The simplest policy, used by Spark Structured Streaming, sets it to the highest event time seen minus allowed lateness; Flink tracks it as a special progress signal. A stream never tells you a window is complete, so the choice is a per-pipeline trade of correctness, latency and cost.

| Allowed lateness | Dropped late events | Share |
|---|---|---|
| 0 s | 46 | 7.7% |
| 5 s | 22 | 3.7% |
| 30 s | 11 | 1.8% |
| 120 s | 7 | 1.2% |
| 300 s | 1 | 0.2% |
| 600 s | 0 | 0.0% |

A 10-minute wait catches everything but makes every number 10 minutes old. No value is right without the business: a live dashboard tolerates loss for freshness; an invoice does not.

## Late events: drop, count or correct

- **Drop, count and alert.** Without a metric you cannot tell loss from a quiet day.
- **Correct.** Emit early and update: at 30 s lateness with retractions, the total reached 600 of 600 with 11 corrections sent downstream. Corrections help only if downstream applies them; an append-only sink must become an upsert sink keyed on window.

## Windows and timestamps

Window kinds: tumbling (fixed, non-overlapping), hopping (fixed, overlapping), sliding (events within an interval of each other), session (closed by a gap in activity). All inherit the completeness problem, and sessions worsen it: a late event can merge two sessions. Log three timestamps: the event on the device clock, when the device sent it and when the server received it; the difference of the last two estimates clock skew to subtract from the first.

## Pitfalls

- **One idle partition holds a watermark back.** With per-partition watermarks the minimum wins, so one stalled source freezes all windows; most engines let you mark sources idle.
- **A stateful aggregate with no state limit.** Without a watermark, state for old windows grows forever.
- **Windows on arrival time.**

## See Also
- [[Kafka Log, Partitions and Offsets]] — prerequisite-for
- [[Delivery Guarantees and Effectively-Once Processing]] — related
- [[Stream Joins Replay and Lambda Architecture]] — related
