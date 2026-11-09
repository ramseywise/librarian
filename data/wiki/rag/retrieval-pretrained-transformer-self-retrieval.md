---
title: Retrieval-Pretrained Transformer Self-Retrieval
tags: [rag, concept]
summary: "RPT trains a retriever jointly with the LM from scratch, taking queries from the LM's own hidden states and supervising it with a scoring LM; on four long-document sets it lowers perplexity against a Transformer-XL and a BM25 RETRO."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-rubin-2023-retrieval-pretrained-transformer.md
---

# Retrieval-Pretrained Transformer Self-Retrieval

The Retrieval-Pretrained Transformer (RPT, Rubin and Berant) asks whether a retriever can be a native part of the language model, trained with it from scratch, and whether supervising it with a meaning-based signal does better than a word-matching one. Each document is split into 64-token chunks. For each chunk the model retrieves K earlier chunks of the same document, scoring them with a learned bilinear function over pooled states from the lower decoder layers, and fuses them with RETRO-style chunked cross-attention in the upper layers.

## Supervision from a scoring LM

BM25 proposes 20 candidates for each chunk. A frozen Pythia 1.4B scores each candidate by the log of its effect on the probability of the next chunk, relative to using only the two preceding chunks; candidates with a score above 0 are positives. A LambdaRank loss trains the retriever alongside the LM loss. Neighbor gating and scheduled sampling are added to keep training stable.

## Results (self-reported)

Setup for all: 242M parameters, 500K steps, 2 neighbours, the authors' own implementations of the baselines.

- Test perplexity of RPT-Sem is 2.77 on ArXiv, 2.17 on CodeParrot, 10.96 on PG19 and 13.91 on Books3. The Transformer-XL baseline scores 3.11, 2.30, 11.48 and 15.00 on the same sets; RETRO with BM25 scores 2.94, 2.17, 11.44 and 14.60.
- Semantic supervision beats lexical supervision: RPT-Lex lands at 2.92, 2.23, 11.59 and 14.32 in the same order. Average Precision@2 is 25.2% for BM25, 23.2% for RPT-Lex and 30.0% for RPT-Sem.
- Replacing the jointly trained retriever with a separately trained DPR-style one hurts on every dataset; Books3, for instance, goes from 13.91 up to 14.66.
- Without neighbor gating, Books3 perplexity climbs from 13.91 to 18.68; without teacher forcing, PG19 goes from 10.96 to 13.10.
- With the scoring LM choosing neighbours as an oracle, Books3 drops from 13.87 to 12.74 while PG19 drops from 10.92 to 10.26, so retriever quality still holds the model back.
- Training takes 1.51x the time per update of the Transformer-XL baseline, against 1.35x for RETRO with BM25.

## Limits

- Candidates come only from earlier chunks in the same document, which makes the index the context itself; web-scale corpora are not tried, and the authors list scaling and corpus construction as open problems.
- The models are small (242M parameters, 65B tokens), baselines are the authors' own implementations, runs are single, with no confidence intervals; the main metric is perplexity and no downstream or factuality result is given.
- Supervision only reorders the 20 BM25 candidates, so recall is capped by BM25; a frozen scoring LM is required; Books3 is not released.

## See Also
- [[RETRO Chunked Cross-Attention Retrieval]] — prerequisite-for
- [[kNN-LM Nearest Neighbor Language Models]] — related (test-time-only retrieval)
- [[In-Context RALM and REPLUG]] — related (scoring-LM signals reused for reranking and retriever tuning)
- [[LLM-R Learned In-Context Example Retriever]] — related (also supervises a retriever with an LM score)
