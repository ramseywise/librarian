---
title: Graph-R1 Agentic GraphRAG
tags: [graph, rag, llm, pattern]
summary: "Graph-R1 trains an LLM with GRPO to query a hypergraph over several turns; its paper finds prompt-only GraphRAG methods below plain chunk RAG and RL as the component that matters most."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-luo-2025-graph-r1.md
  - data/raw/papers/2026-11-06-du-2026-rag.md
---

# Graph-R1 Agentic GraphRAG

Graph-R1 (arXiv 2507.21892, ICML 2026 per the footer) has three parts: a hypergraph knowledge store, multi-turn retrieval, and end-to-end RL.

- **Hypergraph.** Knowledge is built as hyperedges that group several entities (a hypergraph rather than binary relations). Retrieval is a dual path fused with reciprocal-rank fusion, with the top 5 facts per turn.
- **Multi-turn agent.** The model alternates reasoning and retrieval over the graph, averaging about 2.3 to 2.5 turns and 1200 to 1500 tokens (3B, training curves).
- **Reward.** Format credit accrues at 0.5 per valid step up to 1.0, answer F1 is added only once the format is fully valid, and the whole is offset by -1.

## Results (self-reported)

Setup: Qwen2.5 1.5B, 3B and 7B Instruct, GRPO, six QA sets with 128 test questions each; graph baselines run with GPT-4o-mini.

- Average F1 40.09, 51.26 and 57.82 at 1.5B, 3B and 7B, against 46.19 for Search-R1 at 7B and 32.05 for chunk RAG with GPT-4o-mini.
- With GPT-4o-mini the graph baselines average between 20.02 (PathRAG) and 29.40 (HyperGraphRAG), with GraphRAG at 24.87, LightRAG 23.57 and HippoRAG2 25.49, all below chunk RAG. The authors conclude graph structure alone is not sufficient.
- Ablation (3B, average over 2Wiki and HotpotQA only): full 57.16, without knowledge construction 46.11, without multi-turn 35.99, without RL 10.74 (the untrained model).
- Construction cost on 2Wiki (7B): 5.69 s and $2.81 per 1K tokens against 8.04 s and $3.35 for GraphRAG; HippoRAG2 is cheaper to build (3.25 s, $1.26). Answer-time cost is $0 because inference uses a local model, while construction still uses GPT-4o-mini.
- Out of domain, 3B average F1: 44.10 against 25.28 for Search-R1 in a single-domain transfer setting; zero-shot over five specialised domains 39.26 against 24.32.

## A-RAG, a second agentic result

A-RAG (arXiv 2602.03442, a work-in-progress preprint) gives a ReAct-style agent three tools (keyword search, semantic search, chunk read). With a GPT-5-mini backbone and top-5 everywhere, its full version scored 74.1 (self-reported) on MuSiQue against 52.8 (self-reported) for chunk RAG, and 94.5 (self-reported) against 81.2 (self-reported) on HotpotQA (LLM-judged accuracy, with GPT-5-mini as backbone, Qwen3-Embedding-0.6B, top-5 for every method, baselines reproduced locally, and GPT-5-mini as judge). With GPT-4o-mini it was best on three of five datasets, and HippoRAG2 beat it on HotpotQA and 2Wiki, so the authors tie agentic gains to a strong tool-using model. Its one-tool variant beat chunk RAG everywhere, and the authors report that GraphRAG and workflow methods did not consistently beat chunk RAG in their unified setup.

## Limits

- Graph-R1: the paper has no limitations section. The extraction notes list 128 test questions per set with no seeds, confidence intervals or significance tests, so per-set differences are noisy. They also note that the graph is built with GPT-4o-mini, so only answer-time cost is zero, and that the GPT-4o-mini graph baselines are not RL-trained and use a larger retrieved context, so the comparison mixes training with graph type; the one controlled comparison is Search-R1. The ablation covers two sets, and the generation-quality comparison used GPT-4o-mini as the judge.
- Graph-R1 inconsistencies: the extraction notes the text gives 57.28 in one place and 57.82 elsewhere for 7B (the table says 57.82), and that the text says cost per 1K tokens while the table column is per 1M tokens. The extraction notes the retrieval-representation ordering (none, chunks, graph, hypergraph) is read from curves with no table.
- A-RAG: the authors concede no systematic comparison of tool subsets, that the larger models they name were not tested in the main results, and that generalisation beyond multi-hop QA is unverified. The extraction notes no latency or dollar cost, no variance or seeds, baselines reproduced locally by the authors, and a judge from the same family as the backbone.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for (graph retrieval fundamentals)
- [[RL for Retrieval Policies]] — prerequisite-for (RL over retrieval actions)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for (the fusion step in hypergraph retrieval)
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for (agentic retrieval in general)
- [[LightPROF Knowledge Adapter for KGQA]] — alternative-to
