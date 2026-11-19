---
title: Harness-Zero Harness Distillation
tags: [llm, agent-training, pattern]
summary: "Harness-Zero evolves a task harness, uses a reviewer agent to correct the student's own proposals during data collection, and SFTs the corrections into the weights so the harness can be removed at deployment; reported macro-average success exceeds the base model with the harness attached (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-ye-2026-harness-zero.md
---

# Harness-Zero Harness Distillation

Harness-Zero (Ye et al., September 2026) moves what a specialised harness provides into model weights. The authors summarise the result as not removing the need for a harness but narrowing what the harness must provide.

## Mechanism (agent-as-harness)

1. An evolved harness h* (evolved by Kimi K3 over three rounds with a skill-guided loop) is adapted into private knowledge K.
2. During collection the student acts under a plain target harness h (mini-SWE-agent with one Bash tool). A harnessing agent (GPT-5.6 Sol) reviews each student response at the response boundary and either passes it or replaces it.
3. The collected trajectories are used for SFT. The loss masks reviewer-perspective reasoning.
4. At deployment the model runs under h alone, with no reviewer and no K.

Training data comes to 487 trajectories for SpreadsheetBench, 282 for AppWorld and 500 for USPTO. Two domains (SpreadsheetBench, AppWorld) keep only trials with reward 1.0; USPTO keeps every trial, which did better than keeping successes alone. The recipe is Tinker SFT with one model per domain, LoRA at rank 32 and alpha 32, batch size 8, 65,536-token sequences, 2 epochs, a peak learning rate of 2e-4 and seed 42.

## Reported results (self-reported)

Setup: Qwen3.5-9B base, one run, pass@1. Benchmarks are SpreadsheetBench Verified (100 held-out tasks), AppWorld (the 168 test_normal tasks, scored on scenario goal completion) and USPTO Retrosynthesis (100 tasks).

| Benchmark | Harness-Zero | Base | Base with h* |
|---|---|---|---|
| SpreadsheetBench | 44.0 | 31.0 | 39.0 |
| AppWorld | 58.9 | 26.8 | 48.2 |
| USPTO | 30.0 | 12.0 | 38.0 |
| Macro average | 44.3 | 23.3 | 41.7 |

- Procedural behaviour distils well; deep domain knowledge less so (USPTO 30.0 against 38.0 with h*).
- USPTO ablation (same collection split): fine-tuning on GPT-5.6 Sol's own trajectories leaves the student at 12.0 although that teacher succeeded on 52.0% of collection tasks; teacher under h* gives 3.0; student under h* 12.0; review with empty K 11.0; review with the oracle answer 15.0. The authors conclude that supervision comes from harness-guided review of the student's proposals, not stronger demonstrations. Trajectories collected under h* fail because the distilled student attempts harness tools it does not have and exhausts the turn limit.
- Recovery of behaviours that appear only under h*: 82.3% on average over 28 patterns (the base scores 0% by construction). Weak spots on AppWorld: "retrieve complete pages" 21/53 and "read back mutations" 6/12.
- Without any training, using an agent as the harness at inference averages 81.1% over six benchmark-model settings. The code-as-harness (meta-harness) averages 78.1%, mini-SWE-agent 68.6%, and the agent harness with an empty K 69.2%. Gains vary by setting.
- General-purpose harnesses hurt the 9B base: macro averages DeepAgents 20.5 and Claude Code 15.9 against 23.3 for mini-SWE-agent.
- Cost: review adds time during collection only (237.2 s per USPTO trial against 100.1 s for mini-SWE-agent, about 2.4x); no token counts or deployment latency reported.

## Limits

- Needs a capable harnessing model: on USPTO the review turns help little or hurt weaker students (agent-as-harness minus meta-harness, by model: GPT-5.6 Sol +1.0, DeepSeek-V4-Pro +4.0, DeepSeek-V4-Flash -1.0, Qwen3.6-35B-A3B -12.0).
- Deep domain knowledge may not be fully absorbed by SFT, and harness mechanisms like context management cannot be written as student responses. Reviewing each proposal is expensive. The paper leaves selective review and preference learning to future work, and its rejected/preferred pairs are unused.
- Single seed and single run, 100-task test sets with no intervals, one student size (9B), no comparison with RL, an ablation on USPTO only, and no transfer to harnesses other than h shown.

## See Also
- [[Harness-R1 Learned Harness Editing]] — related (learned changes to the harness rather than the weights)
- [[Harness Anatomy]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
- [[ClawGym II Black-Box Harness RL]] — related
- [[AutoHarness Synthesized Code Harness]] — related
