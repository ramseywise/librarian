---
title: Metric Tree Decomposition
tags: [foundations, pattern]
summary: A metric tree splits a top number into identity edges that can be asserted and attributed exactly (log-mean weights) and dashed causal edges that need a test before anyone acts; a count north star needs a paired check.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--11-metric-trees.md
---

# Metric Tree Decomposition

A metric tree starts at one number and asks what it is made of. Two kinds of edge are read differently:
- **Identity edge (solid):** arithmetic, checkable with an assert. Revenue = active customers x orders per customer x value per order holds whatever the business does.
- **Causal edge (dashed):** a belief that a lever moves a leaf (reminder emails raise orders per customer). It can be false while the identity above it stays true, and it needs an experiment or other design before action.

If the leaves stop multiplying back to the ledger, a definition changed. Tables that do not reconcile (a web log with 37,329 purchases against 20,852 ledger orders over the same dates) stay beside the tree, not under it; rescaling them to pass the assert hides the problem.

## Attributing a change along the identity
Multiplying leaves one at a time depends on the order and leaves an interaction term. Weight each leaf's log change by the log mean of the totals, weight x ln(after/before) with weight = (after - before) / ln(after/before): logs of a product add, so the parts sum to the change with no residual and no order dependence.

```python
w = (after.revenue - before.revenue) / np.log(after.revenue / before.revenue)
parts = {leaf: w * np.log(after[leaf] / before[leaf]) for leaf in leaves}
```

Worked case: a year with revenue up 2.1% split into +374,320 from more active customers, -333,706 from fewer orders per customer and -13,352 from value per order, summing to the 27,263 change; two large moves almost cancelling. Had the extra customers kept the prior frequency, revenue would have been 1,698,403, a gap of about 403k. A monthly version localises timing: orders per customer stepping from 1.22 to 1.12 and staying for three months is not seasonal, and a year-on-year comparison of the same month showed -9,531 from frequency against +10,761 from customers. Attribution says which leaf moved, not why; the reason needs [[Rate and Mix Decomposition]] or [[Cohort Retention Triangle]] work.

## North star and drivers
A north star is the one number a team steers by across quarters. It should follow customer value, lead revenue rather than restate it, and change what someone would do. It is too slow to decide a single launch (that is the OEC's job, see [[OEC, Guardrails and North Star Metrics]]).

Candidate here: repeat customers, those with two or more orders in the trailing 365 days. Over 2025 it rose 3.5% (4,430 to 4,587) while the share of actives repeating fell from 43.0% to 33.2%: a count rises with scale, a share punishes healthy acquisition, so neither alone catches the problem. Split into new and returning customers, since they are different businesses: a new customer's first-year spend fell from 101.41 to 75.38 on 33% more of them. Owned drivers sit under the star (new customers by channel, share returning within 90 days), then input metrics a team controls directly. Write the goal, then the signal, then the metric, so a metric is not picked only because it is on a dashboard.

Revenue less spend fell 17.1% in the same year while revenue rose 2.1%: pair every target with a cost line ([[Counter-Metrics, Guardrails and Goodhart Variants]]).

## Pitfalls
- A tree of identities only: tidy and not actionable until causal edges are drawn and tested.
- Reading a dashed edge as solid ("opens feed repeat purchase, so raise opens"): correlated leaves are not levers.
- A north star that merely restates revenue.
- Forty scoreboard rows: each needs an owner and a decision it would change, else it is diagnostic and belongs a level down.

## See Also
- [[Counter-Metrics, Guardrails and Goodhart Variants]] — extends
- [[Writing a Metric Definition Two Analysts Agree On]] — prerequisite-for
- [[OEC, Guardrails and North Star Metrics]] — related
- [[Rate and Mix Decomposition]] — related
- [[Ratio Metrics and the Denominator Trap]] — related
