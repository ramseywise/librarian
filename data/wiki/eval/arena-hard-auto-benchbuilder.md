---
title: Arena-Hard-Auto and BenchBuilder
tags: [eval, llm, pattern]
summary: "BenchBuilder filters crowdsourced Chatbot Arena prompts by seven LLM-scored quality criteria and topic clusters into a 500-prompt benchmark judged pairwise by GPT-4-Turbo; the authors report 3x the separation of MT-Bench and 98.6% confidence agreement with human rankings at about $20 per model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-li-2024-crowdsourced-data-high-quality-benchmarks.md
---

# Arena-Hard-Auto and BenchBuilder

Li and colleagues (arXiv 2024) build a benchmark from crowdsourced prompts without hand curation. The paper's hypothesis is that prompts scoring high on seven quality criteria, sampled evenly across topic clusters, separate models more confidently and agree more with human preference than random or hand-written prompt sets.

## BenchBuilder pipeline

1. Deduplicate, keep single-turn English prompts, embed 200,000 Chatbot Arena prompts and cluster them into 4,000 topics.
2. GPT-4-Turbo scores each prompt 0 to 7 on seven criteria (the extraction names real-world, domain knowledge, specificity and creativity among them).
3. Drop prompts scoring below 6 and clusters whose mean is below 5; over 500 clusters remain. Pick 250 clusters at random and take two prompts from each, giving 500 prompts.

Arena-Hard-Auto judges each model pairwise against a GPT-4-0314 baseline using GPT-4-Turbo with its own chain-of-thought answer, two position-swapped games per prompt, Bradley-Terry scores and bootstrap confidence intervals. The paper adds three measures: **Separability with Confidence** (share of model pairs with non-overlapping intervals), agreement with confidence against a reference ranking, and a pair-rank Brier score. It argues Spearman correlation alone hides ranking variance: MT-Bench scores 89.9% Spearman but 26.6 confidence agreement (self-reported, top-20-model Table 1 setup).

## Results (self-reported)

Setup unless noted: top-20 Chatbot Arena models (13 April 2024 snapshot), Chatbot Arena English ranking as reference, GPT-4-Turbo judge, 100 bootstrap rounds.

- Against the style-controlled Chatbot Arena English Hard Prompts board, 98.6% confidence agreement (Brier 0.055 for the unmodified version); style-controlled separability 86.8% against 87.4% without control.
- Against a random 500-prompt Chatbot Arena sample, confidence agreement 84.2% against 57.5% and 66.1% for two samples. On WildChat (150,000 queries, 250 prompts), 88.6% against 36.4% for a random 250.
- Judge choice: GPT-4-Turbo 90.9% confidence agreement, Gemini-1.5-Pro 84.8%, Claude-3-Opus 66.7%, Llama-3-70B 65.6%. A two-judge panel of GPT-4-Turbo plus Gemini-1.5-Pro reaches 89.5% separability and a Spearman correlation of 96.5%.
- Self-bias: the GPT-4-Turbo judge ranks 5 OpenAI models 0.6 places above the human ranking and 4 Claude models 0.8 below; the ensemble gives -0.4 and +0.4.
- Style gaming: a prompt that asks Llama-3.1-70B-Instruct for more detail lifts its uncontrolled score from 44.5 to 53.5; under style control the score goes from 41.7 to 39.8. Style control cuts the Pearson correlation of score and token length from 0.364 to 0.193.
- Prompt annotator: GPT-4-Turbo agrees 85.6% with a three-model majority on 200 queries. Llama-3-70B-Instruct as annotator gave 86.0% confidence agreement against 55.8% and 58.1% for random samples (10 of the 20 models).
- Cost: about $20 to evaluate one model (500 prompts, 1,000 judgments), against $10 for MT-Bench and AlpacaEval 2.0 LC; the curation run over 200,000 prompts costs about $500 with GPT-4-Turbo or $45 with Llama-3-70B-Instruct (2024 pricing).
- On 75K Chatbot Arena queries labelled by GPT-3.5-Turbo, 17.9% reach score 6 or more and 0.2% reach 7.
- Top of the board: Claude-3-5-Sonnet-20240620 at a 79.3 win rate against the baseline.

## Limits

- Seven criteria may skew toward technical domains; English and single-turn only.
- Agreement rests on 20 models and a single reference snapshot, which gives few model pairs; judge decoding parameters are not stated.
- The headline 98.6% is the style-controlled comparison (the extraction notes), not the Table 1 Spearman figure.
- Single-judge self-bias remains; the ensemble is a first step. Models and pricing are from 2024.

## See Also
- [[LLM-as-Judge Evaluation]] — prerequisite-for (pairwise judging with position swaps)
- [[LLM Judge Biases]] — related (self-preference and style effects measured here)
- [[Eval Error Bars and Sample Size]] — related (bootstrap intervals as the basis of separability)
- [[Dynabench]] — related (another way to keep benchmarks informative)
- [[LMSYS-Chat-1M]] — prerequisite-for (conversation data from the same arena)
