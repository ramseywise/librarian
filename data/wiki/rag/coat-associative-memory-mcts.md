---
title: CoAT Associative-Memory MCTS
tags: [rag, pattern]
summary: "CoAT runs Monte Carlo tree search over reasoning steps and gives each node an associative memory (retrieved or generated knowledge); an ablation moved a score from 0.67 to 0.77 at 32B (self-reported), though baselines are not compute-matched."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pan-2025-coat.md
---

# CoAT Associative-Memory MCTS

CoAT (Pan et al., 2025) searches over candidate reasoning steps with MCTS, and at each node attaches an associative memory: extra knowledge pulled in for the current step and kept with the node, so later steps and the final answer can use it. The paper compares against KAG and reports better exact match.

## Reported results

- Ablation on CRB, the authors' own set of 205 questions, scored by an unnamed judge, at 32B: 0.67 to 0.77 (self-reported; the extraction does not say what CRB stands for).
- Beats KAG on exact match (self-reported).

## Limits

- Baselines are not compute-matched; tree search spends many more calls.
- The extraction notes that the stated 22% and 18% relative gains do not match the arithmetic of the table values.

## See Also
- [[Adaptive Branching MCTS]] — related (another search over answers with a budget)
- [[Tree of Thoughts]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — related
- [[Knowledge Graph Retrieval]] — related
