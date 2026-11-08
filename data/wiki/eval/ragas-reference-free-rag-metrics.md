---
title: Ragas Reference-Free RAG Metrics
tags: [eval, rag, pattern]
summary: "Ragas scores a RAG pipeline on faithfulness, answer relevance and context relevance by prompting gpt-3.5-turbo-16k, with no reference answers; on the 50-question WikiEval set it agreed with human pairwise preference 0.95, 0.78 and 0.70 of the time, above two direct-prompting baselines (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-es-2023-ragas.md
---

# Ragas Reference-Free RAG Metrics

Es et al. (arXiv 2309.15217, 2023, preprint) ask how a retrieval-augmented generation pipeline can be evaluated without ground-truth reference answers. Ragas is their suite of three reference-free metrics (faithfulness, answer relevance, context relevance) and WikiEval, a dataset of human judgements of the same three aspects. Their hypothesis is that prompted reference-free metrics align with human judgement better than direct LLM scoring or ranking.

## Method

The three metrics are computed by prompting gpt-3.5-turbo-16k, with ada-002 embeddings added for answer relevance. They are validated on WikiEval (50 Wikipedia pages on post-2022 events) by pairwise agreement with human annotators, against two prompting baselines, GPT Score and GPT Ranking.

## Results (self-reported)

Setup for all rows: WikiEval, pairwise comparison of two answers or two contexts, agreement with human annotators, metrics computed with gpt-3.5-turbo-16k.

| Aspect | Ragas | GPT Score | GPT Ranking |
|---|---|---|---|
| Faithfulness | 0.95 | 0.72 | 0.54 |
| Answer relevance | 0.78 | 0.52 | 0.40 |
| Context relevance | 0.70 | 0.63 | 0.52 |

Context relevance is the weakest dimension; the authors observe that ChatGPT struggles to pick the crucial sentences, especially from longer contexts. Two annotators agreed on about 95% of cases for faithfulness and context relevance and about 90% for answer relevance, before discussion.

## Limits

Only 50 questions from Wikipedia, and the task is a pairwise choice against deliberately degraded alternatives, not absolute scoring. The judge is a single closed model with no variance, seeds or significance reported. Answer relevance ignores factuality by design. The paper defines no context recall or context precision, and later Ragas versions differ from it, so the metric definitions on [[RAG Eval Metrics Suite]] are not these.

## See Also
- [[RAG Eval Metrics Suite]] — alternative-to (a different metric set for the same pipeline)
- [[RAGChecker]] — alternative-to (a claim-level metric set that also reports Ragas metrics, in its own setup)
- [[GPTScore]] — related (another prompted metric; the paper's GPT Score baseline is a different, direct ChatGPT scoring)
- [[LLM-as-Judge Evaluation]] — extends (reference-free judging for RAG)
