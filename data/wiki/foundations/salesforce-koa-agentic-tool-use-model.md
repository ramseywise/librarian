---
title: Salesforce Koa
tags: [foundations, reference]
summary: "Koa is Salesforce's Nemotron-3-Super-120B model trained with a GRPO variant in spec-driven CRM environments; it scored 87% on the internal CRMAgentBench against 82% for GPT-4.1, while giving back 2.3 BFCL points after the in-domain stage (all self-reported, single runs)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-salesforce-koa.md
---

# Salesforce Koa

Chen et al. (Salesforce Agentforce and AI Research, with NVIDIA, a 2026 technical report) post-train Nemotron-3-Super-120B for enterprise tool use. The base was already RL post-trained. The reported checkpoint is a single-environment run at step 100, quantized to FP8.

## Recipe

- **Environments:** Agent Script specifications compile to a typed workflow graph and expand into persona and scenario sessions in NeMo Gym. In-domain data are production Salesforce specs, using only specification-derived and synthesised interactions.
- **Reward:** coverage, the share of numbered sub-questions resolved, judged one by one by a frozen Nano-30B helper that also plays the customer and the tools; the reward drops to zero if the same tool call is made twice in a row; and sub-questions that need data count only when a successful call grounds them. A sandbox variant uses binary state equivalence, and a constrained-decision mode withholds a needed tool.
- **GRPO variant:** leave-one-out baseline with normalisation, dynamic sampling that drops zero-variance groups, one update per batch, truncated token-level importance weighting, a fixed negative advantage for malformed syntax and masking of over-length trajectories.

## Results (self-reported)

- CRMAgentBench has 97 tasks over 5 domains, scored all-or-nothing against an LLM user simulator. Scores were 87% for Koa, 91% for GPT-5.5, 82% for GPT-4.1 and 79% for the base model. Customer Service and Marketing were flat or lower than GPT-4.1.
- Human-labelled production tool-calling success: 0.819 base, 0.825 after public RL, 0.842 BF16, 0.848 FP8. On the synthetic judged set, success was flat (0.846 base, 0.847 FP8) and frontier models led (GPT-5.5 0.902).
- BFCL overall, in the order base, after public RL, Koa BF16, Koa FP8: 64.73, 66.63, 64.31, 63.87. Multi-turn BFCL, again in that order, gave 54.12, then 59.50, 57.50 and 53.50.
- SFT against RL from this base: BFCL multi-turn 53.25 against 59.50; tau2 70.04 against 69.41 (base 68.64). The SFT run used a deliberately small learning rate and was not tuned further.
- On the Tau2Bench weighted average (pass^1 over 4 trials) Koa scored 69.33 against 68.64 for the base and 83.99 for GPT-5.5.

## Limits

- The authors concede that favouring RL over SFT may not carry over to a checkpoint that has not already had RL, and that some enterprise evaluations use modest task counts.
- Not shown: seeds or intervals, human-labelled set size, judge identities, training curves, reward-hacking analysis, ablations of the duplicate gate or coverage reward, and any GPU-hours or dollars. The internal benchmarks are not public and no overlap check with training data is described.
- Gains are 1 to 3 points in single runs; "capability preserved" on BFCL means no gain. GPT-4.1 BFCL numbers come from the public leaderboard, not the same harness. FP8 latency and memory are not reported.
- The extraction flags some GPT-4.1 table values as its own best reading.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[APIGen]] — prerequisite-for
- [[RL Training Frameworks for LLMs]] — related
