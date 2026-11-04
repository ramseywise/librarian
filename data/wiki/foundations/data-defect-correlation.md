---
title: Data Defect Correlation
tags: [foundations, concept]
summary: "Error of a sample mean equals the correlation between being recorded and the value, times sqrt((1-f)/f), times the standard deviation, so a large self-selected sample can be worth a few hundred random rows while reporting a tiny standard error."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--03-distributions-and-sampling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# Data Defect Correlation

More rows reduce sampling error and do nothing for selection bias. A survey where buyers reply four times as often as non-buyers produced 57,152 responses with a mean spend of 11.06 against a true 3.12, while a simple random sample of 5,000 gave 3.00.

## The identity

Let R = 1 if a person is in your data, G the quantity averaged and f = n/N the sampling fraction. As an algebraic identity with no probability model:

```text
sample mean - population mean = rho(R, G) x sqrt((1 - f)/f) x sd(G)
                                data quality   data quantity   problem difficulty
```

rho(R, G) is the **data defect correlation**. A check at N = 10 million, f = 0.10, rho = 0.02 matched to 1e-14. The defect is small: responders with the trait replied at 10.9% against 9.6% without.

## Effective sample size

Under simple random sampling rho is about 1/sqrt(N). Equating errors gives an effective sample size of about f/(1-f) x 1/rho^2:

| f | rho | n | n_eff |
|---|---|---|---|
| 0.1 | 0.02 | ~1,000,000 | 278 |
| 0.1 | 0.005 | ~1,000,000 | 4,442 |
| 0.01 | 0.005 | ~100,000 | 404 |

A self-selected million rows had RMSE 0.0275, matching a random sample of 278 (RMSE 0.0276); but the random sample's interval covered the truth 95.3% of the time while the million-row interval covered it in 0 of 50 draws, because its reported SE was 0.00046 against a true error near 0.027. At fixed f and rho, scaling the population from 100,000 to 10 million leaves n_eff near 278 while the error in standard errors climbs from 3.8 to 57.8: more data makes the claim more confident and no more correct. An election-scale example: 1% of about 231.6 million voters with rho = 0.005 is 2.3 million responses worth about 404 random ones.

## Limits

- You usually cannot estimate rho from your sample, since everyone in it has R = 1; you need outside information or a benchmark with a known population value.
- The identity is about means and totals, not every estimate from big data.
- Weighting reduces the error a lot but does not remove the penalty when weights are imperfect, and reaches only the variables you weighted on.

Before admiring a large N, ask how the rows got in. The reported standard error describes sampling variation, not selection.

## See Also
- [[CLT on Heavy-Tailed Metrics]] — related (the theorem describes sampling error only)
- [[External Validity and Transportability]] — related (who got into the sample decides what generalises)
- [[Explain vs Predict Modelling]] — related (selection also distorts fit)
- [[Data Generating Process Simulation Check]] — related (simulate the selection mechanism)
