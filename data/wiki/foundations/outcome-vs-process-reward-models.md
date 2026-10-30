---
title: Outcome vs Process Reward Models
tags: [foundations, llm, comparison]
summary: "An outcome reward model scores the whole rollout and a process reward model scores each reasoning step. ORM is cheap but cannot tell a lucky guess from sound reasoning. PRM assigns credit better but needs step-level data, and in 2025 practice swung back to ORM with a light PRM used only for verification."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
---

# Outcome vs Process Reward Models

When RL is used to train reasoning, the reward model can score at two levels. Which one
you choose decides how credit flows back through a long chain of thought.

| | **Outcome Reward Model (ORM)** | **Process Reward Model (PRM)** |
|---|---|---|
| Scores | One scalar per *rollout*: was the final answer right? | One scalar per *reasoning step* |
| Training cost | Fast and simple | Slower; needs step-labelled data |
| Credit assignment | Coarse: every step gets the outcome's credit | Fine: catches the step where reasoning went wrong |
| Blind spot | Cannot separate sound reasoning that slipped at the end from bad reasoning with a lucky final answer | Labelling steps is expensive and the labels themselves can be wrong |

## The ORM blind spot

An ORM gives the same reward to a correct derivation and to a wrong derivation that lands
on the right number by accident. Over many updates, the policy is reinforced for whatever
correlates with right answers, including shortcuts. A PRM addresses this by rewarding the
steps directly. This is the same proxy problem as [[Reward Hacking and Overoptimization]],
moved from the response level to the step level.

## Why practice swung back to ORM

The 2025 picture in the source, reported with medium confidence, is that **ORM became
dominant again** for simplicity and scale. Two things made that possible:

- **Verifiable rewards.** For math and code, the outcome can be checked exactly (symbolic
  or numerical checking, running tests). A checked outcome is a much stronger signal than a
  learned outcome score, and it removes most of the reason to pay for step labels. This is
  the setting GRPO and DAPO are built for. See [[Preference Optimization Algorithms]].
- **Multi-trajectory majority voting.** At inference, sample 10–100 rollouts per prompt and
  take the majority final answer. The source reports significant accuracy gains over a
  single pass on competition math. Aggregating many outcomes recovers some of the
  robustness a PRM would provide, without step labels.

The emerging pattern is a **hybrid**. The ORM drives the training loop because it is
simpler, and a light PRM is used after inference for verification or confidence scoring.
The step-level signal moves out of the optimizer and into a checker. That is the same
maker/checker split described in [[Verification Loops]].

## The agent case

For multi-step agents, the same choice appears as **step rewards versus a binary outcome**.
Hand-designed per-step rewards (V-IRL navigation: +1 correct move, −1 wrong move, −1.5
landmark error) give easy credit assignment, but exploration is bounded by the designer's
bias. A binary success reward leaves exploration free at the cost of harder credit
assignment and more samples: SimpleVLA-RL used nothing else, took a robot-manipulation
task from 17.3% (SFT on one demo per task) to 91.7%, and discovered a grasp no human had
demonstrated. The rule of thumb: use process rewards when intermediate correctness is easy
to define, outcome rewards when the optimal path is unknown. An RLVR verifier is a
rule-based ORM; other reward forms for agents are summarized in [[Post-Training for Agents]].
[[RLVP — Verifiable Path Penalties]] sits between ORM and PRM: it keeps an outcome reward
and adds deterministic penalties for path violations, without a learned step scorer.

## See Also
- [[Preference Optimization Algorithms]] — prerequisite-for (GRPO and DAPO, the reasoning methods that consume these rewards)
- [[Reward Hacking and Overoptimization]] — extends (the proxy problem, at step level rather than response level)
- [[RLHF Pipeline]] — extends (Stage 2's reward model, specialised for reasoning)
- [[Verification Loops]] — alternative-to (step checking moved to inference time instead of training)
- [[RL Training Frameworks for LLMs]] — complements (where these reward models are wired into training)
- [[RLVP — Verifiable Path Penalties]] — alternative-to (outcome reward plus deterministic path penalties)
- [[Post-Training for Agents]] — extends (reward forms for agent RL)
