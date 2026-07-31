---
title: Positional Encoding
tags: [foundations, llm, concept]
summary: Sinusoidal or learned position signals injected into Transformer input embeddings — required because self-attention is permutation-invariant and has no inherent notion of sequence order.
updated: 2026-07-19
sources:
  - raw/pdfs/2017-06-12-attention-is-all-you-need.md
---

# Positional Encoding

Since the [[Transformer Architecture]] contains no recurrence and no convolution, it has no inherent notion of sequence order. Positional encodings are added to input embeddings to inject position information.

## Sinusoidal Encoding (Original)

The original Transformer uses sine and cosine functions of different frequencies:

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

Each dimension corresponds to a sinusoid with wavelengths forming a geometric progression from 2pi to 10000 * 2pi.

**Why sinusoidal?** For any fixed offset k, PE(pos+k) can be represented as a linear function of PE(pos) — the model can learn to attend by relative positions. This also allows extrapolation to sequence lengths longer than those seen during training.

## Learned Positional Embeddings

An alternative where position embeddings are learned parameters. Vaswani et al. found this produces nearly identical results to sinusoidal encoding, but sinusoidal was preferred for its extrapolation capability.

## Modern Extensions

- **Relative positional encoding** (Shaw et al., 2018): encodes pairwise distance rather than absolute position — used in DIET and other dialogue models
- **RoPE** (Rotary Position Embedding): applies rotation to query/key vectors based on position, enabling length extrapolation — used in LLaMA family
- **ALiBi** (Attention with Linear Biases): adds a linear bias to attention scores based on distance — no learned parameters

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Self-Attention Mechanism]] — extends
- [[LLM Fundamentals Interview Study Guide]] — instance-of
