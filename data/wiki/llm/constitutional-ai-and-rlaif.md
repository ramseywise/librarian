---
title: Constitutional AI and RLAIF
tags: [llm, preference-and-alignment, eval, concept]
summary: "Anthropic's two-phase replacement for human preference labels — critique-and-revise SL-CAI followed by RLAIF against a written constitution — plus what AI feedback provably matches and where it still underperforms humans."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--constitutional-ai.md
  - data/raw/papers/2026-11-07-bai-2022-constitutional-ai.md
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

## What the paper reports

The Constitutional AI paper (Bai et al. 2022) asks if a helpful and harmless assistant can be built without any human harmlessness labels, relying on a brief list of written principles. In the RL-CAI stage a feedback model picks the more harmless of two responses by multiple choice, giving either soft log-probability labels or chain-of-thought labels clamped to 40-60 percent; the preference model blends these AI harmlessness labels with human helpfulness labels. All findings are (self-reported); the model size is 52B unless stated.

- The SL-CAI critique-and-revision data are 4 revisions for each of 182,831 red-team prompts (no model size given).
- Clamping chain-of-thought probabilities to 40-60 percent did best (20-80 helped slightly, while leaving them unclamped gave extreme responses). For RL-CAI without chain of thought, soft labels did much better than hard ones.
- By crowdworker Elo, RL-CAI models are clearly more harmless than both RLHF and SL-CAI; the chain-of-thought variant is slightly less helpful and slightly more harmless. No Elo values are printed.
- By preference-model score, critiqued revisions outperform direct ones on small models while the two are close on large ones (sizes unstated; 52B was inspected), and the critiques were frequently wrong. Varying the principle count N from 1 to 16 does not shift the harmlessness preference-model score.
- RL-CAI trained too long Goodharts, producing harsh or boilerplate replies (one example: "you are valid, valued, and cared for").
- Absolute harmfulness (0-4 scale, 64 held-out red-team prompts with 256 responses each): helpful RLHF grows more harmful over RL, whereas HH RLHF, RL-CAI and RL-CAI with chain of thought grow less harmful.
- Elo gaps for HH RLHF are far smaller than in earlier work, because workers were instructed to favour answers that do not evade.

## Limits

- The principles were picked ad hoc for research, and the authors want a wider set of stakeholders to refine them.
- The approach still needs human labels for helpfulness and an RLHF model trained to be helpful.
- The main results are Elo plots without printed values, seeds or significance tests; RL hyperparameters are deferred to an earlier paper.
- Preference-model scores are less well calibrated at the high end, and absolute harmfulness scores may be miscalibrated across workers.
- The HH RLHF comparisons depend on a modified worker instruction that penalises evasion, and on older preference data gathered under other instructions (Upwork and MTurk against Surge).

## See Also
- [[RLHF Pipeline]] — extends (replaces the Stage 2 label source, leaves Stage 3 intact)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the preference-model objective, unchanged)
- [[Preference Optimization Algorithms]] — related (generates preference data; any optimizer can consume it)
- [[Reward Hacking and Overoptimization]] — related (an explicit constitution makes the alignment target auditable)
- [[LLM-as-Judge Evaluation]] — related (the general primitive: a model judging model output, at training time rather than eval time)
- [[Constitutional Classifiers]] — extends (a constitution used to train input and output classifiers rather than the policy)
- [[ETHICS Benchmark]] — related (a dataset for testing predicted human moral judgments)
- [[LM Red Teaming]] — related (automated red-team prompt generation)
- [[ETHICS Benchmark]] — related (a dataset for testing predicted human moral judgments)
- [[LM Red Teaming]] — related (automated red-team prompt generation)
- [[Self-Critiquing Models for Human Evaluators]] — related
- [[Self-Rewarding Language Models]] — alternative-to (the judge is the policy itself rather than a fixed feedback model)
- [[UltraFeedback Scaled AI Feedback Dataset]] — related (GPT-4 feedback data at scale)
- [[BeaverTails Decoupled Safety Preference Dataset]] — related (separate harmlessness and helpfulness annotation)
