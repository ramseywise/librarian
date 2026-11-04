---
title: "Regularisation Knobs and Early Stopping"
tags: [foundations, pattern]
summary: "Every family has a complexity-limiting knob whose validation curve peaks in the middle; early stopping is the same penalty in training time, but libraries may keep the rounds waited past the best."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
---

# Regularisation Knobs and Early Stopping

Regularisation is one idea: minimise training loss plus lambda times complexity. It works because signal repeats across rows and the data pays for it, while noise does not repeat, so a small price removes much of it (a little bias for more variance; see [[Bias-Variance Decomposition and Model Complexity]] and [[Regularisation as a Prior]]).

## Reading the training curves

Learning curves (AUC, 16,000 rows): a depth-2 tree underfits (train 0.834, validation 0.833: lines meet, both low, more rows will not help); an unlimited tree overfits (0.999 vs 0.760, gap 0.239, shrinking only from 0.299 with 64 times the rows); boosting is healthy (0.953 vs 0.927). A small gap says nothing about whether the model is good. See [[Learning Curves and Bias-Variance Diagnosis]]. Iteration curve: a boosting model set to overfit had train log-loss 0.0640 at round 300 while validation bottomed at 0.2900 at round 17 and rose to 0.4524.

## One knob per family (1,500 training rows, validation AUC)

| Knob | Weak | Best | Strong or extreme |
|---|---|---|---|
| Logistic L2 strength C | 0.001: 0.877 | 1: 0.902 | 1000: 0.891 |
| Tree max_depth | 1: 0.761 | 6: 0.879 | 24: 0.740 (train 0.999) |
| Tree min_samples_leaf | 1: 0.725 | 20: 0.877 | 200: 0.841 |
| Boosting learning rate | 0.003: 0.888 | 0.03: 0.908 | 1: 0.853 |
| Boosting subsample | 0.1: 0.815 | 1.0: 0.903 | (full rows best) |
| Network weight decay | 0: 0.860 | 10: 0.904 | 100: 0.500 |
| Network dropout | 0: 0.860 | 0.95: 0.900 | 0.98: 0.888 |

The shape repeats: too little capacity, a peak, then train rising while validation falls. L1 and L2 tied at best (0.901, 0.902) but L1 at C=1 kept 29 non-zero weights against 83 (see [[Penalised Linear Models: Ridge, Lasso and Elastic Net]]). Subsampling did not help on one seed, so a knob is a hypothesis until a validation curve agrees. Weight decay values look huge because AdamW multiplies by the learning rate each step; do not copy values between setups with different learning rates.

## Early stopping is regularisation

Gradient descent on a linear model starts at zero weights and grows them, so stopping early keeps them small. Weight norm and AUC: step 1,000 |w| 3.88, AUC 0.9013; step 100,000 |w| 13.18, AUC 0.8947; the L2 fit at C=1 had |w| 4.88, AUC 0.9016. Training time and penalty strength are two handles on one path.

**Patience** (rounds without improvement before giving up) exists because validation curves wobble (one published curve had 16 local minima before true overfitting); in published runs slower rules bought about 4% lower test error for about four times the training. Trap: with patience 5, 25, 100 a library stopped at 21, 41, 116 rounds though the best round was 16, and the as-fitted validation loss worsened 0.2960, 0.3083, 0.3561; cut back to the best round all gave 0.2918, against 0.8426 with no stopping. Check whether your library rolls back; keep the best weights. Rows that decide stopping cannot also give the final score; afterwards you may refit on train plus validation.

## See Also
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Gradient Boosting Mechanics and Library Choice]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Supervised Model Families and Complexity Knobs]] — related
