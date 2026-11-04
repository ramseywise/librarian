---
title: "Materialise or Query and Cost Tests"
tags: [foundations, pattern]
summary: "Decide whether to store a daily aggregate by comparing rebuild cost to scans saved at the real read rate, and stop cost regressions with dry-run byte budgets and per-job attribution instead of finding them on the invoice."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--05-cost.md
---
# Materialise or Query and Cost Tests

A dashboard refreshing every 15 minutes (96 runs a day) over a 2 TiB table cost about $36,000 a month. Nobody chose that: someone wrote `SELECT *` on a table that was small at the time, a scheduler ran it, and the table grew.

## Dashboard arithmetic

At $6.25 per TiB with the first TiB free ([[Warehouse Cost Meters: Bytes, Slots and Egress]]), 96 runs a day for 30 days:

| Query | Scanned per month | Cost |
|---|---|---|
| `SELECT *` | 5760 TiB | $35,993.75 |
| two columns | 1130 TiB | $7,053.28 |
| two columns, one month | 92 TiB | $571.35 |

Sixty-fold from a column list and a date filter ([[Partition Pruning, Clustering and Column Pruning]]).

## Materialise or query

An aggregate table rebuilt once a day costs a full scan of the base each day, plus cheap reads and a little storage. Over a 2 TiB base with an aggregate 2% of its size:

| Reads a day | Query the base | Daily aggregate |
|---|---|---|
| 0.2 | $75.00 | $377.44 |
| 1 | $375.00 | $383.44 |
| 5 | $1,875.00 | $413.44 |
| 96 | $36,000.00 | $1,095.94 |

Under one read a day the rebuild costs more than the queries it replaces; at five it wins. "Materialise your marts" is right for dashboards and wrong for a table queried weekly. The aggregate must be much smaller than its base: with an aggregate only five times smaller (reads 10 times costlier per run), five runs a day cost about $760 against $1,875, about 2.5 times cheaper instead of 4.5. Run the arithmetic per model; in a transform tool the choice is a one-word config.

## Make cost a test

Cost problems surface on the invoice because nothing fails earlier. Put a guard in the pipeline: a dry run (free, reports bytes before execution) or a maximum-bytes-billed limit that fails a query reading more. A pre-merge check estimating the cost on a 2 TiB table against a $1.00 budget gave: full scan $12.50 FAIL, two columns $2.45 FAIL, two columns in one month $0.20 pass. The principle matches data tests: state an expectation in code and fail loudly and early ([[Medallion Layers Need Tests]]).

## Attribute

A bill by team, job or dashboard makes cost something a team can act on. Job-history views record bytes billed and slot time per job, and job labels carry the owner; group by user and query over 30 days and the top twenty usually hold most of the spend. Fix in order: the query (columns, filters), then layout (partition, cluster), then an aggregate, then the pricing model, because each step changes what the next should be.

## Pitfalls

- **`LIMIT` as cost control.** On a non-clustered table it does not change data read or billed; use a preview or a filter.
- **Materialising everything.** A table nobody reads costs a daily rebuild for nothing.
- Small files add operations and open overhead: 3,000 files read twice each, 96 runs a day for 30 days, cost $6.91 a month in operations, minor next to the compute time ([[Small Files, Prefix Layout and Storage Tiers]]).

## See Also
- [[Warehouse Cost Meters: Bytes, Slots and Egress]] — prerequisite-for
- [[Medallion Layers Need Tests]] — related
- [[Small Files, Prefix Layout and Storage Tiers]] — related
