---
title: Multiple Comparisons Corrections
tags: [data-analytics, probability-and-statistics, pattern]
summary: "Running many tests makes a false positive likely, 64 percent for 20 tests at 5 percent, so adjust: Bonferroni and Holm control the chance of any false positive, Benjamini-Hochberg controls the share of false discoveries and keeps more power."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch04-p-value-base-rate-fallacy.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch03-statistical-experiments-significan.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch02-data-sampling-distributions.md
  - data/raw/papers/2026-11-08-2017-08-kddmetricinterpretationpitfalls.md
  - data/raw/papers/2026-11-08-islp-ch13-multiple-testing.md
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

## Reinhart's chapter 4 additions

- With 45 independent true nulls at p < 0.05 the chance of a false positive somewhere reaches up to 90% (P = 1 - 0.95^n).
- Benjamini-Hochberg as he states it: sort the p values ascending, pick a false discovery rate q with m tests, find the largest p with p <= iq/m (i is its rank); it and all smaller p values are significant. The extraction's limits add that Bonferroni lowers power and BH does not remove the base rate problem ([[Bayes Rule and the Base Rate Fallacy]]).
- Cited cases: a survey of 1980s medical trials averaged 30 therapeutic comparisons each; 241 fMRI studies used 207 distinct method-and-correction combinations; and with no correction a dead Atlantic salmon showed a significant response (p = 0.001, an 81 mm3 cluster) among tens of thousands of voxels. Physicists call multiple comparisons the look-elsewhere effect.

## Other cited cases

- Practical Statistics for Data Scientists gives the 20-test figure with 20 random predictors against one random outcome (0.64, independence assumed), and cites Bayer fully replicating only 14 of 67 studies it tried. For predictive models it advises cross-validation and a holdout sample.
- Its sampling chapter's thought experiment: if 20,000 stadium attendees each toss a coin 10 times, someone almost surely (over 99%) lands 10 heads in a row, while for a single person the odds are 1 in 1,000. It calls this the vast search effect and guards against it with holdout sets and target shuffling.
- A Microsoft metric-pitfalls paper advises a Bonferroni correction when analysing segments of an experiment.

## ISLP chapter 13 on the Fund and Khan data

- On the first five Fund managers (n = 50 monthly excess returns each; raw p near 0.006 (One), 0.012 (Three), and 0.918, 0.601, 0.756 for the rest), Bonferroni at FWER 0.05 (threshold 0.01) rejects only Manager One, while Holm and BH at q = 0.05 reject Managers One and Three. ISLP says Holm should always be preferred to Bonferroni: it is uniformly more powerful and assumes no independence.
- For all pairwise comparisons it recommends Tukey (adjusting Managers One and Two from p = 0.038 to 0.186) and for post-hoc contrasts Scheffe, which needs alpha_S = 0.002 for the chosen contrast, so an unadjusted p = 0.004 is not rejected.
- Across the full set of 2,000 managers, BH controlling FDR at 10% rejects 146 nulls, whereas Bonferroni controlling FWER at 0.1 rejects nothing. It suggests about 10% FDR if follow-up is costly, about 30% if cheap.
- Plug-in permutation FDR (B = 10,000) on 2,308 Khan genes gives nearly the same curve as BH on theoretical p-values; the 500 smallest-p genes have FDR about 17.7%. Use a permutation null when small samples or skew break the theoretical one.
- For intervals on cases chosen by an FDR rule, see [[Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates]] (the BYq rule).

## Where multiplicity hides

Many metrics, many segments, many looks at a running experiment, and forking analysis choices all multiply the number of tests even when only one is reported. Declare the primary metric and analysis in advance.

## Birthday problem

23 people give a 0.507 chance of a shared birthday: pairs grow quadratically (253 pairs), so coincidences appear sooner than intuition says. The same arithmetic: 118 users in 10,000 hash buckets give a 0.5 chance of a collision. Many comparisons are always more than they look.

## Limits

Reinhart's chapter 4 arithmetic is illustrative, and the 1980s and 1992 survey figures come from endnotes not in the excerpt.

Bonferroni and Holm are valid whatever the dependence; BH wants independence or mild dependence among the p-values, and ISLP gives no proof. FWER power falls fast as the number of tests grows, though the simulation behind that is not specified. The permutation approach needs identical null distributions across groups, which is stronger than equal means. FDR levels have no standard value.

The Practical Statistics extraction flags that book's Bonferroni wording as wrong: alpha is divided by n observations in the text, when n should count tests.

## See Also
- [[P-Value Misreadings]] — prerequisite-for
- [[Winner's Curse]] — related (picking the best of many)
- [[Small-N Trap and Shrinkage]] — related (subgroups are small and many)
- [[Statistical Test Selection]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
- [[Peeking and Sequential Testing]] — related (repeated looks as multiple tests)
- [[Difference in Significance and Error Bar Overlap]] — related
- [[False-Discovery Rate, the Two-Groups Model and Local fdr]] — extends
- [[Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates]] — extends
- [[Dichotomising Continuous Variables]] — related (searching cutoffs is a hidden multiple test)
- [[Researcher Degrees of Freedom and Prespecification]] — extends
