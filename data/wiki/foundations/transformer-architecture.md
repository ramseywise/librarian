---
title: Transformer Architecture
tags: [foundations, llm, concept]
summary: The Transformer model architecture (Vaswani et al., 2017) — encoder-decoder stacks of self-attention and feed-forward layers that replaced RNNs/CNNs for sequence transduction, enabling parallelized training and constant-length dependency paths.
updated: 2026-07-19
sources:
  - raw/pdfs/2017-06-12-attention-is-all-you-need.md
---

# Transformer Architecture

The Transformer (Vaswani et al., 2017, "Attention Is All You Need") is the first sequence transduction model based entirely on attention, dispensing with recurrence and convolutions. It is the foundation architecture behind all modern LLMs.

## Core Architecture

**Encoder-decoder stacks**, each with N=6 identical layers:

- **Encoder layer**: multi-head [[Self-Attention Mechanism]] + position-wise feed-forward network (FFN), each with residual connections and layer normalization.
- **Decoder layer**: same as encoder plus a third sub-layer performing multi-head attention over the encoder output. Decoder self-attention is masked to prevent attending to future positions.

All sub-layers produce output of dimension d_model = 512.

## Key Components

### Scaled Dot-Product Attention

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

Scaling by `1/sqrt(d_k)` prevents dot products from growing large in magnitude, which would push softmax into regions with vanishingly small gradients.

### Multi-Head Attention

Instead of single attention, project Q/K/V h times with different learned projections, attend in parallel, concatenate, and project again:

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O
where head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)
```

Base model: h=8 heads, d_k = d_v = d_model/h = 64. This allows attending to information from different representation subspaces at different positions.

### Three Uses of Attention

1. **Encoder-decoder attention**: queries from decoder, keys/values from encoder output (cross-attention)
2. **Encoder self-attention**: all Q/K/V from previous encoder layer
3. **Masked decoder self-attention**: prevents leftward information flow (auto-regressive property)

### [[Positional Encoding]]

Sinusoidal functions of different frequencies injected at the bottom of encoder/decoder stacks — the model has no recurrence, so position information must be explicitly added. Learned positional embeddings produce nearly identical results.

### Position-wise FFN

Two linear transformations with ReLU: `FFN(x) = max(0, xW_1 + b_1)W_2 + b_2`, with inner dimension d_ff = 2048.

## Computational Properties

| Layer Type | Complexity/Layer | Sequential Ops | Max Path Length |
|---|---|---|---|
| Self-Attention | O(n^2 * d) | O(1) | O(1) |
| Recurrent | O(n * d^2) | O(n) | O(n) |
| Convolutional | O(k * n * d^2) | O(1) | O(log_k(n)) |

Self-attention connects all positions with O(1) sequential operations — faster than recurrent layers when sequence length n < representation dimension d (typical for NLP).

## Training Details

- **Optimizer**: Adam with warmup schedule (linear increase for 4000 steps, then inverse square root decay)
- **Regularization**: residual dropout (P=0.1), label smoothing (epsilon=0.1)
- **Hardware**: 8 NVIDIA P100 GPUs; base model ~12 hours, big model ~3.5 days

## Results

- **WMT 2014 EN-DE**: 28.4 BLEU (new SOTA, +2 BLEU over best ensembles)
- **WMT 2014 EN-FR**: 41.8 BLEU (new single-model SOTA, <1/4 training cost of previous SOTA)
- **English constituency parsing**: 92.7 F1 (semi-supervised), competitive with task-specific models

## Why It Matters for Agent Engineering

The Transformer is the foundation of every LLM used in agent systems. Understanding its attention mechanism, context window constraints, and computational scaling properties is essential for:
- **Context management**: understanding why context windows have quadratic cost
- **Prompt engineering**: leveraging attention patterns for effective instruction placement
- **Architecture decisions**: when to use encoder-decoder vs decoder-only variants

## See Also
- [[Self-Attention Mechanism]] — extends
- [[Positional Encoding]] — prerequisite-for
- [[Batch Normalization]] — prerequisite-for (layer norm in Transformer is the successor)
- [[Neural Probabilistic Language Model]] — prerequisite-for (word embeddings that Transformers build on)
- [[LLM Fundamentals Interview Study Guide]] — instance-of
