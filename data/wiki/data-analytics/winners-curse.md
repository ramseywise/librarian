---
title: Winner's Curse
tags: [data-analytics, experimentation-and-causality, concept]
summary: "When a test is underpowered, the estimates that reach significance are exaggerated: a true 1 percent lift with a 1 percent standard error had power 0.17, significant estimates averaged 2.5 times the truth, and some had the wrong sign."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch02-statistical-power-underpowered-statistics.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch06-double-dipping-data.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch03-bayesian-inference.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch20-inference-after-model-selection.md
---

# Winner's Curse

Select on significance and you select on luck. Estimates are truth plus noise; those that clear the threshold are disproportionately the ones where noise pushed upward.

## Numbers

True lift 1%, standard error 1%:
- power is only 0.17;
- among significant results the mean estimate was 0.0245, about 2.5x the true effect;
- 0.9% of significant results had the wrong sign.

The smaller the power, the worse the inflation: a win from a small test is likely an overestimate, and shipping on it then sees the lift shrink in the next measurement.

## Reinhart's cited cases (chapters 2 and 6)

- Chapter 2 calls it truth inflation (type M error). A corrected estimate in the Kanazawa attractive-parents study gave 4.7% more girls with an interval running from 13.3% more to 3.9% fewer on nearly 3,000 parents. If the true effect were 0.3%, significant results would occur about 5% of the time, exaggerate it at least 20-fold, and 40% would point the wrong way.
- He cites a median neuroscience power of 20%, and negative randomised trials from 1975-1990 in which more than four-fifths lacked data to detect a 25% difference.
- Chapter 6 cites medical trials stopped early exaggerating effects by an average of 29% against similar trials not stopped ([[Double Dipping and Selection on the Test Data]]).

In the prostate study of Efron and Hastie (6,033 genes, 52 patients against 50 controls) the largest statistic is 5.29. A flat prior gives 5.29 as the estimate, an overestimate, while an empirical Bayes prior gives 4.11. They caution that Bayesian immunity to selection bias needs care with uninformative priors.

## Mitigation

A data-driven correction is Tweedie shrinkage, which adjusts a selected estimate using the marginal density alone: [[Empirical Bayes: Tweedie's Formula and g-Modeling]]. On the same prostate data (N = 6,033, fourth-degree log-polynomial fit of the marginal density), CASI ch. 20 shrinks the top gene's z = 5.29 to 4.03, close to the 4.11 above; in a simulation of 100 datasets of N = 1,000 the corrected top-20 differences centre at zero, where uncorrected ones sit about one unit too high.

- Power tests properly ([[Minimum Detectable Effect and Sample Size]]).
- Report the interval, not the headline estimate ([[P-Value Misreadings]]).
- Pick the best of many variants and expect regression toward the mean ([[Multiple Comparisons Corrections]]); shrink estimates toward the overall mean ([[Small-N Trap and Shrinkage]]).

## Limits

- The chapter 2 figures from Reinhart are quoted from endnotes missing in the extract, and are other researchers' data, not his own.
- The CASI ch. 20 simulations use single designs and report no random seeds.
- CASI ch. 3 says Bayesian immunity to selection bias needs caution when the prior is uninformative.

## See Also
- [[Eval Error Bars and Sample Size]] — related
- [[Confidence Interval Coverage and Wilson]] — related
- [[Experiment Ramps and Overlapping Tests]] — related (portfolio-level inflation of shipped lifts)
- [[Partial Pooling for Segment Winners]] — extends
- [[Stepwise Selection and Overfitting on Noise]] — related
- [[Publication and Outcome Reporting Bias]] — related
- [[Double Dipping and Selection on the Test Data]] — extends
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — extends
- [[Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates]] — extends
