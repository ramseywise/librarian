---
title: ClawGym II Black-Box Harness RL
tags: [llm, agent-training, pattern]
summary: "RL that trains a model through an existing agent harness treated as a black box (OpenClaw or Claude Code), recording token ids and logprobs at a serving proxy and rebuilding trajectories as a prefix tree; the paper reports gains on ClawGym-Bench over the initial policy (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-song-2026-clawgym-ii.md
---

# ClawGym II Black-Box Harness RL

ClawGym II (Song, Bai et al., August 2026) trains a model by running it inside an existing agent harness, OpenClaw or Claude Code, treating that harness as a black box; the training system only sees the model calls it makes.

## Pipeline

- Each rollout gets its own sandbox.
- A serving proxy sits at the model boundary and logs the exact tokens and logprobs.
- A rollout's model calls are arranged in a prefix tree. Retry leaves, rollouts that branch too much, and subagent or compaction trajectories are discarded, so only the main agent's trajectories are trained on.
- All trajectories from one rollout share the terminal reward, and shared-prefix tokens count once.
- Task = (instruction, workspace, verifier) triplet; reward is a final-workspace check, either rule-based or a rubric/LLM judge (GPT-5.4 with 0.7 code and 0.3 rubric weights).
- PPO is simplified with gamma and lambda both 1, leaving the advantage as R_i - V(s_t). Training is token-in, token-out, with a truncated token-level importance-sampling weight (the smaller of exp(log pi_old - log pi_rollout) and a cap c). Further safeguards cover timeouts, sandbox failures that are thrown away, tool calls parsed from a buffered pseudo-stream, and a wait until trajectory records settle.
- Data and benchmark come from the earlier ClawGym (ClawGym-SynData, ClawGym-Bench).

## Reported results (self-reported)

Setup: Qwen3-8B and Qwen3-30A3B, 64K context, one run per cell, no seeds. The OpenClaw run (ClawII-OC) begins from a cold-start model with light SFT; the Claude Code run (ClawII-CC) starts from the base model.

- ClawGym-Bench average Pass@1 for the 30A3B model: OpenClaw 45.11 to 62.62, Claude Code 37.06 to 51.87. The paper states the gains as +9.98 (OpenClaw) and +14.81 (Claude Code). PinchBench (a 30-task text-only subset): +11.71 and +17.28.
- In the matching harness the 30A3B models also finish ahead of Qwen3-235A23B, a margin of 8.14 points for one and 6.28 for the other, and they also beat the ClawGym-30A3B SFT baseline under OpenClaw (62.62 vs 56.82).
- White-box RL in a simple AgentLoop (bash, search, fetch, code interpreter, file ops) scores 59.90 in-loop against 51.37 for the OpenClaw-trained model, but under OpenClaw it scores 50.33 against 62.62 for the model trained there; the authors say a simple white-box loop may not capture harness-specific interaction patterns.
- Joint OC+CC training (GRPO, advantages normalised per task-harness group, 32 instances x 8 rollouts) shows no evident instability or degradation against single-harness training; shown as curves only.
- GRPO (32 tasks x 8 rollouts) and PPO (256 tasks x 1 rollout) both train stably for 200 to 400 steps and end up comparable at equal rollout budget; PPO has smoother entropy and needs value pretraining. Harness and initialisation are confounded in this comparison.
- Cold start helps (higher starting reward, smoother entropy) but is not required; the base-init run shows a late entropy decline. Curves only.
- Harder tasks with synthesised data (Claude Code harness): JobBench-Easy 20.46 to 27.20, OfficeQA-Full 8.53 to 21.54.

## Limits

- The prefix-tree filters, the importance-sampling correction and the safeguards are described but never ablated.
- No seeds or intervals; OC runs are warm-started and CC runs are not, with no cold-start-versus-none table; mix-harness results are curves with no final table.
- Subagent and compaction trajectories are excluded and left to future work; the PPO simplification may raise advantage variance.
- Only Qwen3 8B and 30A3B, two harnesses, one data source and one judge; no check for contamination between ClawGym-SynData and ClawGym-Bench, both from the same group; no wall-clock, throughput or cost.
- The paper concedes white-box in-loop training beats black-box on the white-box loop.
- Table 1 columns were partly inferred when the paper's table was read, so per-column numbers carry that uncertainty.

## See Also
- [[Agent Lightning v1.0 Harnessed Agentic RL]] — alternative-to (another way to train through an existing agent's loop)
- [[Post-Training for Agents]] — prerequisite-for
- [[Harness Anatomy]] — prerequisite-for
- [[RL Training Frameworks for LLMs]] — related
- [[Training-Agent Disaggregation]] — related
