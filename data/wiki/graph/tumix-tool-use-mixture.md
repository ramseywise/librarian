---
title: TUMIX Tool-Use Mixture
tags: [graph, pattern]
summary: "TUMIX runs about fifteen differently-built tool-using agents in rounds, each reading the others' answers, stops when an LLM judge says to, and takes a majority vote; the authors report gains over matched-cost baselines on Gemini 2.5 but note that picking the right answer is the bottleneck (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2025-tumix.md
---

# TUMIX Tool-Use Mixture

Chen et al. (MIT, Harvard, Google; arXiv 2510.01279, a preprint, code not released at the time) build a test-time ensemble from agents that differ in how they use a code interpreter and web search: text-only, code-only, search-only, mixed, with and without guidance. Every round, each agent sees the question plus all answers from the previous round and answers again. After a minimum of two rounds an LLM judge decides whether to stop; the final answer is a majority vote over the last round. Each agent's tool loop is capped at five calls with a 60-second code limit.

## Results (self-reported)

Setup: Gemini 2.5 Pro and Flash on three benchmarks, HLE with 2,500 questions, GPQA Diamond with 198 and AIME 2024-25 with 60; mean of three runs; every baseline also had code and search, with matching by inference count, not tokens.
- Average accuracy: Pro 72.3 against 70.3 (Symbolic-MoE) and 69.2 (majority vote); Flash 60.6 against 55.0 (SciMaster) and 53.7 (majority vote).
- Mixing agent types beat repeated sampling of one agent at equal rounds and inference counts: Pro on HLE 32.3 (15 agents), 30.2 (three types, five samples each), 29.0 (one agent type); Flash on GPQA 77.3, 67.1 and 65.8. The authors note this differs from the Self-MoA finding.
- LLM-judged termination kept accuracy while using about 49% of the inferences (judge calls counted) and about 46% of the tokens. A one-round minimum did worse because the judge is overconfident.
- Agent types gave little gain past about a dozen. A larger variant (TUMIX+) reached HLE 34.1 on Pro and 23.1 on Flash, at roughly two orders of magnitude more tokens than a single call.

## Selection is the bottleneck

On HLE with Pro, per-round coverage (some agent was right) fell from 51.92 in round 1 to 33.87 in round 6 while accuracy rose from 21.13 to 32.37 and plateaued near 34% (self-reported), because refinement narrows the answers and the model struggles to pick the right one from noisy candidates (authors' account). Token-confidence selection did not help.

## Limits

- Two Gemini 2.5 models (Google's own, with Google search), three reasoning or QA benchmarks, no long-horizon agent tasks, no dollar or latency cost, and no variance beyond the three-run mean; AIME and GPQA are small and some gaps are about a point.
- The extraction notes that inference-count matching may flatter TUMIX on tokens because each call grows as earlier answers are fed in; no per-method token table is given.
- Some baselines (Self-MoA, Symbolic-MoE, DEI) and the LLM-designed variant are starred because Pro's HLE results chose their agents or the agent pool, so they are not clean test numbers.
- The coverage figure of 65% or more in the text cannot be tied to a table, and the abstract and introduction word the 3.55% average gain differently (the extraction's notes). SciMaster fell short of its published numbers.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Self-Consistency]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — alternative-to
- [[Archon Inference-Time Architecture Search]] — related
- [[Best-of-k Headline Inflation]] — related
