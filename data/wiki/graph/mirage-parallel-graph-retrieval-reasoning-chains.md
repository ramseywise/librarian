---
title: MIRAGE Parallel Graph-Retrieval Reasoning Chains
tags: [graph, concept]
summary: "MIRAGE splits a medical question into entity-grounded sub-questions, runs parallel reasoning chains that query a knowledge graph in anchor or bridge mode, and has a synthesizer cross-check the chains; with QwQ-32B it ranked best or tied-best by GPT-4o on three medical QA sets, by small margins on two (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wei-2025-mirage.md
---

# MIRAGE Parallel Graph-Retrieval Reasoning Chains

Wei et al. (arXiv 2508.18260 v2, January 2026; AAAI-format preprint). It is knowledge-graph retrieval-augmented generation for medical question answering, where the reasoning model decides when to query the graph.

## Mechanism

- **Decomposer.** Produces sub-questions tied to entities, only when the query names several different medical entities, with a default maximum of 4.
- **Parallel chains with two retrieval modes.** In anchor mode a chain takes the neighbourhood of one matched entity, up to a cap of neighbours per relation. In bridge mode, triggered when two entities are identified, it takes typed paths up to a length cap between them. Entity matching uses embedding similarity over a threshold; when nothing matches, a "no entity match" token prompts the model to reformulate. Triples are verbalised between result markers, and only relation types from a curated, clinically validated list are allowed. Retrieval is demand-driven and can stop early, with 5 retrieval steps by default.
- **Synthesizer and coordinator.** On conflicting answers the synthesizer keeps the one supported by chains covering a broader neighbourhood of corroborating relations or fitting the query better, flags graph-level contradictions (for example a drug said both to treat and to cause one symptom), and writes the answer plus an audit record. It may fall back on medical priors when the graph is silent. A coordinator holds shared state.

## Results (self-reported)

- The backbone is QwQ-32B for all three roles (decomposer, retriever, synthesizer), with 32,768 input tokens; datasets follow the MindMap protocol; rank is the mean GPT-4o listwise rank, lower being better: GenMedGPT-5k rank 1.8 against 3.3 for Search-o1; CMCQA 2.8 against 3.0; ExplainCPE accuracy 84.8% against 84.6% for MindMap, 83.5% for BM25, 82.8% for QwQ-32B alone and 77.8% for GPT-4o, with a rank of 3.1 tied with MindMap. The extraction notes the text's "consistently best" is stronger than the table, because MIRAGE trails in some BERTScore columns; on ExplainCPE its F1 of 0.888 is a hair under MindMap's 0.889.
- With DeepSeek-R1-32B on ExplainCPE only, with baselines moved to the same backbone: rank 2.9 and accuracy 84.4%, against 84.1% for MindMap and 81.1% for Search-o1.
- Human check: two medical graduate students compared outputs pairwise on 100 GenMedGPT-5k examples; MIRAGE won 77% against GPT-4o, 60% against QwQ-32B, and 45% and 40% against MindMap and Search-o1. The extraction says the figure's per-baseline mapping is approximate.
- Ablation (win/tie/lose against the full system, GPT-4o judge): without the decomposer 14.31% lose, without the synthesizer 12.73%, without both 13.05%, with many ties.
- Over-decomposition hurts: on dialogue-style CMCQA, going from one to two sub-questions can lower performance. More retrieval budget gives diminishing returns.

## Limits

- No limitations section. Evaluation leans on GPT-4o as judge, backed by one 100-example, two-annotator check on one dataset with no agreement figure or intervals. No cost or latency data despite test-time-scaling claims, and no equal-compute comparison against self-consistency or tree-of-thought on the same backbone.
- Medical QA only, on prebuilt curated graphs; no graph construction or text-to-query. Traceability claims rest on a case study. The appendices (prompts, algorithm) were not in the extraction.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Graph-R1 Agentic GraphRAG]] — alternative-to (agentic graph retrieval inside reasoning)
- [[GraphReader]] — related
- [[Multi-Agent Topology Patterns]] — related (fan-out with a verifying synthesizer)
