---
title: "LongCite and LongBench-Cite"
tags: [rag, pattern]
summary: "LongCite trains long-context models to give sentence-level citations using synthetic data built by a coarse-to-fine pipeline, and LongBench-Cite scores citation quality; the 8B model reached citation F1 72.0 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhang-2024-longcite.md
---

# LongCite and LongBench-Cite

LongCite (arXiv 2409.02897, preprint) addresses long-context answers that carry no verifiable citations. Training data comes from a pipeline the paper calls CoF: the model answers first, chunks are retrieved for the answer, chunk-level citations are added, sentence spans are extracted from the cited chunks, and instances with under 20% cited statements are dropped (50k documents gave 44,600 instances). Models were fine-tuned on this data. LongBench-Cite is the evaluation: correctness plus citation recall, precision and F1, judged by GPT-4o.

## Results (self-reported)

- Citation F1: LongCite-8B 72.0 and LongCite-9B 69.2. CoF on GLM-4 scored F1 65.8 with correctness ratio 100%, while a retrieve-then-answer variant (RAC-S) scored F1 79.1 with correctness ratio 79%.
- Training with citations raised correctness: ratio 107% for 8B and 109% for 9B against the same models trained without citations.
- Judge agreement with human labels for citation precision: kappa 0.655 for the GPT-4o judge against 0.146 for the ALCE metric.
- Evaluation cost about $4 for correctness and $25 for citation scoring.

## Limits

- The paper has no limitations section. The GPT-4o judge scores below human annotators, which the authors attribute to unresolved pronouns in cited snippets.
- Coarse citation granularity inflates both recall and precision (seen on GovReport).
- Inputs are capped at 128k tokens; the benchmark has about 1,250 examples, and the LongBench-Chat part has 50 queries.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[RAG Eval Metrics Suite]] — related
- [[Long-Form QA Evaluation Hurdles]] — related
- [[Self-Reasoning Retrieval-Augmented Model]] — related (both train models to cite evidence)
