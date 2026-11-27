---
title: Least-Angle Regression and the Lasso Path
tags: [data-science, classical-ml, concept]
summary: "Forward stepwise, least-angle regression (LAR) and the lasso are three ways to grow a sparse model one variable at a time; LAR gives the lasso path exactly (with a drop step), and pathwise coordinate descent computes the generalised lasso along a lambda grid."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch16-sparse-modeling-lasso.md
---

# Least-Angle Regression and the Lasso Path

Efron and Hastie (Computer Age Statistical Inference, ch. 16) ask how to choose and shrink variables when regression data are wide, and how best-subset, forward-stepwise, the lasso and LAR relate. Best-subset search is prohibitive beyond p of about 40 because there are 2^p subsets.

## The pieces

- **Lasso:** minimise the mean squared error subject to the l1 norm of the coefficients being at most t, or equivalently with a penalty lambda times the l1 norm added to half the mean squared residual. Coordinate-wise it is soft thresholding: a coefficient is 0 if the unpenalised value is below lambda in magnitude, else shrunk toward 0 by lambda. The path over t is the homotopy path.
- **Least-angle regression (LAR):** a democratic form of forward stepwise. Move the active coefficients toward least squares while keeping their inner products with the residual tied, and stop when a new variable catches up. The LAR path coincides with the lasso path only with a drop-variable modification, with drops most likely among strongly correlated variables. Under technical conditions the lasso spends exactly one degree of freedom per LAR step, while forward stepwise spends more (estimated by the authors from 5000 simulated datasets drawn by parametric bootstrap).
- **Pathwise coordinate descent (glmnet):** fits the generalised lasso over a decreasing lambda grid. For squared error the smallest lambda that zeroes every coefficient is the largest absolute inner product of a column with y, divided by n; for logistic loss the authors use 100 lambdas log-spaced down to a small fraction (say 0.001) of that largest value. Speed comes from warm starts, active-set cycling and strong rules.
- **Elastic net and group lasso:** the elastic net mixes l2 and l1 penalties and is advised when predictors are highly correlated, since the lasso has difficulty choosing among them. The group lasso penalises the l2 norm of each group, selecting whole groups.

## Practice

The authors advise standardising predictors to variance one first (the l1 constraint treats coefficients equally), leaving the intercept unpenalised, and choosing the subset size or lambda by 10-fold cross-validation scored on the metric you care about, such as misclassification, even if fitting used squared error.

## Worked results (spam data)

Setup: spam data, 57 predictors, 3065 training and 1536 test emails (all reported as the chapter's own runs).

- Forward stepwise: the first variable explains R^2 = 0.16 and two variables 0.25 (response coded +1/-1). Linear and logistic stepwise reach their minimum test error after about 25 steps, logistic being more accurate; stepwise reaches the lasso logistic error using roughly half as many terms.
- With binarised variables and pairwise interactions (3061 predictors): best test error 0.057 for lasso logistic, 0.064 for forward-stepwise logistic and 0.071 for lasso logistic on main effects alone. Stepwise went to 134 variables before convergence problems, while the lasso's largest active set was 682.
- On the 3061-variable data glmnet produced the full lasso logistic path in 6 seconds (2015 hardware, unspecified), whereas forward stepwise was slow.

## Limits

- The chapter concentrates on prediction and gives inference little attention; post-selection inference is a brief survey and the HIV example (7 of 30 sites selected, one remaining after adjustment) is shown only as a figure.
- The spam timings reflect 2015 software and hardware that the chapter does not describe beyond the 6-second figure.
- The equations in the extraction lost minus signs, so the signs in the path equations are unconfirmed.

## See Also
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — related (choosing lambda)
- [[Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates]] — related (naive intervals after lasso selection)
- [[Regularisation as a Prior]] — related
