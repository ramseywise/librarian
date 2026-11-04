---
title: "Warehouse Cost Meters: Bytes, Slots and Egress"
tags: [foundations, comparison]
summary: "A warehouse bill is bytes scanned or slot-hours for compute, a small storage line and route-dependent egress; compute the on-demand versus capacity break-even before choosing, using list prices that carry a read date."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--05-cost.md
---
# Warehouse Cost Meters: Bytes, Slots and Egress

Platform bills are sensitive to small decisions because the same query runs thousands of times. Three meters matter: bytes scanned, compute slots and data leaving a region. Figures below are one cloud warehouse's and cloud's US list prices as read on 2026-11-01; prices are regional and go stale, the reasoning shape does not. Storage is cheap and stable; compute grows with how often people ask.

## Bytes scanned (on-demand)

On-demand charges per byte processed: $6.25 per TiB in US regions with the first TiB each month free. Columnar storage reads only named columns and partition filters remove whole partitions, so the bill is a direct function of layout ([[Partition Pruning, Clustering and Column Pruning]]). Measured compressed bytes on a Parquet year of trips: full table 86.8 MB, two columns 17.0 MB (5.1x cheaper), two columns in one month 1.4 MB (62.3x). Ratios depend on schema, and they were measured on compressed Parquet while the bill counts logical bytes per data type: direction carries over, the exact factor needs a free dry run on the real table. Clustering savings do not show in the estimate. See [[Materialise or Query and Cost Tests]] for the dashboard arithmetic.

## Slots (capacity)

A slot is a virtual compute unit. Autoscaled capacity is billed per slot-hour, per second with a one-minute minimum: $0.04 Standard, $0.06 Enterprise, $0.10 Enterprise Plus, with discounts for one- and three-year commitments.

| Slots, hours a day | Standard | Enterprise | Enterprise Plus |
|---|---|---|---|
| 100, 8 | $960 | $1,440 | $2,400 |
| 500, 8 | $4,800 | $7,200 | $12,000 |
| 500, 24 | $14,400 | $21,600 | $36,000 |
| 2000, 24 | $57,600 | $86,400 | $144,000 |

**Break-even.** 100 Enterprise slots for 8 hours a day cost $1,440 a month, the same as scanning 231 TiB on demand. Below that, on demand wins; above it, and with steady load, capacity wins. Worked check: 40 TiB a month on demand is 39 billable TiB, about $244, against $960 for 100 Standard slots, so on demand wins by about four times.

| | On demand | Capacity |
|---|---|---|
| Meter | TiB scanned | Slot-hours |
| Best for | Spiky, small or unpredictable use | Steady heavy load |
| Bad query costs | Money, immediately | Queueing for everyone, with no invoice line |
| Control | Per-query byte limits | Reservations and autoscale caps |
| Layout savings | Lower the bill directly | Free slots; lower bill only if the cap drops |

The same bad query has different owners: finance on demand, the on-call engineer on capacity. Other engines have the same structure under other names (credits per second, DBUs); a local DuckDB run pays only for the laptop.

## Storage

Active logical storage costs $0.000031507 per GiB-hour, falling to a lower long-term rate after 90 days unmodified. Per month: 1 TiB active $23.32, 1 TiB long-term $16.22; 2 TiB stored costs $46.87 against $35,993.75 for scanning it 96 times a day, nearly three orders of magnitude. Aggressive deletion is rarely the first move; storing an aggregate to avoid scans often pays many times over.

## Egress

Per GiB by route: $0.01 across zones in a region, $0.02 between North American regions, $0.05 North America to Europe, $0.08 to Asia, $0.12 for the first internet tier to North America after the first free GiB (tiered). Copying 500 GiB a day for 30 days (14.6 TiB a month): $150, $300, $750, $1,200 and $1,517.32 to the internet. Keep compute beside its data (reads across locations incur charges), and count cross-region replication and a remote BI tool's extracts as recurring transfers.

## Pitfalls

- Comparing list prices and ignoring workload; the price per TiB says nothing until bytes scanned is known.
- Tuning storage first; it is usually the smallest number.
- Autoscale without a cap is unbounded spend with a different label.
- Cross-region defaults: bucket and warehouse in different regions pay on each read.
- Quoting a price without a date.

## See Also
- [[Separated Storage and Compute and Warehouse Billing Shapes]] — related
- [[Materialise or Query and Cost Tests]] — extends
- [[Partition Pruning, Clustering and Column Pruning]] — prerequisite-for
- [[Small Files, Prefix Layout and Storage Tiers]] — related
