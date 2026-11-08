---
title: Critical-State RL
tags: [foundations, llm, pattern]
summary: "Critical-State RL picks which single tool call in a multi-turn trace to train on, ranking candidates by how much the action itself changes the outcome, then runs occurrence-local RL on that call only; it beat the alternative turn in all four BFCL cells tested (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-critical-state-rl.md
---

# Critical-State RL

Critical-State RL (a Salesforce AI Research preprint, September 2026) starts from a credit-assignment complaint: spreading one terminal reward across a whole multi-turn tool-use trajectory dilutes the signal. It instead chooses one occurrence, such as the decision turn or the recovery turn after a missing-function error, and puts the gradient only on that call's tokens.

## Selection rule

- Humans or deterministic rules propose candidate phases; failure patterns are tabulated by error type, comparing the policy with a stronger model.
- A candidate is scored by the corrected variance of the expected outcome across different actions at that point, estimated by nested sampling (several actions, several continuations per action). The estimator is unbiased but can go negative.
- Three gates screen candidates: the label must mediate action to return, some action must beat the reference policy, and the action-level variance must be positive.
- Training is occurrence-local contextual-bandit RL. The authors note that a mixed-outcome filter, which keeps groups whose reward varies, can retain groups where every rollout behaves the same and only the label noise varies.

## Results (self-reported)

Setup: Gemma-4-26B-A4B with thinking off, evaluated on 200 paired BFCL v4 multi-turn items at the step-30 checkpoint; selected cells use four training seeds, alternatives are single runs.

- missing-function recovery turn 0.14 to 0.283 (+14.3 points) while the decision turn fell 0.14 to 0.095; missing-parameter decision turn 0.435 to 0.473 (+3.8), recovery turn +1.
- Full return-to-go credit reached 0.997 on the gym validation set but only 0.45 on BFCL missing-parameter.
- Whole-trajectory optimiser steps cost 16 to 30 times an occurrence-local step (Nemotron-Super-120B, LoRA, GRPO with dynamic sampling).
- Other settings (not matched tests): a Qwen3-235B-based internal checkpoint's BFCL agentic/memory mean 34.54% to 50.54%; the best turn differs by model, so the diagnostic must be rerun per setting.

## Limits

- The authors report only categorical turn selection was tested; alternatives, return-to-go and SFT comparators are single-seed; evaluation noise reaches 3 to 5 points; candidate phases are human-proposed; the missing-parameter result is "directional"; one base model for the main test; one internal checkpoint is unreleased.
- Overall BFCL plateaus around 59 to 60% while other categories decline. The theory for many occurrences (K above 1) is toy or conditional; the applications use K equal to 1.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — alternative-to (dynamic sampling keeps mixed-outcome groups; this ranks by action effect)
- [[APIGen]] — related
- [[Salesforce Koa]] — related
