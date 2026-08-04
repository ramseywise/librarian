---
title: LightGBM vs CatBoost Comparison
tags: [eval, comparison]
summary: Methodology for comparing calibrated GBM rerankers head-to-head — fixing train/inference feature-distribution mismatch before comparing, native categorical handling, and Brier score/log-loss as the metrics that matter for calibrated probability scores.
updated: 2026-08-04
sources:
  - raw/claude-docs/listen-wiseer/docs/plans/phase3c_add_catboost.md
---

# LightGBM vs CatBoost Comparison

A reusable methodology for evaluating a second gradient-boosted-tree estimator as a
drop-in alternative to an existing calibrated reranker, surfaced while adding CatBoost
as an alternative to a LightGBM per-playlist reranker in [[Listen-Wiseer Project]].

## Fix the train/inference mismatch first

Before comparing two estimators, check whether every feature the model sees at
inference is populated identically at training time. In this case two engineered
features — `cluster_prob` (max GMM soft-cluster probability) and `similarity_score`
(cosine similarity to the playlist centroid) — were **zeroed out during training**
(`lit(0.0)` placeholders) but carried real, informative values at inference. A model
cannot learn to weight a feature it never saw vary. The fix: compute the same
real values at train time using the identical logic the inference path uses
(`gmm.predict_proba(row)` for cluster_prob; standard cosine against the full positive-
track centroid for similarity_score — no leave-one-out complexity needed once 20+
tracks contribute to the centroid). **Any estimator comparison run before this fix is
invalid** — both models would be comparing against a training distribution that
doesn't match production.

## Native categorical handling vs one-hot

CatBoost accepts categorical columns natively via a `cat_features` parameter (ordered
target statistics internally) rather than requiring one-hot encoding. This makes it
straightforward to add genuinely categorical signals (`decade` — 8 buckets; `gen_4` —
4 genre buckets) that a one-hot-only pipeline (LightGBM's default path here) would
need encoded separately. Keep both feature-encoding paths behind one config flag
(`model_type: Literal["lightgbm", "catboost"]`) so the comparison is apples-to-apples
on the same underlying feature set, not just the same numeric subset.

## Brier score + log-loss, not just AUC

When the model's output is used as a **calibrated probability that becomes a rerank
score** (not just a binary decision), accuracy/AUC undersell what matters: how
well-calibrated the probability is. Add `sklearn.metrics.brier_score_loss` and
`sklearn.metrics.log_loss` alongside existing metrics — these are the metrics that
actually reflect reranking quality, since a miscalibrated-but-well-ranked model still
produces unusable absolute scores.

## `--compare` CLI pattern

Rather than a one-off comparison script, wire a `--compare` flag into the existing
training CLI: for each group (here, each of 32 per-playlist classifiers), train both
estimators on the identical train/test split, log metrics side-by-side, then
aggregate (mean Brier, mean log-loss, win counts per model) at the end. Default
behavior (no flag) is unchanged — trains the original estimator only. This keeps the
comparison harness a first-class, re-runnable part of the training pipeline rather
than a throwaway notebook cell — the actual EDA notebook (`06_model_comparison.ipynb`)
consumes the same per-playlist metrics JSONL files the CLI produces.

## See Also
- [[Listen-Wiseer Project]]
- [[Track2Vec Playlist Co-Occurrence Embeddings]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[Data Science Curriculum Layers]] — part-of (the Layer 5 ensemble-methods gap this fills)
