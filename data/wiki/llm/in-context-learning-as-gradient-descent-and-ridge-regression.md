---
title: In-Context Learning as Gradient Descent and Ridge Regression
tags: [llm, reasoning-and-planning, concept]
summary: "Akyürek et al. show by construction that a transformer can run a gradient-descent step or a ridge-regression update on in-context examples, and that small transformers trained on in-context linear regression behave like GD, ridge or OLS depending on depth and noise; synthetic linear models only (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-akyurek-2022-what-learning-algorithm-context-learning.md
---

# In-Context Learning as Gradient Descent and Ridge Regression

Akyürek, Schuurmans, Andreas et al. (ICLR 2023) examine whether transformer in-context learners secretly run a standard learning algorithm, holding a small model in their activations and updating it as examples arrive. The test bed is linear regression, not language.

## Method

The authors train small decoder-only transformers, initialised fresh, on sequences of (x, y) pairs with random w and random x, following the recipe of Garg et al. Their predictions are set against kNN, SGD, GD, ridge and OLS reference predictors using two measures: **squared prediction difference** (the mean squared gap between two algorithms' predictions for a new input) and **implicit linear weight difference** (the distance between the linear weights each predictor's outputs imply). The hidden states are also probed to test whether they encode X^T Y and w_OLS. The ridge reference is w_hat = (X^T X + (sigma^2/tau^2) I)^-1 X^T Y.

## Constructions

- Theorem 1: with a constant number of layers and O(d) hidden space, a transformer can compute a single gradient-descent update from one in-context example.
- Theorem 2: with a constant number of layers and O(d^2) hidden space, a transformer can apply a Sherman-Morrison ridge update.
- They show suitable weights exist, not that training finds them.

## Behavioural and probing results (self-reported)

- Noiseless, d=8 (L=16, H=512, M=4 decoder, up to 14 exemplars): predictions track OLS closely and the other references less so. With fewer exemplars than dimensions, the learner agrees with the minimum-norm OLS solution.
- With noisy labels, the ridge parameter that fits best follows the Bayes-optimal sigma^2/tau^2 over the noise and prior variances tried.
- Depth sets which algorithm the model resembles: one layer is nearest a single GD step, two to four layers nearest ridge, eight or more nearest OLS (noiseless, d=8 and d=16).
- The hidden size needed for ridge-like behaviour is much smaller than the O(d^2) of the construction. One attention head is enough for every dimension tried (d from 1 to 20), while layers and hidden size grow in steps as d grows.
- An MLP probe, not a linear one, recovers X^T Y and w_OLS from hidden states; X^T Y appears earlier (around layer 7) than w (around 12). A control with fixed w decodes much worse (d=4, 16-layer learner).
- The learner is not purely linear: the R^2 of a linear fit to it rises gradually through the under-determined regime.

## Limits

- Evidence covers synthetic Gaussian linear regression and freshly trained transformers only; no pretrained language model is tested, though the authors suggest the method could be applied to LLMs.
- The authors describe the probing as preliminary. The trained learners hold their targets in nonlinear form, which the constructions do not, so equivalence with GD or ridge is not established.
- No seeds or confidence intervals are given, and chosen hyperparameter values cannot be read from the cached text.
- The authors observe that ICL need not be risk-minimising: small models settle on GD-like or ridge-like solutions.

## See Also

- [[Implicit Weight-Patch Theory of In-Context Learning]] — related (another mechanistic account of in-context learning)
- [[GPT-3 and Few-Shot In-Context Learning]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
