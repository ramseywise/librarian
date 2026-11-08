---
title: APIGen
tags: [foundations, pattern]
summary: "APIGen generates function-calling training data and keeps only calls that pass format, execution and semantic checks; xLAM-7B trained on its output ranked 6th on BFCL (85.65 overall, June 2024 snapshot, self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2024-apigen.md
---

# APIGen

Liu et al. (Salesforce AI Research, a 2024 preprint) build synthetic function-calling data around one observation: unlike chat data, a function call can be executed and checked. The pipeline applies three stages. Format checking turns away malformed output, invented functions or parameters, type errors and absent required parameters. Execution runs the call (Python functions in a subprocess, or REST APIs) and returns fine-grained error types. A semantic check by an LLM judge confirms the result answers the query. Only single-turn calls are covered.

## Results (self-reported)

- **Pass rates by generator** (target 40,000 generations each, temperature 0.7): 34.42% for DeepSeek-Coder-33B, 38.46% for Mixtral-8x7B, 65.96% for Mixtral-8x22B, 84.15% for DeepSeek-V2-Chat. Execution failures were the largest rejection bucket for every model except DeepSeek-V2-Chat.
- **Dataset:** 60,000 entries over 3,673 executable APIs (134 Python functions plus 3,539 REST APIs that remained after cleaning ToolBench's 16,464) in 21 categories, with simple, multiple, parallel and parallel-multiple query styles. Only Mixtral-8x22B and DeepSeek-V2-Chat produced the entries. A human check of 600 samples by three evaluators found 28 with minor issues.
- **Relevance detection:** 8,000 extra examples where the needed tool is dropped or a required argument is missing, with an empty tool-call list as the correct output.
- **Models:** on BFCL (about 2,000 cases, snapshot of 15 June 2024), xLAM-7B(FC), a fine-tuned DeepSeek-Coder-7B, scored 85.65 against 82.94 for GPT-4o and 82.88 for GPT-4-turbo (function-calling mode); xLAM-1B(FC) scored 74.41 against 63.88 for GPT-3.5-Turbo-0125 and 74.29 for Claude-3-Haiku, which ran in prompt mode.
- Restoring examples that the execution and semantic stages had rejected lowered BFCL performance, more for the smaller model (values only in a figure).

## Limits

- Only REST APIs and Python functions, and single-turn calls; multi-turn is future work by the authors' account.
- Evaluation is on BFCL alone at a dated snapshot; the leaderboard has moved. Comparisons mix function-calling and prompt modes.
- The semantic checker's error rate is not measured separately; the human check bounds quality. No comparison with ReAct loops or multi-step use.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Tool Design as Harness Surface]] — related
- [[Play2Prompt]] — alternative-to
- [[Salesforce Koa]] — extends (Koa's SFT baseline uses APIGen and APIGen-MT data)
