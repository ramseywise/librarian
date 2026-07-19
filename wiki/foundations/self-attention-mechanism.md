---
title: Self-Attention Mechanism
tags: [foundations, llm, concept]
summary: Self-attention (intra-attention) relates different positions of a single sequence to compute a representation — the core primitive enabling Transformers to model long-range dependencies in O(1) path length.
updated: 2026-07-19
sources:
  - raw/pdfs/2017-06-12-attention-is-all-you-need.md
  - raw/pdfs/2020-10-01-rasa-dialogue-transformers.md
---

# Self-Attention Mechanism

Self-attention (also called intra-attention) is an attention mechanism that relates different positions of a single sequence to compute a representation. It is the core building block of the [[Transformer Architecture]].

## Mechanism

Given an input sequence, self-attention computes queries (Q), keys (K), and values (V) from the same source. Each position attends to all other positions (including itself), producing a weighted sum of values where weights are determined by query-key compatibility:

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

**Key properties:**
- **Constant path length**: any two positions interact in O(1) operations (vs O(n) for RNNs)
- **Full parallelization**: no sequential dependency during training
- **Interpretable**: attention weights can reveal which positions influence each other
- **Quadratic cost**: O(n^2 * d) per layer — the reason context windows are expensive to scale

## Multi-Head Variant

Multi-head attention runs h parallel attention functions with different learned projections, allowing the model to jointly attend to information from different representation subspaces. The original Transformer uses h=8 heads with d_k = d_v = 64.

Attention heads learn specialized roles — some capture syntactic dependencies, others handle anaphora resolution or long-distance verb phrases.

## Self-Attention for Dialogue

The Rasa TED (Transformer Embedding Dialogue) policy applies self-attention at the **discourse level** — over the sequence of dialogue turns rather than tokens. This allows the dialogue policy to:

- Selectively ignore irrelevant turns (e.g., chit-chat interruptions)
- Attend to distant relevant turns for task completion
- Learn sparse attention patterns naturally, without explicit architecture modifications

This is more suitable than RNNs for multi-turn dialogue because conversations contain interleaved discourse segments — topics that overlap and interrupt each other. An RNN processes the entire sequence by default; self-attention selects which turns matter.

## Variants and Extensions

- **Masked self-attention**: prevents attending to future positions (used in decoder / autoregressive models)
- **Cross-attention**: queries from one sequence, keys/values from another (encoder-decoder attention)
- **Sparse attention**: restricts attention to local neighborhoods to reduce quadratic cost
- **Relative position attention**: encodes relative rather than absolute positions (used in DIET, TED)

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Dialogue Transformers — TED Policy]] — instance-of
- [[Prefix Caching]] — extends (exploits repeated attention computation)
- [[LLM Fundamentals Interview Study Guide]] — instance-of
