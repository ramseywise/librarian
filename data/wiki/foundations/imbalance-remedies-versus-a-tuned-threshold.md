---
title: "Imbalance Remedies Versus a Tuned Threshold"
tags: [foundations, comparison]
summary: "On a 3% default book no resampling remedy beat leaving the data alone and setting the threshold from the cost ratio, and every balancing method wrecked the probabilities until recalibrated."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--10-imbalance-errors-and-drift.md
---

# Imbalance Remedies Versus a Tuned Threshold

Setting: a public card-default dataset (22.1% default) thinned to 3% defaulters by discarding defaulters only, so the base rate changes and nothing else; 24,087 rows, train 14,452 (434 defaulters), validation 4,817 (144), test 4,818 (145). Rates belong to that thinned population. Costs per 1,000 applicants in units of one lost customer.

## Accuracy lies, errors cost

Always-approve scores 0.97 accuracy and catches nothing; a boosted model at 0.5 also caught 0.0 of defaulters. With H0 "applicant is good", declining a good customer is Type I (quiet lost margin), approving a defaulter Type II (loud credit loss). The cost-minimising rule declines when P(default) is at least cost of a lost customer over the sum of both costs: 1/6 at 5:1 and 1/21 at 20:1, valid only for calibrated probabilities ([[Calibrated Score, Deterministic Decision Rule]]). Lowering the threshold trades beta for alpha: at 0.05 the lender caught 45% of defaulters but alpha rose 1.5% to 9.7% and cost rose (89,165 to 105,479 on the money scale used there).

## Count events, not rows

The same 20% cut needs 1,284 per arm at a 22% rate (about 282 defaults) and 11,452 per arm at 3% (about 343 defaults; simulated power 0.809); 1.0% vs 0.8% needs 34,999 per arm. The SD of test ROC-AUC is 0.090 with 10 defaulters, 0.039 with 50, 0.018 with 200, more than most gaps between methods. Good customers saturate early: 434 defaulters plus 434 good customers gave ROC-AUC 0.759 against 0.762 with all 14,018; all good customers with 25 defaulters gave 0.676. With no defaults in 1,000 approved loans the rule of three bounds the true rate at 0.3%.

## Remedies compared (20 paired seeds, boosted)

Nothing, class weights, random under- and oversampling, SMOTE (interpolate toward one of 5 nearest minority neighbours; needs scaled features), plus threshold moving, which cannot change ROC-AUC, PR-AUC or Brier. Results:
- Discrimination: no method beat nothing (PR-AUC 0.142, ROC-AUC 0.760). SMOTE 1:1 was 0.022 lower on ROC-AUC (SD 0.018, lower on 18 of 20 seeds); SMOTE for coded columns tied it at 0.738.
- Brier: every balanced method 0.122 to 0.188 against 0.028, on all 20 seeds.
- Cost with a tuned threshold at 5:1: 142.4 to 144.5, below the seed SD of 5.9. The untouched model with the 1/6 formula cost 142.9 (1/21 at 20:1: 420.2) against 143.0 and 419.8 tuned.
- At 0.5, a 1:1 training set moves the effective cut to about the base rate (0.03 before resampling, a 32:1 ratio): 298 for undersampling at 5:1 against 150 for nothing, but 433 against 599 at 20:1. Resampling at 0.5 is threshold moving with an unstated cost ratio.
- Prize is modest: 143.0 against 150.5 approve-all at 5:1 (5%), 419.8 against 601.9 at 20:1 (30%).

SMOTE at 0.5 lost to the tuned threshold beyond noise in 8 of 10 learner/rate/ratio rows and never won; with its own tuned threshold it was within noise in all 10 but worse on average in 9 (a tie leaning one way). A small neural net did worse with SMOTE (ROC-AUC 0.683 against 0.742, lower on all 10 seeds). A 73-dataset study found balancing and threshold tuning comparable except for weak learners; another found imbalance "not a problem in itself" for logistic models. One original SMOTE study favoured it, ranking by ROC area without examining probabilities; rerun here its recipe on a tree was 0.0175 lower than plain undersampling. Conclusion: on this data tune the threshold and leave the data alone.

## Probabilities after balancing

SMOTE as trained gave mean PD 0.272 (0.305 over seeds) on a 3.0% book, calibration intercept -2.93, and approved 20.6% predicting 11.3% default where about 1.0% occurred; cost at 1/6 was 777 against 143. Repairs fitted on untouched validation data: Platt scaling or intercept recalibration restore mean PD to 0.030 and Brier to 0.028 for every method (see [[Probability Calibration and Reliability Curves]]); isotonic left slopes near 0.8 with only 144 defaulters. Prior-shift correction ([[Prior Shift Correction for Oversampled Defaults]]) is right for undersampling (intercept -0.036) but leaves +0.23 and +0.27 for class weights and oversampling and +0.545 (mean PD 1.8%) for SMOTE, which moves the boundary, not only the prior. After repair every method matches doing nothing, so resampling plus repair cancels out.

## See Also
- [[Resampling Before the Split Leaks]] — related
- [[Drift Types and What Monitors Can See]] — related
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Precision-Recall vs ROC and Average Precision]] — related
- [[Choosing a Metric From the Cost of Errors]] — related
