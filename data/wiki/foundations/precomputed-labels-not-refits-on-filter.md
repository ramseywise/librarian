---
title: Precomputed Labels, Not Refits on Filter
tags: [foundations, pattern]
summary: Cluster ids are arbitrary and refits on filtered data move customers between groups, so a batch job should publish labels and the app should only read them.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--06-dashboard-stacks-from-python-to-frontend.md
---

# Precomputed Labels, Not Refits on Filter

The tempting design refits the clustering whenever a user filters to a region. Speed is not the objection: one k-means fit (10 random starts, 50,000 rows, five features) took 49 ms, against 4.7 ms to read Parquet and aggregate and 2.7 ms to aggregate in-memory. But it burns threads and reduces concurrent viewers.

## The real argument: meaning

Cluster ids are arbitrary: any permutation of labels scores the same, so cluster 2 today has no reason to be cluster 2 tomorrow, and a dashboard or email list keyed on the number silently changes meaning. The adjusted Rand index (ARI) compares groupings ignoring ids (1 identical, about 0 chance). On overlapping groups a new seed kept the same id for only 49.1% of customers, yet ARI was 0.994. A fixed `random_state` makes one fit repeatable but not a fit on changed data, and a filter changes the data:

| Refit on | Well-separated | Overlapping |
|---|---|---|
| Same 50,000, new seed | ARI 1.000, 0.0% change group | ARI 0.994, 0.2% |
| One region (2,001 customers) | ARI 0.999, 0.0% | ARI 0.932, 2.6% |
| Spend above the median (25,000) | ARI 0.799, 14.8% | ARI 0.614, 25.3% |

On a filter touching a modelled feature, about one in seven customers changed segment on clean data and one in four on messier data. The groups are planted and simple, so treat the percentages as illustration and measure your own. Choosing k from 2 to 8 by silhouette on a 10,000-row sample took 3.6 s, not something to do per request.

## Rule

A scheduled job writes labels, names and the model version to a table; the app only reads and filters rows. Refitting becomes a decision a person reviews; between refits the job assigns new customers to the approved model. This follows precompute-versus-compute-on-request reasoning. Also fix colours by segment name ([[Chart Colour Scales and Accessibility]]).

## See Also
- [[Clustering Validation Against Named Baselines]] — related
- [[Dashboard Stack Layers and Choosing a Route]] — related
- [[Dashboard API Exposure and Payload Cost]] — related
