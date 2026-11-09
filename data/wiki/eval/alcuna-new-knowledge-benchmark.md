---
title: ALCUNA New Knowledge Benchmark
tags: [eval, reference]
summary: "ALCUNA is a benchmark of questions about artificial organisms that cannot be in any training set, testing how well LLMs use new in-context knowledge; multi-hop association with existing knowledge is hardest for all four models tested (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yin-2023-alcuna.md
---

# ALCUNA New Knowledge Benchmark

Yin, Huang and Wan (2023 preprint) ask how well LLMs can understand new knowledge, tell it apart from old, and reason with it when it is supplied in context and cannot be in the training data. The benchmark measures in-context use of new knowledge. It runs no retriever.

## How it is built

**KnowGen** creates artificial entities from the Encyclopedia of Life taxonomy through four operations: heredity, variation, extension and dropout. ALCUNA contains 84,351 questions on 3,554 artificial organisms. Entity properties enter the prompt as structured JSON, and template-generated questions probe three abilities: understanding (KU), telling an entity apart from its parent (KD) and linking multiple hops to existing knowledge (KA). Template questions and recall filtering follow the earlier LAMA probe; the models tested are ChatGPT plus three open models, Alpaca-7B, Vicuna-13B and ChatGLM-6B.

## Results

Self-reported, few-shot vanilla prompting on the filtered set with structured in-context knowledge unless stated.

- ChatGPT averages 64.37 but only 41.52 on knowledge association. Averages for the open models: Alpaca 7B 35.09, Vicuna 13B 42.74, ChatGLM 6B 42.56. Association is the hardest ability for all four models across all four prompt settings.
- KA questions: supplying the entities on the reasoning chain raises accuracy (ChatGLM from 27.47 to 44.43; Vicuna from 30.10 to 33.25), whereas irrelevant entities reduce it (ChatGLM 18.56).
- KD questions: putting the parent entity's knowledge in context hurts differentiation (ChatGLM 41.42 to 24.71; Vicuna 46.76 to 35.04); irrelevant entities cost less. Confusion grows with property overlap between an entity and its parent; only ChatGPT is nearly insensitive.
- For all three open models, JSON input outperforms natural-language input (ChatGLM average 42.56 against 20.54).
- Chain-of-thought and few-shot prompting raise the average in most cases, though ChatGPT's CoT leaves association unfixed (37.88 few-shot CoT against 41.52 vanilla).

## Limits

- Biology taxonomy only; other domains are untested. Just four models were tested, three being small open ones, and none is GPT-4-class.
- Questions come from templates and are scored by string matching; a human check of 100 questions found 98 percent (one-hop) and 95 percent (multi-hop) correct.
- Keeping only entities whose parent was recalled perfectly leaves a different number of questions for each model, so comparisons use the intersection.

## See Also
- [[Knowledge Conflicts Taxonomy]] — related
- [[Context-Faithful Prompting]] — related
- [[LAMA Knowledge Probe]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — related
- [[RAG Evaluation]] — prerequisite-for
