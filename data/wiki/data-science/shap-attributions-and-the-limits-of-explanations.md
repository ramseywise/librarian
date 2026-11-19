---
title: "SHAP Attributions and the Limits of Explanations"
tags: [data-science, concept]
summary: "SHAP splits one prediction into a baseline plus per-feature log-odds that sum exactly; it explains the model, not the world, and studies show explanations help only for some tasks and people."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-huang-2023-can-large-language-models-explain.md
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--08-model-interpretability.md
  - data/raw/papers/2026-11-07-1901-07694v1.md
  - data/raw/papers/2026-11-07-lundberg-2017-unified-approach-interpreting-model-predictions.md
  - data/raw/papers/2026-11-07-ribeiro-2016-why-should-i-trust-you.md
  - data/raw/papers/2026-11-08-ribeiro-2016-why-should-i-trust-you.md
---

# SHAP Attributions and the Limits of Explanations

## What it is

Several local methods (LIME, DeepLIFT, layer-wise relevance, earlier Shapley-based ones) are additive feature attributions: each prediction is written as a baseline plus a single contribution per feature. Shapley values from cooperative game theory give the only such solution, given a rule for handling an absent feature, and meet local accuracy (baseline plus numbers equals the prediction), missingness and consistency (if a model relies on a feature more whatever the others, its number does not fall). Exact Shapley needs all feature subsets; a tree-specific explainer computes exact values in polynomial time, and the model-agnostic kernel version is exponential in the feature count M, so it suits small M and is approximated by sampling otherwise.

On the adult-census boosted model, base value plus the SHAP sum matched the raw score on all 2,000 rows (gap 0.0). One false positive (P = 0.543): base -2.387 + SHAP sum 2.559 = 0.172 log-odds, pushed up by education 0.828, relationship 0.753, marital status 0.653, occupation 0.452, age 0.347, down by no capital gain -0.253. A reviewer can then dispute it, for instance whether a 66-year-old works full time, which none of the features asked.

## Where the uniqueness claim comes from

Lundberg and Lee (NIPS 2017) call methods whose explanation is a baseline plus a sum over binary feature indicators additive feature attribution methods, and say six existing methods fit that form: LIME, DeepLIFT, layer-wise relevance propagation, plus the Shapley regression, Shapley sampling and quantitative input influence families. Their theorem says only Shapley values of a conditional expectation (SHAP values) meet local accuracy, missingness and consistency, so methods outside the Shapley family break local accuracy or consistency (self-reported). They also say LIME with its default loss, kernel and regulariser does not recover Shapley values (self-reported). Kernel SHAP is linear regression with a derived Shapley kernel; Deep SHAP adapts DeepLIFT; Max SHAP handles a max over M inputs in quadratic rather than exponential-times-M time (claim; the algorithm is in the supplement). With approximate conditional expectations, the kernel version costs O(2^M + M^3) (self-reported).

Evidence offered (self-reported, figures only, no numbers): on a decision tree Kernel SHAP estimated values from fewer model evaluations than Shapley sampling and LIME; in two Mechanical Turk studies (30 and 52 people) participants' own explanations matched SHAP more closely than LIME or the original DeepLIFT, without a significance test; and on an MNIST convnet SHAP changed log-odds more than LIME when 20% of pixels were masked. See [[LIME Local Surrogate Explanations and Submodular Pick]] for the baseline method.

## Global ranking differs from permutation

Mean absolute SHAP put age first at 0.827, then marital status 0.724, relationship 0.641 and capital gain 0.537. Capital gain is fourth here yet first by permutation, since it is zero for most people; SHAP averages the typical per-row shift and permutation shows what breaks when a column is scrambled. The junk ID column still got 0.065, since SHAP describes the model as fitted. Compare both rankings as a sanity check; see [[Tree Ensemble Interpretation Beyond Impurity Importance]].

## Caveats

- The uniqueness result holds for a fixed mapping from input to simplified input. The estimators assume feature independence and approximate the conditional expectation, the proofs sit in a supplement, and the authors' evaluation is qualitative.
- With correlated features credit splits in algorithm-dependent ways; the kernel version assumes feature independence when filling missing features.
- Values look causal and are not: a large value for marital status shows the model relies on it; it does not show that marriage raises income. A causal question needs a design (see [[Explain vs Predict Modelling]]).
- State the output space (log-odds or probability) and the background data when comparing.
- Where a person can demand reasons, a directly readable model may be the better answer.

## LIME

LIME fits a small linear model on perturbed copies of one input, weighted by closeness (mechanism and experiments: [[LIME Local Surrogate Explanations and Submodular Pick]]). Its experiments use text and images only, and a strongly non-linear neighbourhood may have no faithful local explanation. In a deliberately flawed image classifier (20 hand-picked training images), explanations moved subjects naming the spurious feature from 12 to 25 of 27 (small sample, no control group).

## Does explaining help?

Evidence on the human step is sobering. People want explanations that are contrastive, selected and causal, which a default bar chart is not. A perceived-fairness study (Dodge and colleagues, IUI 2019: 160 MTurk raters, six predictions each, a logistic regression on COMPAS data, four explanation styles) found local styles widened rating gaps more than global ones, with marginal significance (p = 0.07) and no decision outcomes measured. The extraction notes the study had no no-explanation control, and the three-way interaction the authors expected became significant only once individual-difference terms (race position, ML position) were added post hoc. A study of four explanation types on two tasks found that on the low-expertise task no type improved understanding, spotting uncertainty and calibrated trust all at once; feature contributions helped with more expertise and counterfactuals did not improve calibrated trust. Test an explanation on the person it is for, and evaluate decisions made with it, not satisfaction with it.

## When the model explains itself

A 2023 preprint (Huang and colleagues; no venue stated in the text) asked ChatGPT to rate how much each word of a movie-review sentence mattered to its own sentiment label, then compared those self-explanations with occlusion and LIME. The setup was narrow: 100 random sentences from the Stanford Sentiment Treebank, greedy decoding, an unspecified API version, and the confidence number the model writes standing in for a prediction score because there are no logits. Two orderings were tried, explanation before prediction (E-P) and prediction before explanation (P-E).

- Faithfulness was about level: comprehensiveness 0.19 for the self-explanation in E-P against 0.15 for occlusion and 0.17 for LIME (0.27, 0.20 and 0.27 in P-E). The authors report no clear winner.
- Agreement was low even so: rank correlation with occlusion and LIME was 0.07 to 0.13 in E-P and 0.06 to 0.21 in P-E.
- Cost differed sharply: LIME's default is 5,000 API calls per sentence (cut to an average 183 perturbations, around 20 minutes each), while the self-explanation comes with the answer.
- Asking for an explanation cost accuracy: 92% with the label alone, 88% for P-E and 85% for E-P.
- Self-attributions were coarse, averaging 2.72 distinct levels per sentence in E-P and 5.69 in P-E over 18.2 words. Occlusion scored exactly zero for 82.6% of words in E-P and 54.5% in P-E, which the authors say weakens the metrics.

Limits the authors state: sentiment and word attribution only, one model, no human study, no confidence intervals or repeated runs (so gaps of a few hundredths are within noise), and metrics that may not separate good explanations from bad.

## See Also
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — prerequisite-for
- [[LIME Local Surrogate Explanations and Submodular Pick]] — prerequisite-for
- [[Gradient Boosting Mechanics and Library Choice]] — related
- [[Weight-of-Evidence Logistic Scorecard]] — alternative-to
- [[Error Analysis by Confusion-Matrix Cell]] — related
- [[EK-FAC Influence Functions for LLMs]] — related (attributing outputs to training data rather than features)
- [[Lipton's Notions of Interpretability]] — prerequisite-for
