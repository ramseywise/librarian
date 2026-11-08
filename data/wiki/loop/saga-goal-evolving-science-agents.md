---
title: SAGA Goal-Evolving Science Agents
tags: [loop, pattern]
summary: "SAGA nests an outer loop that rewrites the objectives and scoring functions inside an inner optimiser, so the objective keeps pace with what the optimiser exploits; it defines three autonomy modes by which stages a human touches."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-du-2025-accelerating-scientific-discovery-autonomous-goal.md
---

# SAGA Goal-Evolving Science Agents

SAGA (Du et al., arXiv December 2025, revised March 2026) treats objective design as part of the loop. An outer loop of four LLM agents (Planner, Implementer, Optimizer, Analyzer) analyses results, proposes new objectives and turns them into scoring functions; an inner loop optimises candidates against the current objectives. It was applied to antibiotics, nanobodies, DNA enhancers, inorganic materials and chemical process design.

## Autonomy modes

- Co-pilot: humans work with both the planner and the analyzer.
- Semi-pilot: humans touch only the analyzer stage; continuing, ending or pivoting stays human-guided.
- Autopilot: all four modules run without a human.

In most tasks the three modes performed about alike, and autopilot was often comparable to the human-guided modes. Chemical process design was the exception, with more variance in individual objectives as human input fell.

## Findings (self-reported)

- A fixed-objective optimiser alone over-optimised the primary objective (poor drug-likeness for antibiotics, poor stability for magnets); the authors call this reward hacking by the optimiser.
- Nanobody task: 2 to 5 times fewer oracle calls than two baseline pipelines. In wet-lab testing 3 of 24 designs bound; no single metric separated binders (all p>0.05) but the evolved composite did (p=0.03).
- Antibiotics: 28 compounds tested, 4 with over 80% inhibition under the stated assay.

## Limits

- The extraction covered the main text and some supplement; roughly half of the 114 pages were skimmed.
- The comparison of modes is qualitative; the paper gives no numbers for most of it.
- Wet-lab sample sizes are small.
- Preprint, authors' own system and baselines.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop Autonomy Ladder]] — prerequisite-for
- [[Loop Scorekeeper]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — prerequisite-for
