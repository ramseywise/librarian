---
title: Ratio of Sums vs Mean of Rates
tags: [foundations, pattern]
summary: A group's rate is the sum of numerators over the sum of denominators; averaging per-row rates weights tiny and huge rows equally and can reverse the ranking of groups.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
---

# Ratio of Sums vs Mean of Rates

## The trap

The error that most often survives into a real report: compute a rate per row (margin / revenue), then average the rates by group. That gives a 13.00 order the same weight as a 96.00 order. The figure the business means is total margin over total revenue. **Sum the top, sum the bottom, then divide.** The same trap applies to conversion rate, average order value, cost per click.

```python
g = orders.groupby("region").agg(revenue=("revenue", "sum"), margin=("margin", "sum"),
                                 mean_of_rates=("rate", "mean"))
g["true_rate"] = g["margin"] / g["revenue"]
```

## Worked numbers

In a four-region example, the `east` region had two orders: a 13.00 order at about 62% margin and a 95.00 order at about 37%. Mean of rates: 0.492. True rate: 43.0 of 108.0, or 0.398. For `north`: 0.453 against 0.408. The two measures rank the regions differently: east beats north on the mean of rates, north beats east on the true rate.

## When it is harmless

Grouped by category, the two agreed to three places (0.372, 0.615, 0.455 for the three categories) because every order of one product shares a rate and products within a category have similar rates. Regions mixed very different products, which is why they diverged. So the error hides until groups mix heterogeneous rows.

## Related fixes

- Weighted average of a price: `np.average(d["unit_price"], weights=d["qty"])` inside `apply`.
- Print a count beside every mean. A mean from one observation prints with the same confidence as one from ten thousand.
- Check that groups add up to the total (see [[Groupby Silent Group Loss and Pivot Defaults]]).
- Statistical treatment of ratio metrics: see [[Delta Method for Ratio Metrics]].

## See Also
- [[Groupby Split-Apply-Combine and Result Shapes]] — prerequisite-for
- [[Groupby Silent Group Loss and Pivot Defaults]] — related
- [[Delta Method for Ratio Metrics]] — related
- [[Ratio Metrics and the Denominator Trap]] — related
