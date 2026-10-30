---
title: ML Foundations Interview Study Guide
tags: [interview, foundations, reference]
summary: Exam-prep reference for the classical ML round — bias/variance and leakage discipline, the model menu with reasons, metric choice tied to the decision the system drives, deep-learning basics via the structuring-ML-projects habits, unsupervised/embeddings, ML system hygiene, and the SQL/analytics screen.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--1-foundations--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--1-foundations--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--1-foundations--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--foundations.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--ml-foundations.md
  - data/raw/repos/sisyphus/interviewing--guides--1-foundations--00-overview.md
  - data/raw/repos/sisyphus/interviewing--notes--foundations.md
---

# ML Foundations Interview Study Guide

The classical round still opens most MLE and DS loops, and AI-engineer loops sanity-check
it. The bar is **fluency on trade-offs and metrics, not derivations**.

## Supervised learning core

- **Bias–variance** — diagnose with learning curves; remedies are regularisation (L1 gives
  sparsity, L2 shrinks), early stopping, more data, a simpler model.
- **Leakage is the number-one practical sin.** Fit scalers and encoders on train only, split
  *before* any target-aware transform, use time-based splits for temporal data, and wrap
  preprocessing and model in one pipeline so leakage is structurally impossible. The full
  failure catalogue is [[Tabular ML Leakage Taxonomy]].
- **Model menu with reasons:** linear/logistic (baseline, interpretable, roughly
  calibrated); random forest (robust default); gradient boosting (tabular state of the art,
  native categorical handling — see [[LightGBM vs CatBoost Comparison]]); SVM (small clean
  data); kNN (lazy baseline); neural nets (unstructured data).
- **Always name the naive baseline first** (majority class, mean predictor). An improvement
  means nothing until it is measured against it.
- **Class imbalance:** resampling, class weights, threshold moving — and never report
  accuracy alone.

## Metrics: the metric follows the decision

The answer shape interviewers want is *metric ← the decision the system drives*: "AUROC over
accuracy because we rank-order for a capacity-limited intervention."

- Classification: precision vs recall framed as a business cost asymmetry; F1; **PR-AUC
  beats ROC-AUC under heavy imbalance**; calibration (Brier score, reliability curves) when
  probabilities feed a downstream decision; precision@K for ranking-ish work.
- Regression: MAE vs RMSE (outlier sensitivity); MAPE blows up near zero; R².
- Clustering: silhouette and stability across seeds.

## Deep learning basics

Backprop intuition; vanishing/exploding gradients (initialisation, normalisation layers,
residuals); SGD → momentum → Adam, LR schedules, batch-size effects;
[[Batch Normalization]] and its caveats; dropout; CNN locality and weight sharing; RNN →
transformer for sequences. The **structuring-ML-projects** material is the most
interview-useful part of the deep-learning curriculum: orthogonalisation, a single-number
eval metric, human-level performance as a Bayes-error proxy, error analysis by slicing. Its
case-study quizzes are practice case interviews.

## Unsupervised and embeddings

k is a modelling choice in k-means, and the honest answer to "how do you pick K?" is that it
encodes a product decision (how many segments can operations act on), with elbow and
silhouette as supporting evidence. GMM gives soft assignments. PCA preserves linear variance;
UMAP preserves neighbourhoods and is for *looking*, not for downstream features without care.
Word2vec's predict-your-neighbours trick generalises anywhere co-occurrence exists — see
[[Track2Vec Playlist Co-Occurrence Embeddings]].

## ML system hygiene

Reproducibility (seeds, pinned configs, logged params — the bar in
[[ML Run Reproducibility Bar]]); hidden technical debt (entanglement, feedback loops,
pipeline jungles); train/serve skew; covariate vs concept drift with retrain triggers;
feature importance vs SHAP/LIME local explanations, and when interpretability outranks
accuracy (healthcare, credit).

## SQL and analytics screen

GROUP BY + HAVING, LEFT vs INNER row-count reasoning, CASE bucketing, date truncation,
window functions, CTEs over nested subqueries, and the dedup-latest-row idiom. Analytics
judgment: **define the metric before writing the query.** Detail in
[[Programming Interview Study Guide]].

## Question bank (answer sketches)

- *"Great offline, poor in production."* — check in order: leakage, train/serve skew, drift,
  survivorship in training data, feedback loops, eval metric ≠ business metric.
- *"Explain regularisation to a stakeholder."* — a penalty on complexity, so the model must
  earn every parameter; L1 also selects features.
- *"Why gradient boosting over a neural net for tabular?"* — sample efficiency, native
  missing/categorical handling, less tuning, interpretability tooling; neural nets win with
  huge data or mixed modalities.

## See Also
- [[Tabular ML Leakage Taxonomy]] — extends (the leakage failure classes in depth)
- [[Data Science Curriculum Layers]] — prerequisite-for (the curriculum this guide compresses)
- [[Data Engineering and MLOps Interview Study Guide]] — extends (hygiene → production)
- [[Programming Interview Study Guide]] — related (the SQL screen)
- [[LLM Fundamentals Interview Study Guide]] — extends (sequence models → transformers)
