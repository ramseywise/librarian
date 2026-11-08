---
title: GraphReader
tags: [graph, concept]
summary: GraphReader turns a long document into a graph of atomic facts and key elements and has an LLM agent explore it coarse to fine within a 4K window; with GPT-4 it beat 128K full-text reading on multi-hop QA, with the gap widening up to 256K tokens (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2024-graphreader.md
---

# GraphReader

Li et al. (EMNLP Findings 2024).

## Mechanism

- **Build.** Split into chunks of at most 2K tokens, have the LLM extract atomic facts and key elements per chunk, normalise the elements, and make a node per key element with its facts. Link nodes when one's key element appears in the other's facts.
- **Explore.** The agent drafts a rational plan and keeps a notebook, starting from five chosen nodes. At each node it reads the atomic facts first, then chunks, then neighbours, through a few functions (read chunk, read neighbour, search more, terminate).
- **Answer.** Notes from the parallel agents are compiled, with chain-of-thought and majority voting to settle conflicts.

## Results (self-reported, GPT-4-1106, 4K window)

- HotpotWikiQA-mixup (LV-Eval, 250 samples): LR-1 at 16K 42.0 against 38.0 for GPT-4-128k full reading, 128K 28.0 against 16.0, 256K 30.0 against 14.0. The 128K and 256K inputs were truncated for the baseline.
- LongBench QA: HotpotQA LR-1 84.3 against 83.3 for full reading, 2Wiki 83.7, MuSiQue 59.0, NarrativeQA 65.0. BM25 retrieval scored 57.7 and Ada-002 72.0 on HotpotQA. Margins over full reading are small on HotpotQA and NarrativeQA.
- Random node choice cost about 18% on average. About 3 to 4 function calls per question. Exploration used 52.8K tokens per question against 48.7K for ReadAgent.
- The graphs are large: a 256K document yields roughly 14.9 thousand nodes and 8.6 thousand atomic facts.

## Limits

- Relies on closed GPT-4 for graph, agent and judge, so judge and system share a model. No intervals or seeds, 200 to 300 samples per set, and graph-building cost and latency are not counted in per-question cost.
- Mostly Wikipedia QA under 128K, 2024 baselines. The extraction notes the Table 8 caption does not match its contents and one metric is mislabelled "LR-2".

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[MemWalker Summary-Tree Navigation]] — alternative-to
- [[Context Retrieval Strategies]] — related
