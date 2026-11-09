---
title: "Astute RAG"
tags: [rag, pattern]
summary: "Astute RAG has the model write its own passages, merge them with retrieved ones while tagging sources, and answer with a confidence per group; on the authors' 1,042-question benchmark it beat plain RAG with Claude and Gemini (self-reported), with no gain for one 12B model."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wang-2024-astute-rag.md
---

# Astute RAG

Astute RAG (arXiv 2410.07176, preprint) targets two problems it measured: retrieved passages often lack the answer, and the model's own knowledge sometimes conflicts with the retrieved text. With Google Search results for 1K sampled questions, roughly 70% of retrieved passages did not directly contain the answer. Claude 3.5 Sonnet's answers with and without retrieval conflicted on 19.2% of cases, and the internal answer was right in 47.4% of those and the external one in 52.6%.

The method has three steps, run as up to three calls (the last two can be merged). First, the model generates up to a fixed number of its own passages, told to say "I don't know" when unsure. Second, source-aware consolidation merges consistent passages, separates conflicting ones, drops irrelevant ones, and keeps tags for memory versus external retrieval and the original passage numbers. Third, finalization scores each answer group with a confidence and picks one. Defaults are one iteration and one generated passage.

## Results (self-reported)

- Own benchmark of 1,042 short-form questions from NQ, TriviaQA, BioASQ and PopQA, each with 10 web passages, zero-shot, string-match accuracy. Claude: Astute RAG 61.7, RAG 55.5, no retrieval 54.5. Gemini 1.5 Pro: 59.2, 53.7 and 51.3. Mistral-Large: 59.9, 54.7 and 51.1. Mistral-Nemo: 51.3, 48.3 and 40.2, where the best baseline (Self-Route, 51.2) is nearly tied.
- On Claude, plain RAG scored below no retrieval on NQ (44.4 against 47.1) and TriviaQA (76.7 against 82.0) and above it on BioASQ (58.0 against 50.4) and PopQA (36.0 against 29.8).
- The authors report cost under 5% extra tokens and calls for over 11% improvement over RAG (read from charts, Claude).
- Source labels matter little on Gemini: 59.2 with them, 58.6 without.
- Reordering passages moved plain RAG on Claude between 54.51 and 55.66 and Astute RAG between 61.42 and 62.00.

## Limits

- The benchmark is the authors' own, with no human-annotated passage relevance, single runs and no variance.
- The authors concede the method relies on models with strong instruction following and reasoning, and long inputs are untested.
- Mistral-Nemo gains are about zero against the best baseline; the worst-case and per-precision claims rest on charts, with no values in the text.
- The judge for intermediate steps (98.2% and 95.0% accurate, self-reported) sees the correct answer and its model is not specified.
- Models date from mid-2024.

## See Also
- [[Knowledge Conflicts Taxonomy]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[ClashEval Prior Versus Context Benchmark]] — related (measures the same prior-versus-context tension)
- [[CRAG Corrective Retrieval Evaluator]] — alternative-to
