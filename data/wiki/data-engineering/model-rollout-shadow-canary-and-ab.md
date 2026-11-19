---
title: "Model Rollout: Shadow, Canary and A/B"
tags: [data-engineering, ml-platform, pattern]
summary: "A model that won the offline gate has won on old data; shadow shows disagreement before labels exist, canary routes a stable hashed share, and A/B is the only option when predictions change future data."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--03-batch-and-online-serving.md
  - data/raw/papers/2026-11-07-building-applications-with-ai-agents-ch10-monitoring-production.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch01-what-is-machine-learning-engineer.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch04-before-you-model-communication-logistics-projects.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch11-model-measurement-why-its-so-important.md
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

## In agent services (Albada)

Albada (*Building Applications with AI Agents*, O'Reilly 2025, chapter 10) applies both stages to agent versions. In shadow mode the new version runs beside production on the same inputs, linked by a shared request ID, without serving its outputs to users. A canary then serves 1 to 5% of traffic, tags metrics by version, alerts on regressions and rolls back immediately. These are the chapter's recommendations, not measured results.

## In Wilson's project advice

Wilson (*Machine Learning Engineering in Action*) advises planning an A/B test before full rollout and agreeing the attribution measure with the business during planning; in his hypothetical, a good production model was cancelled when nobody could say what it earned. He advises setting up self-service A/B metrics datasets at the preproduction review, never releasing on a Friday, and asking stakeholders to hold judgement until the data is statistically valid. These are practitioner recommendations from his experience, not measured results.

## Wilson on measuring a model's business impact

Wilson (*Machine Learning Engineering in Action*, chapter 11) advises judging a model by the business's metrics (here revenue and coupon use) and not ML loss alone, with both kept for the project's life, and agreeing the metric definitions with the teams that already compute them. His running example tests a personalised send-time model for a weekly coupon email to 50,000 customers against a fixed Monday 8 a.m. bulk send as control (simulated data).

- **Stratify, then sample randomly inside strata.** He buckets customers on recency, frequency and monetary value into five quantile buckets each (125 cohorts), collapses them with marketing experts into high, medium and low value, and samples within those groups so control and test are balanced. He warns against a split such as 90% of the top group landing in control. See [[RFM Segmentation Validated on a Holdout]] for a holdout check of the segments themselves.
- **Size the test before release.** He works out, with statsmodels `tt_ind_solve_power` how many samples and how long a conclusive result needs (effect sizes 0.01 to 0.5, power 0.8, alpha 0.2 and 0.01, two-sided) and tells the business; a smaller alpha or a smaller lift needs many more samples. He advises fixing the evaluation rules and a significance-monitoring job in advance and not reading early daily deltas.
- **Pick the test from the data's shape.** He advises plotting the density first, since revenue is often heavy-tailed. For his non-stationary high-value cohort over 150 days he uses Mann-Whitney U and reads about 97% certainty that the groups differ; he reserves t-test and ANOVA for stationary normal data, Tukey HSD for pairwise comparison across many groups, and Fisher's exact or chi-square on a 2x2 table for yes/no outcomes (50,000 coupons over 50 days, one pooled group). See [[Statistical Test Selection]].
- **No causal claim.** He advises against claiming causation, whether the evidence is a model correlation or a significant A/B outcome on its own: in his view the test only rules out equivalence and shows the predictions are useful. When several changes ship together he accepts the confounding, releases the best solution first and runs variation tests later.

Limits: all data are simulated; the power calculation assumes normality and balanced groups, and nonparametric power is left out; the chapter names bias measurement for customer-facing models without covering it; the listings use deprecated or fragile calls (a `wilcoxon` on unpaired samples).

## See Also
- [[Passive Retraining and the Promotion Gate]] — prerequisite-for
- [[Choosing Batch, Stream or Online Serving]] — related
- [[Model Registry Aliases and the Run Record]] — related (a challenger alias can drive shadowing)
- [[Peeking and Sequential Testing]] — related
- [[Online Eval Sampling]] — related (what to score on the live traffic once a version is exposed)
- [[ML Deployment Challenges: Interview Study and the Three Vs]] — related
