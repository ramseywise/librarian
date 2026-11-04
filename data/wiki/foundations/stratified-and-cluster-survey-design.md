---
title: Stratified and Cluster Survey Design
tags: [foundations, concept]
summary: Stratify to guarantee coverage of known groups, allocate proportionally unless one statistic dominates (Neyman allocation helps one number and hurts others), and cluster only when travel cost beats the design-effect loss.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--12-surveys-and-sampling-design.md
---

# Stratified and Cluster Survey Design

## Stratification and allocation
Split a frame into groups known in advance and sample each separately, so no draw falls short on a small, important group. Allocation chooses how many per stratum:
- **Proportional:** each stratum its population share, equal chance for all customers; never worse than simple random sampling.
- **Neyman:** n_h = n x N_h S_h / sum(N_k S_k), more to strata that vary more; minimises variance for one statistic with equal interview costs.

For 1,000 completes over three order-count segments (26,342 customers), standard errors on spend: simple random 6.43, proportional 4.88, Neyman-for-spend 2.97 (596 of 1,000 interviews on the heavy-buyer segment). On share satisfied: 0.0155, 0.0154, and 0.0218 for Neyman-for-spend, about 42% worse. For a share near one half S_h barely varies, so Neyman lands near proportional. Optimising for one number can cost others (an allocation best for mean income lost on median income). Use proportional for a many-question survey; use disproportionate allocation when one number matters most or a small stratum needs its own estimate.

**Finite population correction:** variance times (1 - f), f = n/N. For 1,000 of 26,342 the standard error shrinks 2% (factor 0.981); for 150 of 400 accounts it shrinks 21% (0.791), and ignoring it overstates the margin. A common rule ignores it up to a sampling fraction of 5% (second-hand). For plus or minus 5 points at 95% on 400 accounts, worst case p = 0.5: 384 completes ignoring it, 196 with it.

## Clusters
Visiting places costs travel; cluster sampling takes several people per place. Neighbours resemble each other, so each extra interview adds less. The design effect is 1 + (m - 1) rho (m interviews per cluster, rho intra-cluster correlation; see [[Pseudoreplication and Intraclass Correlation]]); compare designs by effective sample size, interviews / deff. With a fixed budget of 12,000, 60 per area visited, 8 per interview, rho = 0.026:

| per area | areas | interviews | deff | effective n |
|---|---|---|---|---|
| 5 | 120 | 600 | 1.105 | 543 |
| 10 | 85 | 850 | 1.236 | 688 |
| 15 | 66 | 990 | 1.367 | 724 |
| 20 | 54 | 1,080 | 1.499 | 721 |
| 40 | 31 | 1,240 | 2.023 | 613 |

More interviews (1,240) with less information (613 vs 724) at 40 per area. Costlier travel pushes toward fewer areas with more people each (peaks at 15, 25, 30 per area for travel 60, 120, 240). The sampler cannot control rho but can set cluster size. A handbook example with rho 0.03: 50 per cluster gives deff 2.5, 100 gives 4.0; effects much above 2.5-3.0 are undesirable for key indicators. The formula's errors ran a little above simulation because it treats areas as from an endless supply.

## See Also
- [[Survey Error Sources and Nonresponse Bias]] — prerequisite-for
- [[Survey Weighting, Raking and Effective Sample Size]] — related
- [[Pseudoreplication and Intraclass Correlation]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
