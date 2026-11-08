---
title: ComputerRL API-GUI Agent RL
tags: [foundations, llm, pattern]
summary: "ComputerRL combines an action space mixing generated APIs with GUI actions, step-level GRPO with a binary outcome reward, and Entropulse, which alternates RL with SFT on collected successes to restore entropy; its 9B agents scored 48.9% on OSWorld (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lai-2025-computerrl.md
---

# ComputerRL API-GUI Agent RL

ComputerRL (Tsinghua and Z.AI, a preprint revised October 2025; the paper says its method is used in AutoGLM) trains desktop agents with online RL across a large pool of parallel virtual machines.

## Components

- **API-GUI action space.** Generated application APIs sit alongside click and type actions. The authors say tasks need at most a third of the steps of the strongest baselines; no step counts are tabulated.
- **Reward.** Rule-based, binary, with a format check; each valid step in a successful trajectory scores 1 and counts as its own training instance. The advantage is standardised across every step of every rollout for that task.
- **Data.** Around 8k tasks with hand-written evaluation functions; behaviour-cloning data of 180k+ correct steps from closed models, stratified by pass rate, keeping only successes.
- **Entropulse.** When RL plateaus (about 180 steps), successful rollouts from earlier policies are collected (about 130,000 steps), an SFT pass restores action entropy, and RL resumes. Raising the clip threshold, a DAPO-style change, slowed entropy decline but also slowed improvement.
- **Infrastructure.** Containerised virtual machines, a multi-node cluster and fully asynchronous training with a limited replay buffer.

## Results (self-reported)

- Ablation with Qwen2.5-14B on OSWorld: untrained 15.2, behaviour cloning 31.9, first RL phase 42.0, Entropulse 41.5, second RL phase 45.8.
- API-GUI against GUI-only with GPT-4o and no RL: 26.2 vs 11.2.
- 9B models on OSWorld: 48.9 and 48.1, against 42.9 for an OpenAI computer-use agent and 30.7 for Claude 4.0 Sonnet; on the authors' own 180-task OfficeWorld, 43.3 and 41.1 against 33.9.
- The extraction's failure breakdown (case study, size unstated): multi-app 34.4%, vision 25.8%, illusion 25.6%.

## Limits

- The extraction notes that the "66% gain from RL" has no stated baseline; 30.7 to 48.9 does not give 66%.
- The Entropulse-versus-reset comparison is read from reward curves, with no final-score table; the second RL phase adds only 3.8 points; only one pulse was run.
- Ablation model (14B) differs from headline models (9B); single runs; reward credits wasted steps equally; comparisons against proprietary agents mix scaffolds; OfficeWorld is the authors' own benchmark. Safety and unseen-app robustness are listed as open.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Computer Use Visual Grounding]] — related
- [[DAPO]] — related (clip-higher compared against)
- [[AgentBench]] — related
