---
title: LM2 Large Memory Models
tags: [foundations, pattern]
summary: "LM2 adds a gated cross-attention memory bank to every decoder block of a transformer; at about 1.7B parameters it beats a recurrent-memory baseline and a same-size vanilla model on BABILong, but the gains are concentrated in a few task types and the memory lives only within one context (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kang-2025-lm2.md
---

# LM2 Large Memory Models

LM2 (a 2025 preprint) is a decoder-only transformer with an auxiliary memory module in each block. The memory bank has 2,048 slots, read by cross attention from the block's hidden states. Three gates control it: an input gate decides how much new content is written, a forget gate decides how much of the old memory is kept, and an output gate decides how much of the read-out is added to the residual stream. The update is a gated mix, M_next = g_in * tanh(new content) + g_forget * M, and the block output is the attention output plus g_out * the memory read. With a roughly 1.2B base (Llama-3.2 style) and about 0.5B memory parameters, the model has about 1.7B parameters. The memory path sits beside the normal attention path, which is left intact.

## Results (one 1.7B model, one run; pretrained from scratch)

- BABILong (reasoning over facts in long text), 0K context average: 92.5% for LM2 against 75.0% for a vanilla 1.7B model, 76.4% for RMT (recurrent memory transformer, 1.7B) and 40.7% for Llama-3.2-1.2B (self-reported).
- At 4K context the table gives LM2 55.9, vanilla 42.2, Llama 36.8, RMT 38.4. The text quotes RMT at 48.4, which contradicts the table.
- For contexts from 8K to 128K, the aggregate is 39.9 for LM2, 35.5 for RMT, 32.3 for Llama with RAG, 31.2 for vanilla and 28.2 for Llama (self-reported). Most of LM2's margin comes from the counting task (92.8 against RMT's 73.3); RAG beats LM2 on two other tasks.
- MMLU 29.4 for LM2 against 28.0 vanilla and 26.5 RMT, all near the 25% chance level; the abstract's "5.0%" gain is a relative figure of about 1.4 points.
- An ablation reports lowest perplexity with memory in all 16 blocks.

## Limits

- One model size, one run, no variance. RMT was fine-tuned on bAbI while LM2 was pretrained, so the comparison is not like-for-like. No cost or latency numbers.
- Interpretability evidence is qualitative. The paper has no limitations section; the extraction notes the memory persists only inside one context and nothing carries across sessions.
- The 4K RMT figure is inconsistent between text and table (above), and the MMLU headline is a relative gain on a near-chance score.

## See Also
- [[Recurrent Memory Transformer (RMT)]] — alternative-to
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[MeMo Memory as a Model]] — alternative-to (memory held in model parameters versus a memory bank)
- [[Delta-Mem Fixed-Size State Memory]] — alternative-to
