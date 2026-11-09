---
title: "ITER-RETGEN"
tags: [rag, pattern]
summary: "ITER-RETGEN alternates retrieval and generation, using the previous output as part of the next query; with text-davinci-003 it gained up to 8.6 absolute points on four of six datasets with fewer LLM calls than ReAct or Self-Ask (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-shao-2023-enhancing-retrieval-augmented-large-language.md
---

# ITER-RETGEN

ITER-RETGEN (arXiv 2305.15294, preprint) runs T rounds. In each, the retriever fetches the top 5 passages for the question concatenated with the previous round's output, and the model answers with a 3-shot chain-of-thought prompt. An optional distillation step trains the dense retriever's query encoder against a TART re-ranker that sees the first answer. Setup: text-davinci-003, Contriever-MSMARCO, six datasets.

## Results (self-reported)

- Up to 8.6% absolute gains over baselines on four of six datasets.
- T=2 uses 2 LLM calls and 10 paragraphs, against about 2.8 to 3.2 calls and 14 to 16 paragraphs for ReAct and Self-Ask.
- EM undercounts: among 80 sampled cases where EM and the model-judged accuracy disagreed, EM was 0 and accuracy 1 in 98.75%.
- Bamboogle answer recall went from 20.8 to 36.0 between iterations 1 and 2.
- The authors find 65% of failures are retrieval-related.

## Limits

- Black-box text-davinci-003, since retired; code availability is not stated.
- 500-question subsets and a single greedy run. The accuracy judge is text-davinci-003, validated on 80 samples.
- On MuSiQue, Self-Ask comes out ahead.

## See Also
- [[Self-Ask Prompting]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[EfficientRAG]] — alternative-to
- [[HyDE Hypothetical Document Embeddings]] — related
