---
title: Promptagator Few-Shot Synthetic Retrieval Data
tags: [rag, pattern]
summary: Promptagator prompts a large LLM with up to 8 task examples to write queries for a corpus, filters the pairs by round-trip consistency, and trains a small task-specific retriever on the survivors.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-dai-2022-promptagator.md
---

# Promptagator Few-Shot Synthetic Retrieval Data

Promptagator (Dai et al.) asks whether a handful (at most 8) of examples for one task, expanded through an LLM that writes queries, can produce a dense retriever for that task which outperforms retrievers built on big supervised collections like MS MARCO. The authors argue that tasks differ in search intent and query distribution, so one or two QA datasets generalise poorly.

## Mechanism

FLAN 137B is prompted with a task description and up to 8 query-document examples, and writes queries for as many as 1M corpus documents. A dual encoder is first trained on the resulting pairs and used to filter them by round-trip consistency: a pair survives only when its source document ranks first for its query. The encoder is then fine-tuned on the surviving pairs. The same synthetic data also trains a 110M cross-attention reranker, called Promptagator++.

## Results

Self-reported; 11 BEIR datasets excluding MS MARCO, NQ and Quora; 110M T5-base dual encoder.
- Few-shot (2-8 examples per task): average nDCG@10 of 47.8, above BM25 and above SPLADE v2 and ColBERT v2. Zero-shot with a universal prompt: 45.5.
- Promptagator++ reranking the top 200: 52.8 few-shot, 49.9 zero-shot.
- Filtering by round trip helps on 8 of the 11 datasets (+2.5 points on average), but hurt NFCorpus and SciFact, the datasets with the fewest generated queries; the authors guess overfitting.
- For a plain dual encoder, eight examples plus the LLM reach about the level of 50k labelled MS MARCO examples (read from a figure caption).
- Touche-2020 few-shot is 34.5 against BM25 at 36.7. Climate-FEVER is lower few-shot (16.8) than zero-shot (21.4); using the FEVER prompt gives 24.0.
- Taking NQ and Quora out of FLAN's training lowers the few-shot average, 48.5 down to 47.0.
- Generation cost: 58.46M queries (29.23M x 2 prompts), 610M words.

## Limits

- Data efficiency (how many generated pairs a task needs) and prompt sensitivity are not studied.
- A fixed K=1 filter may discard good pairs; query-specific K is future work.
- Poor few-shot examples hurt, as on Climate-FEVER.
- Single runs, no seeds or significance tests; optimizer and learning rate not reported.
- FLAN 137B is not public and generation is expensive; no wall-clock or hardware stated.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Syntriever Synthetic Retriever Training]] — alternative-to (another synthetic-data route to a retriever)
- [[Synthetic Dataset Generation for RAG Eval]] — related
- [[ARES Automated RAG Evaluation]] — extends (reuses its query-filtering approach)
