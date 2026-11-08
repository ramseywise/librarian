---
title: CorpusMap Entity Navigation for Agentic Search
tags: [rag, pattern]
summary: Build once an entity-page layer that links entities to the documents mentioning them, and give a file-searching agent that map; reported quality gains with fewer input tokens, while direct entity-to-entity edges added nothing.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-jeong-2026-follow-entities.md
---

# CorpusMap Entity Navigation for Agentic Search

CorpusMap lays Entity Pages over a document corpus. An LLM extracts and links entities offline, each page lists the documents that mention the entity, and an agent using find, grep and cat can follow the pages to candidate files. BM25 over Entity Pages pools linked documents for a query, which are reranked by BM25. Numbers are the paper's (self-reported); setup is multi-document questions only, a terminal agent, four GPT models, three benchmarks (EnterpriseRAG-Bench, HERB, WixQA), means of 3 runs, the same LLM building the map and answering.

## Reported results

- **Headline.** Overall quality up 6.4 to 11.7 points with 34% to 57% fewer input tokens than searching the raw corpus. For GPT-5.5, quality 72.55 against 66.11, at 0.43 times the tokens; paired-bootstrap intervals over questions give p below 1e-4.
- **Versus retrieve-then-generate** (EnterpriseRAG-Bench, 80 questions, GPT-5.5): 76.60, with BM25 at 63.66, dense retrieval at 65.05, HippoRAG at 64.66 and GraphRAG at 47.95. The extraction notes this mixes an agent with a map against fixed-context retrievers.
- **Other navigation layers** (document pages, group pages, an LLM wiki, Corpus2Skill) did not consistently beat the raw corpus; for example Corpus2Skill scored 45.49 on GPT-5.5.
- **Candidates matter.** With relevant candidate documents 76.60; none 69.04; random candidates 60.76.
- **Cost.** Build cost is estimated at up to $4,732 (GPT-5.5 builder) with break-even near 9.0K queries; a map built by the cheaper Luna model still helped every answering model. Incremental updates saved 34% to 71% of build tokens (read from a figure).
- **Entity-to-entity edges** moved document recall by between -2.6 and +0.2 points, and grew pages 27% to 52%.

## Limits

- Corpora of 2.8k to 6.4k documents (20k in a scaling test); enterprise-style, partly synthetic benchmarks. Gains differ by benchmark and model: on HERB with GPT-5.5 content was 64.37 against 62.31, and the raw baseline is already strong on one model (Sol, 67.69).
- Break-even and scaling values are read from figures; costs are the authors' estimates; baselines are the authors' reimplementations. The candidate ablation covers one benchmark and one model.
- Ethics statement: pooling per entity may expose documents to users without permission; the authors suggest a map per permission level.

## See Also
- [[Knowledge Graph Retrieval]] — alternative-to
- [[RAG Reranking]] — related
- [[Dynamic Tool Discovery]] — related
