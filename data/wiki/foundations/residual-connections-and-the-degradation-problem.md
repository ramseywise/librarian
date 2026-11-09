---
title: "Residual Connections and the Degradation Problem"
tags: [foundations, concept]
summary: "A block that outputs F(x)+x makes the identity the easy default, fixing the optimisation failure of very deep plain networks (62-layer plain net: train 0.379), and makes blocks optional so stochastic depth can drop them as regularisation."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
  - data/raw/papers/2026-11-07-huang-2016-deep-networks-stochastic-depth.md
---

# Residual Connections and the Degradation Problem

A deeper network can represent anything a shallower one can, since extra layers could be the identity. In practice deeper plain networks train worse, and the cause is optimisation, not overfitting: the plain net has low training accuracy too. A residual block learns F(x) and outputs F(x) + x, so driving F to zero recovers the identity. Skip connections carried straight into transformers ([[Transformer Architecture]]).

## Numbers (8x8 digits, train / test)

| Depth | Plain | Residual |
|---|---|---|
| 6 layers | 0.986 / 0.969 | 0.984 / 0.965 |
| 22 layers | 0.946 / 0.924 | 0.982 / 0.978 |
| 62 layers | 0.379 / 0.370 | 0.983 / 0.965 |

At shallow depth the skip changes nothing; it matters only when depth makes optimisation hard.

## Stochastic depth

Drop whole residual blocks at random for each mini-batch (only the identity path remains), survival probability falling linearly from 1 at the input to 0.5 at the last block; at test all blocks run, scaled by survival probability. On a 110-layer ResNet CIFAR-10 error fell from 6.41% to 5.25%, with about 25% less training time because expected depth is about three quarters. A 1,202-layer network reached 4.91% against 6.67% trained normally. No gain on a 152-layer ImageNet ResNet (21.98% vs 21.78%), and no seeds or variance are reported.

The stochastic depth paper (Huang et al., ECCV 2016, arXiv 1603.09382) adds these numbers (self-reported). Survival probability decays linearly with depth from 1 at the first block to p_L at the last, and with p_L = 0.5 the expected count of active blocks is (3L-1)/4, roughly 40 of the 54 in the 110-layer net. Training time on CIFAR-10 fell from 20h42m to 15h7m. CIFAR-100 error with stochastic depth is 24.98%; without augmentation CIFAR-10 improves 13.63% to 11.66% and CIFAR-100 44.74% to 37.8%. SVHN (152-layer net, no augmentation) gives 1.75% against 1.80%. On ImageNet after 90 epochs, stochastic depth comes out marginally worse (23.38% against 23.06%). With p_L = 0.2 CIFAR-10 error matches the constant-depth net with a 40% speedup; linear decay beats uniform survival and is robust for p_L between 0.4 and 0.8. The authors report that dropout gives practically no gain on 110-layer batch-norm ResNets (no numbers).

## Rule of thumb

If a deeper model does worse on training accuracy, add residual connections before touching regularisation.

## Limits

- For the stochastic depth numbers, the authors say the ImageNet net is probably too small to benefit.
- The extraction notes single runs, gradient evidence drawn only from the average size of one layer's gradients, which does not test causation, a constant-depth CIFAR-100 baseline printed with three different values (27.76, 27.22, 27.88), and the 1,202-layer result reported on CIFAR-10 only.

## See Also
- [[Convolution, Shift Sensitivity and Parameter Sharing]] — prerequisite-for
- [[Pre-Norm vs Post-Norm and Warm-Up]] — related (the same skip path, where the norm sits)
- [[Transformer Architecture]] — related
- [[Intrinsic Dimension of Objective Landscapes]] — related (another parameter-count result for deep nets)
