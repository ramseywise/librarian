---
title: "Staging Dedupe Keys and Fact Join Row Loss"
tags: [foundations, pattern]
summary: "A dedupe is only as right as its key, and an inner join in a fact silently turns missing dimension rows into missing revenue with every test green; left join through an explicit unknown row and reconcile."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--01-transform.md
---

# Staging Dedupe Keys and Fact Join Row Loss

Two quiet ways a transform loses or keeps the wrong rows. Neither raises an error.

## Check the dedupe key before trusting it
Staging dedupes with `row_number() over (partition by key) ... where rn = 1`. Count distinct on the candidate key first. On a synthetic table of 100,000 trips with pickup times drawn at random across a month, the key (vendor, pickup time) saw 99,040 distinct values because distinct trips sometimes start in the same second; adding pickup zone and amount recovered all 100,000. The figures come from generated data, but the check transfers.
- Too narrow a key deletes real rows; too wide leaves duplicates.
- `row_number()` with no `order by` keeps an arbitrary row when duplicates differ, and the choice can change between runs. Order by something meaningful, usually load time descending.
- Cast with a safe cast so a bad value becomes null instead of failing the run, then map null to an explicit unknown code that a macro labels.

## Inner joins in a fact lose rows
A fact joined to a dimension with an inner join drops every row whose key has no parent. In a synthetic month of 300,000 trips, zone ids ran to 265 while the lookup stopped at 260, so about 2 percent of rows were orphans: the inner join lost 5,680 trips and about $96,000 of revenue. No test failed:
- `relationships` became trivially true because the orphans were gone;
- `unique` still held;
- only a reconciliation against staging notices.

The fix is a left join to a dimension with a default row (key -1, "Unknown") and a count of the unknowns. A real source will eventually send a new code and do the same thing. Keeping the rows also repairs history for free: adding the missing zones to the reference table and rebuilding took unknown rows from 5,680 to 0 with the total still 300,000, whereas dropped rows would have to be noticed and reloaded.

## Why the join type is a business decision
Dropping unknown-zone trips is a statement that unmapped revenue does not count. Make that choice visibly, in a model that says so, not by the default behaviour of a join keyword.

## See Also
- [[dbt Layers, Materialisations and the ref Graph]] — prerequisite-for
- [[dbt Singular, Generic and Unit Tests with Reconciliation]] — extends
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[SQL Join Patterns]] — related
