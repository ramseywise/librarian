---
title: "ClashEval Prior Versus Context Benchmark"
tags: [eval, reference]
summary: "ClashEval is a 1,294-question benchmark that perturbs retrieved context to contradict the model's own answer and measures which side the model follows; its headline says models adopt wrong context over 60% of the time, though a table gives a lower figure for one model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wu-2024-clasheval.md
---

# ClashEval Prior Versus Context Benchmark

ClashEval (arXiv 2404.10198, preprint) tests what a model does when the retrieved document disagrees with what it already believes. It has 1,294 questions across 6 domains. Each question's reference document is perturbed to a wrong value, in graded steps, and the model is scored on three rates: accuracy, context bias (follows wrong context when its prior was right) and prior bias (keeps a wrong prior when the context was right).

## Results (self-reported)

- Headline: models adopt incorrect retrieved content over 60% of the time (Table 2 value 0.608).
- For Claude Opus the paper reports accuracy of 74.3%, with context bias at 15.7% and prior bias at 2.1%.
- Across models, the slope of preference for the context against the model's token probability on the prior ranges from -0.1 to -0.45: a more confident prior is overridden less often.
- Calibrating with token-probability percentiles raised GPT-4o accuracy from 0.615 to 0.754 and cut context bias from 0.304 to 0.107.
- Adding documents (k=1 to 5) lowered Opus accuracy from 0.939 to 0.843.

## Limits

- Internal inconsistency: Table 4 lists a context bias of 0.304 for GPT-4o, well under the 60% headline, and the paper does not explain the gap.
- Perturbations are synthetic edits. Models are the 2024 generation. Token probabilities are needed for the calibration method.

## See Also
- [[Knowledge Conflicts Taxonomy]] — prerequisite-for
- [[RAG Evaluation]] — prerequisite-for
- [[Astute RAG]] — related
- [[Sufficient Context Autorater]] — related
