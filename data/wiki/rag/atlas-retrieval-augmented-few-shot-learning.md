---
title: Atlas Retrieval-Augmented Few-Shot Learning
tags: [rag, concept]
summary: Atlas jointly pre-trains a Contriever retriever and a T5 Fusion-in-Decoder reader, so a retrieval-augmented model fine-tuned on few examples competes with far larger prompted LLMs on knowledge tasks, with an updatable and compressible index.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-izacard-2022-atlas.md
---

# Atlas Retrieval-Augmented Few-Shot Learning

Atlas (Izacard et al.) asks whether few-shot learning on knowledge-intensive tasks needs knowledge stored in parameters, or whether a jointly pre-trained retrieval-augmented model can cover it. The authors' hypothesis is that memorisation can be moved to a non-parametric index.

## Mechanism

A Contriever dual encoder (BERT-base) feeds a T5 Fusion-in-Decoder reader. Both are pre-trained jointly on unlabelled text with masked language modelling plus a retriever loss derived from the reader, then fine-tuned per task. Perplexity Distillation (PDist) trains the retriever to match a distribution over the top-K documents built from how well each document helps the reader predict the output (KL between retriever and reader-posterior). Query-side fine-tuning freezes the document encoder and updates just the query encoder, which means document embeddings never need refreshing. A further loss, Leave-one-out Perplexity Distillation (LOOP), scores each document by the drop in output probability when that document is removed.

## Results

Self-reported.
- With 64 training examples (30 steps of query-side tuning, 40 passages), Atlas-11B outperforms prompted PaLM-540B on NQ by nearly 3 points. Using a Dec 2018 Wikipedia index instead, Atlas-11B scores 45.1 in the 64-shot NQ setting and 64.0 on full NQ.
- Atlas follows answers that changed when its index is swapped from 2017 to 2020 Wikipedia with no retraining, which closed-book T5 cannot do (248 fine-tuning and 806 test questions, small and templated).
- With product quantisation the Wikipedia index shrinks from 49 GB to 4 GB and accuracy barely changes (Atlas-3B, 64-shot NQ).
- Ablations at 3B: the four retriever losses show no systematic difference (ADist 43.0, EMDR2 43.3, LOOP 43.7, PDist 45.7); joint pre-training helps a lot; freezing the retriever hurts; at 64 shots query-side tuning is best, at 1024 shots standard tuning is.
- MMLU: beats closed-book T5 at every size; Atlas-11B 5-shot with de-biased inference (4 cyclic permutations, 4x inference cost) exceeds GPT-3 with 15x fewer parameters. Chinchilla 5-shot (67.5) beats Atlas (47.9).
- Per a worked cost model, re-embedding the full index every 1000 steps adds about 30% overhead, and re-ranking ten times as many documents as the reader consumes adds about 10%.

## Limits

- The headline compares fine-tuning (Atlas) against in-context prompting by PaLM, Chinchilla, Gopher and GPT-3, so method differs along with size.
- The ablations are single 3B runs over three tasks, with no error bars. MMLU 5-shot alone was run repeatedly (std 0.5), and that used a slightly different index.
- KILT numbers cannot be compared directly to those on the original datasets; MMLU leakage was estimated for CCNet only.
- Hardware, wall-clock and seeds are unreported; the 11B result relies on an index that can reach 587 GB in fp16.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[RAG Sequence and RAG Token]] — prerequisite-for
- [[Contriever Unsupervised Contrastive Retrieval]] — prerequisite-for
- [[RA-DIT Dual Instruction Tuning]] — related
