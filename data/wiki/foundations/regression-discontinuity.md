---
title: Regression Discontinuity
tags: [foundations, pattern]
summary: "Units just either side of a cutoff are nearly comparable, so fitting a line on each side and reading the jump estimates the effect at the cutoff; report several bandwidths and check for pile-up at the cutoff, and do not extrapolate away from it."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Regression Discontinuity

When treatment is assigned by a threshold on a running variable (a status tier at a points total, a credit-score cutoff), people just below and just above are nearly identical and only one gets the treatment.

## Mechanism

Fit a line on each side within a bandwidth and read the jump at the cutoff. Simulation (true jump 2.50): the raw gap between treated and untreated was 22.54, nine times the truth, because treated users simply spend more. Local estimates: bandwidth plus or minus 100 points, n 2,855, effect 3.41 (SE 0.60); plus or minus 300, n 8,833, effect 2.69 (SE 0.35); plus or minus 1,000, n 30,000, effect 2.17 (SE 0.19). Narrow bandwidths have less bias and more noise, wide the reverse, so report several.

## Checks and limits

- Count users around the cutoff: a pile-up just above suggests people game the score, which breaks the comparison.
- The estimate applies only to people near the cutoff.
- The assumption is no manipulation of the running variable at the cutoff.

## See Also
- [[Causal Design Selection Beyond Randomisation]] — related
- [[Instrumental Variables and LATE]] — related
- [[Functional Form Misspecification]] — related (a linear fit across a wide bandwidth can mislead)
