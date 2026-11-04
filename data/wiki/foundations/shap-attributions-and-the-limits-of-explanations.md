---
title: "SHAP Attributions and the Limits of Explanations"
tags: [foundations, concept]
summary: "SHAP splits one prediction into a baseline plus per-feature log-odds that sum exactly; it explains the model, not the world, and studies show explanations help only for some tasks and people."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--08-model-interpretability.md
---

# SHAP Attributions and the Limits of Explanations

## What it is

Several local methods (LIME, DeepLIFT, layer-wise relevance, earlier Shapley-based ones) are additive feature attributions: a prediction explained as a baseline plus one number per feature. The Shapley values of cooperative game theory are the unique such solution, once you fix how an absent feature is treated, satisfying local accuracy (baseline plus numbers equals the prediction), missingness and consistency (if a model relies on a feature more whatever the others, its number does not fall). Exact Shapley needs all feature subsets; a tree-specific explainer computes exact values in polynomial time, and a model-agnostic kernel version costs O(2^M + M^3) for M features, so it is practical for small M and sampled in practice.

On the adult-census boosted model, base value plus the SHAP sum matched the raw score on all 2,000 rows (gap 0.0). One false positive (P = 0.543): base -2.387 + SHAP sum 2.559 = 0.172 log-odds, pushed up by education 0.828, relationship 0.753, marital status 0.653, occupation 0.452, age 0.347, down by no capital gain -0.253. That gives a reviewer something to argue with (whether a 66-year-old works full time is a question the features never asked).

## Global ranking differs from permutation

Mean absolute SHAP ranked age 0.827, marital status 0.724, relationship 0.641, capital gain 0.537 (fourth, though first by permutation, because it is zero for most people: SHAP measures typical movement per row, permutation measures what breaks the ranking). The junk ID column still got 0.065, since SHAP describes the model as fitted. Compare both rankings as a sanity check; see [[Tree Ensemble Interpretation Beyond Impurity Importance]].

## Caveats

- With correlated features credit splits in algorithm-dependent ways; the kernel version assumes feature independence when filling missing features.
- Values look causal and are not: a large value for marital status says the model uses it, not that marriage raises income. A causal question needs a design (see [[Explain vs Predict Modelling]]).
- State the output space (log-odds or probability) and the background data when comparing.
- Where a person can demand reasons, a directly readable model may be the better answer.

## LIME

LIME fits a small linear model on perturbed copies of one input, weighted by closeness. Its experiments use text and images only, and a strongly non-linear neighbourhood may have no faithful local explanation. In a deliberately flawed image classifier (20 hand-picked training images), explanations moved subjects naming the spurious feature from 12 to 25 of 27 (small sample, no control group).

## Does explaining help?

Evidence on the human step is sobering. People want explanations that are contrastive, selected and causal, which a default bar chart is not. A perceived-fairness study (160 raters, six predictions) found local styles widened rating gaps more than global ones, with marginal significance (p = 0.07) and no decision outcomes measured. A study of four explanation types on two tasks found none reliably improved understanding, uncertainty recognition and calibrated trust together on the low-expertise task; feature contributions helped with more expertise and counterfactuals did not improve calibrated trust. Test an explanation on the person it is for, and evaluate decisions made with it, not satisfaction with it.

## See Also
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — prerequisite-for
- [[Gradient Boosting Mechanics and Library Choice]] — related
- [[Weight-of-Evidence Logistic Scorecard]] — alternative-to
- [[Error Analysis by Confusion-Matrix Cell]] — related
