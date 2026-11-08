---
title: CORAL LLM-Native Recommender Harness
tags: [harness, pattern]
summary: A fixed-order loop in which an LLM agent tunes a live recommender's resource allocation each cycle, under a constrained optimizer and an outcome-attributed memory, improving across A/B-tested rounds without retraining; gains were small.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-azhar-2026-coral.md
---

# CORAL LLM-Native Recommender Harness

CORAL (Azhar et al., Meta AI, a September 2026 preprint) puts an LLM agent in a closed loop around a production recommender. The harness fixes the control flow: analysis, retrieval, attribution, a constrained optimizer and an apply step run in the same fixed order every cycle, and the optimizer projects choices onto the budget so every change fits it by construction. The agent's memory has three stores: observations, its own assessments, and decisions with their attributed outcomes. It reinforces changes that helped and reverses those that did not, with no retraining. Defaults were not tuned: a cadence of 3 days and a memory of 3 cycles. Each decision is a structured output with a unit, an action from a feasible set, a rationale and a confidence.

## Results (self-reported)

- Retrieval-budget allocation on a video service, A/B tests over millions of users, 3 rounds (round 1 zero-shot, round 3 aggregating several cycles): once the loop had converged, sessions were up 0.16% and watch time up 0.15%, with serving cost unchanged. Round 1 gave +0.13% watch time, round 2 was neutral after an overcorrection, round 3 gave +0.15%. Allocating per segment lifted sessions by 0.23% among new users with little signal.
- Serving capacity on a different service, 2 rounds: round 2 widened round 1's change and grew the savings by 44% with engagement statistically unchanged.
- LLM cost: about 10 calls per cycle (about 1,500 tokens in, 2,500 out) for retrieval and about 8 calls for serving, totalling about 10^6 tokens, tens of dollars per deployment. Token counts are estimated because the pipelines do not log usage.
- The authors assert that tuning shrank from weeks of engineer time to a few days, which they did not measure.

## Limits

- Conceded: the loop runs under human supervision, only constrained resource allocation was tested, and each piece of evidence needs an expensive A/B test in one specific setting.
- Gains are mostly under 1%, with no confidence intervals, no human-tuned or non-LLM optimizer baseline, no ablation of memory or attribution, and only 2 or 3 rounds. The in-context learning claim is inferred from the round trajectory alone.
- The "no engineer in the loop" wording sits beside continuing human supervision.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Harness Continual Learning]] — related (also adapts the harness around a fixed model, with a gate)
- [[Verification Loops]] — related
