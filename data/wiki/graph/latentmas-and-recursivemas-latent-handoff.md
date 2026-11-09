---
title: "LatentMAS and RecursiveMAS Latent Handoff"
tags: [graph, pattern]
summary: "LatentMAS and RecursiveMAS let agents pass hidden states or KV caches instead of text; LatentMAS reports 70.8-83.7% fewer output tokens, RecursiveMAS 34.6-75.6% fewer across recursion rounds, both against text hand-off (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zou-2025-latent-collaboration-multi-agent-systems.md
  - data/raw/papers/2026-11-06-zou-2026-recursive-multi-agent-systems.md
---

# LatentMAS and RecursiveMAS Latent Handoff

Both methods replace the text message between agents with a latent one. Both need white-box access to model internals and open-weight models. The extraction for the second paper calls it weak and off-topic for context engineering.

## LatentMAS (training-free)

Each agent takes several auto-regressive steps over last-layer hidden states (its latent thoughts). It then hands its per-layer KV cache to the next agent through an alignment matrix, and only the final agent writes out text. Tested in sequential (planner, critic, refiner, solver) and hierarchical settings; agents must share the same architecture.
- Nine benchmarks on five backbones (Qwen3 at 4B, 8B and 14B; Llama3 at 3B and 8B), averaged over three runs on 8 A100s: +14.6% (sequential) and +13.3% (hierarchical) accuracy over single-model baselines and +2.8% and +4.6% over multi-agent systems that pass text; output tokens fell 70.8% to 83.7% and speed rose 4x to 4.3x (self-reported).
- Against text systems accelerated with vLLM, 2.6x to 7x speedup (self-reported).
- The extraction notes the accuracy gain over text systems is small and sometimes zero or negative on easy tasks (one backbone: 99.1 text against 98.8 latent on ARC-E), so most of the benefit is cost.

## RecursiveMAS (trained adapters)

Frozen agents are linked by small trained RecursiveLink adapters that pass latent thoughts through repeated recursion rounds.
- Sequential planner-critic-solver, small agents, means over 5 runs: token savings of 34.6%, 65.5% and 75.6% with speedups of 1.2x, 1.9x and 2.4x at recursion rounds 1, 2 and 3 (self-reported).
- +8.3% average over the strongest baseline per benchmark at round 3, six benchmarks (self-reported). One scaled setting: AIME2025 86.7 against 73.3 for the authors' own text-recursion baseline; text recursion did not improve with more rounds while the latent version rose (30.7, 33.3, 34.0 on one small setting).
- Trains 13.12M parameters (0.31%) at $4.27 (self-reported).

## Limits

- Both are white-box and same-family; models are small (1B-14B). A person cannot read or audit latent messages, and the papers do not address that.
- The text comparator in RecursiveMAS is the authors' own text recursion that decodes all intermediate text again in each round, so the savings are against a deliberately naive hand-off. AIME has 30 problems per year, so those gains are noisy. RecursiveMAS has no limitations section; its theory rests on stated assumptions.
- LatentMAS reports tables with several ties and small drops; no isolated test of the alignment matrix is summarized here.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Multi-Agent Context]] — prerequisite-for
- [[Context Window Budgeting]] — related
