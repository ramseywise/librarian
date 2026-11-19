---
title: P-Value Misreadings
tags: [data-analytics, probability-and-statistics, concept]
summary: "A p-value is the chance of data at least this extreme if the null were true, not the chance the null is true, not an effect size, and not evidence of no effect when large; with millions of users a negligible lift is highly significant."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch01-introduction-statistical-significance.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch04-p-value-base-rate-fallacy.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch05-bad-judges-significance.md
  - data/raw/papers/2026-11-08-think-stats-ch07-hypothesis-testing.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch01-algorithms-inference.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch01-golem-prague.md
---

# P-Value Misreadings

## The recipe

State H0 (no effect) and H1, fix alpha, choose a test statistic, compute the **p-value** (probability of a statistic at least this extreme if H0 holds), then decide. Under a true null the p-value is uniform on [0, 1], so 5% of true nulls are "significant" by construction.

## Four misreadings

1. **p is not P(H0 is true).** Turning one into the other needs a prior and base rates ([[Bayes Rule and the Base Rate Fallacy]]).
2. **A large p does not mean no effect.** p = 0.2 means the data are compatible with zero, not that zero is established; look at the interval and power ([[Minimum Detectable Effect and Sample Size]]).
3. **A tiny p does not mean a big effect.** With 5 million users per arm a lift of 0.0004 (0.9% relative) gave p = 2.9e-3. Significance measures detectability; size is the estimate.
4. **Significant here and insignificant there is not a significant difference.** One study under 0.05 and another over it does not show the two disagree; compare the groups directly instead ([[Difference in Significance and Error Bar Overlap]]).

## The p-value belongs to the design

Reinhart's worked example (chapter 1): a guesser gets 9 of 12 true/false questions right. With 12 questions fixed in advance (binomial) p = 0.073; if instead the quiz stops at the third wrong answer (negative binomial) p = 0.033. Identical data, a different stopping rule, and the verdict at 0.05 flips. He adds that alpha describes the procedure chosen beforehand, not one experiment, so p = 0.032 is not a 3.2% false positive rate, and that 0.05 is merely conventional. Cited surveys: 97% of experimental psychology papers use significance tests while roughly 10% give confidence intervals, and 89% of Nature articles give p values without intervals or effect sizes. He recommends intervals, with domain knowledge to judge importance. In a survey he cites, two-thirds of doctors misread p < 0.05 as a 95% chance the finding is true.

## Two more cautions

- In a leukemia study (7,128 genes; 47 ALL and 25 AML patients): gene 136 has t = 3.01 on 70 df, p = 0.0036, but about 400 of the 7,128 genes (5.6%) exceed that t, so the p-value overstates the evidence (Efron and Hastie, Computer Age Statistical Inference ch. 1). A low false-discovery rate needs t above 6.16, which 47 genes meet.
- Downey (Think Stats ch. 7) turns the 0.166 resampled p-value for pregnancy length (NSFG, 4,413 first babies against 4,735 others) into a naive posterior near 0.748 (prior 0.5, P(E|HA) = 0.494, P(E|H0) = 0.166), where HA is defined from the observed difference. He concedes the calculation overstates the evidence; with random half-split cross-validation on NSFG Cycle 6 the average posterior is 0.621. He advises reporting the likelihood ratio so readers can apply their own priors, and, for a negative result, the test's power.

McElreath (Statistical Rethinking ch. 1) argues that scientists commonly read p-values and confidence intervals as if they were posterior probabilities and credible intervals, while the reverse mistake is rare; he offers this as a teaching argument for Bayesian methods, with no data.

## Pairing matters

The same data gave p = 0.0004 when analysed as paired and 0.33 unpaired. Using the test that matches the design is not optional ([[Statistical Test Selection]]).

## Defaults for reporting

Report the estimate and its interval, not just the verdict. Significant results from underpowered tests are inflated ([[Winner's Curse]]), and running many tests breaks the nominal alpha ([[Multiple Comparisons Corrections]]). A [[Permutation Test]] shows the null distribution the p-value refers to.

## Limits

- Reinhart's chapter 1 examples are hypothetical, and his journal-survey figures are old and come from other people's work.
- Think Stats ch. 7 uses one dataset (NSFG), so its numbers are illustrations; the naive posterior is acknowledged as flawed; the chi-square example reuses data already used to explore; its Type I/II wording is confusing; and the power exercise computes no value.
- CASI ch. 1 asserts the 6.16 threshold without derivation and gives one dataset per example.
- Gene 136 appears here as t = 3.01, p = 0.0036 (CASI ch. 1), but [[Permutation Test]] uses CASI ch. 4's t printed as 3.13 and p = 0.0025; the two extractions disagree, and I have not reconciled them.
- McElreath's ch. 1 point is an argument only, with no data; it does not claim Bayesian results are more correct, only closer to scientists' intuitions.

## See Also
- [[Confidence Interval Coverage and Wilson]] — related
- [[Data Defect Correlation]] — related (a tiny p on selected data is still wrong)
- [[Eval Error Bars and Sample Size]] — related
- [[Bayesian A/B Testing with Expected Loss]] — alternative-to
- [[Difference in Significance and Error Bar Overlap]] — extends
- [[Researcher Degrees of Freedom and Prespecification]] — related
- [[Publication and Outcome Reporting Bias]] — related
- [[Bayes Factors and Composite Hypotheses]] — related
