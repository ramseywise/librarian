---
title: LLM-R Learned In-Context Example Retriever
tags: [rag, pattern]
summary: "Train a dense retriever to pick few-shot examples by ranking BM25 candidates with a frozen LLM's log-likelihood of the gold output, distilling through a cross-encoder reward model; the paper reports gains over random and BM25 selection on 30 tasks and weaker gains on knowledge-heavy tasks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-wang-2023-learning-retrieve-context-examples-large.md
---

# LLM-R Learned In-Context Example Retriever

Wang, Yang and Wei (preprint, 2023) ask whether a frozen LLM's feedback can train a retriever whose in-context examples beat BM25 or stock embeddings over many tasks and several LLMs.

## Pipeline

1. BM25 pulls 100 candidates for each training example out of a pooled example set (about 6.3M training examples across 30 datasets in 9 task categories).
2. A frozen LLaMA-7B ranks each candidate by the log-likelihood it gives the gold output, `log p(y | x, example input, example output)`.
3. A cross-encoder **reward model** (ELECTRA-base) is trained on the best and worst candidates.
4. A bi-encoder with a shared E5-base encoder is distilled from the reward model, using a KL term and an InfoNCE contrastive term.
5. The loop can repeat with the new retriever. At test time the top-k retrieved examples are placed before the test input.

## Results

Setup for every row: LLaMA-7B both ranks and evaluates, with 8 in-context examples, averaged by task category. The extraction records the direction of each comparison but not most of the point values, so only directions are given here (self-reported).

- Two iterations of LLM-R beat random selection on the 30-task average, and one iteration already beats the best baseline, an EPR re-implementation. BM25 is a strong baseline over random. A third iteration adds nothing over the second.
- Choosing examples by K-means does no better than random (57.0 against 57.9). Zero-shot is far below random few-shot.
- Ablations at one iteration: removing the reward model lowers the average; training it without the positive-label loss costs the most; distilling from raw LLM log-likelihood trails the reward model; starting from BERT-base rather than E5-base costs a little.
- Four held-out tasks (QNLI, PIQA, WSC273, Yelp): LLM-R outscores the runner-up E5-base overall, gaining most on QNLI and falling below E5-base on Yelp.
- Transfer: retrievers trained with LLaMA-7B also beat BM25 on GPT-Neo-2.7B and LLaMA-13B; with gpt-35-turbo the gain is small and not comparable with other rows. The evaluating LLM matters more than the ranking LLM.
- Gains shrink beyond 4 retrieved examples (k from 1 to 16). Retriever size: small is about base, large gives a larger boost.
- Knowledge-intensive tasks gain less, and SQuAD v1 scores under random, since many of its questions share a passage and the retrieved examples are not varied.

## Limits

- Examples are retrieved independently, so interactions between examples are ignored.
- Averaging metrics arithmetically puts generation tasks at a disadvantage, since their ROUGE and BLEU span a narrower range; it also ignores differences in dataset quality.
- The held-out tasks belong to categories also present in training; categories with no overlap are left for future work.
- Only the random baseline has a standard deviation (3 runs); gpt-35-turbo used different templates; NQ has acknowledged train and test overlap.
- Training needs data and about 12 hours of LLaMA-7B ranking, and the gain is small for gpt-35-turbo.

## See Also
- [[UPRISE Universal Prompt Retrieval]] — related (the dataset collection it reuses; cross-task prompt retrieval)
- [[Few-Shot Prompting]] — prerequisite-for
- [[RAG Retrieval Strategies]] — related
- [[Prompt Order Sensitivity and Entropy Probing]] — related
- [[Retrieval-Pretrained Transformer Self-Retrieval]] — related
