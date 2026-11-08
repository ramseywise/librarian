---
title: ARC-AGI-3
tags: [eval, reference]
summary: "ARC-AGI-3 is an interactive benchmark of turn-based grid environments with no stated goal, scored by RHAE, the squared ratio of a human action count to the agent's; on its semi-private set the best frontier model scored 0.50% (Opus 4.6), while the authors say every environment was solved by at least 2 of 10 humans (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-foundation-2026-arc-agi-3.md
---

# ARC-AGI-3

The ARC Prize Foundation (arXiv 2603.24621, 2026) moves ARC from static puzzles to interactive
environments. The agent sees a 64x64 grid with 16 colours, acts through five keys, Undo and a
cell click, and gets no instructions or stated goal. There are 25 public demo environments, 55
semi-private and 55 fully private; the private set is deliberately out of distribution relative
to the public one, and environment names are withheld.

## Scoring: RHAE

Relative Human Action Efficiency gives each level the score min(1.15, (h/a)^2), with h the
human baseline's action count and a the agent's own. An agent needing 100 actions where the baseline
needed 10 earns 1% for that level. Level scores are combined with linearly increasing weights by
level number, capped at the weighted share of levels completed, and averaged over environments.
Only environment actions count, not tool calls or reasoning steps, and agents are stopped at
five times the human median actions per level. The authors credit the Success weighted by Path
Length metric as the inspiration.

## Human baseline and validation

486 members of the public took part in person in 90-minute sessions at a San Francisco centre
(2,893 attempts across 414 candidate environments). An environment counts as human-solvable if
at least 2 of the 10 people who attempted it solved it; the baseline action count is that of the upper-median completer. Random play (runs of 50,000 steps and of one million steps, together with a state-graph analysis)
must solve a level less than once in 10,000 times, except the tutorial level, and a novelty test
rejects environments solvable by a program much shorter than the concatenated solutions of two others.

## Results (self-reported)

- **Frontier models, semi-private set, no harness or tools, one shared system prompt:** Opus 4.6
  (Max) scored 0.50%; Gemini 3.1 Pro Preview scored 0.40%; GPT 5.4 (High) reached 0.20%; and
  Grok-4.20 got 0.10%.
  The paper puts the API bill only at tens of thousands of dollars.
- **Harness gains did not transfer.** Opus 4.6 moved from 0.0% with no harness to 97.1% with the
  Duke harness, built on three public environments, yet scored 0.0% under both settings on
  one environment (BP35).
- **Preview competition** (July to August 2025, three hidden environments): StochasticGoose, a
  convolutional network with reinforcement learning, scored 12.58% and Blind Squirrel 6.71%, both
  search-based; it is not stated that the same formula applied.
- **Contamination anecdote.** On earlier ARC versions, Gemini 3 Deep Think referred to the ARC colour mapping while
  reasoning, although its prompt never supplied that mapping.

## Limits

No run counts, seeds or intervals are given for AI scores, so gaps of a few tenths of a point cannot be
interpreted; there are no per-environment results or per-model costs and nothing on
the fully private set. The human baseline rests on at most 10 people per environment, as few as
2 completers, so "solvable by humans" does not imply most people can solve them. Rejections among the 414
candidates are not counted (135 shipped). The authors concede a small leakage risk for the semi-private set, the 5x action cutoff may lower scores slightly, the models tested are a March 2026
snapshot and community leaderboard scores are unverified. The paper is inconsistent on levels
per environment and on its attempt counts.

## See Also
- [[Eval Contamination Defenses]] — related (public demo set against private held-out sets)
- [[Parameterised Benchmark Instances]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
