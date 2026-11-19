---
title: Cognitive Behaviors for Self-Improving Reasoners
tags: [llm, reasoning-and-planning, concept]
summary: "Gandhi et al.'s account of why one base model improves under RL on a verifiable task while another plateaus: four behaviours (verification, backtracking, subgoal setting, backward chaining) in the initial policy, tested on Countdown with two 3B models."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gandhi-2025-cognitive-behaviors-that-enable-self.md
---

# Cognitive Behaviors for Self-Improving Reasoners

Gandhi et al. (2025, COLM) ask what separates base models that gain a lot from RL on a verifiable task from those that stall. They hypothesise that the initial policy needs four behaviours before RL can exploit additional test-time compute well. Backtracking means openly revising an approach once an error is noticed; verification means methodically checking intermediate results; subgoal setting breaks a complex problem into manageable steps; backward chaining works backwards from a desired outcome. A GPT-4o-mini classifier counts the behaviours in model outputs.

## Method

Countdown is the task; the RL algorithm is PPO via VERL's TinyZero code, and the two models are Llama-3.2-3B and Qwen-2.5-3B. Llama is first prepared in one of two ways, then RL-trained: SFT on Countdown traces written by Claude-3.5-Sonnet with chosen behaviours, or continued pretraining on 8.3M tokens of OpenWebMath that were filtered for behaviours and rewritten.

## Results (self-reported)

- Same PPO, 250 steps, 4 rollouts per prompt: Qwen-2.5-3B reaches about 60% on Countdown, Llama-3.2-3B about 30%.
- Priming Llama with empty or length-matched placeholder thoughts leaves it at about 30-35%, so extra tokens alone do not help.
- Priming with the right behaviours performs the same whether the priming solutions are correct or incorrect, and priming with backtracking matches Qwen's trajectory.
- Continued pretraining on the behaviour-curated 8.3M-token set gives RL performance comparable to Qwen; the behaviour-minimised control of the same size improves little.
- A Qwen-2.5-32B classifier finds backtracking and verification rare in both OpenWebMath and FineMath.
- Qwen RL-trained on Countdown goes from 38% to 50% on 200 MATH questions (their prompt format; 44% 4-shot to 50% zero-shot).
- Over 200 GPQA questions, the Llama with curated pretraining averages 6.5 subgoal-setting instances per question against 0.7 for the control, yet both score about 12%.

## Limits

- The main causal tests are on Countdown only; the authors concede the priming data was domain-specific and the behaviour set is not exhaustive, and that which behaviours matter is likely task-dependent.
- Only two 3B model families, plus a Llama-70B baseline analysis, and no seeds or error bars.
- Behaviour counts come from a GPT-4o-mini classifier, whose agreement with humans is weaker on backward chaining (ICC3 of 0.55 and 0.40).
- The paper omits compute, hardware and the continued-pretraining hyperparameters.

## See Also
- [[RLVR Pass@k Reasoning Boundary]] — related (whether RL adds anything beyond the base model's own paths)
- [[STaR Self-Taught Reasoner]] — prerequisite-for (the older self-improvement loop this paper extends)
- [[Chain-of-Thought Prompting]] — related
- [[Reinforcement Learning Foundations]] — prerequisite-for
