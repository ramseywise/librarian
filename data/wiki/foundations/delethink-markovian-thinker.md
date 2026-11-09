---
title: Delethink Markovian Thinker
tags: [foundations, concept]
summary: "Delethink trains a reasoning model with RL in fixed-size chunks, resetting context at each boundary to the query plus the last m tokens, so thinking length no longer sets context size; a 1.5B model trained at 24K matched or beat LongCoT-RL at the same budget on math (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-aghajohari-2025-markovian-thinker.md
---

# Delethink Markovian Thinker

In standard RL for reasoning models, the environment's state is the prompt together with all earlier reasoning tokens, so the state grows without bound and compute is quadratic in thinking length. Aghajohari et al. (2025) change the environment. Reasoning runs in chunks of C tokens; at each boundary the context restarts from the query plus the final m tokens of the previous chunk, and RL trains the model to write a text summary of its state toward the end of each chunk. The maximum thinking length is C + (I-1)(C-m) for I iterations. The KV cache is cleared at each boundary and the carryover is re-encoded, which adds an O(m²) cost per boundary.

## Results (self-reported)

- Trained setup: R1-Distill 1.5B, DeepScaleR data, C=8K, m=4K, I=5 (24K total), GRPO 1,000 steps. AIME24 0.46 for Delethink against 0.40 for LongCoT-RL 24K and 0.35 for LongCoT-RL 8K (bar labels read from a figure in the extraction, flagged as ambiguous there). Out-of-distribution gains (GPQA-Diamond, LiveCodeBench) were modest.
- Cost: at 24K on 8 H100s, 215 s per RL step against 248.5 s. The paper's estimate for an average 96K thinking length is 27 H100-months against 7; it comes from per-step timings extrapolated to a full run.
- Theory: FLOP crossover near 30K tokens and a 17x FLOP reduction at 1M tokens, computed in closed form for the 1.5B architecture.
- Test-time scaling: trained at 24K, Delethink kept improving to 128K while the LongCoT baselines plateaued. A short 96K run (150 steps) reached 49% on AIME24 and is called preliminary.
- Zero-shot, no training: Delethink tracing on R1-Distill 1.5B gave AIME24 37.2 against 29.3 for LongCoT at 32K; C=8K recovered LongCoT performance on 7B and 14B.

## Limits

- Only one model (R1-Distill 1.5B) was trained, on math; larger models appear zero-shot only. The best checkpoint was chosen on AIME24, which is also reported, and no run-to-run variance is given.
- At 24K tokens its backward passes run slower than LongCoT, and its FLOPs exceed LongCoT's for lengths under roughly 30K.
- CrossWordBench: on 14x14 puzzles performance declined relative to LongCoT. C=2K fails to terminate. The authors concede it could not work for long-context retrieval, and why it works is hypothesis.
- The extraction notes the paper says 96K in the abstract and 94K elsewhere for the cost comparison.

## See Also
- [[Overthinking and Concise Reasoning]] — related (reasoning length as a cost)
- [[Reasoning State Pass-Back]] — related (what the model carries between steps)
- [[Post-Training for Agents]] — prerequisite-for (the RL setting it modifies)
- [[KV Cache Reduction Methods]] — related (another route to bounded KV during long generation)
