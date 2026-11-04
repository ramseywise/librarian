---
title: SQL Fan-Out and Source Reconciliation
tags: [foundations, pattern]
summary: Joining before aggregating repeats rows of the one side once per match and inflates sums with no error; aggregate the many side to the one side's grain first, and reconcile every report total to the source.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--06-sql-for-analytics.md
---

# SQL Fan-Out and Source Reconciliation

The most common serious bug in analytics SQL: when a join key is not unique on one side, each row on the other side is repeated once per match and every sum over that side grows. No error, no warning.

Example: refunds with several lines per order, left-joined straight to orders, gave revenue 3,641,037 against a true 3,364,669, an overstatement of 276,368 (8.2%). Refunds were right in both queries (the many side is never fanned out), so a spot check on refunds would pass.

Fix: aggregate the many side to the grain of the one side (sum refunds per order) before joining. Net revenue = 3,364,669 - 164,342 = 3,200,327; use coalesce on the refund amount or orders with no refund become NULL and drop out of the sum.

## Detection
State each table's grain before joining. Compare row count and sum after the join with the source; a total that matches proves no row was dropped or counted twice and is the single most useful test on any report built from joins. Schedule it so a broken join alerts before it reaches a slide.

## Related traps
- A WHERE on the right table of a left join turns it into an inner join; put the condition in ON.
- NOT IN over a column with NULLs returns nothing; use NOT EXISTS.
- Dialects differ (QUALIFY, FILTER, date_diff); interpolate only trusted text into SQL strings, user values as parameters.

## See Also
- [[SQL Join Patterns]] — extends
- [[SQL NULL and Three-Valued Logic]] — related
- [[Revenue Bridge Query]] — related
