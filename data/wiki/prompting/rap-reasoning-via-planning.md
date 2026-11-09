---
title: RAP Reasoning via Planning
tags: [prompting, concept]
summary: A framework that prompts one frozen LLM as both reasoning agent and world model and searches reasoning traces with Monte Carlo Tree Search; the paper reports large gains on Blocksworld planning and small ones on GSM8K (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-hao-2023-reasoning-language-model-planning-world.md
---

# RAP Reasoning via Planning

RAP (EMNLP 2023) starts from the view that LLM weaknesses in planning and multi-step reasoning stem from missing two things: a model of the world internally, and a signal for reward. It repurposes one frozen LLM in two roles. As the *reasoning agent* it proposes a number of candidate actions at each node. As the *world model*, prompted differently, it predicts the next state after an action. Monte Carlo Tree Search then builds a reasoning tree: selection by UCT, expansion, simulation by a greedy local-reward roll-out, and back-propagation. The best-reward path is returned. For answer-only tasks such as GSM8K, RAP-Aggregation combines the answers from several traces.

Rewards are task dependent: action likelihood, state confidence, self-evaluation and task-specific heuristics are the designs the paper lists.

## Results (all self-reported)

- Blocksworld, LLaMA-33B, 4-shot, temperature 0.8: RAP with 20 iterations solves 42% of 6-step cases where CoT with the same model solves none, all 2-step cases and 88% of 4-step cases. The paper's GPT-4 CoT figures are 0.50, 0.63 and 0.40 on 2, 4 and 6 steps. RAP averages 64% over the three step counts, and LLaMA-33B with CoT pass@10 still solves no 6-step case.
- Full Blocksworld with Llama-2 70B, RAP(10): 0.65 overall on the Easy setting against 0.08 for CoT; 0.51 against 0.05 on the Hard setting, falling to 0.09 at 12 steps.
- GSM8K, LLaMA-33B, 4-shot: RAP(10) reaches 48.6%, while CoT with self-consistency over 10 samples gets 46.8%, and RAP-Aggregation reaches 51.6%. A single RAP iteration already beats single-sample CoT (40.0 against 29.4).
- PrOntoQA, true ontology, random order, 3 to 5 hops, 20 iterations against 20 samples: RAP reaches 94.2% on prediction and 78.8% on proof accuracy, where CoT gets 87.8 and 64.8, and CoT with self-consistency 89.8.
- Reward ablations: on Blocksworld, action likelihood combined with a task heuristic gives 0.88, self-evaluation on top gives 0.91, and having no reward gives 0.02. On the first 300 GSM8K examples, state confidence plus self-evaluation is best, reaching 0.503 with aggregation.

## Limits

- Only frozen LLMs are used, and the authors leave world-model fine-tuning and tool use for later work.
- No variance, seeds or significance tests; the compute cost of MCTS (model calls and tokens per question) is not reported.
- Three task families only; the search hyperparameters are not stated in the text.
- Reward choice rests on heuristics and exploratory runs, and the effect varies by task; on GSM8K, action likelihood hurts as iterations increase.
- The size and split of GSM8K for the main table are not stated, and GPT-4 appears only in the Blocksworld comparison.

## See Also
- [[Tree of Thoughts]] — alternative-to (search over thoughts without a world-model state predictor)
- [[ThoughtSculpt]] — alternative-to (MCTS whose actions include revising earlier output)
- [[Chain of Thought]] — prerequisite-for
- [[Self-Consistency]] — prerequisite-for
- [[Task Decomposition Patterns]] — related
- [[Discriminator Bottleneck in LLM Planning]] — related
