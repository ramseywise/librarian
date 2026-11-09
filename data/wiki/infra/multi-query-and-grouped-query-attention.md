---
title: Multi-Query and Grouped-Query Attention
tags: [infra, concept]
summary: "Sharing one key-value head (multi-query) or a few key-value groups (grouped-query) across all query heads shrinks the key-value cache and the data loaded per decoding step; grouped-query can be reached by uptraining a multi-head checkpoint on a small fraction of pre-training compute."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-shazeer-2019-fast-transformer-decoding.md
  - data/raw/papers/2026-11-07-ainslie-2023-gqa.md
  - data/raw/papers/2026-11-07-deepseek-ai-2024-deepseek-v2.md
---

# Multi-Query and Grouped-Query Attention

Incremental decoding re-reads the stored keys and values at every step. Shazeer analyses batched incremental decoding for multi-head attention and gets a ratio of memory traffic to arithmetic that scales as Theta(n/d + 1/b); sharing keys and values divides the n/d term by the head count h (the derivation assumes equal source and target length n, per-head key and value width d/h, and n at most d). Multi-query attention keeps h query heads but gives all heads one shared set of keys and values; the feed-forward layer is widened to keep parameters equal.

## Multi-query attention (Shazeer 2019)

- Setup for all numbers in this list: WMT14 EN-DE, a 211M-parameter 6-layer encoder-decoder, one TPUv2 (8 cores); decoding numbers use incremental greedy inference at batch 1024 with source and target length 128.
- Amortized incremental decoder time per token is about 12x lower than multi-head (self-reported); under beam-4 search the decoder is about 6x faster (self-reported).
- One decoder step costs 3.9 ms where multi-head costs 47 ms, and the encoder pass is a little quicker too, 195 ms against 222 ms (self-reported).
- Cost per training step barely moves, 13.0 against 13.2 us per token, with 32,768 input and 32,768 target tokens in each step (self-reported).
- Quality drops a little: dev BLEU 26.7 to 26.5 and Billion-Word LM perplexity 29.9 to 30.2 (self-reported). Cutting to one head (h=1, dk=dv=128, dff 6784) costs more, with dev BLEU 25.8 (self-reported).

## Grouped-query attention (Ainslie et al. 2023)

Grouped-query attention sits between the two extremes, with a middle count of key-value heads. GQA-G has G groups; GQA-1 is multi-query and GQA-H is multi-head. A public T5.1.1 multi-head checkpoint is converted by mean-pooling its key and value projection matrices into 1 or G heads, and the model then continues pre-training for a fraction alpha of its original step count (uptraining). Mean pooling beat selecting the first head, which beat random initialisation, in a T5-Large to MQA ablation at alpha=0.05 (values only in a figure).

- Setup: T5-XXL, alpha=0.05, average dev score across five summarisation sets (CNN, arXiv, PubMed, MediaSum and MultiNews, scored by ROUGE-1), WMT translation (BLEU) and TriviaQA (F1); greedy decoding; time per sample on each TPUv4 chip. The extraction gives these as comparisons without the table values: GQA-8-XXL is close to MHA-XXL on quality and close to MQA on time, while MQA-XXL scores lower than MHA-XXL (self-reported).
- An MHA-Large model (0.37 s per sample) is slower and worse than the uptrained MQA-XXL (self-reported).
- On T5-XXL, uptraining with alpha=0.05 takes roughly 600 TPUv3 chip-days (self-reported).
- Right after conversion GQA already performs reasonably whereas MQA needs uptraining first; both improve with 5% uptraining and the gain tapers by 10% (T5-XXL, read from a figure).
- MQA trained from scratch (T5-Large) showed loss spikes and diverged on long-input fine-tuning, while uptrained GQA appeared stable (T5-Large, multiple runs, count not stated).
- The paper's design argument is that going from multi-head to multi-query cuts the key-value cache size and the data loaded by a factor of H (a claim, not measured).

## Comparison inside DeepSeek-V2

In dense models of about 7B parameters trained on 1.33T tokens, with layers adjusted so parameter counts match, MHA scored 45.2 on 5-shot MMLU against 41.2 for GQA with 8 groups and 37.9 for MQA (setup from the DeepSeek-V2 report; self-reported). That report presents this as motivation for [[Multi-Head Latent Attention]].

## Limits

- Shazeer's experiments use one small configuration (a 211M WMT14 EN-DE model and a 192M Billion-Word model, each trained for a few hours) and include no large-scale or decoder-only quality tests; single runs, no variance; the speed test uses fixed padded shapes.
- Ainslie et al. test only encoder-decoder models; no GQA-XXL was trained from scratch, so how uptraining compares with scratch training is unknown; ROUGE is a flawed measure; ablation values appear only in figures and on three tasks; no variance except a 3-run average for unstable MQA tasks.
- The 7B dense comparison is single-run and from a paper whose subject is a different method.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Multi-Head Latent Attention]] — alternative-to (compresses the key-value cache by a latent projection instead of sharing heads)
- [[FlashAttention and FlashAttention-2]] — related (FlashAttention-2 supports MQA and GQA by index manipulation)
- [[LLM Inference Economics]] — related
- [[Disaggregated Prefill-Decode Serving]] — related (KV size per token)
- [[Partitioning Layouts for Transformer Inference]] — extends (shards multiquery attention over batch)
- [[Medusa Decoding Heads]] — related
