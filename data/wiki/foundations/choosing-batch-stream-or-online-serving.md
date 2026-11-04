---
title: "Choosing Batch, Stream or Online Serving"
tags: [foundations, decision]
summary: "Pick the serving shape by when the consumer needs the answer; batch is the default because a failure is a rerun, precompute works only when traffic concentrates on few keys, and online latency is mostly features and framework, not the model."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--03-batch-and-online-serving.md
---

# Choosing Batch, Stream or Online Serving

A model is only as good as the moment and place its answer arrives. One team precomputed hotel-deal predictions in batches; an A/B test showed nothing because the lists covered under 5% of user sessions, and precomputing for everyone else would have blown up storage. The first serving question is when the consumer needs the answer.

| Shape | Latency | Trigger | Output |
|---|---|---|---|
| Web service | milliseconds, synchronous | HTTP request | JSON response |
| Streaming | seconds, asynchronous | event on a stream | event on an output stream |
| Batch | minutes to hours | schedule | table partition |

Batch unless someone is waiting; stream if a backend system can wait seconds; online if a person or synchronous call waits. The simplest thing meeting the need wins, often serving from a warehouse table. Two axes drive the choice (how soon a prediction is used, how many are needed), and a one-size serving platform suits almost nobody.

## Batch: rerun-safe by construction

Failure at 03:00 means rerun at 04:00 while consumers read yesterday's table. Write to a deterministic location and replace it whole (`existing_data_behavior="delete_matching"` on a partitioned Parquet write): scoring March twice left 200,000 rows, not 400,000. Put `model_version` on every row; once actual durations arrive, a join on `ride_id` gives error per model version. Make the scheduled run and the backfill one function with a different date. Row ids must be reproducible (month plus row number); an id from `uuid4()` at read time makes two scorings of one ride unjoinable. A linear model scored about a million rows per second on one laptop, so reading, joining and writing are the bottleneck, not the model.

## Precompute or compute on request

Precomputing into a key-value store works when traffic concentrates. Estimate before building (illustrative extremes, not measurements): with Zipf-distributed requests, 1,000 keys cover 95.1% of 500,000 requests; with uniform traffic over about 15.9 million keys (zone pair, hour, rider segment), 100,000 keys cover 21.5%. Use your request logs for the real cumulative-coverage curve. If inputs include current session data, precomputing is not possible.

## Online: validate and measure

- A model always returns a number. A request schema at the boundary (typed, range-checked fields) turns a client mistake into a 422 instead of a 500 and rejects impossible values (negative distance, zone 9,000) before they reach the model. Return `model_version` in the response.
- Loading by run path straight from object storage removes the runtime dependency on the tracking server.
- Latency, in-process on one laptop (read ratios only): one prediction about 0.08 ms; HTTP stack about 1 ms; one 1,000-row call 0.5 ms, less than seven single-row calls, which is why batching inside a service helps. Feature fetch is usually larger: an indexed key lookup p50 0.003 ms against a file scan 0.978 ms, 286 times slower. Spend a latency budget on paper in order: network, features, model.

## Streaming

A handler reads batched, base64-encoded records, predicts, writes to an output stream keyed by `ride_id` for per-ride ordering. Delivery is at least once, so a retried batch can repeat a prediction: treat `ride_id` as an idempotency key.

## Pitfalls

- Going online by default (needs on-call, a latency budget, a fallback).
- Appending batch output on rerun.
- Precomputing without measuring key coverage.
- Measuring the model and calling it latency.

## See Also
- [[Model Rollout: Shadow, Canary and A/B]] — extends
- [[Feature Stores: Parts and When You Need One]] — related (the online store exists for the lookup cost above)
- [[Model Registry Aliases and the Run Record]] — related
- [[Train-Serving Skew and the Shared Feature Function]] — related
