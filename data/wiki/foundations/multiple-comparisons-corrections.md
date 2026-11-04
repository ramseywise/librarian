---
title: Multiple Comparisons Corrections
tags: [foundations, pattern]
summary: "Running many tests makes a false positive likely, 64 percent for 20 tests at 5 percent, so adjust: Bonferroni and Holm control the chance of any false positive, Benjamini-Hochberg controls the share of false discoveries and keeps more power."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Multiple Comparisons Corrections

## The problem

With 20 independent true nulls at alpha = 0.05, the chance of at least one false positive is 1 - 0.95^20 = 64.2%. Simulated: 0.619 uncorrected, 0.052 under Bonferroni.

## Corrections

- **Bonferroni:** test each at alpha/m. Controls the family-wise error rate (FWER, chance of any false positive). Simple, conservative.
- **Holm:** step-down version; same FWER guarantee, never less powerful than Bonferroni.
- **Benjamini-Hochberg (BH):** controls the false discovery rate (FDR, share of rejections that are false). More rejections; suits screening many candidates.

On 100 tests with 10 real effects:

| Rule | Rejected | False among them |
|---|---|---|
| raw p < 0.05 | 11 | 3 |
| Bonferroni | 5 | 0 |
| Holm | 5 | 0 |
| BH | 7 | 0 |

## Where multiplicity hides

Many metrics, many segments, many looks at a running experiment, and forking analysis choices all multiply the number of tests even when only one is reported. Declare the primary metric and analysis in advance.

## Birthday problem

23 people give a 0.507 chance of a shared birthday: pairs grow quadratically (253 pairs), so coincidences appear sooner than intuition says. The same arithmetic: 118 users in 10,000 hash buckets give a 0.5 chance of a collision. Many comparisons are always more than they look.

## See Also
- [[P-Value Misreadings]] — prerequisite-for
- [[Winner's Curse]] — related (picking the best of many)
- [[Small-N Trap and Shrinkage]] — related (subgroups are small and many)
- [[Statistical Test Selection]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
