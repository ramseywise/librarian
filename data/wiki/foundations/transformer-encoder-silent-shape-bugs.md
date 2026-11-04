---
title: "Transformer Encoder Silent Shape Bugs"
tags: [foundations, reference]
summary: "Three transformer-encoder bugs raise no error and still train: attending to padding (or an inverted mask), the batch_first=False default that makes digits attend across the batch (0.966 as a batch, 0.658 one at a time), and a (batch,1) vs (batch) broadcast in the loss."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05b-transformer-encoders.md
---

# Transformer Encoder Silent Shape Bugs

## 1. Padding and masks

Batches are padded, and attention will attend to padding unless told not to. `src_key_padding_mask` takes **True = ignore**. Assertable test: padding a sequence must not change its output. Padded to 10, logits moved 0.2876 without the mask and 0.000000 with it; padded to 20, 0.4305 vs 0.000000. Without the mask the same input gives different logits depending on the longest member of its batch. The pool must also skip padding. Passing the mask inverted raises nothing and produces no nan; real tokens' outputs moved by 1.37 because they attended only to padding.

## 2. batch_first=False

`nn.TransformerEncoderLayer` defaults to batch_first=False. Fed (batch, n, d) it reads the batch as the sequence, so each example attends to the others in its batch. The model still trains well: test accuracy 0.966 scored as a batch, 0.658 scored one example at a time (production sends single requests). Catch it by scoring the same examples at batch sizes 1 and 32 and checking that the logits match. `nn.MultiheadAttention` has the same default.

## 3. Broadcast in the loss

A regression head outputs (batch, 1) and the target is (batch). Subtracting broadcasts to (batch, batch), so every prediction is compared with every target and the best constant is the mean: R2 per seed [-0.084, 0.089, -0.135] against [0.897, 0.966, 0.946] after squeezing the output. PyTorch warns about differing target sizes; do not silence it. Add `assert pred.shape == target.shape` before the loss.

## Common thread

All three are tests that a model is invariant to what it should be (padding, other batch members) or that shapes mean what you think. Compare with the train-mode batch-norm bug in [[Batch Norm Eval Mode and Small-Batch Failure]] and the checklist in [[PyTorch Training Loop Silent Bugs]]. Architecture background: [[Transformer Architecture]], [[Self-Attention Mechanism]].

## See Also
- [[PyTorch Training Loop Silent Bugs]] — related
- [[Encoder Tokens, Position and Attention Scaling]] — related
- [[Self-Attention Mechanism]] — related
