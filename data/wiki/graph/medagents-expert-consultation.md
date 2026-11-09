---
title: MedAgents Expert Consultation
tags: [graph, concept]
summary: Training-free five-stage pipeline in which role-played domain experts analyse a medical question, summarise, vote until unanimous and hand off to a decision maker; reported 86.7 average on nine medical QA sets with GPT-4 (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-tang-2024-medagents.md
---

# MedAgents Expert Consultation

MedAgents (2024) runs medical question answering as a simulated consultation with no training. It has five stages. Experts are recruited for the question and for the options; each writes an analysis; a summary report is produced; the experts then vote yes or no and propose edits until they all agree (at most 5 rounds); finally a decision maker chooses the answer. GPT-3.5-Turbo and GPT-4 are the models used.

## Results (self-reported)

Setup: nine medical QA datasets with 300 randomly chosen examples each, run zero-shot at temperature 1.0 and top_p 1.0.

- GPT-4 average: 86.7 for MedAgents against 83.0 for zero-shot CoT with self-consistency (CoT+SC) and 80.6 zero-shot. For GPT-3.5 the averages are 72.1, 70.9 (zero-shot CoT+SC) and 71.6 (few-shot CoT+SC).
- On MedQA with GPT-4 MedAgents gets 83.7; the self-consistency baselines get 74.5 (zero-shot CoT) and 82.9 (few-shot CoT). With GPT-3.5, zero-shot CoT lands under plain zero-shot (58.3 against 67.8 on average) and on MedQA with GPT-4 (61.8 against 73.0). MedAlpaca-7B gets 55.2 on MedQA.
- Stage ablation on MedQA, adding one stage at a time: direct prompting 49.0, then CoT 55.0, analysis 62.0, summarisation 65.0 and consultation 67.0 (the extraction notes the model and sample count are not stated for this table).
- Agent make-up on MedQA with GPT-3.5, 6 agents: 6 different domains 64.1 against 59.2 for 6 of the same domain, 57.5 for 5 and 55.9 for 4. Removing the least relevant expert raised accuracy to 66.2 from 63.8 and removing the most relevant lowered it to 60.5 (20 samples, manual relevance labels). The best counts read from a figure are 5 question and 2 option agents.
- Cost is about $1.41 per 100 examples and about 40 s per example. Repetition changes little: GPT-4 on MedQA gets 83.7 in a single run and 83.5 over 5 repeats.
- Of 40 sampled errors from MedQA and MedMCQA, 77% come from missing or wrongly retrieved domain knowledge and 8% from CoT errors.

## Limits

- The authors concede stale parametric knowledge, no tests of mixing models across stages, limited use for low-resource languages, and a cost above CoT or direct prompting; the pipeline cannot fix the knowledge gaps behind the 77% error share.
- Each dataset has just 300 samples, and there are no seeds or significance tests; the domain-relevance study uses 20 samples.
- The same-domain comparison mixes up agent count with domain diversity, and the self-consistency baseline is not cost-matched.
- Medical QA benchmarks only, on GPT-3.5 and GPT-4.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Multiagent Debate for Factuality and Reasoning]] — related
- [[Self-Consistency]] — related
