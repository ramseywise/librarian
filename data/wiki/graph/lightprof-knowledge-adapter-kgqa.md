---
title: LightPROF Knowledge Adapter for KGQA
tags: [graph, pattern]
summary: "LightPROF keeps the LLM frozen (LLaMa3-8B) and trains a small adapter that encodes retrieved knowledge-graph paths as soft prompts; it scored 83.8 Hits@1 on WebQSP and 59.3 on CWQ with about 98% fewer tokens than StructGPT (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ao-2025-lightprof.md
---

# LightPROF Knowledge Adapter for KGQA

LightPROF (Ao et al., 2025) is a Retrieve-Embed-Reason pipeline for knowledge-graph question answering. Retrieval pulls a reasoning path from the graph; a trained Knowledge Adapter embeds the path's entities and relations into the frozen LLM's input space instead of pasting triples as text; the LLM then answers.

## Reported results

- Hits@1 on WebQSP 83.8 against 75.1 for UniKGQA, and on CWQ 59.3 against 57.6 for ToG (self-reported, frozen LLaMa3-8B).
- Against StructGPT: about 98% fewer tokens and about 30% less time (self-reported).

## Limits

- Two Freebase benchmarks only.
- The adapter encoder is tied to the graph it was trained on.
- The baseline comparison pits a trained component against untrained prompting methods.
- The text gives 83.7 for WebQSP and Table 1 gives 83.8.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Graph-R1 Agentic GraphRAG]] — alternative-to (agentic retrieval with RL instead of a trained adapter)
- [[GraphReader]] — related
- [[TANS Node Descriptions for Text-Free Graphs]] — related
- [[Graph Neural Prompting]] — alternative-to (soft prompt from a GNN)
- [[Reasoning on Graphs]] — alternative-to
