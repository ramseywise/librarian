---
title: "Pre-Norm vs Post-Norm and Warm-Up"
tags: [foundations, comparison]
summary: "Post-norm keeps large output-layer gradients that need learning-rate warm-up (without it BLEU 8.45 vs about 34; at lr 0.01 accuracy stuck at 0.101), while pre-norm's gradients shrink with depth and train without warm-up."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05b-transformer-encoders.md
---

# Pre-Norm vs Post-Norm and Warm-Up

The original transformer block is **post-norm**: LayerNorm(x + Sublayer(x)), trained with a learning rate that warms up for 4,000 steps then decays. `norm_first=True` gives **pre-norm**: normalise, apply the sub-layer, then add. Post-norm's gradients near the output are large at initialisation, which is why it needs warm-up; the evidence shows faster training and easier tuning for pre-norm, not a more accurate model. See [[Batch Norm Eval Mode and Small-Batch Failure]] for layer norm's role and [[Transformer Architecture]].

## Gradient at the last feed-forward (encoder on digits)

| Layers | post-norm | pre-norm |
|---|---|---|
| 2 | 0.291 | 0.323 |
| 6 | 0.265 | 0.119 |
| 12 | 0.263 | 0.058 |

Post-norm stays flat around 0.26; pre-norm falls more than five times from 2 to 12 layers. On IWSLT14 translation, post-norm with Adam and no warm-up reached BLEU 8.45 against about 34 with warm-up; pre-norm reached about 34 with none. "Needs warm-up" holds for Adam and SGD there; RAdam or a very small fixed rate also trained post-norm.

## Digits, 6 layers, AdamW, 200-step warm-up

At lr 0.001 all four combinations land between 0.963 and 0.973. At lr 0.01: post-norm no warm-up 0.101 (stuck at chance), post-norm with warm-up 0.905, pre-norm 0.935 without and 0.948 with warm-up. This is near the edge of the learning-rate range on one small dataset and three seeds: use pre-norm and sweep the learning rate by factors of ten ([[Adam, AdamW and Decoupled Weight Decay]]).

## Open question

ViT is pre-norm and still warms up for 10k steps, and it reports no run without; it also found strong regularisation key from scratch. Neither paper compares regularisation against warm-up or norm placement.

## See Also
- [[Residual Connections and the Degradation Problem]] — related
- [[Choosing an Encoder vs CNN vs LSTM]] — related
- [[Adam, AdamW and Decoupled Weight Decay]] — related
