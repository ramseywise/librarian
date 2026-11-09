---
title: StreamingLLM Attention Sinks
tags: [infra, concept]
summary: "StreamingLLM keeps the cached keys and values of the first few tokens plus a rolling recent window, which the paper reports stops perplexity collapsing on streams of millions of tokens without fine-tuning; it does not extend the usable context."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-xiao-2023-efficient-streaming-language-models-attention.md
---

# StreamingLLM Attention Sinks

Xiao et al. ask whether a model trained with a finite attention window can run on an unbounded stream. Their observation is that initial tokens collect large attention scores regardless of meaning (attention sinks), which they connect to the softmax having to sum to one. Window attention fails once those first tokens leave the cache. StreamingLLM retains cache entries for the 4 initial tokens together with a sliding window over the latest ones, assigns positions by cache slot, and needs no fine-tuning. A second proposal is to pretrain with one learnable sink token so a single initial token suffices.

## Results (all self-reported)

- Setup: Llama-2-13B on the first PG19 test book (65K tokens) with a 1024-entry cache. Window attention gives perplexity 5158.07 when no initial tokens are kept, against 5.40 for 4 initial plus 1020 recent tokens.
- Replacing the 4 initial tokens with line-break tokens still restores perplexity, which the authors read as position mattering more than content. On Llama-2-7B (400K tokens, cache 4096), four initial tokens suffice; one or two do not fully recover.
- Stable perplexity on text over 4 million tokens across Llama-2 (7B, 13B, 70B), Falcon, Pythia and MPT models (cache 2048 for Llama-2, 1024 for the rest).
- Decoding is up to 22.2x faster per token than sliding window with recomputation at similar memory (Llama-2-7B/13B, one A6000, Hugging Face Transformers, cache 256-4096).
- Pretraining 160M models (Pythia recipe) with a sink token: a 1+1023 cache matches the full window's streaming perplexity, and zero-shot accuracy is unharmed (ARC-Easy 45.6 against 45.2). A second sink token gave no gain.
- In the streaming ARC-Easy setting with Llama-2-13B-Chat, window attention scores close to zero and StreamingLLM outperforms the one-shot baseline.

## Limits

- It does not extend the context window or add long-term memory; the paper states it is unsuited to long-document question answering and summarisation.
- Enlarging the cache does not reliably reduce perplexity: for Llama-2-7B the 4+4092 setting gives 9.59 while 4+2044 gives 9.08.
- StreamEval accuracy falls to 0.00 once the query-to-answer distance exceeds the cache; on LongBench the 4+3496 setting underperforms plain truncation (NarrativeQA 11.6 against 18.7), and 1750+1750 restores it.
- Sink-token results come from 160M models only; no seeds or intervals; the latency figure is a 2023 Hugging Face implementation.

## See Also

- [[Star Attention]] — related (anchor blocks follow the sink idea)
- [[Multi-Query and Grouped-Query Attention]] — related (another way to cut cache cost)
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Prefix Caching]] — related
