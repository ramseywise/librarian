---
title: "Advanced RAG Retriever: Self-Query, Query Expansion, Filtered Search and Rerank"
tags: [rag, pattern]
summary: "The LLM Engineer's Handbook builds its retrieval step as a chain of self-querying for metadata filters, query expansion, filtered vector search per data category, deduplication and cross-encoder reranking; this page records that chain and the pre- and post-retrieval options it was picked from."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch04-rag-feature-pipeline.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch09-rag-inference-pipeline.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch05-vector-databases-faiss-pinecone.md
---

# Advanced RAG Retriever: Self-Query, Query Expansion, Filtered Search and Rerank

Iusztin and Labonne (*LLM Engineer's Handbook*, chapters 4 and 9) divide RAG into three parts (retrieval, augmenting the prompt, generation), and advise spending most effort on retrieval. Chapter 4 lists optimisations by stage, following a third-party advanced-RAG article, and chapter 9 codes a subset. The chapters evaluate none of the techniques.

## Options by stage (chapter 4)

- **Pre-retrieval.** Small-to-big keeps a small sequence for the embedding while storing the sequence and a wider window in metadata for the prompt. Query routing picks an action from the input, like if/else statements in natural language. Self-query maps an unstructured query to a structured one, with an LLM extracting entities to use as filters. [[HyDE Hypothetical Document Embeddings]] has an LLM write a hypothetical answer and passes both it and the query to retrieval. The authors call pre-retrieval tuning experimental: try several methods and iterate.
- **Retrieval.** Filtered vector search uses the metadata index to filter on keywords before or after the vector search. Hybrid search blends vector and keyword search with an alpha parameter weighting the two. For domain tailoring they advise trying instructor models before fine-tuning an embedder, starting with filtered or hybrid search, and fine-tuning the embedder after that.
- **Post-retrieval.** Retrieve with a bi-encoder, then rerank with a cross-encoder, because a cross-encoder is too costly for the first stage.

## The chain the book codes (chapter 9)

1. **Self-query.** An LLM extracts metadata from the query (the author) and the result is a hard filter on the vector search. The chapter says this improves accuracy and latency, with no numbers.
   Phoenix and Taylor (*Prompt Engineering for Generative AI*, ch. 5) show self-querying retrieval too and advise running it at temperature 0 so the generated metadata filter stays consistent; they give no measurements.
2. **Query expansion.** A zero-shot prompt to GPT-4o-mini at temperature 0 writes the variants. The original query stays, and `expand_to_n - 1` variants join it (3 queries by default).
3. **Filtered search per category.** Each query searches the three data categories, taking `k // 3` from each, so one query returns at most K chunks (defaults k=3; the code asserts k >= 3). The searches for the expanded queries run in a thread pool to cut latency.
4. **Deduplicate** the aggregated results before reranking.
5. **Rerank.** A sentence-transformers cross-encoder scores (query, chunk) pairs and the top `keep_top_k` survive. The authors retrieve more than K and rerank down to K, combined with query expansion.
6. **Prompt and call.** The prompt is built from the kept chunks and sent to the SageMaker-hosted fine-tuned LLM in a five-line `rag()` function.

At query time the same cleaning, chunking and embedding code and the same model are used as at ingestion, through a shared embedding class. Each RAG step carries a mock flag that cuts cost while debugging.

## Proposed, not implemented

A router that skips categories; hybrid search running vector and BM25 in parallel, normalising the scores and merging by weighted sum; conversation memory as the last K turns or a summary plus the last K; and multi-index vectors, shown as a Superlinked snippet. The authors advise building the end-to-end solution first and iterating.

## Ingestion figures from the same pipeline (chapter 4)

One run of the LLM Twin feature pipeline turned 76 documents from three authors into 2,373 chunks, with `chunk_size` 500 and `chunk_overlap` 50 for articles. A content hash (MD5) is the chunk ID, which deduplicates. Batching chunks through the embedding model on a GPU is said to speed inference tenfold or more, depending on batch size and hardware, with no measurement.

## Limits

- No retrieval, latency or answer-quality measurement anywhere in either chapter; the LLM was not tested here because deployment comes in chapter 10.
- The cross-encoder id, embedding model and Qdrant settings live in settings files and are not named in chapter 9. Chapter 4's prose names all-mpnet-base-v2 while the settings default in code is all-MiniLM-L6-v2, and some cross-references in chapter 4 use stale figure numbers.
- The chapter says its list of advanced methods is not exhaustive and covers text only; the router, memory, hybrid and multi-index ideas are proposals.
- GPT-4o-mini may be deprecated (the model is a setting), and libraries date from 2024.

## See Also
- [[RAG Reranking]] — prerequisite-for (cross-encoder reranking in more detail)
- [[Reciprocal Rank Fusion (RRF)]] — alternative-to (rank-based fusion in place of the weighted-sum merge proposed here)
- [[HyDE Hypothetical Document Embeddings]] — related (one of the pre-retrieval options)
- [[Vector Database Comparison]] — related
- [[FTI Pipelines and the Logical Feature Store]] — related (the feature pipeline that fills the index)
