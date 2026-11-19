---
title: "Regularisation Knobs and Early Stopping"
tags: [data-science, pattern]
summary: "Every family has a complexity-limiting knob whose validation curve peaks in the middle; early stopping is the same penalty in training time, but libraries may keep the rounds waited past the best."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--09-training-and-tuning.md
  - data/raw/papers/2026-11-08-prechelt-1998-early-stopping-but-when.md
  - data/raw/papers/2026-11-08-liu-2023-dropout-reduces-underfitting.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch02-training-feed-forward-neural-networks.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch05-convolutional-neural-networks.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch18-neural-networks-deep-learning.md
  - data/raw/papers/2026-11-08-islp-ch10-deep-learning.md
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

Prechelt's three families of stopping rule (generalisation loss, progress quotient, successive increases) and his 1296-run comparison are on [[Prechelt's Stopping Criteria: GL, PQ and UP]].

Dropout can also be scheduled: Liu et al. report that, for ViT-T/16 on ImageNet-1K (basic recipe, 300 epochs), switching it on only for early epochs raised accuracy over no dropout while standard dropout at 0.1 lowered it (self-reported) (see [[Early and Late Dropout]]).

## Overfitting controls in a 2017-era textbook

*Fundamentals of Deep Learning* chapter 2 treats overfitting with four tools, using ConvNetJS toy visualisations (two inputs, softmax of two, mini-batch size 10).

- **L2 / weight decay** adds 1/2 lambda w^2 per weight, so weights decay linearly toward zero in the update. The figures show lambda of 0.01, 0.1 and 1 on a 20-neuron hidden layer.
- **L1** adds lambda |w| and drives weights sparse. The authors advise L2 unless feature selection or interpretability is wanted, and say L2 empirically performs better (unsupported there).
- **Max norm** projects a neuron's incoming weight vector back to a ball of radius c when its norm exceeds c; the chapter gives 3 or 4 as typical c.
- **Dropout** keeps a neuron with probability p and zeroes it otherwise during training. Inverted dropout rescales the surviving activations by 1/p during training, which removes any scaling at test time. The chapter's p is a keep probability, the opposite of PyTorch's drop-probability convention.

Its procedure: split data into training, validation and test sets; divide training into epochs (an epoch is d/b updates for d examples and batch size b); halt when validation accuracy plateaus while training accuracy keeps rising; pick hyperparameters by grid search against the validation set and quote the test accuracy a single time (illustrative grid: learning rate 0.001, 0.01, 0.1 and batch size 16, 64, 128). The authors' diagnosis: a stalled training error calls for a rethink of architecture or features, a stalled validation error for more regularisation, and a poor test error for more data.

Chapter 5 of the same book uses dropout at 0.5 in the fully connected layer (1 at evaluation), and its batch-norm example drops dropout and L2 (see [[Batch Normalization]]).

## Dropout as a ridge penalty, and regularised networks against linear baselines

For a linear model with squared error, Efron and Hastie (Computer Age Statistical Inference, chapter 18, citing Wager et al.) show that the expected score equations under dropout match a generalised ridge regression, and that adding iid noise to the inputs behaves roughly like ordinary ridge. The extraction tags this a claim, after Wager et al. 2013. Details: [[Dropout and Input Distortion as Ridge Regression]].

*An Introduction to Statistical Learning with Python* (ISLP, chapter 10) pairs regularised networks with penalised linear baselines. Setups are stated where they matter:

- **MNIST** (60,000 training and 10,000 test images; a ReLU net with hidden layers of 256 and 128 units): the dropout net reaches 1.8% test error, a ridge-penalised version 2.3%, multinomial logistic regression 7.2% and LDA 12.7%. The book's own PyTorch lab (30 epochs, batch 256, dropout 0.4 and 0.3) gets 96.81% accuracy, so about 3.2% error, against 92.41% for logistic regression.
- **Hitters salary** (263 players, 176 train, 87 test): linear regression, lasso and a 64-unit net with 10% dropout reach test MAE 254.7, 252.3 and 257.4. A lasso-then-least-squares refit on four variables wins at 224.8. In the lab, a 50-unit net with dropout 0.4 gets 229.5 against 259.7 for least squares and 257.2 for lasso.
- **IMDb sentiment** (bag of 10,000 words): lasso logistic regression and a 2x16 ReLU net both score about 88% in the text; in the lab the net scores 85.5%.
- **Double descent**: in a simulated spline fit with n=20, test error peaks where the number of parameters equals n and falls again beyond it. The authors say ridge-penalised fits never interpolate, show no such peak, and give lower test error, and advise regularising or early stopping instead of relying on double descent.
- **Practice**: early-stop on a validation set, never on test data.

## Limits

- Chapter 2 is conceptual: no experiments or benchmark numbers, only toy figures.
- The early-stopping description is informal, and 'L2 performs better than L1' is unsupported.
- The extraction notes that random search has superseded grid search in common practice, which the chapter does not say.
- The CASI chapter's own limits: single runs, a heavily reused test set, and equations that lost their minus signs in extraction.
- The ISLP Hitters comparison is a single split (87 test points) with no repeats, and its lab used the test set as validation. Text and lab figures disagree (MNIST 1.8% against 3.2%, Hitters 257.4 against 229.5), and the authors say they spent effort tuning the net. Tree-based models and boosting are not compared, and the 2020 state-of-the-art figures are dated.
- Learning-rate schedules, adaptive rates, initialisation and batch norm are deferred to later chapters.

## See Also
- [[Prechelt's Stopping Criteria: GL, PQ and UP]] — extends
- [[Early and Late Dropout]] — extends
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Gradient Boosting Mechanics and Library Choice]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Supervised Model Families and Complexity Knobs]] — related
- [[Soft Inductive Bias, Benign Overfitting and Double Descent]] — related
- [[Weight Initialisation and Activation Scale]] — related
- [[Batch Normalization]] — related
- [[Dropout and Input Distortion as Ridge Regression]] — extends
- [[Dropout, Thinned Networks and Weight Scaling]] — instance-of
