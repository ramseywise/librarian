---
title: "CRAG Corrective Retrieval Evaluator"
tags: [rag, pattern]
summary: "CRAG scores each retrieved document with a small fine-tuned evaluator and picks one of three actions (use and refine, discard and search the web, or both); on four QA sets with LLaMA2-7B generators it lifted accuracy over plain RAG (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yan-2024-corrective-retrieval-augmented-generation.md
---

# CRAG Corrective Retrieval Evaluator

CRAG (arXiv 2401.15884, preprint) puts a retrieval evaluator between the retriever and the generator. The evaluator is a fine-tuned T5-large (0.77B parameters) that scores each question and document pair separately, about 10 documents per question, on a scale from -1 to 1. It was trained on PopQA signals and used unchanged on the other sets. Two thresholds, set empirically per dataset, pick the action. **Correct**: some document clears the upper threshold, so the documents are cut into strips, filtered and recomposed. **Incorrect**: every document is below the lower threshold, so the retrieved set is discarded, GPT-3.5 Turbo turns the question into up to three keywords and a Google web search supplies the knowledge. **Ambiguous**: anything else, which uses both sources.

## Results (self-reported)

- Evaluator accuracy on PopQA retrieval results is 84.3 for the T5 evaluator against 58.0, 62.4 and 64.7 for GPT-3.5 Turbo prompted directly, with chain-of-thought and few-shot.
- With the Contriever retrievals released by Self-RAG, accuracy on PopQA rose from 52.8 to 59.8, PubHealth from 39.0 to 75.6 and ARC from 53.2 to 68.6, and Biography FactScore from 59.2 to 74.1, using SelfRAG-LLaMA2-7b as the generator. With LLaMA2-hf-7b the PopQA figure went from 50.5 to 54.9.
- Adding web search to plain RAG alone gave smaller gains than the full mechanism: PopQA with LLaMA2-hf-7b was 52.2 for RAG with web search against 54.9 for CRAG.
- Removing one action on PopQA (LLaMA2-hf-7b, 54.9 with all three): dropping Correct gave 53.2, dropping Incorrect gave 54.4, dropping Ambiguous gave 54.0. Running only the web action scored 47.0, the lowest single-action run. The paper reports that using only Correct and Incorrect made results depend on evaluator accuracy.
- Generation-phase overhead on PopQA (A800 GPU, retrieval and web search excluded) was 0.363 s per instance for RAG and 0.512 s for CRAG.

## Limits

- The authors concede the fine-tuned external evaluator cannot be avoided and defer removing it.
- Generators are all LLaMA2-7B variants; thresholds are tuned per dataset and the evaluator is trained on PopQA, so transfer of a threshold is not shown.
- No confidence intervals or seeds. Many ablation gaps are small (54.9 against 54.4 without the Incorrect action).
- Latency in Table 6 covers generation only, not retrieval or web search. Web results depend on a live commercial search API.
- On PubHealth, LLaMA2-hf-7b scores about zero for both Self-RAG (0.7) and Self-CRAG (0.6); the authors attribute this to the model not producing True or False.
- Models and retrieval are from the LLaMA2 era.

## See Also
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[CRAG Retry Logic]] — related (a graph-gated re-implementation, not this trained evaluator)
- [[Prompted Reflection vs Graph-Gated CRAG]] — related
- [[Sufficient Context Autorater]] — alternative-to (another way to judge whether retrieved context is enough)
