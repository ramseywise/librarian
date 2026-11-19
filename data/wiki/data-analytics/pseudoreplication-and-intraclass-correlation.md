---
title: Pseudoreplication and Intraclass Correlation
tags: [data-analytics, probability-and-statistics, concept]
summary: "Rows from the same unit are correlated, so m rows per unit with intraclass correlation rho inflate the variance of a mean by 1+(m-1)rho; analysing at a finer level than the randomisation unit makes standard errors too small and null effects look significant."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--README.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch03-pseudoreplication-choose-data-wisely.md
---

# Pseudoreplication and Intraclass Correlation

The standard error s / sqrt(n) assumes independent rows. If a user contributes several rows, those rows resemble each other and the formula is too optimistic. With intraclass correlation rho between rows from the same user and m rows per user, variance inflates by 1 + (m - 1) rho.

## Numbers

- Five sessions per user with rho = 0.5: simulated true SE 0.0175 against naive 0.0100, so the naive SE was 1.75 times too small (formula sqrt(1 + 4 * 0.5) = 1.73). You have roughly a third of the information the row count suggests.
- Duplicating every row halves the variance without adding information, narrowing intervals by sqrt(2).
- A user-randomised test with 6 sessions per user and a true effect of zero, analysed at session level, called the effect significant 27.8% of the time at a nominal 5%; clustering on user brought it to 3.5%. More rows per user make the naive analysis worse, not better.

## Reinhart's examples (chapter 3)

- Blood pressure drug: 2,000 patients randomised (1,000 per group) against 10 patients measured 100 times each, which also yields 1,000 points per group from just 10 distinct patients; the sample size and power it seems to offer are not real.
- He critiques an early-1970s menstrual synchronisation study (McClintock, Nature) as pseudoreplicated: with cycles of 28 and about 30 days the starts drift apart by two days, then four, and out-of-step cycles slide in and out of line by luck, and the maximum gap between two 28-day cycles is 14 days, an average of seven, so periods of five to seven days often overlap by chance. He reports that later studies using corrected statistics found no sign of synchronisation, a conclusion he calls controversial.
- Corrections for dependence usually give wider intervals and larger p values. Other fixes he lists: average the points per subject (weighted if measured unequally often), analyse each time point separately (mind multiple comparisons), randomise treatments to blocks within each field, and split each biological group across microarray batches while recording batch details and checking with PCA.

## When it appears

In an A/B test it appears whenever you randomise by user and analyse by session. It applies equally to cells from one culture, fish in one aquarium, and sessions inside users.

## Fixes

- Aggregate to the randomisation unit, or
- keep rows but use [[Clustered Standard Errors]] at the level of randomisation, or
- bootstrap whole units ([[Bootstrap Resampling and Its Failures]]), or
- for ratio metrics use [[Delta Method for Ratio Metrics]].

If the group effect may be correlated with the predictor, standard-error fixes are not enough: see [[Panel Data Fixed Effects]].

## Limits

Chapter 3 has no data of its own and its endnote list is missing. Statistical fixes quantify dependence rather than remove it; poor design cannot be rescued.

## See Also
- [[Clustered Standard Errors]] — extends (the regression fix)
- [[Expectation and Variance Rules]] — prerequisite-for (variances add only for uncorrelated rows)
- [[Inspection Paradox in Metrics]] — related
- [[CLT on Heavy-Tailed Metrics]] — related (the central limit theorem also needs independence)
- [[Interference and Cluster-Randomised Experiments]] — related
- [[Partial Pooling and Multilevel Models]] — related
- [[Stratified and Cluster Survey Design]] — related
