---
title: Rejection Sampling Fine-Tuning
tags: [foundations, llm, pattern]
summary: "Sample several candidates per prompt, keep only those a rule, test or reference answer verifies, deduplicate and cap per prompt, SFT on the survivors, and repeat as the model improves — the STaR/RFT loop that sits between SFT and RL with no reward model and no policy gradient."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/papers/2026-11-06-chen-2023-fireact.md
---

# Rejection Sampling Fine-Tuning

Rejection-sampling fine-tuning (RFT; the STaR family) turns a verifier into SFT data:

1. Sample k candidates per prompt (k = 4–16 is typical).
2. Verify each with rules, tests or a reference answer.
3. Keep the passes, deduplicate, and **cap how many each prompt contributes** so easy
   prompts do not dominate.
4. Run SFT on what survives.
5. Repeat as the model improves, so later rounds sample from a stronger policy.

## Where it sits

RFT uses the **verify–generate asymmetry** that makes RL work — recognising a right answer
is easier than writing one — but trains with the plain SFT loss. There is no reward model
and no policy gradient, so it is cheap and stable. The data is partly on-policy (the model's
own samples) but the signal is still pass/fail filtering rather than a per-token gradient,
which is what [[On-Policy Distillation]] adds.

It is also the third layer of a typical SFT data supply: human seed demos pin the format, a
teacher model scales them, and rejection sampling raises quality to the bar. Filtering wrong
reasoning before training matters because SFT bakes noise into the weights.

## FireAct as an agent instance

FireAct (a 2023 preprint) is the clearest agent example: GPT-4 few-shot ReAct trajectories on HotpotQA are filtered to the successful ones, then a smaller model is tuned on 500 of them, with chain-of-thought and Reflexion trajectories reformatted as ReAct in the mixed variants. Reward only decides which trajectories to keep. Reported (self-reported, 500 dev questions, Google search tool): Llama-2-7B rose from 14.8 to 26.2 EM and GPT-3.5 from 31.4 to 39.2, which beats GPT-4 with plain prompting but not GPT-4 with chain-of-thought or ReAct. Time per trial dropped from 9.0s to 2.7s, and the tuned agent degraded less under a corrupted search tool (33.6 against 20.8 when half the results were empty). Mixing methods helped some bases and hurt others; picking the right method per question would reach 52.0 against 32.4 for random choice. Single-task LoRA reached 26.2 where full tuning reached 30.2.

## Limits

- FireAct covers one task type (question answering) and one search tool, with no RL or preference baseline and no seeds; standard errors of 1.6 to 2.2 EM make some gaps small. Mixed-data runs add samples as well as diversity, so quantity is confounded. The extraction notes Table 13's caption names Llama-2 while its rows are CodeLlama, and the intro says four times faster where the table gives about 3.3. The models are 2023 vintage and live search can drift.

## See Also
- [[Post-Training for Agents]] — instance-of (one of the jobs SFT is good for)
- [[On-Policy Distillation]] — alternative-to (dense per-token signal instead of pass/fail filtering)
- [[Outcome vs Process Reward Models]] — prerequisite-for (the verifier is a rule-based outcome check)
- [[RLHF Pipeline]] — alternative-to
- [[RISE Recursive Introspection]] — related (best-of-N relabelling of rollouts as training targets)
- [[Post-Training Reasoning Data Primer]] — related
- [[Agent-FLAN Agent Tuning Data Design]] — related (mixture design for agent SFT data)
