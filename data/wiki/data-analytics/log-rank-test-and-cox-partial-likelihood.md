---
title: Log-Rank Test and Cox Partial Likelihood
tags: [data-analytics, applied-analyses, concept]
summary: Censored survival is summarised by life tables and Kaplan-Meier curves, compared across arms by summing observed-minus-expected deaths over periods, and regressed on covariates with a partial likelihood that leaves the baseline hazard unspecified.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch09-survival-analysis-em-algorithm.md
  - data/raw/papers/2026-11-08-islp-ch11-survival-analysis-censored-data.md
---

# Log-Rank Test and Cox Partial Likelihood

Efron and Hastie (*Computer Age Statistical Inference*, ch. 9) take life tables, Kaplan-Meier, the log-rank test and Cox regression in turn, each more computational and more conditional than the last. Censored times are known only to exceed the reported value; the chapter covers right censoring and left truncation.

## Life table and Kaplan-Meier

The hazard at age i is h_i = y_i / n_i, deaths over those at risk, and survival is the product of (1 - h_k). Setup: Table 9.1, a fictitious insurer whose deaths follow 2010 US male rates; the product of (1 - h) from age 30 up gives 0.506 for a 30-year-old surviving past 80 from one year of data. Kaplan-Meier is the same calculation with the time unit going to zero, and Greenwood's formula gives its standard deviation as S(j) times the square root of a sum, over earlier times k, of deaths y_k divided by n_k times (n_k minus y_k).

## Log-rank test

Each period gives a 2x2 table of arm against death, with nA and nB at risk in the two arms, nd deaths and ns survivors among the n at risk. If the hazards are equal, arm A's expected deaths are E = nA x nd / n, with hypergeometric variance V equal to the product nA nB nd ns over n squared times (n-1). The test adds the observed-minus-expected differences y_i - E_i over periods and divides by the square root of the summed variances to get Z. Adding the differences, instead of using each period's Z_i or Z_i^2, is what Efron and Hastie recommend for power against hazards that are consistently ordered.

Setup: NCOG head and neck trial, 51 patients in Arm A (chemotherapy) and 45 in Arm B (chemotherapy plus radiation), binned monthly over 47 months.
- Kaplan-Meier medians are 324 days for Arm B and 182 for Arm A, but the Greenwood intervals at single time points overlap too much to settle the comparison.
- Month 6 alone: Arm A was expected to lose 5.42 patients (variance 2.28) and lost 7.
- Across the 47 months the observed Arm A deaths total 42 against 32.9 expected, with total variance 16.0, so Z = 2.27 and the one-sided p is about 0.012.
- A cubic-linear spline logistic fit of the hazards, separately per arm, gives Arm B a hazard roughly 2.5 times below Arm A's after year one; the 95% limits do not overlap at months 15 and 30.

## Proportional hazards

The hazard of person i is h0(t) exp(c_i' beta) with the baseline h0 left open. The partial likelihood multiplies, over the observed deaths j, the dying person's exp(c_ij' beta) divided by the sum of exp(c_k' beta) across the risk set R_j (everyone still observed just before that death), and is then used like an ordinary likelihood.

Setup: pediatric cancer data, 1620 children of whom only 160 were observed to die; covariates age, entry date and distance from treatment centre (far) standardised to mean 0 and sd 1, with sex and race binary. Far has a hazard ratio of 1.34 per sd (confidence interval 1.17 to 1.55), a later entry date 0.63 per sd (0.54 to 0.74) and age 0.79 per sd (0.67 to 0.94). Race (1.33, p = .095) and sex (0.98, p = .887) show no clear effect. The authors suggest the falling hazard with later entry may reflect an improving protocol.

## Censored brain-tumour and publication data (ISLP ch. 11)

James and colleagues (*An Introduction to Statistical Learning with Python*, ch. 11) work the same tools on two datasets.

Setup: BrainCancer, 88 patients who had stereotactic radiotherapy for a primary brain tumour; 53 were alive at the end of the study. To estimate the chance of surviving past 20 months, the Kaplan-Meier estimate gives 71%. Two shortcuts miss it. Dividing the 48 patients known to exceed 20 months by all 88 gives about 55%, too low because 17 of the 40 who did not reach 20 months were censored, not dead. Dropping those censored before 20 months and dividing 48 by the remaining 71 gives about 68%, which is biased because censoring is informative here.

On the same data a log-rank test of female (45) against male (43) survival gives W = 1.2, a two-sided p of 0.2 from the theory and 0.25 from 1,000 permutations: no evidence of a difference. A Cox model on sex, diagnosis, tumour location, Karnofsky index, tumour volume and stereotactic method puts the male hazard at e^0.18, about 1.2 times the female, p = 0.61. Each extra Karnofsky point multiplies the hazard by about 0.95 (p = 0.0027). High-grade glioma carries roughly 8.6 times the hazard of meningioma (87 patients, one had no diagnosis recorded).

Setup: Publication, 244 NHLBI-funded trials, 156 published within the study period and the rest censored. A log-rank test of positive against negative trial result gives p = 0.36. The Cox model on seven covariates: posres, multi and clinend, then mech (14 levels), and finally sampsize, budget and impact gives a hazard ratio of e^0.55 = 1.74 for a positive result (z = 3.02): holding the other covariates fixed, a positive result raises the instantaneous chance of publication by a factor of 1.74. The authors' reading is that confounding hid the effect in the univariate test.

For prediction, the trials were split into equal training and test halves. A lasso-penalised Cox model, with the penalty chosen by cross-validated partial-likelihood deviance on the training half, kept two predictors, budget and impact. Harrell's C-index for a Cox fit on the training half, scored on the test half, is 0.733. Risk-score tertiles built from the training coefficients (budget and impact) split the test-half curves in the right order.

With one binary covariate and no ties the Cox score test for beta = 0 is the log-rank test.

## Limits

- ISLP ch. 11 develops only right censoring; left and interval censoring are named, not worked.
- ISLP ch. 11 assumes independent censoring, which cannot be checked from the data.
- Its check of proportional hazards is graphical only, and it names survival trees and random survival forests without working them.
- The log-rank test leaves out the counts lost to follow-up, which costs some power, usually little.
- Proportional-hazards inference is only as good as the model; the efficiency claim for partial likelihood needs it to hold.
- A life table can mislead badly when hazards drift over time.
- Formulas assume no ties. Left- and right-censoring together need more elaborate treatment.
- Greenwood's formula under censoring rests on successive conditional independence.

## See Also
- [[Survival Analysis for Customer Lifetimes]] — prerequisite-for
- [[Expectation-Maximisation for Gaussian Mixtures]] — related (the chapter derives EM from the same missing-data logic)
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
