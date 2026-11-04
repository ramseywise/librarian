---
title: "Model Rollout: Shadow, Canary and A/B"
tags: [foundations, pattern]
summary: "A model that won the offline gate has won on old data; shadow shows disagreement before labels exist, canary routes a stable hashed share, and A/B is the only option when predictions change future data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--03-batch-and-online-serving.md
---

# Model Rollout: Shadow, Canary and A/B

Passing the [[Passive Retraining and the Promotion Gate]] means winning on old data. Rollout is how a model meets current traffic without risking all of it. In an interview study, engineers used between one and four stages, in the order test, canary, shadow and A/B, tied where possible to a product metric.

Flow: gate, shadow (both run, champion answers), canary (small share gets the challenger), A/B (compare the product metric), full traffic with the champion kept for rollback.

## What each stage shows

- **Shadow:** both models see every request, only the champion's answer is returned. Disagreement is visible immediately, before labels, and is often the first alarm for a broken deployment. Setup: a deliberately weak challenger trained on 200 rides, 3,000 live rides. Mean absolute difference 1.74 min (p99 5.81) with no labels; once labels arrived, champion RMSE 3.08 against challenger 3.68, and nobody was affected.
- **Canary:** route by a hash of a stable key (`sha256(key) % 100 < 5`), not a random draw per request, so one user stays on one side. A 5% canary gave 4.7% of rides in the test.
- **A/B:** the real comparison on the product metric.

## Limits

- Shadow fails in feedback loops: if the output changes what happens next (a recommender), the shadow model never sees the results of its own choices. The interviewees called shadow impossible there; only an A/B test will do.
- Keep a fallback (previous model or a rule) for when the model fails.
- Expect a gap: engineers reported production performance short of what offline evaluation promised. Continuous delivery for ML has three change axes (code, model, data) where conventional delivery considers only code.
- A random per-request canary puts one user on two models and pollutes the comparison.

## See Also
- [[Passive Retraining and the Promotion Gate]] — prerequisite-for
- [[Choosing Batch, Stream or Online Serving]] — related
- [[Model Registry Aliases and the Run Record]] — related (a challenger alias can drive shadowing)
- [[Peeking and Sequential Testing]] — related
