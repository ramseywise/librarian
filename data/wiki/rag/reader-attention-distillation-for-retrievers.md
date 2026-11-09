---
title: Reader-Attention Distillation for Retrievers
tags: [rag, pattern]
summary: "A Fusion-in-Decoder reader's cross-attention over passages is turned into soft relevance labels, and a bi-encoder retriever is trained to match them with a KL loss, iterating without query-document labels."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-izacard-2020-distilling-knowledge-reader-retriever-question.md
---

# Reader-Attention Distillation for Retrievers

The question is whether a retriever can be trained with no query-document labels by using the reader's attention as a proxy for passage relevance. A [[Fusion-in-Decoder]] reader (T5) is trained on retrieved passages. The cross-attention paid by the first output token to each passage, averaged across that passage's tokens, the layers and the heads, yields one score per passage. A BERT bi-encoder retriever with a shared encoder is then fitted to those scores using a KL loss; it fetches fresh passages and the cycle begins again.

## Results

All numbers are self-reported.

- Starting from BM25 passages, the trained retriever beats supervised DPR on Natural Questions test and TriviaQA test top-20 recall (BERT-base bi-encoder; FiD reader on T5 base); the extraction states the comparison without figures.
- Starting from non-finetuned BERT retrieval leaves Natural Questions test top-20 recall well below DPR; initial BERT recall@20 on dev is 4.8.
- Keeping only the 10 passages the reader attends to most, out of 100 from DPR, costs little exact match relative to feeding all 100 (48.2).
- A T5 large reader, begun from DPR passages, reaches 54.4 exact match on Natural Questions test; FiD-large gets 51.4.
- On Natural Questions validation after one iteration from BM25, the KL objective beats MSE (40.6) and the best max-margin (45.8, gamma 0.2). Mean aggregation over input tokens gave the best recall@5; max over tokens was worse.
- Iterating from BM25 with the reader reinitialised from T5 base each time, dev exact match is 41.2 at iteration 0, peaks at iteration 2, and is 46.2 at iteration 3.
- Starting from BERT passages, dev exact match climbs with iterations but stays below the BM25 start.
- On NarrativeQA test, Rouge-L improves after a single iteration compared with DPR plus FiD.

## Limits

- The authors flag recall@k as a questionable retriever metric because an unrelated passage may hold the answer string.
- The quality of the first retrieval matters; a BERT start does much worse.
- Treating attention as relevance is an assumption, mainly tested through one experiment that picks the top 10 passages.
- No seeds, variance, hardware or compute are given; only T5 base and large are used; which iteration Table 3 reports is unspecified.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Fusion-in-Decoder]] — prerequisite-for
- [[Dense Passage Retrieval (DPR)]] — alternative-to (supervised retriever baseline)
- [[REALM Retrieval-Augmented Pre-Training]] — alternative-to (another label-free retriever training signal)
- [[Syntriever Synthetic Retriever Training]] — related
