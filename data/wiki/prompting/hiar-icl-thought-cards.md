---
title: HiAR-ICL Thought Cards
tags: [prompting, reasoning, concept]
summary: "HiAR-ICL replaces worked examples in the prompt with abstract thought cards, reasoning-action chains found offline by Monte-Carlo tree search on 200 seed questions and retrieved by problem complexity; the authors report 80.6% on MATH500 with a 7B model and about 7 to 22 times less time than rStar (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wu-2024-beyond-examples.md
---

# HiAR-ICL Thought Cards

The idea is to widen what in-context learning supplies as context: instead of concrete demonstration examples, give the model an abstract reasoning pattern matched to how hard the question is.

## Mechanism

**Offline.** Monte-Carlo tree search runs over a menu of five basic reasoning moves: system analysis, a single-step thought, chain-of-thought, splitting a problem into parts, and self-reflection with refinement. It runs on 200 seed training questions. For each question the best path, scored as reward minus a cost for the number of actions (weight k = 0.95), is distilled into a **thought card**: an action chain, for example system analysis then one-step thought then chain-of-thought, stored with the average complexity attributes of the questions that share it. One attribute is problem condition complexity, the number of conditions already known in the question. Distilling a single path into an average template discards the question's content.

**Online.** The five cards nearest the new question by complexity attributes guide generation. A process reward model scores the candidates, and the three best enter a self-consistency vote.

## Reported results

All self-reported. Unless noted, seeds come from the same benchmark's training split.

- Qwen2.5-7B-Instruct reaches 80.6% on MATH500 and 62.5% on AMC (40 problems, so one problem is 2.5 points), against GPT-4o with chain-of-thought and four-sample self-consistency at 57.5% on AMC. Llama3-8B-Instruct on MATH rises from 17.8% (few-shot chain-of-thought) to 46.6%.
- Against the tree-search method rStar on Llama3-8B with an A100-80GB, time per sample from start to finish, with offline construction spread in, drops 21.8x for GSM8K, 21.0x for StrategyQA and 7.0x for MATH (159.5 s versus 1105.8 s on MATH). Accuracy on MATH is 46.6 versus rStar's 42.9, while rStar leads on GSM8K, 91.1 to 89.6.
- Ablations on Llama3-8B-Instruct, four-task average: random action chains instead of cards cost 10.4 points, a random rather than complexity-matched card 5.0, random solution selection 4.8, self-consistency alone 2.5 and the reward model alone 1.2.
- Cards built by Llama2-7B raised GPT-4o's MATH score from 77.2 to 79.6. On GPQA-Diamond (198 questions) Qwen2.5-7B went from 34.3 to 43.4. Stacked on a Qwen2.5-1.5B trained with GRPO, MATH rose from 43.8 to 52.8 and GSM8K from 71.9 to 79.5; for QwQ-32B-Preview, MATH rose from 90.6% to 93.6%.
- A 150-sample multi-task card set averaged 73.7 against 75.6 for task-specific cards. Using more selected cards kept lifting MATH, reaching 46.6, compared with a Pass@5 ceiling of 59.6.

## Limits

- Each figure comes from a single run with no seeds or variance reported, and the AMC set holds only 40 problems.
- Comparisons mix self-run and copied numbers. The extraction notes the GPT-4o figure of 77.2 described as few-shot in the text is the chain-of-thought plus self-consistency row of the main table, while few-shot chain-of-thought there is 76.6.
- Search iterations, children per expansion, the discount, and the GRPO and fine-tuning recipes behind two tables are not given.
- The authors concede more cards add overhead and the best balance is future work, and that per-domain action-space tuning is left open. Offline cost is fixed per seed set and the time comparison is on Llama3-8B only. At test time the seeds come from the same benchmark's training split except in the out-of-distribution and weak-to-strong tests.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[Tree of Thoughts]] — related (tree-search baseline)
- [[RAP Reasoning via Planning]] — related
- [[Chain of Thought]] — prerequisite-for
- [[Prompting Technique Selection]] — related
