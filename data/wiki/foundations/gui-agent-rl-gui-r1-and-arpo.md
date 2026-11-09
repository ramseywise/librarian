---
title: GUI Agent RL with GUI-R1 and ARPO
tags: [foundations, llm, comparison]
summary: "Two GRPO recipes for GUI agents: GUI-R1 uses rule-based rewards on 3K filtered examples for action prediction, while ARPO adds a replay buffer of successful trajectories so groups of all failures still carry signal; both report gains with large caveats in their own text."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-luo-2025-gui-r1.md
  - data/raw/papers/2026-11-06-lu-2025-arpo.md
---

# GUI Agent RL with GUI-R1 and ARPO

Both papers apply GRPO to vision-language GUI agents, but at different levels of the stack.

## GUI-R1 (action prediction, rule rewards)

- Base Qwen2.5-VL at 3B and 7B, one action space across five platforms. Reward is a weighted sum of a format term and an accuracy term; accuracy adds exact action match, a click inside the target box, and a text F1 above 0.5. Best weighting was 0.2 format and 0.8 accuracy.
- Data: roughly 14M examples were collected, filtered by 10 rollouts per item from the 7B base to drop all-correct and all-wrong items, and 3K were kept.
- Results (self-reported, zero-shot, eight benchmarks): 3B on ScreenSpot 80.08 against 63.55 for SFT on the same 3K data; low-level overall 80.88 against 55.65 for the base; high-level overall 49.75 (3B) and 56.13 (7B). The 7B gain over its base overall is only about 5.6 points on high-level tasks.
- Response length first fell then rose with no "aha moment".

## ARPO (replay for sparse reward)

- GRPO plus a per-task buffer of successful trajectories. When a whole group of rollouts fails, one failure is swapped for a stored success so the reward still varies. Binary task reward; no KL term; asymmetric clipping; 8 rollouts per task; 256 parallel environments.
- Setup: UI-Tars-1.5 7B, a 128-task OSWorld subset kept because at least one of 16 rollouts succeeded, 15-step limit, single run.
- Results (self-reported): OSWorld 29.9 against 26.0 for plain GRPO and 23.5 base; on the stricter variant with no automatic credit for infeasible tasks, 23.8. On the 32 in-domain training tasks success rose from 68.8 (GRPO) to 81.25, a gain of 4 tasks; on the other 96 tasks from the same pool the scores were 55.2 (base), 52.08 (GRPO) and 56.3 (ARPO).
- Against preference-style baselines on the same data: ARPO scored 27.3 and GRPO 26.0, with KTO at 24.6, DPO at 22.4 and rejection-sampling SFT lowest at 21.8.

## Limits

- GUI-R1: the extraction flags an inconsistent data ratio (0.02% of 13M in the abstract, 0.2% of 14M in Section 4.2); the 0.8/0.2 ablation row duplicates another model's per-column values; no ablation removes individual reward terms; the SFT averages are not in the cited table.
- ARPO: the extraction flags 29.9 in Table 1 against 27.3 in the baseline comparison with no explanation; the out-of-domain claim is worded inconsistently across sections; the replay gain rests on tiny task counts and the benchmark is the authors' hardened variant.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Computer Use Visual Grounding]] — related
- [[ComputerRL API-GUI Agent RL]] — alternative-to
- [[DAPO]] — related (the same reward-variance concern)
- [[Rejection Sampling Fine-Tuning]] — alternative-to
- [[UI-TARS Native GUI Agent]] — related (ARPO builds on a UI-TARS model)
