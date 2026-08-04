---
title: Constitutional AI and RLAIF
tags: [foundations, llm, eval, concept]
summary: "Anthropic's two-phase replacement for human preference labels — critique-and-revise SL-CAI followed by RLAIF against a written constitution — plus what AI feedback provably matches and where it still underperforms humans."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--constitutional-ai.md
---

# Constitutional AI and RLAIF

Constitutional AI (Anthropic, 2022 — arXiv 2212.08073) modifies **one stage** of the
[[RLHF Pipeline]]: it replaces the human preference labels in Stage 2 with AI-generated
critique guided by a written **constitution**. Stage 3 is unchanged PPO. It is a data-
generation method, not an optimizer.

## The problem it solves

Human preference labeling is the pipeline's scaling bottleneck. As models improve, the
labels get more expensive, slower, and require expert labelers capable of evaluating
outputs that are already good. Human labeling also introduces inconsistency, demographic
bias, and is hard to scale internationally.

## The constitution

A list of principles in natural language. Anthropic's original drew from the UN
Declaration of Human Rights, Apple's terms of service, Anthropic's internal usage
policies, DeepMind's Sparrow rules, and custom principles targeting specific failure modes.

> "Prefer the response that is least likely to contain harmful, unethical, or dishonest content"

> "Which response is less threatening or aggressive to the human?"

The constitution is **not fixed** — it is a design decision encoding the alignment target,
and different constitutions produce different behavioral profiles. This is the property
that makes the approach interesting beyond cost: the alignment target becomes a
**readable, editable, reviewable artifact** rather than the implicit aggregate of what a
labeling pool happened to prefer.

## Phase 1 — SL-CAI (supervised learning from AI feedback)

Reduce obvious harmful outputs *before* RL, by having the model rewrite its own responses:

1. Sample responses from a **helpful-only** model (trained for maximum helpfulness with
   no harmlessness training — it tends to comply with harmful requests)
2. Ask the model to **critique** its response against a randomly sampled principle
3. Ask it to **revise** to address the critique
4. Repeat critique-revise, typically **1–4 rounds**
5. Fine-tune on the final revised responses

The training distribution is **red-team prompts** — inputs designed to elicit harmful
behavior. The model learns from its own revisions: self-improvement through structured
critique.

## Phase 2 — RLAIF (reinforcement learning from AI feedback)

1. Sample response pairs from the SL-CAI model
2. A **feedback model** (same or larger) picks which better satisfies a constitutional
   principle, with a brief explanation
3. Train a preference model on those AI labels — same architecture and same
   [[Bradley-Terry Preference Model]] objective as an RLHF reward model
4. PPO against the preference model score, with the usual KL constraint

Only the *source* of the label changed. Everything downstream is identical.

## The helpfulness–harmlessness separation

Early RLHF on mixed human feedback produced "assistant-brained" models: over-cautious,
refusing legitimate requests, caveat-heavy. Constitutional AI's structural answer is to
train a **helpful-only model first**, then layer harmlessness on top — rather than mixing
helpfulness and harmlessness labels into one reward model.

This matters more than it appears. Mixing the two into a single scalar forces the reward
model to encode a fixed exchange rate between them, and every prompt then gets that same
exchange rate whether or not it is a safety-relevant prompt at all. Separating the stages
keeps the trade-off explicit.

## RLAIF as a standalone result

RLAIF (Lee et al., 2023 — arXiv 2309.00267) tested AI-versus-human feedback directly:

- With a **strong** feedback model (PaLM 2-L), preference rates are **comparable to
  human-feedback RLHF** on summarization and dialogue
- With **smaller** feedback models it degrades — feedback-model quality is the primary
  determinant of alignment quality
- **Distillation works**: a large teacher's feedback can align a smaller student policy,
  so the large model never has to be deployed

Where AI feedback still underperforms humans: nuanced cultural context and regional norms;
tasks needing lived experience; subtle bias the feedback model itself encodes; and novel
failure modes the constitution does not cover. The pattern across all four is that AI
feedback is strong on **stated** criteria and weak on **unstated** ones — which is the
same shape as the coverage limit of any written rubric.

## Self-improvement loop and its limits

```
model_n → critiques own outputs → revised outputs
   ↓
trained on revisions → model_n+1
   ↓
generates pair feedback → preference model
   ↓
PPO → model_n+2
```

Each iteration produces a better model that generates better training data for the next —
the mechanism behind successive Claude releases, each trained partly on feedback from its
predecessor.

**Limits:** a model cannot critique what exceeds its own understanding; constitutional
principles can conflict (helpfulness vs harmlessness) with no built-in arbiter; feedback
quality is bounded by the feedback model's own alignment; and **without human audits at
each iteration, alignment drift is hard to detect** — a closed loop optimizing against
its own judgment has no external reference to drift *against*.

## Versus standard RLHF

| Aspect | Standard RLHF | Constitutional AI |
|---|---|---|
| Feedback source | Human raters | AI model + constitution |
| Stage 2 cost | High (human time) | Low (AI inference) |
| Stage 3 optimizer | PPO | PPO (unchanged) |
| Transparency | Opaque (implicit judgment) | Explicit (constitution is readable) |
| Consistency | Variable (labeler drift) | High (deterministic given prompt) |
| Coverage | Bounded by human availability | Scales with compute |
| Auditability | Hard (rater decisions unlogged) | Easy (critique chains logged) |

## See Also
- [[RLHF Pipeline]] — extends (replaces the Stage 2 label source, leaves Stage 3 intact)
- [[Bradley-Terry Preference Model]] — depends-on (the preference-model objective, unchanged)
- [[Preference Optimization Algorithms]] — complements (generates preference data; any optimizer can consume it)
- [[Reward Hacking and Overoptimization]] — complements (an explicit constitution makes the alignment target auditable)
- [[LLM-as-Judge Evaluation]] — instance-of (a model judging model output, at training time rather than eval time)
