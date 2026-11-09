---
title: Intrinsic Dimension of Objective Landscapes
tags: [foundations, concept]
summary: "Training only a d-dimensional random projection of a network's parameters and finding the smallest d that reaches 90% of normal performance (d_int90) gave about 750 for an MNIST fully connected net of 199,210 parameters, nearly constant across model sizes (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-li-2018-measuring-intrinsic-dimension-objective-landscapes.md
---

# Intrinsic Dimension of Objective Landscapes

Li et al. (ICLR 2018, arXiv 1804.08838) ask how many parameters a network needs to solve a problem. They define the **intrinsic dimension** of an objective as the codimension of its solution set inside the full parameter space, and estimate it by random subspace training.

## Mechanism

Parameters are written theta(D) = theta0(D) + P theta(d). Both the starting vector theta0 and the D-by-d projection P are random and held fixed, and training touches only theta(d), which starts at zero. The sweep over d yields **d_int90**: the lowest d whose performance reaches 90% of what training the full parameter space directly achieves.

## Results (self-reported)

- MNIST, fully connected 784-200-200-10 net (D = 199,210): d_int90 is about 750 (one run). Across 20 such nets of depth 1-5 and width 50-400 (3 runs per d), D varies 24.1 times while d_int90 varies 1.33 times.
- LeNet on MNIST (D = 44,426): d_int90 290, about 150 times compression. Storing the 750-dimension fully connected solution (a seed plus 750 floats) shrinks 793 kB to 3.2 kB. Inference is not made faster by subspace training.
- Permuting the MNIST pixels does not change the fully connected figure (750), while LeNet climbs from 290 to 1,400. Memorising random labels on 50,000 examples needs d_int90 of 190,000.
- CIFAR-10: d_int90 about 9K (fully connected) and 2.9K (LeNet); for over 50% accuracy, fully connected, LeNet and ResNet need about 9K, 2.9K and 1K.
- ImageNet SqueezeNet (D = 1.24M, directly trained top-1 55.5%): d_int90 was not pinned down, only shown to exceed 500K, because every value of d needs 6-7 days on 4 GPUs.
- Reinforcement learning: inverted pendulum needs 4 parameters, Humanoid 700 and Pong 6K (evolution strategies); DQN CartPole 25.
- Both local connectivity and weight tying reduce d_int90; the LeNet variants measure 290, 600, 425 and 2,000.
- Subspace training stays stable at depths where direct training of fully connected nets fails (beyond 5 layers, read from a supplementary figure), and can act as a regulariser on test NLL (qualitative).

## Limits

- Only random linear subspaces; better subspaces might contain solutions more readily. The 90% threshold is a heuristic and d_int100 varies widely; other thresholds are claimed, not tested.
- A near-constant dimension was shown for one family (fully connected MNIST), not claimed generally. Most numbers are single runs.
- d_int is only an upper bound on description length, with unknown tightness. Subspace training costs more per update.
- The paper studies small vision and RL problems from random initialisation, not pretrained or fine-tuned models, LoRA, transformers or language models.

## See Also
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — related (low-dimensional adaptation of large models; this paper does not study it)
