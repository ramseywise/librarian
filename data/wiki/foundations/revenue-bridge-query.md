---
title: Revenue Bridge Query
tags: [foundations, pattern]
summary: A revenue bridge labels each customer-month new, returning or reactivated with a lag window over a CTE chain, so a flat-looking total splits into parts that move in opposite directions; the labelling gap is a stated choice and the total must reconcile to source.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--06-sql-for-analytics.md
---

# Revenue Bridge Query

A bridge splits one period's total into labelled parts so a change in the total becomes changes in the parts. It settles arguments where two teams use different definitions of "returning customer".

## Construction (CTE chain, one idea per step)

1. **monthly**: one row per customer per month with revenue.
2. **history**: add the customer's previous active month with a lag window over the customer, ordered by month.
3. **labelled**: new if no previous month; returning if the previous active month is at most 3 months earlier; otherwise reactivated.
4. Sum revenue by quarter and kind.

Each CTE can be run and checked alone.

## Result (simulated retailer)

Revenue rose 27,264 (2.1%) between 2024 and 2025. New customers added 124,260, reactivated 55,021, returning lost 152,017: a 24% fall in revenue from customers who keep buying hides inside 2.1% growth. Marketing ("growth is new customers") and finance ("customers are leaving") were both right about different rows.

## The definition is a choice

The 3-month rule must be stated with the result. Changing it to 6 months moved 2025 reactivated from 230,947 to 102,942 and returning from 486,293 to 614,297 (new unchanged); returning revenue fell 18% instead of 24% (753,089 to 614,297). Levels depend heavily on the rule, the direction does not; a conclusion that holds under both rules is stronger. In this data only 87 streaks reached six consecutive months, which is why a one-month "returning" would be too strict.

## Prove it adds up

Reconcile against the source and a second implementation (pandas) before anyone reads it: returning matched exactly, new and reactivated differed by 1-2 (rounding per quarter and kind), bridge total 3,364,668 against 3,364,669 in the source. A rounding-explained 2 is fine; an unexplained 2 may be part of offsetting errors. The total check also proves no row was dropped or double counted. Put the reconciliation in a scheduled test and the definition in version control.

## Limits
A bridge says where revenue landed, not why; revenue here is before refunds. Do not project the headline growth forward when it was bought with acquisition.

## See Also
- [[SQL Window Functions]] — prerequisite-for
- [[SQL Subqueries and CTEs]] — prerequisite-for
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Cohort Retention Triangle]] — related
- [[Rate and Mix Decomposition]] — related
