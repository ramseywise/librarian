---
title: Self-Attention Mechanism
tags: [infra, llm, concept]
summary: Self-attention (intra-attention) relates different positions of a single sequence to compute a representation — the core primitive enabling Transformers to model long-range dependencies in O(1) path length.
updated: 2026-11-19
sources:
  - data/raw/pdfs/2017-06-12-attention-is-all-you-need.md
  - data/raw/pdfs/2020-10-01-rasa-dialogue-transformers.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch03-coding-attention-mechanisms.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch02-generative-models.md
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

## Causal attention in code and efficient variants

Raschka's from-scratch LLM book (ch. 3) builds causal attention in PyTorch from simplified attention up to multi-head. Masking future positions with -inf before the softmax gives the same masked, renormalised weights as zeroing them afterwards and renormalising, with no leakage from future tokens (six-token example, d_in=3, d_out=2; self-reported worked example). Dropout is applied to the attention weights after the softmax during training only, and the weights that survive are multiplied by 1/(1-p) so average influence is unchanged at inference; the demonstration uses 50%, and the chapter says GPT training uses 0.1 or 0.2 later. In the two-head wrapper with d_out=2, each token's context vector is the concatenation of both heads' outputs, four values long. The weight-split multi-head class is called more efficient by argument, with no timing or memory measurement.

Xiao and Zhu (*Foundations of Large Language Models*, ch. 2) define three efficient variants in their terms list: sparse attention attends only to a subset G of positions, with weights renormalised over G; linear attention replaces the softmax with a kernel feature map, giving recurrent summaries and constant cost per step; and attention sinks keep the first few tokens (global tokens) attended throughout, soaking up surplus attention scores and steadying long contexts. For the cache of keys and values they give O(L*tau*dh*m) for multi-head, O(L*dh*m) for multi-query and O(L*ng*dh*m) for grouped-query attention, where L is layers, tau heads, dh the per-head dimension and m cached tokens.

## Limits

- The Raschka and Xiao and Zhu passages are textbook material: toy sizes with a fixed seed in the first, almost no experiments of its own in the second (its figures are borrowed or illustrative).

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Dialogue Transformers — TED Policy]] — instance-of
- [[Prefix Caching]] — extends (exploits repeated attention computation)
- [[Encoder Tokens, Position and Attention Scaling]] — extends
- [[Artificial Hippocampus Networks]] — instance-of
- [[MiniMax Sparse Attention]] — instance-of
- [[Query-Only Test-Time Training (qTTT)]] — instance-of
- [[Unlimiformer]] — instance-of
- [[Multi-Query and Grouped-Query Attention]] — extends (shares keys and values across heads)
- [[FlashAttention and FlashAttention-2]] — extends (exact attention computed blockwise in SRAM)
- [[Efficient Attention Approximations]] — extends (Performer, BigBird, Routing Transformer)
- [[Star Attention]] — extends (blockwise-local context encoding across hosts)
- [[GPT From Scratch: Block, Weight Tying and Shortcuts]] — instance-of (causal multi-head attention coded step by step)
- [[Linear Attention (Transformers Are RNNs)]] — extends
- [[Sparse Transformer Factorized Attention]] — extends
- [[Longformer Sliding-Window and Global Attention]] — extends
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — prerequisite-for
