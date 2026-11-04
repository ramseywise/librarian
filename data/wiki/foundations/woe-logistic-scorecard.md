---
title: Weight-of-Evidence Logistic Scorecard
tags: [foundations, pattern]
summary: A credit scorecard bins each characteristic, converts bins to weight of evidence, fits a logistic regression, and prints the result as additive points; it matches gradient boosting within noise on small data while staying defensible line by line.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--02-credit-scoring.md
---

# Weight-of-Evidence Logistic Scorecard

The classic tool for ranking loan applicants, and a model a credit committee, an applicant and a regulator can all read.

## Weight of evidence and information value

For each class of a characteristic: WoE = ln(share of goods in class / share of bads in class). Positive means safer than average. Information value IV = sum over classes of (share of goods - share of bads) x WoE, one number for how well the characteristic separates goods from bads. Conventional reading: under 0.02 not predictive, 0.02-0.1 weak, 0.1-0.3 medium, above 0.3 strong; these are conventions, not theorems.

Why bother: each class gets its own effect on the log odds, so non-linear or unordered variables need no special care; each value is a known transformation; and WoE is the log likelihood ratio that Bayes' rule adds to the prior log odds (see [[Bayes Rule and the Base Rate Fallacy]]), so coefficients sit near 1 when characteristics are independent.

Implementation points:
- Learn bins and WoE on the training fold only: bins learned from the target are part of the model. Quintiles for continuous variables, pool levels under 5%, add 0.5 to each cell so an empty class cannot give an infinite weight, give unseen levels WoE 0.
- Hand-merge classes in production until points run in order. Automatic quintiles on 700 rows gave a non-monotone duration line (24-30 months scored 50, 15-24 months scored 43), almost certainly noise.

## Fit and sign check

Fit logistic regression on the WoE columns. With target "bad" and higher WoE safer, every coefficient should be negative. A positive one (here the job variable, IV 0.027) is usually collinearity; a card where better evidence loses points cannot be defended, so drop or re-bin it.

Protected characteristics (sex and marital status, age, foreign-worker status) are excluded as a decision, not a statistical finding. Dropping a column does not remove its proxies (housing, job), so a real deployment also tests outcomes across groups. Adding them back raised test Gini only from 0.480 to 0.492, inside the bootstrap interval.

## Ranking measures

- **Gini** = 2 x AUC - 1. **KS** = largest gap between cumulative score distributions of goods and bads. Both measure ranking only and are blind to the level of the probability (see [[Prior Shift Correction for Oversampled Defaults]]).
- On 1,000 real loans: train Gini 0.678 vs test 0.480, with a 95% bootstrap interval of 0.355 to 0.600 on 300 rows. A single split is one draw.
- Repeated 5-fold cross-validation (4 repeats), Gini mean/sd: WoE logistic 0.561/0.068, raw-code logistic 0.550/0.059, gradient boosting 0.570/0.066. Indistinguishable on this data; not a general result (with millions of rows and bureau features tree ensembles often win and explainability becomes a real trade-off).

## Points

score = offset + factor x ln(good:bad odds), factor = PDO / ln 2, where PDO is the points that double the odds. With 600 meaning odds 30:1 and PDO 20: factor 28.85, offset 501.86. A PD of 1/6 (odds 5:1) scores 548; one PDO more (568) gives odds 10:1. Per-characteristic points = -(coefficient x WoE + intercept/n) x factor + offset/n, so an applicant's score is the sum of one line per table.

## Pitfalls
- Fitting bins on all data; trusting automatic bins; reporting one Gini from one small split; wrong-sign coefficients; treating a scorecard as a capital model.
- Only approved loans are observed, so the model learns about approved applicants and is applied to all. Reject inference cannot supply outcomes that never existed.
- Validate a famous dataset against its documentation: a widely used German credit code table was wrong for decades, caught by checking a published cross-tabulation.

## See Also
- [[Prior Shift Correction for Oversampled Defaults]] — extends
- [[Population Stability Index]] — extends (monitoring after deployment)
- [[Basel IRB Capital Vocabulary]] — related
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Logistic Regression Separation]] — related
