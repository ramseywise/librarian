---
title: Bradley-Terry Preference Model
tags: [foundations, llm, eval, concept]
summary: "The pairwise-comparison model that converts human choices between two responses into a scalar reward — the shared formal core underneath RLHF reward models, DPO, and RLAIF preference models."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--constitutional-ai.md
---

# Bradley-Terry Preference Model

A statistical model of pairwise choice. Given a latent quality score for each item, it
gives the probability that one is preferred over the other:

```
P(y_w ≻ y_l | x) = σ( r_θ(x, y_w) - r_θ(x, y_l) )
```

Preference probability depends only on the **difference** of the two scores, squashed
through a sigmoid. Equal scores give 50/50; a one-unit gap gives ~73%.

## Why it is the hinge of the whole alignment stack

Preference alignment has a data problem before it has an optimization problem: what
humans can reliably produce is *"B is better than A"*, and what an optimizer needs is a
scalar to ascend. Bradley-Terry is the bridge, and every method below reuses the same
bridge:

| Method | What Bradley-Terry supplies |
|---|---|
| [[RLHF Pipeline]] | The Stage 2 reward-model loss |
| [[Direct Preference Optimization]] | The loss the policy is fitted to directly, no reward model |
| [[Constitutional AI and RLAIF]] | The preference-model objective, with AI-generated labels |

That shared lineage is why these methods are far less different from each other than
their names suggest. They disagree about *where* the Bradley-Terry objective is applied,
not about the model of preference itself.

## Consequences worth knowing

**Rewards are only identified up to an additive constant.** Since only differences are
supervised, adding any constant to every score leaves the loss unchanged. Absolute reward
values are therefore meaningless — a reward of 4.2 says nothing on its own, and reward
magnitudes are not comparable across training runs.

**Transitivity is assumed, not observed.** The model assumes a single consistent quality
ordering exists. Genuinely cyclic or context-dependent human preference gets flattened
into whatever scalar ordering minimizes loss, so irreducible disagreement between
labelers shows up as a low-confidence reward model rather than as a visible signal that
the preference is contested.

**Label noise sets the ceiling.** Because the objective is pure maximum likelihood over
observed choices, systematically biased labels produce a confidently biased reward model.
This is the mechanism behind the verbosity and sycophancy failures in
[[Reward Hacking and Overoptimization]] — the model is not malfunctioning, it is fitting
the preferences it was actually shown.

## See Also
- [[RLHF Pipeline]] — part-of (the Stage 2 reward-model objective)
- [[Direct Preference Optimization]] — implements (fits the same objective directly on the policy)
- [[Reward Hacking and Overoptimization]] — extends (what goes wrong when the fitted proxy is over-optimized)
- [[Constitutional AI and RLAIF]] — instance-of (same objective, AI-generated labels)
- [[LLM-as-Judge Evaluation]] — complements (pairwise comparison as an eval-time rather than training-time primitive)
