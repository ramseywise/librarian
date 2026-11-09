---
title: COCOM Context Embeddings Compression
tags: [rag, pattern]
summary: "COCOM compresses each retrieved passage into a few context embeddings produced by the same LLM that decodes, with the decoder tuned jointly; the authors report up to 5.69x faster inference and 22x fewer GFLOPs at 128x compression, but the extraction's text and tables disagree in places (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-rau-2024-context-embeddings-efficient-answer-generation.md
---

# COCOM Context Embeddings Compression

Rau and colleagues (2024 preprint) ask whether a handful of context embeddings can stand in for several retrieved passages, making RAG answer generation much faster without losing answer quality. The hypothesis is that freezing the decoder hinders the use of compressed contexts, so tuning the decoder jointly with the compressor beats frozen-decoder compression.

## Mechanism

- Each passage of n tokens is compressed on its own into k = ceil(n / xi) **context embeddings**, where xi is the **compression rate**. They are last-hidden-layer states of special `<CTX>` tokens, taken from the same Mistral-7B LLM that acts as decoder. COCOM-light swaps in a bert-base-uncased compressor followed by a learned linear projection applied block by block.
- Training has two LoRA stages. The LLM is first LoRA-pretrained on two tasks, auto-encoding and language modelling from context embeddings, and then LoRA fine-tuned with five compressed passages as input on a multi-QA mix of 493k examples.
- Compressed passages can be indexed; at xi=128 the index for 24M contexts is 0.19 TB.

## Results

Self-reported. Setup: Mistral-7B-v0.2 with the top five passages, five QA sets (NQ, TriviaQA, HotpotQA, ASQA, PopQA) unless stated. The extraction records the average EM and the drop against uncompressed RAG as labels without values, so those are not quoted.

- Efficiency at xi=128 (NQ, A100 40GB, batch 16): up to 5.69x inference-time reduction and 22x GFLOPs reduction (1138 against 25031 GFLOPs); uncompressed RAG decoding takes 1064 ms. GPU memory is 14.2 GB against 18.1 GB.
- Comparisons: xRAG with Mixtral-8x7b zero-shot (single top-1 context, xi=128) is far below COCOM on average EM; ICAE (frozen decoder, x4, top-5 concatenated and truncated to 512 tokens) is below too.
- Ablations on NQ EM at xi=128: freezing the decoder lowers COCOM below its 0.519 baseline and COCOM-light below its tuned 0.444; skipping pretraining lowers COCOM-light below 0.444. Five passages beat one (the k=1 result is 0.499) for COCOM at xi=4.
- Cost: compressing 24M contexts takes COCOM 89 h but COCOM-light 1 h (xi=4, one A100 80GB). Auto-encoding Rouge-L reaches 0.9979 at xi=4 but collapses at xi=128 for COCOM. The extraction gives no value for the fine-tuned uncompressed RAG average (the upper bound); 0.614 Match is COCOM's own score at xi=4 (Table 9).

## Limits

- Only Mistral-7B-Instruct-v0.2, only 5 passages, only English QA. Efficiency was measured only on NQ at batch 16; no seeds or variance.
- Baselines use frozen decoders and single contexts, so the comparison mixes tuning regime with method.
- Internal inconsistencies noted in the extraction: text uses xi=1 in 4.1 but tables use xi=4; the FineWeb subset is described as both 10 million tokens and 10m samples; COCOM xi=128 NQ EM is 0.519 in Table 6 and 0.511 in Table 2; the text gives 1.27x memory reduction at xi=128 while the table's memory figures read 14.2 GB against 18.1 GB.
- Higher compression degrades auto-encoding sharply.

## See Also
- [[Soft Context Compression for RAG (CLaRa and REFRAG)]] — alternative-to
- [[Context-Aware Compression]] — related
- [[LLMLingua Coarse-to-Fine Prompt Compression]] — alternative-to (lexical rather than embedding compression)
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[KILT Benchmark]] — related (supplied the Wikipedia corpus)
