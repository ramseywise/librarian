---
title: CoELA Modular Embodied Agents
tags: [graph, concept]
summary: Five-module cooperative embodied agent (perception, memory, communication, planning, execution) with LLM-driven communication and planning, tested on TDW-MAT and C-WAH with one run per setting (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zhang-2023-building-cooperative-embodied-agents-modularly.md
---

# CoELA Modular Embodied Agents

CoELA (2023) assembles a cooperative embodied agent from five modules, two of them driven by an LLM: **Communication**, which writes the messages, and **Planning**, which makes a zero-shot chain-of-thought selection from a multiple-choice Action List. Perception relies on a Mask-RCNN fine-tuned on 53K training images (mAP@50 of 81.4% on TDW test data), a Memory module, and Execution runs A*-based procedures. The agent is tested on TDW-MAT and C-WAH using GPT-4, LLAMA-2-13b-chat and CoLLAMA (fine-tuned with LoRA on 572 filtered trajectories), and in a human study with 8 subjects. Efficiency Improvement (EI) is the gain in the key efficiency metric when a partner is present rather than working solo, taken relative to the larger of the two.

## Results (self-reported)

CoELA runs are one run per setting; the RHP and MHP planning baselines use 5 runs.

- TDW-MAT total transport rate (TR): RHP alone 0.43 (0.50 with oracle perception). Two GPT-4 CoELA agents score 0.71 without oracle perception and 0.85 with it; CoELA paired with RHP beats two RHP agents.
- Comparing models without oracle perception, CoLLAMA gets 0.70, un-tuned LLAMA-2 gets 0.53 and GPT-4 gets 0.71. Given oracle perception, the scores are 0.62 for LLAMA-2, 0.80 for CoLLAMA and 0.15 for the MAT baseline.
- C-WAH symbolic observation, 10 episodes: MHP with CoELA needs 59 steps against 75 for two MHP agents (111 alone); two CoELA agents reach 57 steps (49% EI).
- Human study, 80 trials: trust score 6.3 for CoELA with natural-language communication against 4.7 without (t-test p=0.0003).
- Ablations (values only in Fig 4): turning off communication between two AI agents produced no significant drop; dropping the Memory module nearly doubles the steps; GPT-3.5 in place of GPT-4 takes more steps, with more reasoning errors and unhelpful messages; and without the Execution module, with the LLM issuing low-level controls itself, no trial completed any task.

## Limits

- Cost limited CoELA to one run per setting, so no variance is available, and the test sets are small (24 TDW-MAT episodes and 10 C-WAH episodes).
- The authors concede that 3D spatial information is little used, that low-level actions are not reasoned over, and that complex reasoning such as counting the remaining goals is unstable; they put the missing gain from AI-to-AI communication down to communication cost and LLM limits.
- The MAT baseline was given an oracle semantic map and central observation, so it is not like-for-like; ablation values are only in figures; 2023-era models.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Agent Fundamentals]] — prerequisite-for
- [[CAMEL Role-Playing Inception Prompting]] — related
