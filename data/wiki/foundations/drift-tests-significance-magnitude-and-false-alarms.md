---
title: "Drift Tests: Significance, Magnitude and False Alarms"
tags: [foundations, concept]
summary: "KS, chi-squared and PSI answer different questions: p-values go to zero on any shift at scale, PSI is noisy on small windows, and testing many features daily rings daily unless corrected; a domain classifier catches changes in feature relationships."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--04-drift.md
---

# Drift Tests: Significance, Magnitude and False Alarms

Three standard tests: the Kolmogorov-Smirnov (KS) test compares two numeric samples with no binning; chi-squared does the same for categories; [[Population Stability Index]] compares binned shares, `PSI = sum (c_i - r_i) ln(c_i / r_i)`, and returns a magnitude rather than a p-value. Bin edges come from the reference window.

## Scenarios (5,000 rows per window)

| Scenario | KS p | PSI | zone chi-squared p |
|---|---|---|---|
| no change | 0.3154 | 0.0063 | 0.9288 |
| miles to km | 0.0000 | 0.4300 | 0.9288 |
| mean distance +5% | 0.0003 | 0.0152 | 0.9288 |
| airport share up | 0.3154 | 0.0063 | 0.0000 |

Chi-squared catches the category shift numeric tests cannot see. On the 5% row KS calls it highly significant while PSI calls it barely there; both are right.

## Significant is not large

The same 5% shift, by window size: KS p falls from 4.30e-03 at n=200 to 8.07e-164 at n=500,000, while PSI settles near 0.004. On a busy model every feature is "significantly" different daily; report a magnitude. But small windows make PSI mostly noise: with no shift, the 95th percentile of PSI is 0.175 at n=200, 0.035 at n=1,000 and 0.006 at n=5,000. The 0.1 (watch) and 0.25 (act) thresholds are conventions with no traceable study; at 200 rows a null window can reach a level that would mean something at 5,000. Calibrate on pairs of historical windows where nothing went wrong and set the alarm above that distribution.

## Many features, many false alarms

With 100 features tested daily at alpha 0.05 and no drift, 200 of 200 days alarmed (theory 0.994). Bonferroni (reject only if the smallest p is below alpha/K) brought it to 10 of 200 days (theory 0.049). The price is power on small single-feature shifts; also restrict monitors to the features that carry the model. With windows of 50 rows the correction still held (3 alarm days of 200), but a real shift becomes much harder to catch.

## Relationship changes: the domain classifier

Per-feature tests miss a change in how features relate, the classic sign of a corrupted join: each column looks fine, rows no longer belong together. Two features with correlation 0.8 against 0.0 gave KS p of 0.888 and 0.610 (nothing). A **domain classifier** labels reference rows 0 and current rows 1, trains on half, and tests accuracy on the other half against chance with a binomial test: it scored 0.680 (p 4.0e-117), and 0.492 on two same-distribution windows, so its alarm is trustworthy. Its most confident rows show what changed.

## Which detector by default

A systematic comparison on image data (alpha 0.05, five random splits): aggregated univariate tests did about as well as multivariate ones; the best detector reduced inputs to the softmax outputs of the existing classifier and tested those, reaching detection accuracy 0.19, 0.47, 0.70, 0.79 at 10, 100, 1,000, 10,000 samples against 0.03, 0.36, 0.54, 0.72 without reduction. The domain classifier was weak below about 100 samples but useful for describing a detected shift. Small shifts were hard for all (14% detection at 100 samples, 54% at 10,000). These are image results and may not carry to tabular data; a practical default is to test predictions first, which needs no new infrastructure.

## See Also
- [[Population Stability Index]] — prerequisite-for
- [[Drift Triage: Broken Feeds, Benign Shifts and Concept Drift]] — extends
- [[Drift Types and What Monitors Can See]] — related
- [[Multiple Comparisons Corrections]] — related
- [[Sample Ratio Mismatch]] — related
