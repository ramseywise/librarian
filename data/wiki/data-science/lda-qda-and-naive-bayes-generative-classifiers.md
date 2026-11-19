---
title: LDA, QDA and Naive Bayes Generative Classifiers
tags: [data-science, concept]
summary: "LDA, QDA and naive Bayes model each class's predictors and apply Bayes' theorem to get a posterior; which of them, logistic regression or KNN wins depends on whether the true boundary is linear, quadratic or irregular, and on class balance."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-islp-ch04-classification.md
  - data/raw/papers/2026-11-08-islp-ch01-introduction.md
---

# LDA, QDA and Naive Bayes Generative Classifiers

ISLP's Chapter 4 contrasts two ways to predict a qualitative response. Logistic regression models the probability of the class directly; the generative classifiers below model the distribution of the predictors within each class and turn it around with Bayes' theorem into a **posterior probability** pk(x), the chance of class k given the predictors. The **Bayes classifier** sends each observation to its highest-posterior class and, with correctly specified terms, attains the smallest achievable error.

- **LDA** is the choice the authors give when data are few or the classes are well separated with roughly normal predictors; logistic regression is preferred when normality fails.
- **QDA** is advised when the training set is large or the class covariances clearly differ.
- **Naive Bayes** assumes the p predictors are independent within each class, fk(x) = fk1(x1) * ... * fkp(xp), and is advised when n is small relative to p. In a worked toy case with p = 3, two classes and equal priors, the point x* = (0.4, 1.5, 1) receives a class-1 posterior of 0.944.
- **KNN** suits a strongly non-linear boundary when n far exceeds p; features are standardised first because distance depends on scale, and K is chosen by cross-validation.

## Six simulated scenarios

Over 100 random training sets per scenario (p = 2, large test set), LDA and logistic regression won when the boundary was linear and QDA won with unequal covariances. Naive Bayes won only when independence held. KNN with K = 1 was worst when its smoothness assumption was wrong. No method dominated. The scenarios were: 20 per class uncorrelated; correlation -0.5; t-distributed with 50 per class; correlation +0.5 against -0.5 under normality; a logistic function of a non-linear term; and n = 6 per class with diagonal covariances. In a one-dimensional example (two Gaussians at -1.25 and 1.25, unit variance, equal priors, 20 training observations per class) the Bayes error was 10.6% against 11.1% for LDA; in a three-class two-dimensional example (20 per class, common covariance) it was 0.0746 against 0.0770.

## Thresholds and imbalance on Default

On the simulated Default data (10,000 individuals, 333 defaulters, about 3% default rate), LDA on balance and student status at the 0.5 threshold had a training error of 2.75% against 3.33% for the **null classifier** that always predicts no default. It caught 81 of 333 defaulters (sensitivity 24.3%, specificity 99.8%). Lowering the threshold to 0.2 brought the share of defaulters missed down from 75.7% to 41.4% and raised overall training error to 3.73% (235 non-defaulters flagged). Gaussian naive Bayes had slightly higher overall error than LDA at 0.5 but caught more defaulters (89 of 333), and at 0.2 caught 203 of 333, almost two-thirds. LDA's ROC AUC on these training data was 0.95 and logistic regression's ROC was almost the same. The authors advise judging a classifier against the null rate and the confusion matrix, not overall error, and choosing the threshold from domain costs.

On the Caravan data (5,822 individuals, 348 purchasers), logistic regression at 0.5 predicted nobody and at 0.25 predicted 29 purchasers with 31% correct (test set of 1,000). In ISLP's Smarket split (train 2001-2004, test the 252 days of 2005, Lag1 and Lag2) QDA reached 0.599 test accuracy against about 56% for LDA and logistic regression, naive Bayes about 59.5%, and KNN 50% at K = 1 and 53.2% at K = 3.

## Limits

- The Default confusion matrices use the 10,000 training observations, so errors are optimistic; the authors also note the data are simulated with an overstated link between balance and default.
- The scenario comparison is shown as boxplots, so the text gives rankings and no error numbers.
- The Smarket results are a single 252-day split; the authors advise a bigger test set before trusting QDA's 59.9%.
- LDA with a dummy predictor (student) violates normality, which the authors say it tolerates; Caravan KNN precision per K rests on 3 to 62 predicted purchasers.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Bayes Rule and the Base Rate Fallacy]] — prerequisite-for
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — related
