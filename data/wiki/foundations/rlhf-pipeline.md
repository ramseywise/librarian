---
title: RLHF Pipeline
tags: [foundations, llm, concept]
summary: "The three-stage InstructGPT pipeline — SFT, then a Bradley-Terry reward model on ~33k comparisons, then PPO with a KL penalty against the SFT policy — and why all three stages are load-bearing."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--README.md
---

# RLHF Pipeline

Reinforcement Learning from Human Feedback turns a next-token predictor into an
instruction-follower by learning a **model of human preference** and then optimizing
against it. The InstructGPT formulation is three stages, run in order, each producing an
artifact the next stage consumes.

```
Pretrained LM
    │
    ▼
[Stage 1] Supervised fine-tuning on demonstrations   →  π_SFT
    │
    ▼
[Stage 2] Reward model on pairwise comparisons       →  r_θ
    │
    ▼
[Stage 3] PPO against r_θ, KL-anchored to π_SFT      →  π_RLHF
```

## Stage 1 — Supervised fine-tuning

Human labelers write demonstration responses to prompts; the base model is fine-tuned on
them. InstructGPT used roughly **13k** demonstrations.

**Why SFT must come first.** A pretrained model's output distribution is too diffuse to
be a useful RL starting point — most sampled responses are off-task, so the reward signal
carries almost no gradient information. SFT concentrates the distribution on plausible
responses first, and only then is preference optimization discriminating between things
worth discriminating between. It also becomes the **reference policy** the KL penalty in
Stage 3 anchors to, so its quality bounds the whole pipeline.

## Stage 2 — Reward model

The reward model is the SFT model with the language-modeling head replaced by a **scalar
head** — one number per (prompt, response) pair. It is trained on human **rankings** of
multiple responses to the same prompt (~33k comparison pairs for InstructGPT), not on
absolute scores.

Ranking rather than scoring is deliberate: humans are unreliable at assigning calibrated
absolute quality scores but comparatively reliable at picking the better of two options.
The formal machinery for converting those pairwise choices into a scalar is the
[[Bradley-Terry Preference Model]], giving the loss

```
L_RM(θ) = -E_[(x, y_w, y_l) ~ D] [ log σ( r_θ(x, y_w) - r_θ(x, y_l) ) ]
```

where `y_w` is the preferred (won) response and `y_l` the rejected one. Only the
*difference* of rewards is ever supervised, so `r_θ` is identified up to an additive
constant — which is fine, because Stage 3 only uses relative reward.

## Stage 3 — PPO with a KL penalty

The policy is optimized to maximize reward while being penalized for drifting from the
SFT reference:

```
L_PPO(θ) = E[ r_θ(x, y) ] - β · KL[ π_θ(y|x) ‖ π_SFT(y|x) ]
```

with **β typically 0.02–0.2**, and PPO's clipped surrogate objective
`min(r_t · A_t, clip(r_t, 1-ε, 1+ε) · A_t)` bounding per-step policy movement.
InstructGPT used ~31k prompts here.

The KL term is not a regularizer in the ordinary sense — it is the thing preventing
[[Reward Hacking and Overoptimization]]. `r_θ` is a *learned approximation* of preference,
valid only near the distribution it was trained on. Unconstrained optimization walks the
policy off that distribution and into the reward model's errors. β sets how far you are
willing to walk.

## Practical cost

Stage 3 holds **four models simultaneously** — policy, reference, reward model, and
value/critic — for roughly **4× the memory** of ordinary fine-tuning. This cost is the
main reason the field moved toward the offline methods in
[[Preference Optimization Algorithms]], which drop one or more of the four.

**Labeler quality dominates labeler volume.** Inconsistent preference labels put a
ceiling on the reward model that no amount of additional Stage 3 compute can lift — the
policy will faithfully optimize toward whatever the labels actually encoded.

## See Also
- [[Data Engineering Foundations]] <!-- auto-linked -->
- [[Bradley-Terry Preference Model]] — part-of (the Stage 2 objective)
- [[Reward Hacking and Overoptimization]] — extends (the three failure modes of Stage 3)
- [[Preference Optimization Algorithms]] — alternative-to (offline methods that collapse or skip stages)
- [[Constitutional AI and RLAIF]] — extends (replaces the human labels in Stage 2 with AI feedback)
- [[Direct Preference Optimization]] — alternative-to (removes the reward model entirely)
