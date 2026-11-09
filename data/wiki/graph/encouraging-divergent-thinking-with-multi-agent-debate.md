---
title: Encouraging Divergent Thinking with Multi-Agent Debate
tags: [graph, concept]
summary: Two debater LLMs argue under a tit-for-tat prompt while a judge ends the debate early or extracts the answer, aimed at the Degeneration-of-Thought problem of self-reflection; reported gains on counter-intuitive reasoning and translation, at 2.46 times the CoT tokens (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-liang-2024-encouraging-divergent-thinking-large-language.md
---

# Encouraging Divergent Thinking with Multi-Agent Debate

This paper (MAD, 2024) targets **Degeneration-of-Thought** (DoT): once an LLM agent is confident in an answer, it cannot produce new thoughts through self-reflection even if the first stance was wrong. The proposed fix is a debate. An affirmative and a negative debater take turns, each reading the shared debate history, and a meta prompt asking for *tit for tat* has them argue against each other. A judge LLM has two ways to finish: in discriminative mode it stops the debate early (*adaptive break*) once it judges the right answer to have appeared, and in extractive mode it pulls out the final answer when the iteration limit is reached. The extraction notes that self-reflection shows low disagreement between iterations in manual labels, which the paper reads as sticking to the CoT answer.

## Results (self-reported)

Setup: GPT-3.5-Turbo-0301, zero-shot, unless stated.

- Counter-Intuitive AR (200 questions, temperature 0): MAD 37.0% against CoT 28.0, Self-Consistency 29.5 and Self-Reflect 27.5; GPT-4-0314 reaches 51.0%.
- Common MT, lexical-ambiguity subset (200 examples, 3 human translators): human score 3.78 for MAD against 3.41 for GPT-4, 3.43 for Self-Reflect and 3.14 for plain Turbo. Contextless subset (450 examples): 3.67 against 3.63 for GPT-4.
- Vicuna gains are small: Vicuna-7b 2.55 to 2.67, Vicuna-13b 2.81 to 2.96.
- Compared with Self-Reflect on Common MT, translation bias falls from 29.0 to 24.8 and diversity rises from 19.3 to 49.7.
- Cost on Counter-Intuitive AR is 2.46 times the tokens CoT generates, compared with 1.83 for Self-Reflect.
- More than two debaters hurts: COMET 84.4 with two, 83.1 with three and 82.9 with four; human score 3.69, 3.58, 3.49.
- Judge behaviour: when one LLM fills every role the judge leans to the negative side (104 against 87, 9 ties), and with mixed LLMs it prefers the side built on its own backbone. Pairing strong debaters with a weak judge works better than the reverse: with Turbo debaters, a Turbo judge gives COMET 84.4 and human 3.69, while a Vicuna-13b judge gives 83.2 and 3.47.
- Forcing more rounds hurts (best COMET is at the first iteration), and demanding total disagreement does not give the best result; modest tit for tat is best.
- Math and symbolic: GSM 73.8 against 70.2 for CoT and AddSub 92.1 against 87.3, with the model not stated in the appendix.

## Limits

- The authors concede the extra time cost of multi-round interaction; adding debaters beyond two degrades results because the LLMs lose track of other views and the judge has trouble extracting from long text.
- A judge LLM may prefer output it generated itself. On Counter-Intuitive AR, GPT-4 (51.0) remains ahead of MAD (37.0).
- The paper gives no variance, seeds or significance tests; it covers two main tasks, one a self-built 200-question set; dated models.
- No compute-matched comparison with majority voting: MAD uses 2.46x CoT tokens while the Self-Consistency token cost is not reported; its sample count is also not stated.

## See Also
- [[Multiagent Debate for Factuality and Reasoning]] — alternative-to
- [[Multi-Agent Debate Failure Modes]] — prerequisite-for
- [[Diversity Collapse in Multi-Agent Ideation]] — related
- [[Self-Refine]] — related (a single-agent refinement baseline family)
