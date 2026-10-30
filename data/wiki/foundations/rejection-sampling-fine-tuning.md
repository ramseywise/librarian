---
title: Rejection Sampling Fine-Tuning
tags: [foundations, llm, pattern]
summary: "Sample several candidates per prompt, keep only those a rule, test or reference answer verifies, deduplicate and cap per prompt, SFT on the survivors, and repeat as the model improves — the STaR/RFT loop that sits between SFT and RL with no reward model and no policy gradient."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
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

## See Also
- [[Post-Training for Agents]] — instance-of (one of the jobs SFT is good for)
- [[On-Policy Distillation]] — alternative-to (dense per-token signal instead of pass/fail filtering)
- [[Outcome vs Process Reward Models]] — prerequisite-for (the verifier is a rule-based outcome check)
