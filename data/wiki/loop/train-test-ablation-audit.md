---
title: Train-Test Ablation Audit
tags: [loop, pattern]
summary: "After an LLM evolutionary search, remove each discovered component and compare the effect on training and held-out games; components that matter on both generalise, those that matter only on training are overfit and can be dropped."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-discovering-multiagent-learning-algorithms-large.md
---

# Train-Test Ablation Audit

Li et al. (Google DeepMind, a 2026 preprint) used AlphaEvolve with Gemini 2.5 Pro to evolve game-solving algorithms: VAD-CFR and PSRO variants. The search proposes combinations of mechanisms; the audit decides which to keep.

## The audit

The search scored candidates on four training games. Afterwards each component of the winner was removed in turn and the change in exploitability, in log10 units, was measured on the four training games and on 14 held-out games, aggregated with the interquartile mean.

## Findings (self-reported, one search trajectory)

- Removing secondary features such as a volatility tracker or an instantaneous regret boost hurt the training score a lot (-0.842, -0.954) but the test score little (-0.029, -0.204).
- Three structural pieces carried generalisation: a hard 500-iteration warm start before averaging (test -2.003 when removed), an asymmetric discount (-1.065) and optimistic prediction (-0.905).
- A distilled variant keeping those three scored +0.119 on test against the raw discovery, but -0.802 on train, with far less code.
- For PSRO, removing hybrid blending and annealing slightly improved test scores (+0.020, +0.016), so they were overfit artefacts.
- The authors frame the loop as a proposal mechanism within a human-in-the-loop pipeline: the model proposes, the audit separates, a researcher distills.

## Limits

- Only one evolutionary trajectory was examined, so whether the distilled components recur across runs is unverified.
- Train and test games share three families, so most of the generalisation is within family; only Blotto and Battleship lie outside.
- The train-test split was chosen by hand; no intervals on the main tables; effect sizes of a few hundredths in log10 units.
- Distillation needs human judgment.
- Evolution cost is not reported, and the backbone has dated.

## See Also
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — prerequisite-for
- [[EvoPrompting Code-Level Architecture Search]] — related
