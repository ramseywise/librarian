---
title: Multiagent Debate for Factuality and Reasoning
tags: [graph, concept]
summary: Several copies of one chat model answer independently, read each other's answers and revise over rounds; reported to beat single-agent, self-reflection and majority-vote baselines on arithmetic, GSM8K, MMLU and biography accuracy (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-du-2023-improving-factuality-reasoning-language-models.md
---

# Multiagent Debate for Factuality and Reasoning

In this preprint (arXiv v1, marked under review), N copies of gpt-3.5-turbo answer a question separately. Every agent is then shown the other agents' answers, joined into a consensus prompt, and revises its own; R rounds of this follow. The comparisons are a single agent, single-agent self-reflection and majority voting, all from identical starting prompts.

## Results (self-reported)

Setup unless stated otherwise: gpt-3.5-turbo-0301 run zero-shot with 3 agents and 2 rounds, on about 100 items per task.

- Arithmetic (100 generated six-number expressions): 67.0 to 81.8; majority vote 69.0; self-reflection 72.1.
- GSM8K (100 problems): 77.0 to 85.0; majority vote 81.0; self-reflection 75.0, below the single agent.
- MMLU (100 random questions): 63.9 to 71.1, with reflection at 57.7. Giving each agent a persona (professor, doctor, mathematician) takes debate accuracy up from 71.1 to 74.2.
- Biographies of 524 computer scientists, judged yes or no against a Wikipedia bullet by ChatGPT: 66.0 to 73.8.
- Chess: relative Stockfish pawn score of the move 91.4 to 122.9 (300 games, depth 20); BIG-Bench move validity 29.3 to 45.2.
- A debate between ChatGPT and Bard solves 17 of 20 GSM8K problems, where they solve 14 and 11 alone.
- Scaling: arithmetic accuracy rises with the number of agents at 2 rounds (past 3 agents the responses are summarised by ChatGPT, which does better than concatenation) and with rounds up to four; longer "stubborn" prompts converge more slowly but end better (read from figures).

## Limits

- Costlier, since each round needs several generations multiplied by agents and rounds, and no cost or token figures are given.
- Models attend to the most recent generations in long debates, and converged answers are not necessarily correct; models can confidently affirm a wrong consensus.
- Small evaluation sets (the mixed-model test is 20 problems) with unexplained error bars; the biography judge cannot catch facts outside the ground truth, and the majority baseline is omitted for factuality tasks.
- The main results use only gpt-3.5-turbo-0301, agents are agreeable because of instruction tuning, and there is no fixed-compute ablation against many majority-vote samples for more than 3 agents.
- The PDF is arXiv v1; the extraction notes a later venue is not in this text.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Multi-Agent Debate Failure Modes]] — prerequisite-for
- [[Encouraging Divergent Thinking with Multi-Agent Debate]] — alternative-to
- [[Self-Consistency]] — related
