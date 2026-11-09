---
title: "LongMem Side-Network Memory"
tags: [foundations, pattern]
summary: "LongMem caches key-value pairs from a frozen backbone layer into a 65k FIFO memory bank and reads them through a trainable SideNet with gated joint attention; it reached 40.5% on ChapterBreak AO3 at an 8k prefix (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2023-augmenting-language-models-long-term.md
---

# LongMem Side-Network Memory

This is a model-architecture memory, not agent memory: it extends how much past text a language model can attend to.

## Mechanism

A frozen backbone encodes earlier text and its attention keys and values from one upper layer (layer 18 of 24) go into a first-in-first-out bank of 65,536 pairs. A trainable SideNet retrieves from the bank (chunk-level, mean-pooled keys, top K/chunk-size chunks) and fuses the result with local attention through gated joint attention. Keeping the backbone frozen is claimed to avoid the memory staleness of coupled designs; the paper has no isolated staleness test.

## Results (self-reported)

Backbone: a reproduced GPT-2 407M (558M total with SideNet), 1k local context.
- ChapterBreak AO3 suffix identification, zero-shot: 40.5% at an 8k prefix (37.7% at 4k, 39.4% at 6k), against 28% for GPT-3 and 18.4% for the memoryless backbone.
- Perplexity: PG-22 splits improved by 1.38 to 1.62 and ArXiv by 1.0 against the backbone, with 1k in-context and 65k in-memory.
- In-context learning with 2,000 extra demonstrations in memory: 20-shot average 66.7 against 58.7 for the backbone (+8.0), over five classification tasks, six seeds.
- At an 8k effective length, 21,343 tokens/s and 13,437 MB against 8,417 tokens/s and 54,195 MB for dense attention. Retrieval costs 15 ms per 1k tokens, about 55% of backbone forward time.
- For books of 8k-50k tokens on average, a 16k memory did better than a 65k one.

## Limits

- GPT-2 scale only; needs white-box access to a frozen model's keys and values, and the FIFO bank is not unbounded.
- Internal inconsistencies in the extraction: the chunk-size legend shows 1/2/4 while the text gives {2,4,8}; a memory size of "65 tokens" is a typo; no venue is printed.
- Baselines for GPT-3 and sparse-attention models are quoted from other papers.

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[Focused Transformer Crossbatch Training]] — alternative-to
- [[MemLong Retrieval Memory Layers]] — alternative-to
- [[Recurrent Memory Transformer (RMT)]] — related
