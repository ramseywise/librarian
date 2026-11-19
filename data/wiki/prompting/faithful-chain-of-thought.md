---
title: Faithful Chain-of-Thought
tags: [prompting, pattern]
summary: "Faithful CoT has a code LM translate a question into a chain of natural-language subquestions interleaved with symbolic code, then a deterministic solver executes it, so the executed chain is the explanation; it set new few-shot bests on 7 of 10 datasets but lost to CoT on StrategyQA (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lyu-2023-faithful-chain-thought-reasoning.md
---

# Faithful Chain-of-Thought

Lyu, Havaldar, Stein et al. (IJCNLP-AACL 2023) ask whether chain-of-thought reasoning can be made a faithful explanation of how an answer is produced without losing accuracy. Faithfulness here means an explanation accurately represents the reasoning behind the model's prediction; plausibility is how convincing it is to humans (definitions after Jacovi and Goldberg). The hypothesis is that guaranteeing faithfulness by executing a symbolic chain with a deterministic solver costs no accuracy and may improve it.

## Two stages

1. **Translation.** A few-shot prompted OpenAI code LM converts the query into a chain that alternates natural-language subquestions (each with its dependencies and supporting rationales) with symbolic code. Table 12 of the paper shows a line such as `trees_today = trees_end - trees_begin` under a subquestion that "depends on 1 and 2".
2. **Problem solving.** A deterministic solver executes the chain and returns the answer: a Python interpreter, a Datalog executor, a PDDL planner or, for CLUTRR, a transitivity-rule engine. The symbolic language is chosen per domain (Python, Datalog, PDDL, relational expressions across four domains).

The method is compared with standard prompting, chain-of-thought and [[Least-to-Most Prompting]] on 10 datasets, under greedy decoding and [[Self-Consistency]] (40 samples, T = 0.4 on CLUTRR).

## Reported results (self-reported)

- GSM8K (code-davinci-002, few-shot, greedy, test set of 1,319): Faithful CoT beats CoT. On CLUTRR the margin under greedy decoding is 21.4% relative, and it widens with self-consistency.
- With GPT-4 and greedy decoding, Faithful CoT reaches 95.0 on GSM8K against a cited few-shot best of 92.0. Over GSM8K, SVAMP, MultiArith, ASDiv and AQuA with GPT-4 the average is 91.6, against 87.5 for least-to-most and 77.1 for CoT.
- It sets new few-shot bests on 7 of the 10 datasets (best of GPT-4 or code-davinci-002 per dataset against published numbers).
- It underperforms CoT on StrategyQA (Datalog). Of 70 sampled errors where CoT was right and Faithful CoT wrong, Datalog syntax errors were the largest share.
- Ablation (greedy): taking out the external solver loses 50.8 points on GSM8K, 22.9 on Date and 19.4 on CLUTRR, and gains 2.9 on SayCan. On CLUTRR, including only the nudge line scores 39.6 against 9.3 with no natural language, a 31.3-point difference.
- Robustness: across six exemplar sets on GSM8K the mean is 71.8 (standard deviation 0.6); across three phrasing variants (order, variable names, nudge line) the mean is 70.5 (standard deviation 1.3).
- Human study (100 chains per domain, at least 3 Prolific annotators each): where the answer was correct, raters judged StrategyQA chains correct 66.7% of the time and Sports chains 100%.
- With all three structural constraints enforced, GSM8K accuracy under self-consistency drops by 5.0.
- GSM8K test inference with Codex took 3.5 hours (2.3 with GPT-3) at a 150,000 tokens per minute rate limit.

## Limits

- Part of the results cannot be reproduced without continued access to code-davinci-002, which was withdrawn on 2023-03-23.
- Faithfulness holds just for the solving stage; the way the LM produces the chain remains opaque. A faithful chain is not necessarily a correct one, since a chain can be faithful and wrong.
- Natural-language comments matter little on GSM8K, Date and SayCan, and their roles are left to future work. PAL and Program of Thoughts match Faithful CoT within 2.0 on 6 of 10 datasets and beat it on AQuA.
- On StrategyQA it trails CoT; Datalog is rare in pretraining data and retrieving knowledge is the bottleneck.
- The best-of-LM claims compare against published numbers from different models, the baselines were rerun on the authors' cleaned test sets, there are no significance tests, and all models are closed OpenAI API models of 2022-23.
- Crowd workers without expertise ran the human study; StrategyQA annotators saw Scala in place of Datalog, and the authors themselves annotated SayCan.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Program-Aided Language Models (PAL)]] — alternative-to (concurrent Python-only chains)
- [[Chain-of-Thought Unfaithfulness Under Biased Context]] — related (the unfaithfulness result this method answers)
- [[Least-to-Most Prompting]] — prerequisite-for (decomposition in natural language only)
- [[Self-Consistency]] — prerequisite-for (the decoding strategy used)
