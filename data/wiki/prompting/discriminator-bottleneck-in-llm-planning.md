---
title: Discriminator Bottleneck in LLM Planning
tags: [prompting, agents, planning, concept]
summary: "A study of re-ranking, iterative correction and tree search over sampled programs finds that the accuracy of the discriminator that scores candidates matters more than the planning method: advanced methods need roughly 90% discrimination accuracy to beat re-ranking, tree search is 10-20 times slower, and execution feedback lifts weak discriminators (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-chen-2024-when-tree-search-useful-llm.md
---

# Discriminator Bottleneck in LLM Planning

The paper splits a language agent into a **generator** that samples candidate programs, a **discriminator** that scores each one, and a **planning method** that decides what to do with the scores. Three planning methods are compared: re-ranking the sampled candidates, iterative correction (capped at 10 rounds) and a Monte-Carlo tree search built on a heap. Setup unless noted: a CodeLlama-13B-Instruct generator with 5 samples at temperature 0.6, discriminator score P(Yes) to "is the program correct", for text-to-SQL (the Spider and Bird sets) and for GSM8K, which is solved by writing Python. The hypothesis is that the discriminator, not the planner, decides how well the agent does. Two error types are separated: a **discrimination error** (a wrong program scores above a correct one, which no planner can recover) and an **exploration error** (the planner stops before finding the correct program).

## Reported findings

All figures are self-reported.

- **Oracle discriminators.** With a simulated discriminator whose accuracy is capped, iterative correction and tree search need at least 90% discrimination accuracy to significantly beat re-ranking, and about 80% before any agent beats greedy generation on text-to-SQL. Tree search falls behind the other two when accuracy is 0.8 or lower. Given a perfect oracle on Spider, tree search scores 76.2 and iterative correction 76.0, with re-ranking at 71.0.
- **Real discriminators.** No non-oracle discriminator made an advanced method significantly better than re-ranking on text-to-SQL. The best result on Spider is re-ranking with a fine-tuned CodeLlama-13B plus environment observations at 70.3 execution accuracy against 62.3 for greedy; with a naive fine-tuned discriminator re-ranking scored 61.5, below greedy. Tree search with that enhanced discriminator scored below re-ranking on Spider (67.5 versus 70.3) and on Bird (21.7 against 23.7).
- **Environment observations.** Adding an executability check and the execution result added 30.2 points to CodeLlama-13B's accuracy at telling right from wrong on Bird and GPT-3.5-Turbo's from 64.3 to 89.2. Among 50 sampled wrong pairs on Bird, the unaided model ranked a query that would not run above a working one in 25. With GPT-3.5-Turbo the executability check shortened tree-search time on Bird by 142.4 s.
- **Cost.** Tree search takes at least 10 to 20 times as long as the other two; on Bird that is 296.0 s per example, where re-ranking with the naive discriminator takes 17.3 s.
- **Where iterative correction fails.** Of 37 Spider cases where re-ranking was right and iterative correction was not, 29 (78.4%) were discrimination errors, and in 15 of those the correct SQL had been found and then overwritten. On GSM8K, CodeLlama-13B judging its own revisions scored 10.2 against 39.4 greedy, because revisions drifted into non-executable natural language that scored high. A larger model judged best on naive accuracy: GPT-4-Turbo 93.8 on GSM8K, 76.5 on Spider and 76.2 on Bird.
- **Tree-search instability.** Of 25 Bird cases that correction solved and tree search missed, 12 involved search being unable to separate tied scores.

## Limits

- Only instruction-tuned code models as generators; only formal-language plans (programs), not natural-language plans; generator perplexity excluded from scoring.
- Single run with one sampling configuration; tree search on GSM8K was evaluated on only 100 examples, where significance tests are often non-significant. The evaluation subsets are balanced by difficulty, which puts absolute scores under the usual development-set figures.
- The 90% threshold comes from oracle simulation with random label flips, which may not match the structured errors of real models; the models used have since dated.

## See Also
- [[Tree of Thoughts]] — prerequisite-for
- [[RAP Reasoning via Planning]] — related (a tree-search planner of the kind tested)
- [[Self-Refine]] — related (iterative correction)
- [[Verification Loops]] — related (execution feedback as the discriminator signal)
- [[Spider Text-to-SQL Benchmark]] — related
