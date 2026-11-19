---
title: Deep Character-Level Transformer with Auxiliary Losses
tags: [llm, architecture, concept]
summary: "Al-Rfou et al. train a 64-layer causal transformer on fixed 512-byte windows with three auxiliary losses and per-layer learned position embeddings, reaching 1.13 bits per character on text8 and 1.06 on enwik8."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-alrfou-2019-character-level-language-modeling-deeper.md
---

# Deep Character-Level Transformer with Auxiliary Losses

Al-Rfou, Choe, Constant et al. ask whether a deep transformer with no recurrence and a fixed context can outperform RNN variants on character-level language modelling. Their hypothesis: information travelling quickly across any distance in a transformer fits long character sequences, and auxiliary losses make training 64 layers workable. No state carries between batches, unlike truncated backpropagation through time (an RNN scheme where hidden states cross sequential batches while gradients do not).

## Method

The model is a causal transformer of 64 layers; its inputs are windows of 512 bytes drawn from random positions. Three auxiliary losses apply: on intermediate positions (all positions, not just the last), on intermediate layers (decayed), and on multiple targets (two steps ahead). Each layer has its own learned positional embedding.

## Results (all self-reported, single runs)

- text8 test, T64 (64 layers, 235M training parameters, context 512, no dynamic evaluation): 1.13 bits per character. enwik8 test with the same hyperparameters: 1.06 bits per byte. enwik9 (900M/50M/50M split, dropout 0.1): 0.85 bits per byte.
- T12 (12 layers, 41M inference parameters, 8M steps, dropout 0.2) reaches 1.18 on text8 test; it was added because T64 is about 5x larger than prior baselines.
- Ablations (text8 dev, context 512, T64; baseline 1.062): without the multiple-positions loss dev bits per character degrade to 2.482; removing the intermediate-layer losses costs 0.096.
- Context: the best text8 test result comes at context 512 versus 1.34 at context 32; at that context the test accuracy is 75.9%.
- The model reproduces a corrupted fake name 434 characters later (text8 test seed of 512 characters).
- On lm1b the byte-level T64 reaches word perplexity 40.6, against 23.7 for a word-level model (dropout 0). SGD at learning rate 0.1 gets 1.065 dev bits per character, near what momentum gives.
- The best model arrived after roughly 2.5M steps, about 175 hours on a single TPU v2.

## Limits

- Evaluation recomputes the full 512-character context per character, so inference is expensive.
- On lm1b the byte-level model falls behind the word-level one (perplexity 40.6 versus 23.7); the authors describe it as a starting point.
- Learned positional embeddings are workable only because longer contexts are not needed.
- Results are single runs with no seeds or variance; ablations reuse the best model's hyperparameters with no retuning; the comparison is not matched on parameters; compute other than TPU v2 hours is not given; no code release is mentioned.

## See Also

- [[Transformer Architecture]] — prerequisite-for
- [[Transformer-XL Segment Recurrence]] — extends
- [[Sparse Transformer Factorized Attention]] — related (compared on enwik8; the Sparse Transformer paper cites this work for deep-Transformer training difficulty)
