---
title: Generalised Linear Models and Deviance
tags: [data-analytics, probability-and-statistics, concept]
summary: "A GLM pairs a distribution with a link function and is fitted by maximum likelihood; deviance replaces the sum of squares for comparing models, while Pearson dispersion is the better check of the variance assumption."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch08-generalized-linear-models-regression-tre.md
  - data/raw/papers/2026-11-08-islp-ch04-classification.md
---

# Generalised Linear Models and Deviance

| Model | Outcome | Link | Coefficient reads as |
|---|---|---|---|
| Linear | continuous | identity | change in mean |
| Logistic | binary | logit | log odds ratio |
| Poisson | count | log | log rate ratio |
| Negative binomial | overdispersed count | log | log rate ratio |

The choice follows the outcome's distribution ([[Distribution Selection for Metrics]]).

## Deviance

Twice the log-likelihood gap between the fitted model and a **saturated** model (one parameter per row). Maximum likelihood is least total deviance as OLS is least squares. **Null deviance** is for an intercept-only model; **residual deviance** is for yours; the drop plays the explained sum of squares' role and for nested models is the likelihood-ratio statistic (chi-square, one df per added term).

Example: 5482.5 null against 5450.1 residual, a drop of 32.4 for one df, agreeing with the coefficient's z-test (p = 1.2e-8). Only about 0.6% of deviance went, as a small R-squared can accompany a clear effect.

## Check variance with Pearson, compare with deviance

Residual deviance per df was 1.09 where Pearson dispersion was 1.00 on truly Poisson data: with small counts deviance misleads about variance. Use Pearson dispersion for that check ([[Poisson Offsets and Overdispersion]]), deviance for comparing models.

## GLMs as exponential families

In *Computer Age Statistical Inference* (ch. 8) Efron and Hastie write a GLM as an exponential family whose N natural parameters are theta = X alpha, reducing N parameters to p. In the mean parametrisation, Hoeffding's lemma writes the density as f_y(y) times exp(-D(y, mu)/2), with D the deviance (twice the Kullback-Leibler distance, not symmetric), so maximising the likelihood minimises the total deviance. The likelihood is concave, and the estimate solves X'(y - mu(alpha)) = 0 numerically.

- Setup: bioassay, 11 dose groups of 10 mice, doses coded 1 to 11, logit = a0 + a1 x. The regression standard deviation of the fitted probability at dose 6 is .072 against .157 for that dose's own binomial estimate (the largest gap in their table), and the estimated LD50 is 5.69. The price is possible model bias.
- Setup: spam data, 4601 emails (40% spam), 57 predictors in an additive logistic model. The maximum likelihood fit is unstable (george: coefficient -39.62, se 7.12), and the book says this calls for shrinkage.
- Setup: 487 galaxies counted in a redshift-by-magnitude grid of 270 bins (18 by 15), Poisson GLM on r, m, r^2, rm and m^2. This turns density estimation into regression. The total deviance is 610 against about 270 expected if the model were right, a poor fit. Their rule of thumb: the sum of squared deviance residuals should be about the number of bins.

James and colleagues (*An Introduction to Statistical Learning with Python*, ch. 4) motivate the Poisson GLM with hourly bike-share counts (8,645 rows). Linear regression on month, hour, working day, temperature and weather gives negative fitted counts for 9.6% of rows, and the spread grows with the average: rainy winter nights at 1 to 4 am average 5.05 riders (sd 3.73), clear spring mornings at 7 to 10 am average 243.59 (sd 131.7). The authors fit a log-link Poisson model instead. Cloud cuts expected ridership to 0.923 of its clear-sky level (a coefficient of -0.08 on the log scale), and rain cuts it by a further factor of 0.607 (coefficient -0.5). See [[Poisson Offsets and Overdispersion]] for the overdispersion they flag.

## Limits

- The CASI ch. 8 fits are illustrations, and the spam logistic fit has no held-out accuracy.
- The 57-variable spam maximum likelihood fit is unstable; the book defers shrinkage to a later chapter.
- ISLP ch. 4: the Bikeshare Poisson fit is overdispersed, which inflates the z-values, and the authors leave this uncorrected.
- The source text lost some minus signs and Greek symbols, so equations in the CASI section should be checked against the book.

## See Also
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — instance-of
- [[Logistic Regression Separation]] — related
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Exponential Families and Tilting]] — prerequisite-for
- [[Model Selection Criteria]] — related
- [[Regression Splines, Smoothing Splines and GAMs]] — related
- [[Maximum Entropy Likelihoods and Link Functions]] — extends
- [[Ordered Logit and the Cumulative Link]] — extends
