---
title: Multi-Agent Evolve Self-Play
tags: [foundations, pattern]
summary: "Multi-Agent Evolve trains one model in three roles (proposer, solver, judge) with reinforcement learning on unlabelled seed questions; quality filtering and partial reference use were the stabilisers, on a single 3B model."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2025-multi-agent-evolve.md
---

# Multi-Agent Evolve Self-Play

Multi-Agent Evolve (MAE; Chen et al., a 2025 preprint from UIUC, PKU and NVIDIA) is a self-play loop for general reasoning without labelled answers. One Qwen2.5-3B-Instruct model plays three roles and is updated synchronously, with advantages normalised per role (the Task-Relative REINFORCE++ scheme borrowed from the Absolute Zero Reasoner).

## Loop and rewards

- The proposer writes a question. It is kept only if the judge's quality score is at least 0.7 on a 0 to 1 scale.
- The solver answers; the judge scores each answer with a chain-of-thought rubric from 1 to 10 (1 to 3 for any error or unsolvable question, 8 to 10 only for flawless answers).
- Proposer reward: one third each of quality, difficulty (one minus the mean judge score over five solver samples) and format. Solver reward: half judge score, half format. The judge is rewarded only for clean, parsable output.
- The difficulty term alone could pay the proposer for unsolvable or ambiguous questions; the authors argue the quality score guards against that (argued, not tested directly).

## Findings (self-reported; single runs, no variance)

- Setup: 967 unlabelled seed questions, 28 benchmarks, 300 steps, a separate 70B judge for evaluation. Best variant (half the questions grounded in reference data) averaged 59.87 against 55.33 for the base model.
- With only 16 self-generated seeds, the zero-data variant scored 58.51 against 57.72 for the AZR baseline, losing on GPQA, MMLU and LiveBench.
- Supervised fine-tuning on the seed answers fell below the base model (53.87), which the authors blame on the seed set's width and small size; the extraction calls it a weak baseline.
- Half reference beat no reference (58.18) and full reference (57.11).
- Ablations in the half-reference setting: no quality filtering cost 3.72 points; no format reward cost 0.43; freezing the solver, proposer or judge cost 2.08, 1.97 and 2.63.
- Rising question difficulty went with rising benchmark scores in one example run (correlational).

## Limits

- One 3B model; larger backbones are future work and any claim that they would gain more is speculation.
- The in-training judge is the model being trained, with no external check; the evaluation judge's noise is not measured.
- Gaps are small (about 0.8 between the zero variant and AZR) with no significance tests. Gains are uneven and some benchmarks regress.
- A poorly prompted proposer can collapse into open-ended writing questions; without the format reward and filtering the judge emits malformed scores and training reverts to neutral rewards.
- The comparison with R-Zero rests on its reported step counts, not a re-run.
- The text mislabels tables (it points to Table 2 for the main results, which are in Table 1, and to Table 5.3 for the ablation), a minor numbering slip.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Multi-Agent Reinforcement Learning]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — prerequisite-for
- [[Recursive Self-Improvement]] — prerequisite-for
- [[MASS Multi-Agent Self-Supervision]] — alternative-to
- [[Autodata Agentic Self-Instruct]] — related
