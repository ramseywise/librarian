---
title: Play2Prompt
tags: [harness, pattern]
summary: "Play2Prompt has an LLM play with each tool zero-shot, then uses what it observed to write demonstrations and rewrite the tool's documentation; it raised BFCL Executable accuracy for all six task models tested, by 3 to 7 points (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fang-2025-play2prompt.md
---

# Play2Prompt

Fang et al. (MIT and MIT-IBM Watson AI Lab, a 2025 preprint) optimise how a single tool is described and demonstrated to an agent without labelled data. The extraction stresses the scope: single-tool description and example optimisation, scored on tool-calling accuracy, not planning.

## Mechanism

- **Tool play.** An optimiser model proposes executable calls, runs the tool, and an error critic checks the response (the critic is told the "error" field may be empty while the response still holds an error). Beam search keeps promising trajectories.
- **Reverse example construction.** Valid invocations are explored first, the output is observed, and only then a query and answer are written, so every example is grounded in a call that ran.
- **Two adversarial rewards.** Example reward is quality plus a difficulty term, the negative of the task model's score when given the original docs and no demos, which favours examples the task model fails. Documentation reward is the score the task model gets on the generated examples, which serve as the validation set.

## Results (self-reported)

- BFCL Executable (310 queries; the optimiser was llama-3.1-8b-instruct with five demos per tool; mean of 3 runs, no variance reported): LLaMA-8B went from 85.9 to 92.9, LLaMA-70B from 90.8 to 94.5, then GPT-3.5 moved 87.0 to 92.5, GPT-4o from 92.4 to 94.9, ToolACE-8B from 87.4 to 90.3 and Hammer-7B from 82.6 to 87.2.
- StableToolBench (790 queries under ReAct, judged by llama-3.3-70b-instruct, one demo per tool): LLaMA-8B went from 55.8 to 62.2, LLaMA-70B from 63.1 to 69.2, then GPT-3.5 moved 60.7 to 65.9 and GPT-4o from 62.8 to 64.9. EasyTool lowered GPT-4o on every subset.
- Gains grow as documentation degrades: mean weighted gain 5.0% with no parameter descriptions dropped and 7.1% with all dropped (BFCL Executable).
- Demos only versus docs only: demos-only gave larger gains in most cases, both together were best. The extraction notes LLaMA-70B on BFCL contradicts this (docs only 93.6, demos only 92.7).
- Dropping the difficulty reward cost 1 to 2 points on average (extraction: 1.0 to 1.5 in the supporting figure).

## Limits

- Single-tool only; multi-tool queries concatenate separately optimised tools. Rejection sampling fails for functions needing long IDs or tokens from other calls.
- Needs executable tools; side-effecting tools are not addressed. Exploration cost per tool is not reported (about 1M API calls overall).
- No baseline of hand-written docs, or of equal compute spent on few-shot sampling; no confidence intervals; some categories are small.
- Not uniform: GPT-4o fell on BFCL Simple-REST (98.6 to 95.7) and on three StableToolBench subsets.
- Optimised docs are more verbose; inference-time token cost is not discussed. MCP-style descriptions and current frontier models are untested.

## See Also
- [[Tool Design as Harness Surface]] — prerequisite-for
- [[Trace-Free+ Tool Description Rewriting]] — alternative-to
- [[Agent-Oriented Error Messages]] — related (error feedback drives the doc rewrites)
- [[APIGen]] — alternative-to (another route to verified tool-call examples)
