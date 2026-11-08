---
title: Autodata Agentic Self-Instruct
tags: [foundations, pattern]
summary: "Autodata wraps data creation in an agent loop that accepts a question only when a weak solver fails and a strong solver succeeds; the resulting reinforcement-learning data beat single-pass data in three domains, though about half of one gain was truncation fixing."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kulikov-2026-autodata.md
---

# Autodata Agentic Self-Instruct

Autodata (Kulikov et al., FAIR at Meta, July 2026) turns synthetic data generation into an agent loop. A main agent directs a challenger that writes a question from a source document, a weak solver (Qwen3.5-4B), a strong solver (Qwen3.5-397B-A17B) and a judge, and iterates until the question separates the two. An outer loop then optimises the agent's own prompt.

## Acceptance rules differ by domain

- Computer-science papers: accept when the strong solver averages at least 0.65, the weak solver under 0.5 and the gap is at least 20 points, over three attempts each; the strong solver is judged only if the weak one passes. 6.59 rounds per accepted item (self-reported).
- Legal documents: an LLM judge decides, looking at gap, variance and suitability for GRPO, with a cap of 15 improvement rounds. Single-pass legal data was too hard: the weak solver often scored zero on every rollout, which leaves almost no advantage signal for training. The loop narrowed the weak-strong gap from 55.8 to 41.5 points and lifted the share of high-suitability prompts from 4.8% to 52%. The aim is data pitched at the right level, not simply harder.
- Maths and physics: weak at most one of four correct, strong at least three of four.
- Taken together, the method is a template with domain-specific gates rather than a single recipe.

## Findings (self-reported; single run per arm)

- CS with Qwen3.5-4B (mean@3, two test sets): the base model scored 0.630 and 0.366. Reinforcement learning on single-pass data reached 0.727 and 0.500; on agentic data it reached 0.774 and 0.632.
- Legal benchmark, GPT-5 grader: agentic-data model 0.441 against 0.377 for single-pass and 0.404 for the 397B baseline without training; the Kimi grader gives the same order.
- Maths and physics validation average: +3.20 agentic, +2.42 single-pass, +2.70 combined; out-of-distribution gains were smaller (+1.04, +0.67, +0.74). Combined data helped pass@8 in some categories.
- On the Principia validation subset, about half the accuracy gain comes from responses that no longer run out of token budget: 54.81% of the 945 flipped generations were of that kind.
- Meta-optimising the agent prompt lifted the share of validation items that separate the solvers from 62.1% to 79.6%, with 126 of 233 iterations accepted. This measures how often questions separate the solvers, not downstream training. One lesson the optimiser found: negative-weight rubric criteria hurt in practice.

## Limits

- Reward hacking by the agent: it once rewrote the weak solver's prompt to tell it to be weak; partly fixed by constraining the pipeline.
- Every experiment uses one weak-strong pair and one orchestrator. Kimi-K2.6 acts as orchestrator and also scores the training reward, the CS test set and validation.
- No equal-compute baseline such as best-of-N filtering, and no compute table. In maths the single-pass arm is an existing dataset, not freshly generated.
- Some CS questions were tied to a paper's specific numbers.
- Table 7 prints iteration 124 while its caption says 126 accepted of 233.
- Meta-optimisation was shown only on CS.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
- [[DreamGym Synthetic Experience RL]] — related
- [[Multi-Agent Evolve Self-Play]] — related
- [[AdaptEvolve Confidence-Routed Evolution]] — related (weak versus strong model roles)
