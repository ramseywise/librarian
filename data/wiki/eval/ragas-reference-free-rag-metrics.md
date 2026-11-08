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

Each metric comes from prompts to gpt-3.5-turbo-16k, and answer relevance also uses ada-002 embeddings. Validation uses WikiEval, built from 50 Wikipedia pages about events after 2022: a metric is scored by how often its pairwise choice matches the human annotators', alongside two prompting baselines, GPT Score and GPT Ranking.

## Results (self-reported)

Setup for every row: WikiEval, a pairwise choice between two answers or two contexts, scored as agreement with human annotators, all metrics run on gpt-3.5-turbo-16k.

| Aspect | Ragas | GPT Score | GPT Ranking |
|---|---|---|---|
| Faithfulness | 0.95 | 0.72 | 0.54 |
| Answer relevance | 0.78 | 0.52 | 0.40 |
| Context relevance | 0.70 | 0.63 | 0.52 |

Context relevance is the weakest dimension; the authors observe that ChatGPT struggles to pick the crucial sentences, especially from longer contexts. Before discussion, two annotators agreed on roughly 95% of faithfulness and context-relevance cases and roughly 90% of answer-relevance cases.

## Limits

Only 50 questions from Wikipedia, and the task is a pairwise choice against deliberately degraded alternatives, not absolute scoring. The judge is a single closed model with no variance, seeds or significance reported. Answer relevance ignores factuality by design. Context recall and context precision are not defined in the paper, and later Ragas versions differ from it, so metric definitions elsewhere (such as on [[RAG Eval Metrics Suite]]) should not be read as these.

## See Also
- [[RAG Eval Metrics Suite]] — alternative-to (a different metric set for the same pipeline)
- [[RAGChecker]] — alternative-to (a claim-level metric set that also reports Ragas metrics, in its own setup)
- [[GPTScore]] — related (another prompted metric; the paper's GPT Score baseline is a different, direct ChatGPT scoring)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (reference-free judging for RAG)
