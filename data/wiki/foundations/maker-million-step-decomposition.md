---
title: MAKER Million-Step Decomposition
tags: [foundations, pattern]
summary: "MAKER solved a 20-disk Towers of Hanoi (over a million steps) with gpt-4.1-mini by decomposing into one-step agents, voting first-to-ahead-by-k per step and discarding malformed answers, with a theoretical cost of order s ln s (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-meyerson-2025-solving-million-step-llm-task.md
---

# MAKER Million-Step Decomposition

MAKER (Meyerson et al.) attacks compounding per-step error on very long tasks. Three parts: extreme decomposition into steps small enough for one agent each; per-step error correction by first-to-ahead-by-k voting (sample until one answer leads by k votes); and red-flagging, which drops overlong or malformed responses before voting.

## Reported results

- Towers of Hanoi with 20 disks (about a million moves) and gpt-4.1-mini: no errors in a single run (self-reported).
- Per-step error for small non-reasoning models was on par with reasoning models and did not grow with more disks (self-reported).
- Theory (not measured): at one step per agent, cost scales as order s ln s in the number of steps s.
- Preliminary multiplication test: 5x5 digits reached 100% and 6x6 reached 0.95 as k rose (self-reported, appendix).

## Limits

- The solving strategy for Hanoi is supplied in the prompt, and the decomposition is assumed rather than discovered, so the result is about execution reliability, not planning.
- One run at the headline size; the scaling laws are derived, not measured.
- Voting multiplies calls per step; error decorrelation between samples is assumed.
- Multiplication evidence is preliminary.

## See Also
- [[Self-Consistency]] — prerequisite-for (the voting idea, applied per step)
- [[Verification Loops]] — related
- [[Multi-Agent Topology Patterns]] — related (many single-step agents)
- [[Adaptive Branching MCTS]] — related
