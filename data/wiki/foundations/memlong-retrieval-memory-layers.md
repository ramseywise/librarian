---
title: "MemLong Retrieval Memory Layers"
tags: [foundations, pattern]
summary: "MemLong caches chunk key-value pairs from a frozen lower-layer stack and retrieves them with an external dense retriever into upper layers; OpenLLaMA-3B kept lowering perplexity past 2048 tokens (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-liu-2024-memlong.md
---

# MemLong Retrieval Memory Layers

MemLong tests whether retrieving chunks explicitly can stand in for the retrieval a model does implicitly, without the distribution shift seen in earlier memory models.

## Mechanism

In OpenLLaMA-3B the bottom layers stay frozen and the top layers are trained with LoRA. At memory layer 13 a frozen dense retriever embeds each text chunk and the chunk's key-value pairs are cached alongside. Chunks with the highest cosine similarity (top-k) are fetched and combined with the local context in the upper retrieval layers through retrieval causal attention, using a LLaMA-adapter-style gate. A frequency counter drives dynamic memory update. Retrieval in every upper layer hurt; sparser retrieval layers [14, 18, 22, 26] worked best (PG19 2k perplexity 9.85 against 11.43 for one alternative; self-reported).

## Results (self-reported)

- Perplexity kept falling past the 2048 pretrained length where the base model exploded; with 32K memory, PG19 perplexity at 16k was 9.73. At 4k, 9.83 against 9.87 for LongLLaMA-3B with unbounded memory.
- Retrieval-augmented in-context learning, five classification tasks, 20 in-context plus 18 in-memory demonstrations: average 73.4 against 69.0 for the base model and 72.7 for LongLLaMA. Up to 10.2 points gain is claimed in the abstract.
- Fine-tuning used 0.5B tokens, eight 3090 GPUs and eight hours, where LongLLaMA used 5B tokens. Context extension to 80k on a single 3090 is claimed without a results table.

## Limits

- Only OpenLLaMA-3B; fixed retriever with no ablation; no optimizer, learning rate, chunk size, top-k or seeds reported.
- No downstream long-document tasks such as question answering or summarization. The compared models were fine-tuned on different amounts of data (5B against 0.5B tokens). The memory-size threshold at 65536 is read from a figure.
- The authors note single-layer key-value pairs give extra semantic information that is unstable.

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[LongMem Side-Network Memory]] — alternative-to
- [[Focused Transformer Crossbatch Training]] — alternative-to
- [[Unlimiformer]] — alternative-to
