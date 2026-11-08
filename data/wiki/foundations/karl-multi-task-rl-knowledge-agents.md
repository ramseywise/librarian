---
title: KARL Multi-Task RL Knowledge Agents
tags: [foundations, llm, pattern]
summary: "KARL trains a search agent with iterative large-batch off-policy RL (OAPL) on two tasks, using agent-synthesised questions and a learned compression tool; the result matched a frontier model on a six-task suite at lower cost (self-reported) and generalised better than SFT distillation."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chang-2026-karl.md
---

# KARL Multi-Task RL Knowledge Agents

KARL (a Databricks AI Research preprint, March 2026) trains a single-tool enterprise-search agent on GLM 4.5 Air. The tool is vector search over closed corpora; the training tasks are BrowseComp-Plus and TREC-Biogen, evaluated within a six-task suite the authors call KARLBench.

## Mechanism

- **OAPL.** Iterative large-batch off-policy RL. Each sample's squared error pushes the scaled log-ratio to the reference policy toward reward minus a value baseline estimated from a group of rollouts. The authors say it avoids clipped importance weights, data deletion and router replay used to stabilise online GRPO; the algorithm is cited from concurrent work and no GRPO comparison is run here. At most three iterations.
- **Agentic synthesis.** A question-writing agent searches the corpus by vector similarity; a deduplication agent strips near-copies of evaluation questions; eight solver attempts per question discard items every attempt gets right or every attempt gets wrong; a quality agent then screens out ambiguous or incorrect items. The model being trained plays the synthesis and solver roles at each iteration.
- **Reward.** Outcome-only, nugget-based, from LLM judges.
- **Compression tool.** Context is compressed by the agent and the skill is trained in RL; removing it dropped a BrowseComp-Plus score from 0.570 to 0.389.
- **Parallel thinking.** Several rollouts are aggregated by a generative aggregator at test time.

## Results (self-reported)

Setup: KARLBench total, no seeds or intervals, authors' own harness with the best configuration per baseline.

- Total 58.9 single call, against 58.6 for Claude Sonnet 4.5 and 52.6 for the base. With 10 parallel rollouts 67.5, level with Claude 4.6 Opus at 67.5.
- Out-of-distribution, SFT-distilled multi-expert models gained only 59.4 to 59.6 from parallel sampling while in-distribution went 69.1 to 75.3; KARL reached 62.7 with 10 rollouts. Single-task KARL variants did not transfer to each other's task.
- A single call costs under $0.10 per query. At matched quality it is about a third cheaper than Opus 4.6, and latency is about 47% lower at 10 rollouts (cost computed from third-party list prices).
- TREC-Biogen across the three iterations scored 66.0, 76.0, 82.0 and then 85.0; the authors say one sample after iteration 3 matches the base's best of eight.

## Limits

- The extraction notes an unlabeled 84.5 in Fig. 1 that could not be placed.
- Single tool and closed corpora; only two trained tasks, the four "out-of-distribution" tasks are in the same suite; BrowseComp-Plus is a 230-question subset; PMBench is proprietary with 57 questions; LLM judges throughout. The index keeps only the first 512 tokens of each document.
- Concession: more "giving up early" failures, and a refused arithmetic question. OAPL's advantage is asserted, not ablated. Training cost is not reported.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Deep Research Agent Systems]] — related
- [[Harness-1 State-Externalizing Search Agent]] — alternative-to
- [[DAPO]] — alternative-to (a different way of stabilising policy-gradient RL)
