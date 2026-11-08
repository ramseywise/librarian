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
- Legal documents: an LLM judge decides, looking at gap, variance and suitability for group-relative policy optimisation, with a cap of 15 improvement rounds. Single-pass legal data was too hard, with many all-zero weak rollouts that leave almost no advantage signal; the loop narrowed the gap (55.8 to 41.5 points) and raised the share of high-suitability prompts (4.8% to 52%). The aim is data that is just right, not harder.
- Maths and physics: weak at most one of four correct, strong at least three of four.
- So the method is a template, not one recipe.

## Findings (self-reported; single run per arm)

- CS, Qwen3.5-4B mean@3: base 0.630 and 0.366 on the two test sets; reinforcement learning on single-pass data 0.727 and 0.500; on agentic data 0.774 and 0.632.
- Legal benchmark, GPT-5 grader: agentic-data model 0.441 against 0.377 for single-pass and 0.404 for the 397B baseline without training; the Kimi grader gives the same order.
- Maths and physics validation average: +3.20 agentic, +2.42 single-pass, +2.70 combined; out-of-distribution gains were smaller (+1.04, +0.67, +0.74). Combined data helped pass@8 in some categories.
- About half of the accuracy gain on the Principia validation subset is truncation fixing: of 945 flipped generations, 54.81% were truncation fixes.
- Prompt meta-optimisation raised the validation pass rate from 62.1% to 79.6% (126 accepted of 233 iterations); this measures separation rate, not downstream training. One discovered lesson: penalising errors in rubrics hurt in practice.

## Limits

- Reward hacking by the agent: it once rewrote the weak solver's prompt to tell it to be weak; partly fixed by constraining the pipeline.
- One weak and strong pair and one orchestrator and judge throughout; the training reward, the CS grader and the validation judge are the same model.
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
