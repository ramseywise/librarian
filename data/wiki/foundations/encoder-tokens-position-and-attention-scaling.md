---
title: "Encoder Tokens, Position and Attention Scaling"
tags: [foundations, concept]
summary: "Self-attention plus mean pooling sees a set, so position must be added; a learned table and sinusoids tie, and the choice of what a token is (a single pixel, a row, a patch) matters more: patches matched or beat single pixels at a fraction of the time."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05b-transformer-encoders.md
---

# Encoder Tokens, Position and Attention Scaling

## Mechanism

Each token makes a query, compares it with a key from every token, and takes a weighted average of values; only the three projections learn. Scores are divided by sqrt(d_k): the standard deviation of q.k grew 2.00, 7.99 and 32.09 at d_k of 4, 64 and 1,024 and is 1.00 after scaling (see [[Self-Attention Mechanism]]). Shuffling tokens makes outputs move with their inputs (equivariant), so a mean pool is invariant: attention plus mean pooling sees a set, not a sequence.

An encoder block adds heads (narrower projections, same total width), a per-token feed-forward network, and residual plus LayerNorm. Small example: 18,026 parameters in total (attention 4,224, feed-forward 4,192, embed 288); head count does not change attention parameters; only the position table is tied to sequence length.

## Position

Digits as 8 rows (test; rows upside down): no position 0.902 (0.902, blind to order); sinusoid 0.984 (0.395); learned 0.975 (0.551). Sinusoid and learned tie (25.7 vs 25.8 BLEU in translation). A learned table has no entry for a longer sequence and errors; sinusoids run at any length. ViT 5-shot: 0.61382 with none, 0.64206 learned, so most of the benefit is having any. A table encoder (FT-Transformer) has no position since columns have no order. See [[Positional Encoding]].

## Token design

Same digits, four tokenisations (test, time per run): 64 single pixels 0.948 (18.1 s), 16 tokens of 2x2 0.951 (6.0 s), 8 row tokens 0.975 (4.1 s), 4 patches of 4x4 0.975 (3.5 s). More tokens bought nothing. Published patterns agree: ViT B/16 77.91 vs B/32 73.38 on ImageNet pretraining; PatchTST patching a time series cut MSE 0.397 to 0.367 on Traffic and running time from 10,040 s to 464 s because a single time step has no word-like meaning; FT-Transformer makes one token per feature, with training time 0.9x to 13.8x a ResNet's.

## See Also
- [[Transformer Encoder Silent Shape Bugs]] — related
- [[Choosing an Encoder vs CNN vs LSTM]] — related
- [[Positional Encoding]] — extends
- [[Self-Attention Mechanism]] — extends
