---
title: Evaluation-Driven Model Selection
tags: [eval, concept]
summary: "Huyen's four-step workflow for choosing a model (filter on hard attributes, narrow with public information, run your own evaluation pipeline, monitor in production), why public benchmarks are a filter for bad models rather than a way to find the best one, and the three-step recipe for the pipeline you can trust."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch04-evaluate-ai-systems.md
---

# Evaluation-Driven Model Selection

Chip Huyen's *AI Engineering* (O'Reilly, chapter 4) starts from the rule of defining evaluation criteria before building ([[Eval-Driven Development (EDD)]]). It groups criteria into four buckets: domain-specific capability, generation capability (factual consistency and toxicity, the latter probed with RealToxicityPrompts), instruction-following, and cost and latency. Factual consistency is checked either against a supplied context (local) or against open knowledge (global), using an AI judge, [[SelfCheckGPT]], [[SAFE Long-Form Factuality Scoring]] or a textual-entailment scorer (one DeBERTa-v3-base scorer has 184 million parameters, trained on 764,000 annotated pairs). The chapter mostly reports other people's numbers or hypothetical ones; it runs no experiment of its own.

## The four-step workflow

1. Filter out models on hard attributes, the ones you cannot change, and keep soft attributes such as accuracy or toxicity, which can be improved.
2. Narrow the list with public information: benchmarks and leaderboards.
3. Run your own evaluation pipeline on your task.
4. Monitor in production.

For hosted API against self-hosting the chapter weighs seven axes: privacy, lineage, performance, functionality, cost, control and on-device deployment. It also says to check licences for commercial use, user-count limits and permission to train on outputs. Filter by non-negotiable cost and latency requirements first, then choose the best of what is left.

## Public benchmarks are a filter

The chapter treats them as a way to exclude bad models, not to find the best one.

- **Selection and aggregation.** In late 2023 the Open LLM Leaderboard at Hugging Face averaged six benchmarks and HELM used ten, with just two (MMLU and GSM-8K) in common. WinoGrande and MMLU correlated at 0.9011 across the leaderboard's benchmarks (computed January 2024). As of April 2024, multiple choice made up 75% of the tasks in the lm-evaluation-harness from EleutherAI. Stanford is reported to have spent about $80,000 to $100,000 running 30 models through all of HELM (reported).
- **Prompt format.** Freeze the prompt format when scoring multiple-choice questions, because small edits to spacing or wording shift the answers ([[Benchmark Prompt Format Sensitivity]]).
- **Contamination.** Across 13 benchmarks, OpenAI's GPT-3 analysis found at least 40% of the data also present in the training set. A 13-token overlap with training data marks a sample as dirty, which needs access to that data; the chapter advises disclosing performance on the clean samples ([[Eval Contamination Defenses]]).

## Your own pipeline: three steps

- **Test each component and the final output**, both per turn and per task.
- **Write an evaluation guideline** containing rubrics and one example for each score, checked by humans, and tie the metrics to a business metric and a usefulness threshold. Huyen's illustration is hypothetical: factual consistency of 80%, 90% and 98% would let a support bot automate 30%, 50% and 90% of requests.
- **Choose methods and data.** Run cheap classifiers on all data and expensive judges on a sample, keep human evaluation in production, and slice the data. Keep several evaluation sets (production distribution, known failures, user errors, out-of-scope requests). Bootstrap the set to test whether its size suffices. Set the judge's temperature to 0 and log the data, rubric, prompt and sampling configuration.

Why slice: in the chapter's example, model A wins in each of two groups (93% to 87%, and 73% to 69%) yet trails overall (78% to 83%), a Simpson's paradox ([[Rate and Mix Decomposition]]). On sample size, a rule of thumb attributed to OpenAI puts the need at about 100 samples to see a 10% difference at 95% confidence, about 1,000 for 3% and about 10,000 for 1%; the chapter calls it rough. The median benchmark in lm-evaluation-harness has 1,000 examples (mean 2,159). See [[Eval Error Bars and Sample Size]].

## Limits

The benchmark and leaderboard facts date from 2023 and 2024; the chapter notes Hugging Face swapped out its six benchmarks in June 2024. Most numbers come from other work or are hypothetical, and the author concedes there is no perfect evaluation method and that no few scores capture a high-dimensional system. Anecdotes such as a task rising from about 20% to 70% accuracy after being split into two steps carry no dataset or sample size. The sample-size rule is rough, because the true score distribution is hard to know. The chapter's benchmark-correlation table is truncated as printed and not symmetric (HellaSwag with TruthfulQA reads 0.4809 in one row and 0.4228 in the other).

## See Also
- [[Perplexity and Bits-per-Byte]] — related (the preceding chapter's language-modeling metrics)
- [[Eval-Driven Development (EDD)]] — prerequisite-for (the define-criteria-first rule this applies to model choice)
- [[Benchmark Prompt Format Sensitivity]] — related
- [[TruthfulQA]] — related (a benchmark the chapter uses for factual consistency)
