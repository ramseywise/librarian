---
title: Population Stability Index
tags: [foundations, concept]
summary: PSI compares a score's current distribution with the one a model was built on, bin by bin, needing no outcomes, so it warns of drift years before defaults arrive; its 0.10 and 0.25 thresholds are conventions.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--02-credit-scoring.md
---

# Population Stability Index

A model stops being valid without anyone touching it because the scored population moves. PSI measures how far the score distribution has moved from development.

- Bin the development scores (deciles), then sum over bins (actual share - expected share) x ln(actual share / expected share). Add a tiny constant to empty bins.
- Common rule of thumb: under 0.10 little shift, above 0.25 significant shift needing action. These benchmarks are used without reference to error rates, so treat them as review triggers; PSI also grows with sampling noise in small samples.
- Needs no outcomes, so it works long before defaults are observed.
- Worked check: train vs test (random split) 0.043. Recoding the safest checking-account class as "no account" (simulating that class vanishing from the applicant pool) gave 0.252.

## See Also
- [[Weight-of-Evidence Logistic Scorecard]] — prerequisite-for
- [[Prior Shift Correction for Oversampled Defaults]] — related
