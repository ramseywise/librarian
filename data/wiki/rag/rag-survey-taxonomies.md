---
title: RAG Survey Taxonomies
tags: [rag, reference]
summary: Two surveys' maps of the RAG design space, one by pipeline phase and retrieval-loop type (2024), one adding a structuring axis (2025); mostly vocabulary, with only borrowed numbers as evidence.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2024-survey-retrieval-augmented-text-generation.md
  - data/raw/papers/2026-11-06-jiang-2025-survey-retrieval-structuring-augmented-generation.md
---

# RAG Survey Taxonomies

Two surveys give names to the choices in a retrieval-augmented pipeline. Neither runs experiments; the figures below are copied from other papers.

## Huang and Huang (2024): phases and loop types

- **Four phases:** pre-retrieval (covering indexing, query manipulation and data modification), then retrieval, then post-retrieval (re-ranking and filtering), then generation (enhancing and customization). Multi-hop pipelines repeat the same four phases.
- **Five retrieval strategies:** basic (one pass), iterative (loop to a stop condition), recursive (sub-queries by depth), conditional (rule-based branching) and adaptive (query adjusted from feedback). Examples they give: Atlas and REPLUG (basic), IRCoT (iterative), SURGE (recursive), CRAG (conditional), FLARE and Self-RAG (adaptive).
- **Filtering is not re-ranking:** reflection tokens, empty compressor summaries and strip scoring remove content, while re-rankers only reorder.
- **Borrowed evidence (self-reported by the cited papers):** on the MIRAGE medical benchmark with GPT-3.5, average accuracy without retrieval is 60.69, and BM25 over PubMed lifts it to 69.23 (a Wikipedia corpus gives 57.74). Combining four retrievers with reciprocal rank fusion scored 59.14 on Wikipedia, below the two-retriever 60.14, which the text blames on SPECTER. Via BERGEN and eRAG, the survey reports retrieval quality mattering more than generator size, and a 7B model with retrieval beating a 70B closed-book model.

## Jiang et al. (2025): adding a structuring axis

This KDD '25 survey organises work by retrieval, structuring and generation. Its argument is that plain RAG over unstructured passages mixes non-atomic facts and struggles with multi-hop questions, so a structure step (knowledge graph, taxonomy, community summaries) should sit between retrieval and the LLM. It lists HippoRAG, GraphRAG and taxonomy-guided retrievers, and RL-trained query rewriting (DeepRetrieval, s3). It proposes a loop in which a taxonomy-aware retriever feeds a query-specific evolving graph that prompts the next sub-query; the survey never runs it.

## Limits

- Surveys with no controlled comparison; claims such as "iterative rounds generally do better" reflect how the authors read a table of studies.
- Huang's numbers come from one domain (medical QA) and one model; coverage stops in early 2024 and misses long-context and agentic RAG. The Fig. 5b gains have no model mapping in the extraction.
- Jiang's structuring loop is a proposal; it gives no cost, latency or hybrid-chunk comparison. The extraction notes mis-attributed references in the reference list (e.g. a Self-Refine entry and a PaLM 2 blog post), so check citations before reuse.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — related
- [[RAG Reranking]] — related
- [[Reciprocal Rank Fusion]] — related
- [[Agentic RAG — Advanced Patterns]] — related
- [[Knowledge Graph Prompting for Multi-Document QA]] — related
