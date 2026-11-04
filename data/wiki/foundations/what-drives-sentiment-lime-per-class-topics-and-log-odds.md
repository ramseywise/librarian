---
title: "What Drives Sentiment: LIME, Per-Class Topics and Log-Odds"
tags: [foundations, pattern]
summary: "A polarity score says how many are unhappy, not why; LIME explains single predictions, NMF per class names the themes, and class log-odds needs a minimum count or a prior because rare words have high variance."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--06-sentiment-analysis.md
---

# What Drives Sentiment: LIME, Per-Class Topics and Log-Odds

A score of 72% positive tells nobody what to fix. Three tools answer "why".

## LIME for one prediction

LIME drops words at random, watches how `predict_proba` changes, and fits a local linear model whose weights say which words pushed this prediction. It needs a model with probabilities. For a linear pipeline the global coefficients already explain the model ([[Linear Text Classifiers and the TF-IDF Baseline]]), so LIME earns its cost on nonlinear models. Limits: a linear explanation with thousands of active features is unreadable, a model highly non-linear around the prediction may have no faithful local explanation, and it uses random perturbations, so re-run with another seed before quoting a word's weight. Its published check recovered more than 90% of important words, but on sparse logistic regressions and trees limited to 10 features, so it is not evidence on black boxes. SHAP's text explainer is the more principled alternative.

## Topic models split by class

Split the corpus by label and fit NMF on each half ([[Topic Models and Extractive Summarisation]]). Negative-class topics are the complaint themes: bad acting, cheap special effects, disappointing book adaptations, "worst" and "horrible", waste of time and money. The positive side was comedy, series and generic praise. Check the tails: with an L1 penalty most weights go to zero and the sort returns ties arbitrarily, so a list can show only two real words. Check for zeros before reading a list to the end.

## Class-conditional log-odds instead of word clouds

Word clouds encode frequency as font size, which is hard to compare; with the stop list off, the largest words were "the", "a", "i". Prefer a sorted bar chart of counts or of class-conditional log-odds (which words are over-represented in one class). Log-odds has the opposite failure: rare words have high variance, so the most extreme words were names tied to a single film's reviews, a fact about that film, not about sentiment. Fixes: raise `min_df` (20 in the check), or shrink rare words toward zero with an informative prior (the "Fightin' Words" method). The result is a ranked list you can read and compare.

## Pitfalls
- Treating a sad plot as a bad review; lexicons score the plot's words.
- Reading LIME as ground truth.

## See Also
- [[Sentiment Analysis Methods and Failure Modes]] — prerequisite-for
- [[Small-N Trap and Shrinkage]] — related (shrink rare-word estimates toward zero)
- [[Topic Models and Extractive Summarisation]] — related
