---
title: SummHay Benchmark
tags: [eval, concept]
summary: SummHay asks a model to summarise the insights shared across a synthetic 100-document haystack (about 93K tokens) and cite the source documents, scoring coverage, citation and their product; no tested system came near the human estimate of 56.1 (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-laban-2024-summary-haystack.md
---

# SummHay Benchmark

Laban et al. (Salesforce, 2024) built 10 haystacks (5 conversation, 5 news) of about 100 generated documents each, 92 tasks in all. Insights are planted so each appears in at least five documents. The system answers a query with a bullet per insight, citing documents.

## Metrics

Coverage grades each reference insight as 100, 50 or 0. Citation measures the F1 between cited and gold documents, and Joint multiplies the two per insight. Each summary is limited to as many bullets as there are reference insights. An LLM judge replaced manual annotation: GPT-4o correlated 0.716 with humans (human agreement 0.77) at $6.9 against $325, and it overestimates coverage by about 5 points on average.

## Results (self-reported)

- Full-context Joint scores mostly fell between 3 and 21, and Gemini-1.5-pro reached 37.8. Pairing Gemini-1.5-pro with Cohere Rerank 3 gave the best realistic system at 36.0 against a human estimate of 56.1 that comes from 10 summaries in the oracle setting.
- Coverage needs no retrieval for a capable model (Claude 3 Opus 76.2 full against 81.4 oracle), but citation does: 22.3 full against 50.7 oracle. Retrievers kept the top 15K tokens, and 50 RAG systems were run.
- Position bias: GPT-4o Joint 13.8 (relevant documents on top), 24.1 (bottom), 11.4 (random); Gemini preferred the top (47.1 against 38.9).
- Observed failure modes, by inspection only: off-topic insights, over-general insights, hallucinated insights.

## Limits

- The human figure is not an upper bound. Documents are independently generated, with no disagreement and factoid-style insights. Only closed models, English, and relevance rather than factuality.
- The oracle citation F1 at the 15K budget is 0.84, capping RAG. The extraction notes the section 5.2 text reverses the Random and Oracle labels relative to Table 2, and that its tables say tokens where words are meant.

## See Also
- [[Evaluating Context]] — prerequisite-for
- [[Context Retrieval Strategies]] — related
- [[Long-Context Prompting]] — related
- [[Why Context Is Finite]] — related
