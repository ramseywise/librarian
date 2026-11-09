---
title: "RAGEval and DragonBall"
tags: [eval, reference]
summary: "RAGEval generates scenario-specific RAG test sets from a schema and scores answers with Completeness, Hallucination, Irrelevance, Recall and EIR; DragonBall is the resulting 6,711-question finance, law and medical set in Chinese and English (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhu-2024-rageval.md
---

# RAGEval and DragonBall

RAGEval (arXiv 2408.01262, preprint) generates evaluation data in stages: a schema, a configuration, documents, question and answer pairs, reference passages and finally key points. Entities are fictional. Metrics: Completeness (key points covered), Hallucination (contradicting key points), Irrelevance (1 minus completeness minus hallucination), retrieval Recall (a reference counts only if all its sentences appear in the retrieved text) and EIR. DragonBall holds 6,711 questions in finance, law and medical for Chinese and English under a CC-BY-NC licence, across 7 question types (information integration is 22.21%, unanswerable 7.51%).

## Results (self-reported)

- 9 generators, 50 questions per scenario and language, BGE-M3 top 5, chunk 512. On Chinese, GPT-4o has Completeness 79.13 with ROUGE-L 21.30 and BLEU 8.70, while Baichuan-2-7B-chat has Completeness 60.25 but higher ROUGE-L (38.30) and higher BLEU (21.55).
- Human agreement on 210 questions with 3 annotators: an absolute difference of 1.67% and Fleiss' Kappa of 0.7686.
- Retrievers (Llama3-8B-Instruct, 2100 queries), Chinese: BM25 has recall 74.21 and completeness 71.89; BGE-M3 has recall 72.94 and completeness 70.24. Raising top-K from 2 to 8 lifted Chinese recall from 49.18 to 78.94.
- Chunk size and K (finance English, Llama3-8B), settings 128 with K=20, 256 with K=10 and 512 with K=5. FQ scored 86.00, 92.00 and 86.00; MRQ 76.00, 78.70 and 79.03; NCQ 79.33, 68.67 and 63.33. The extraction notes that 128-20 has the highest average in all 6 cells, which the paper does not state.

## Limits

- Internal inconsistency: the BGE-M3 row in Table 2 (70.24) differs from the Table 3 top-K 5 row (70.38).
- The judge model is not named. The human check covered only Baichuan-2-7B outputs.
- Data is synthetic with fictional entities; single runs. The Table 3 relative percentages are the authors' computations.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[RAG Eval Metrics Suite]] — related
- [[Ragas Reference-Free RAG Metrics]] — alternative-to
- [[ARES Automated RAG Evaluation]] — alternative-to
