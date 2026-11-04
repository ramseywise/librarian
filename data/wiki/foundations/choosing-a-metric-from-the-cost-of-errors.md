---
title: "Choosing a Metric From the Cost of Errors"
tags: [foundations, decision]
summary: "A loss rewards a specific answer (mean, median, quantile), MAPE rewards forecasting low, balanced accuracy hides a cost ratio of N:P, and MCC cannot respond to costs; pick the metric from the decision first."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--11-choosing-a-metric.md
---

# Choosing a Metric From the Cost of Errors

A loss is the fine paid in training, a metric the reported score, a baseline the cheapest alternative. Choose them together, from the decision, before reading scores (six metrics give six chances to find one the model wins).

## The loss decides what you estimate

Squared error rewards the mean, absolute error the median, pinball loss a chosen quantile. On a skewed lognormal target (100,000 draws), four constant forecasts each won the column built for them: mean 1.648 (RMSE 2.191), median 0.996 (MAE 1.125), 90th percentile 3.586 (pinball 0.477), best-for-MAPE 0.367 (MAPE 0.684). A shop where a stock-out costs nine times an overstock is a 90th-percentile decision. The implication runs one way: squared error implies the mean, but other losses (Bregman) also reward it.

**MAPE rewards forecasting low**: its favourite forecast sat far under the median and about 84% of outcomes were above it, because percentage error is largest at small actuals and an overforecast is unbounded while an underforecast cannot exceed 100%. A team judged on MAPE is paid to underforecast.

## The map

| Target | Loss | Metrics | Baseline |
|---|---|---|---|
| Continuous | Squared or absolute error | RMSE, MAE, out-of-sample R-squared | Predict the mean |
| Binary | Log loss | PR-AUC, ROC-AUC, Brier, MCC, balanced accuracy, cost at a threshold | Base rate |
| Count | Poisson deviance | Deviance, dispersion, MAE | Constant rate |
| Ranking | Pairwise or listwise | NDCG, MRR, recall at k | Popularity |
| Clusters | Inertia or none | Silhouette, ARI | Shuffled-column control |
| Forecast | Squared error, pinball | MASE, pinball | Seasonal naive |

A metric without a baseline cannot be read. Training loss and metric needn't match, but the metric must match the decision and the loss must estimate something the metric uses (log loss gives the probabilities a threshold needs). Count rows: Poisson deviance 1.968 against 2.672 for a constant rate (D-squared 0.263), dispersion 2.01 meaning standard errors would be too small, hence the negative binomial ([[Generalised Linear Models and Deviance]]).

## Binary metrics on a 3% default book (test 4,818 rows, 145 defaulters)

Accuracy ranked approve-everyone above a depth-2 tree on 10 of 10 seeds though the tree cost less on nine; balanced accuracy, MCC, PR-AUC ranked the tree higher on all ten. Averaged over seeds, boosting and the shallow tree tied on cost (141.5 and 141.4 per 1,000) and MCC, while boosting led PR-AUC (0.143 against 0.102): PR-AUC grades the ordering over all thresholds, cost grades this one. If the threshold is settled cost decides; if it will move, ordering matters.

Tuning the threshold on each metric (boosted, cost per 1,000 at 5:1 and 20:1; approve-all 150.5 and 601.910): accuracy declines nobody (150.5, 601.910); balanced accuracy declines 27% (303.030, 471.150); MCC 150.062, 467.621; cost-tuned 148.817 (5:1) and 428.186 (20:1, tuned for it).

- **Balanced accuracy is a cost ratio.** It equals 1 - (FN/P + FP/N)/2, so maximising it minimises N x FN + P x FP, a cost ratio N:P (32:1 here), changing with the base rate.
- **MCC has no cost term**, so picks the same threshold at both ratios; useful to check a thresholded classifier is not a trick when nobody can supply costs. It is not a guarantee: 0.65 occurred with recall 0.45 and zero false alarms; one case had accuracy 0.900, recall 0.989, MCC -0.032; and it halved (0.326 to 0.144) for the same model between a 22.1% and 3% base rate. It is undefined when a table row or column is empty.
- **ROC steady, PR moves.** Same model, 22.1% vs 3%: ROC-AUC 0.766 vs 0.779, PR-AUC 0.535 vs 0.167, balanced accuracy 0.694 vs 0.700. Read PR-AUC against its baseline (the base rate). If the deployed base rate differs from test, ROC and balanced accuracy describe the model, PR-AUC what users will see ([[Precision-Recall vs ROC and Average Precision]]). With 1,000 positives and 10,000 negatives the same ROC point can hide precision of 25% against 75%.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Precision-Recall vs ROC and Average Precision]] — related
- [[Imbalance Remedies Versus a Tuned Threshold]] — related
- [[Rare-Class Benchmark Quotas and Reweighting]] — related
- [[Ranking Metrics as the Confusion Table Along a List]] — related
- [[Bayes Action and Loss Functions]] — prerequisite-for
