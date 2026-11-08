---
title: D-Adaptation (Learning-Rate-Free Optimisation)
tags: [foundations, pattern]
summary: D-Adaptation sets the learning rate by tracking a running lower bound on the distance from the start point to a minimiser, with no line search or extra gradient evaluations.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-defazio-2023-learning-rate-free-learning-d.md
---

# D-Adaptation (Learning-Rate-Free Optimisation)

D-Adaptation (Defazio and Mishchenko, 2023 arXiv preprint) removes the base learning rate as a hyper-parameter. Everything below is the authors' own (self-reported) account.

## Mechanism

The ideal step size for subgradient methods depends on D, the distance from the starting point x0 to a minimiser x*, which is unknown. The method keeps a running estimate d_k that never decreases. At each step it computes a candidate lower bound d_hat from the dual-averaging bound, then sets d_k to the larger of the old value and the candidate. The step size is built from d_k. There is no line search and no extra gradient evaluation. It needs an initial value d0 no larger than D.

- The candidate d_hat often decreases over time and can go negative; the max keeps d_k monotone. d_k need not reach D; given a mild assumption, it ends up no lower than about 0.37 D (D divided by 1 + sqrt 3).
- Classical hyper-gradient methods need an extra rate controlling how fast the learning rate changes. Here that term yields an estimate of scale instead, so the only extra input is d0, and warmup and annealing can be layered on top.

## Theory (convex, G-Lipschitz, deterministic)

- Asymptotic rate O(DG / sqrt(n+1)), matching the optimal rate with known D (Theorem 1). The authors claim this is the first tuning-free method for the class whose rate carries no added multiplicative log terms.
- Non-asymptotic bound (Theorem 2) costs a factor log2(D/d0), which the authors say is far better than the factor D/d0 paid by a step size proportional to d0.
- The result is for a weighted-average iterate. Related methods obtain better dependence (a bisection scheme with a double-log dependence; coin betting with a square-root-of-log dependence).

## Practical variants

The SGD and Adam versions (Algorithms 4 and 5) go beyond what the theory proves. The SGD variant doubles the D bound and uses the first gradient norm as a crude stand-in for G. The Adam variant uses an exponential moving average and needs no multiplier. Defaults: d0 = 1e-6. Final accuracy was flat for d0 from 1e-16 to 1e-2 on 12 logistic regression problems; in half precision the authors suggest a value between 1e-8 and 1e-6 to avoid underflow.

## Reported results (self-reported)

D-Adaptation supplies only the base learning rate; schedules and warmup are the baselines' own. Baseline learning rates come from papers or code.

| Task and setup | Baseline | D-Adapt |
|---|---|---|
| 12 LIBSVM logistic regressions, Adam, 100 epochs, 10 seeds | grid-searched LR | matches or exceeds on all 12, within 0.5% accuracy |
| CIFAR-10, WRN-16-8, SGD, test acc % | 95.59 | 95.56 |
| CIFAR-100, DenseNet, SGD | 76.41 | 76.90 |
| ImageNet, ResNet-50, SGD | 76.09 | 76.43 |
| RoBERTa (110M, BookWiki), Adam, test ppl | 3.97 | 3.96 |
| Small GPT decoder, Adam, test ppl | 19.49 | 19.46 |
| IWSLT14 LSTM, Adam, test loss | 4.31 | 4.33 |
| ViT-tiny, Adam, 300 epochs cosine, ImageNet top-1 | 74.24 | 71.62 |
| COCO Faster-RCNN, SGD, AP, after raising weight decay to 0.00015 | 42.99 | 43.07 |
| fastMRI VarNet, SSIM | 0.9103 | 0.9105 |
| Criteo DLRM | 0.7906 | 0.7905 |

- Learned rates were usually near hand-tuned ones, tending to sit at the upper edge of a broad good region; ViT (0.0073 vs 0.001) and fastMRI were the outliers.
- A prior parameter-free baseline, COCOB, did not match the tuned baseline on any problem except MRI (CIFAR-10 accuracy 89.13 against 95.59 for the tuned baseline; ImageNet 61.58 against 76.09; RoBERTa and ViT diverged and DLRM ran out of memory). The authors attribute this largely to COCOB lacking schedules and warmup.
- DoG is concurrent work covering the stochastic case; the authors say its rate has extra log factors.

## Limits

- Proofs apply only to convex Lipschitz objectives with exact subgradients; the deep-learning variants rest on experiments alone.
- Requires d0 not above D and returns an averaged iterate; guarantees for the final iterate are not explored.
- ViT is a clear loss with no explanation from the authors; the COCO match needed a retuned weight decay (D-Adapt AP 41.92 before, 43.07 after).
- How finely the baselines were tuned is unknown. The largest model has 110M parameters, with no large LLM runs. The COCOB comparison is confounded, since COCOB lacks schedule and warmup support.
- The extraction notes that no venue is printed in the PDF and that proofs were scanned, not verified.

## See Also

- [[Adam, AdamW and Decoupled Weight Decay]] — prerequisite-for
- [[Hyperparameter Search Budgets and Selection Optimism]] — related (the tuning cost this removes for one hyper-parameter)
