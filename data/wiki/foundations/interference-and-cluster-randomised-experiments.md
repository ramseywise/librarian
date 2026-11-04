---
title: Interference and Cluster-Randomised Experiments
tags: [foundations, pattern]
summary: "When one user's arm changes another's outcome, as with fixed stock in a marketplace, a user-level A/B test overstates the effect (+30% measured against +19% real), so randomise by cluster, switchback or item and pay the design effect 1+(m-1)rho in variance."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# Interference and Cluster-Randomised Experiments

Randomised tests assume one user's arm does not change another's outcome (SUTVA). Marketplaces and networks break it.

## Demonstration

Fixed stock of 120 units, 1,000 buyers, base purchase probability 0.1, treated buyers 30% more likely. Inside one market split 50/50: control 0.0981, treatment 0.1277, a +30.1% lift. Nobody treated sold 100.0, everybody treated sold 119.0: the real lift is +19.0%. The treatment takes units from control. A first-bidder discount in auctions is the same: control users bid on the same items, so the fix was randomising items, not users.

## Designs

| Design | Randomises | Good for | Cost |
|---|---|---|---|
| Cluster | city, seller, network community | spatial and social spillover | fewer units, more variance |
| Switchback | market by time window | ride-sharing, delivery | carryover between windows |
| Two-sided | buyers and sellers crossed | marketplaces | a lot of traffic |
| Holdout | small group kept from the launch | total long-run effect | delay, users left behind |

## Cost: the design effect

Variance multiplies by 1 + (m - 1) rho, with m the cluster size and rho the intra-cluster correlation: m 100, rho 0.01 gives 2.0; m 1,000, rho 0.01 gives 11.0; m 1,000, rho 0.001 gives 2.0. At 11, a million users carry the information of about 91,000. With 200,000 users in 1,000 equal clusters and rho 0.02 the design effect is 4.98 and the effective sample about 40,000. Analyse at cluster level or with cluster-robust errors ([[Clustered Standard Errors]], [[Pseudoreplication and Intraclass Correlation]]); the confidence intervals from treating clusters as users are far too narrow. Multilevel models estimate rho and read segment effects with partial pooling.

## See Also
- [[Pseudoreplication and Intraclass Correlation]] — prerequisite-for
- [[Clustered Standard Errors]] — related
- [[A/B Test Lifecycle and Interval Decisions]] — related
- [[Experiment Ramps and Overlapping Tests]] — related
