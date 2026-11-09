---
title: Gorilla and APIBench
tags: [harness, concept]
summary: A LLaMA-7B fine-tuned on instruction-API pairs, optionally with a retrieved API document in the prompt, and the APIBench set of 1,645 ML-hub APIs scored by AST sub-tree matching; reported to hallucinate less than GPT-4 zero-shot (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-patil-2023-gorilla.md
---

# Gorilla and APIBench

Gorilla (preprint, 2023) tests whether a small fine-tuned model can write correct API calls over a large, changing API set. The data comes from model cards on three ML hubs (HuggingFace, Torch Hub and TensorFlow Hub), 1,645 APIs in all; GPT-4 writes 10 instructions per API by Self-Instruct, and LLaMA-7B is fine-tuned on the instruction-API pairs. In *retriever-aware training* the user prompt is followed by "Use this API documentation for reference" and a retrieved API document in JSON. Output is scored by AST sub-tree matching against the API database. The paper defines a **hallucination** as a call matching no sub-tree of any database API, meaning an entirely imagined tool, which it separates from calling a real API incorrectly.

## Results (self-reported)

- Zero-shot with no retriever, Gorilla beats GPT-4 on all three hubs. On Torch Hub the paper states a 20.43% advantage, which the extraction notes is 59.13 against 38.70, so points rather than percent.
- Hallucination on HuggingFace zero-shot: GPT-4 37.16%, Gorilla 10.95%. Across all three hubs, hallucination is lower for GPT-3.5 than for GPT-4, which the authors tentatively put down to RLHF.
- Retriever quality matters. A Gorilla trained without a retriever drops from 71.68 to 17.04 on HuggingFace with BM25 top-1. Tested with the oracle, a model trained with the oracle retriever beats one trained without a retriever, by 12.37% on Torch Hub and by 23.46% on HuggingFace; real retrievers, however, cost it 29.20% (GPT-Index) and 52.27% (BM25).
- Given the oracle document on HuggingFace, Gorilla reaches 91.26 and GPT-3.5 reaches 89.71.
- With accuracy constraints (the 65.26% of Torch Hub with an accuracy in the model card), Gorilla has the best zero-shot accuracy and matches GPT-3.5 when retrieval is used.
- Two qualitative examples show the model following a test-time documentation change (ResNet-50 to ResNet-101, or a different registry); no quantitative evaluation.

## Limits

- The HuggingFace comparison is not like-for-like: the baselines are scored on domain name alone, whereas Gorilla is scored on the complete API match.
- The test sets are held-out slices of the Self-Instruct data that also supplied the training set, which makes them in-distribution; no seeds, repeats, intervals or decoding settings are reported.
- Only ML model-hub APIs, and example code is not executed, so execution is not evaluated.
- Internal inconsistencies noted by the extraction cover dataset counts (94 or 95 for Torch Hub, 626 or 696 for TF Hub, 16,450 against over 11,000 pairs) and Table 2 column headings that look transposed relative to Table 1.
- The closed models compared are 2023 snapshots (claude-v1, gpt-3.5-turbo-0301, gpt-4-0314).

## See Also
- [[ToolLLM ToolBench and DFSDT]] — related (also evaluated on APIBench)
- [[API-Bank]] — alternative-to
- [[Tool Design as Harness Surface]] — related
- [[Dynamic Tool Discovery]] — related
