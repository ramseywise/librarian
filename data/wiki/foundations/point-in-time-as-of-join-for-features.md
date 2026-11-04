---
title: "Point-in-Time As-Of Join for Features"
tags: [foundations, pattern]
summary: "A feature row has a window it describes and a moment it became knowable; joining a training row to the latest feature known at its event time, not the same-hour window, keeps the offline metric honest even though it makes it look worse."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--01-feature-stores.md
---

# Point-in-Time As-Of Join for Features

A feature has two times. `window_start` says what the row describes; `feature_ts` says when it could first have been read. An average over 19:00 to 20:00 describes that hour but exists only after 20:00. Confusing the two is the root of nearly every temporal leak, and it is a specific case of [[Tabular ML Leakage Taxonomy]].

## The two joins

- **Naive join:** match each event to the window it falls in. The feature then includes the event's own label and every later event in that window.
- **As-of (point-in-time) join:** for each event take the latest feature row whose `feature_ts` is at or before the event time. DuckDB has this as `ASOF JOIN`; every feature store's training path is a version of it. Stream processing calls it a time-dependent join (join to the version in force at event time).

```sql
SELECT r.*, f.avg_duration_1h
FROM rides r ASOF JOIN zone_hourly f
  ON r.zone = f.zone AND r.pickup_ts >= f.feature_ts
WHERE r.pickup_ts - f.feature_ts <= INTERVAL 3 HOUR
```

The interval limit is a staleness limit (Feast calls it a time to live, TTL).

## What it does to the numbers

Setup: 40,000 synthetic rides over three months, a linear model trained before March and tested from March, where production can only ever see the as-of value.

| Training join | Coefficient on the feature | Offline RMSE | Production RMSE |
|---|---|---|---|
| naive | 0.54 | 2.79 | 5.48 |
| point-in-time | 0.12 | 3.81 | 3.81 |

The leaky model reports the better offline number and is the worse model in production. Its coefficient is about four times larger because in training the column partly contained the label. Point-in-time correctness does not improve the model; it makes the offline number honest, and here it makes it worse. A team that selects models by offline RMSE and has no as-of join will reliably select the leak.

## How it fails

- **Silent row loss.** The as-of query returned 37,457 rows from 40,000 because rides in zones with nothing inside the 3-hour limit get no feature. Feast scans backward from each entity timestamp up to the TTL, and rows with nothing in the window do not join, so a training set can shrink without warning. Count rows before and after, and treat a missing feature as a value the model must handle. DuckDB's `ASOF LEFT JOIN` keeps such a row with nulls.
- **Boundary is inclusive.** With a one-hour TTL, a row whose feature is exactly one hour old still joins; one older disappears.
- **`updated_at` as feature time.** If the source backfills, a corrected row looks as if it had always been known. Keep the time it became available separate from the time it describes.
- **Window label.** A 24-hour window labelled with its start rather than its end is read up to 24 hours too early: the same leak in a longer window.
- **Window that includes the label.** Test by shifting: a feature predictive only without a lag is usually leaking.
- Equality-joining to the previous hour does not leak, but returns nothing when that hour was empty, where the as-of join walks further back.

## See Also
- [[Tabular ML Leakage Taxonomy]] — extends
- [[Train-Serving Skew and the Shared Feature Function]] — related (leakage is wrong information across time; skew is the same input producing different features in two code paths)
- [[Feature Stores: Parts and When You Need One]] — extends
- [[Time-Series Leakage: Shift and Rolling Windows]] — related
- [[Forecast Issue Time and Measured Leakage]] — related
