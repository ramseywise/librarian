---
title: GritLM (Generative Representational Instruction Tuning)
tags: [rag, pattern]
summary: One model fine-tuned for both text embedding and generation, so retriever and reader are the same network and a RAG pipeline can reuse cached key-value states; reported to lose nothing on either task, with the speedup shown on long documents only.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-muennighoff-2024-generative-representational-instruction-tuning.md
---

# GritLM (Generative Representational Instruction Tuning)

GRIT trains one Mistral 7B model on two objectives at once: a contrastive embedding loss (bidirectional attention, mean pooling) and a generative loss on instruction data. The recipe uses E5S embedding data and Tulu 2 generative data for 1253 steps. All numbers here are the paper's (self-reported).

## Reported results

- **No cost from unifying (Mistral 7B, 56 MTEB datasets, same step count).** MTEB average 66.8 for GritLM and for an embedding-only variant; generative average 55.5 against 55.2 for a generation-only variant. Training only generation gives 41.2 on MTEB, and the embedding-only model scores near random on generation (MMLU 23.5, random is 25.0).
- **Retrieval score.** MTEB average 66.8 against 66.6 for E5 Mistral 7B and 64.6 for OpenAI v3. The 8x7B variant scores 65.7, which the authors attribute to a smaller embedding batch (256 instead of 2048).
- **Self-reranking.** Reranking its own top 10 by permutation generation lifts the 15-dataset MTEB retrieval average from 57.4 to 57.9, improving 14 of 15 datasets.
- **RAG caching.** Since one model both retrieves and reads, the key-value states from the embedding pass can be reused. Doc Caching stores each document's states in the index; Query Caching reuses the query's. On a 4000-token document with a 1-token query, latency falls 63% on CPU and 31% on GPU (Doc Caching, NQ index of 2.68M documents, one H100, 100 runs). The abstract's "more than 60%" is the CPU figure.
- **Answer quality, NQ match, zero-shot.** No RAG 21.00, RAG 30.50, Query Caching 25.46 and Doc Caching 33.38; the two combined orders score lower (21.63 and 18.39). The authors attribute the weak variants to an attention-format mismatch and propose RAG fine-tuning, not done.
- **Storage.** Doc Caching needs about 30 TB of key-value states for the 2.68M documents, against 43 GB for the index and passages.
- **Embedding ablations (MTEB average).** Bidirectional attention with mean pooling 64.0 against 61.2 for last-token pooling in the unified setup; embedding data choice mattered most (E5 66.0, MEDI 64.0); few-shot examples in embedding prompts lowered scores.

## Limits

- Needs more fine-tuning compute than generation-only tuning; 4096-dimensional embeddings are four times the storage of a 1024-dimensional model, and the 7B model is far costlier to run than a small embedder.
- Caching tests use one dataset (NQ), synthetic extremes (4000 tokens against 1), and a lenient match metric. In the RAG baseline the 7B model serves both stages, unlike typical small-embedder setups.
- Embeddings for inputs over 512 tokens, multilinguality and multimodality are untested. The authors concede the model may be tuned near the generative eval sets.
- The extraction notes an internal inconsistency: the conclusion says "15 of 16" retrieval datasets improved, while Table 3 lists 15 datasets (14 improved).

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[Llama2Vec Unsupervised LLM Adaptation for Dense Retrieval]] — alternative-to
- [[Tuning an Embedding Model from Match Labels]] — related
- [[ANCE Global Hard Negatives for Dense Retrieval]] — related
- [[GTR Large Dual Encoders]] — related
- [[M3-Embedding Self-Knowledge Distillation]] — alternative-to
- [[INSTRUCTOR Instruction-Finetuned Embeddings]] — alternative-to
