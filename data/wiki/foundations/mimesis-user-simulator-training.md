---
title: MIMESIS User Simulator Training
tags: [foundations, llm, pattern]
summary: "MIMESIS trains a 9B user simulator to behave like real users and uses it as the training environment for interactive agents; an agent trained against it scored higher on nine held-out simulators than one trained against GPT-5.5 (self-reported), and coached self-distillation added a further gain."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-phan-2026-mimesis.md
---

# MIMESIS User Simulator Training

MIMESIS (an October 2026 preprint from NYU and Meta) argues that for agents trained to talk with users, the simulated user is the environment, and frontier LLMs used as simulators distort how hard a task looks.

## Mechanism

- **Simulator.** A 9B (and a 4B) model trained in two stages: user-side mid-training on utterance data, then RL with a behaviour reward over 13 realistic behaviours; the reward halves if the simulator describes a behaviour instead of expressing it.
- **Coached On-Policy Self-Distillation (CSD).** During agent training a coach note, assembled from what the simulator privately thought and what it said next, conditions a teacher copy; per-token weights come from a sigmoid of the teacher-student log-probability gap. Loss is GRPO plus a small weight on CSD; the note is used in training only.

## Results (self-reported)

- Simulator realism: with the agent held fixed (GPT-5.5 on tau-bench), real users yield 63.6% success while frontier simulators yield between 82.4 and 84.4%; trained simulators deviate by at most 10.3 points against at least 14.9 for off-the-shelf ones (the extraction could not locate the source of the human rate).
- Simulator benchmarks: SOUL-Index 65.7 against 64.9 for the best frontier model (three seeded runs; the margin is small); it lost to a released 8B simulator on one benchmark (80.17 vs 80.44).
- Agent training: Qwen3-8B, UserRL setup, 100 steps, mean over eight gyms, nine unseen LLM users. Training user MIMESIS instead of GPT-5.5 lifted the mean from 26.10 to 29.54; CSD lifted it to 31.09. One value per cell, no seeds.

## Limits

- Transfer to human users is untested; all nine evaluation users are LLMs. The extraction notes the persuasion gym gave an all-zero invalid column for one user that refused every turn, and that persuasion training could reward manipulation.
- CSD's gain over GRPO with the same simulator is often within a point or two, and the persuasion column is volatile. Behaviour conditioning can exaggerate traits, and utterance-only mid-training suppresses reasoning. The sufficient-condition theory for CSD is not checked empirically. Only an 8B agent was trained.

## See Also

- [[Simulated User Evaluation]] — prerequisite-for
- [[On-Policy Distillation]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
- [[PAHF Pre- and Post-Action Feedback Personalization]] — related
