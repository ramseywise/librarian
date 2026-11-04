---
title: Matching and Weighting Estimators
tags: [foundations, comparison]
summary: "Exact matching, coarsened exact matching, propensity matching, propensity weighting, entropy balancing and regression adjustment answer different questions (ATE, ATT, local ATT) and all landed 3 to 4 pounds above the truth because of an unlogged confounder; report who was kept and judge designs on balance before outcomes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
---

# Matching and Weighting Estimators

Setup: a self-selected club, 9,456 customers, 3,746 joiners, naive spend gap 95.54 against a true ATT of 23.38 (true ATE 15.96, true ATC 11.10). Each design returns weights without reading the outcome; judge them on [[Covariate Balance and Overlap Checks]] first.

## Targets

ATE is the effect over everyone; ATT is the effect on those treated; a local ATT is the ATT on the treated units kept. They differ when effects vary (the club does more for frequent buyers, who join). Pruning treated units changes the target.

## Designs

- Exact matching on every covariate found no match for any joiner; on channel and orders only it kept 3,369 joiners and left recency 0.43 SD apart.
- Coarsened exact matching (CEM): coarsen into defensible bins, match exactly on bins, discard strata lacking a group; the analyst sets the maximum imbalance up front and support is automatic. Kept 2,202 joiners (59%), max SMD 0.024.
- Nearest-neighbour propensity matching on log odds with a caliper (0.2 SD). With replacement keeps more joiners (3,682) at lower precision (control effective n 246); without, 1,972 joiners (53%), max SMD 0.018. A wider caliper keeps more joiners with weaker matches: at 1.0 SD the max SMD reached 0.248 and the gap was about 17.
- Propensity weighting: for the ATT joiners weigh 1 and non-joiners p/(1-p), so a control scoring 0.997 counts as about 330 people. Keeps everyone, max SMD 0.167, control effective n 107.
- [[Entropy Balancing]]: exact moment balance, control effective n 267.
- Regression adjustment: one coefficient targets neither ATE nor ATT cleanly (17.59); by arm 18.21 (ATE) and 26.44 (ATT). A linear model is the wrong shape when the outcome has a floor ([[Regression Covariate Adjustment]]).

## What the scoring showed (20 generated datasets)

- Every sound ATT design landed high by 3.15 to 4.31 pounds on average: a shared bias, so better covariates help, better estimators do not.
- Matching with replacement scored -0.11 on one dataset by luck (sd across runs 2.42, mean gap 4.31). Plain propensity weights were worst (mean gap 8.27, sd 7.76; one dataset missed by over 20); trimming scores to 0.05-0.95 gave 3.15 but changes the target.
- CEM's 20.96 and entropy balancing's 26.49 are not in disagreement: CEM kept customers whose true effect was 17.31. Matching without replacement's 18.26 resembles the true ATE 15.96 but does not estimate it. Report who was kept.
- Twenty datasets from one generator do not give a general ranking.
- Library defaults can mislead: one causal library's weighting estimator clips scores to 0.05-0.95 by default, taking an ATT of 18.75 to 39.24; its propensity column was reused across estimators, so build a fresh model per estimator.

Choosing the design after reading the outcome lets you pick whichever confirms the answer; here the spread was 15 to 32.

## See Also
- [[Covariate Balance and Overlap Checks]] — prerequisite-for
- [[Sensitivity Analysis for Unmeasured Confounding]] — extends
- [[Backdoor and Front-Door Criteria]] — prerequisite-for
- [[Potential Outcomes and Selection Bias]] — prerequisite-for
- [[Causal Design Selection Beyond Randomisation]] — related
- [[Survey Weighting, Raking and Effective Sample Size]] — related
