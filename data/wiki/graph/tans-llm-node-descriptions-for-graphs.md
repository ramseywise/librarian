---
title: TANS Node Descriptions for Text-Free Graphs
tags: [graph, foundations, pattern]
summary: "TANS prompts an LLM with a node's computed topology (five properties with percentile ranks) plus optional node and neighbour text, then embeds the generated description so one GNN can train on graphs with little or no node text."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2024-can-llms-convert-graphs-text.md
---

# TANS Node Descriptions for Text-Free Graphs

Wang and colleagues (preprint, arXiv v2, February 2025) ask whether an LLM can turn a graph with sparse or missing node text into a text-attributed graph, so that a single GNN can be trained on graphs whose raw features differ. Their method is TANS. The hypothesis is that giving the LLM topology and neighbour text produces descriptions that explain a node's role, which makes better and more transferable features than hand-built topology features or other LLM augmentation (TAPE, KEA).

## Mechanism

For each node, five topological properties are computed. A templated prompt then carries the graph and node type, the node's own text if any, five randomly drawn neighbour texts, and each property's value with its percentile rank. GPT-4o-mini is asked for the most likely classes with reasons, in under 200 words. The output (appended to the original text when text exists) is embedded with a small text encoder, and a GCN, GAT or MLP is trained on the embeddings. Because the output is text, the same pipeline covers text-rich graphs (Cora, Pubmed), text-limit graphs (title only) and text-free graphs (airport networks).

## Results (self-reported)

- Text-rich Cora in the low-label setting (20 training and 30 validation nodes per class, MiniLM encoder, mean over GCN, GAT and MLP, 30 seeds), TANS scores above raw text, TAPE and KEA. On Pubmed in the high-label setting the largest gain is with the MLP (88.84 against 85.33 for KEA).
- On the text-free USA, Europe and Brazil airport graphs (GCN, low-label split) TANS posts the top average against degree, eigenvector and random-walk features, and it is also top in domain adaptation across the three.
- Ablations on Cora (low-label): removing neighbour text lowers the average of the three backbones on the text-limit variant, and removing the topology properties lowers GCN accuracy on the text-rich variant. Using the properties directly as features is worse than TANS on Brazil.
- A 54,000-node subsample of ogbn-products (from about 2,500,000 nodes) was run with a GCN.

## Limits

- No graph above 100,000 nodes, because querying the LLM per node is costly; only GPT-4o-mini was tried, and the authors say it is unclear whether GPT-4o would do better.
- Only node classification was tested; edge and graph tasks are future work.
- By the extraction's reading, gains over TAPE and KEA on text-rich graphs are about 1 to 1.5 points on average against a standard deviation of 1.5 to 2, with no significance test.
- Each method was tuned with 500 Bayesian-search runs and the best test score is the one reported; how much tuning the baselines got is not detailed.
- The airport graphs are small, at 131 to 1,190 nodes, and show large deviations (up to 17 points on Brazil). Some negative transfer appeared and the authors left it out of scope.
- The paper gives no LLM cost or latency, omits decoding settings and the generation date, and does not discuss possible pretraining contamination on Cora and Pubmed.

## See Also
- [[Graph Machine Learning and GNNs]] — prerequisite-for
- [[Knowledge Graph Retrieval]] — related (graph-aware LLM use for retrieval rather than node features)
- [[LightPROF Knowledge Adapter for KGQA]] — related (another way to hand graph structure to an LLM)
