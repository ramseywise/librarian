---
title: KnowledGPT Unsupervised Knowledge Selection
tags: [rag, concept]
summary: "KnowledGPT places a learned sentence selector in front of GPT-2 for knowledge-grounded dialogue, trained without selection labels via pseudo ground truth and REINFORCE; it beat truncating the knowledge on two small datasets."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zhao-2020-knowledge-grounded-dialogue-generation-pre.md
---

# KnowledGPT Unsupervised Knowledge Selection

Zhao et al. (EMNLP 2020) address document-grounded dialogue when retrieved knowledge exceeds the generator's input limit and no selection labels exist. On Wizard of Wikipedia each context comes with 61.2 sentences (1625.6 tokens) of retrieved knowledge on average, more than GPT-2's 1024-token limit, and truncating it removed the ground-truth sentence in most test examples.

## Mechanism

Ahead of GPT-2 sit a knowledge encoder built on BERT that reads the dialogue context, and an LSTM selector that works sequentially. At each step the selector adds one sentence, up to a limit Tmax, and GPT-2 then writes the reply from the context and the chosen sentences. Training starts with a warm-up on pseudo ground truth derived from the human response. It then alternates two steps: REINFORCE for the selector (reward is the unigram F1 of the GPT-2 reply, with a mean baseline), and a curriculum step that trains GPT-2 on a blend of pseudo and selected knowledge.

## Results (self-reported)

Setup: GPT-2 117M, greedy decoding; the GPT-2trunc baseline averages 8 runs, each with the knowledge in random order.

- On Wizard Test Seen (Tmax = 1) it has higher unigram F1 than GPT-2trunc, and on CMU DoG (Tmax = 2) it outperforms the strongest baselines, DRD and GPT-2trunc, which tie at 10.8.
- Selection accuracy without human labels exceeds SKT, which uses labels, mainly on unseen topics; absolute accuracy is low (28.0 and 25.4).
- Removing the warm-up on pseudo ground truth hurts Wizard F1 most; larger Tmax lowers perplexity but F1 drops; GPT-2 345M gives no real F1 gain over 117M.
- With the ground truth forced into the input (an oracle), truncated-GPT-2 F1 declines when the token limit is raised from 128 to 1024.
- Human evaluation: leads on knowledge relevance with 3 annotators.

## Limits

- Just two small datasets built by crowd workers, evaluated by word overlap with one human reply, and only GPT-2 at 117M and 345M parameters.
- The forced-gold sweep is an oracle. On CMU DoG the response weakly depends on the document, the warm-up helps little and perplexity is worse than GPT-2trunc.
- Seeds, hardware, joint step count and curriculum constants are not reported; no code linked. Retrieval itself is not studied.

## See Also
- [[RAG Reranking]] — alternative-to (selection by a trained scorer)
- [[Context Window Budgeting]] — related
- [[RECOMP Compression and Selective Augmentation]] — related
- [[Self-RAG Reflection Tokens]] — related
