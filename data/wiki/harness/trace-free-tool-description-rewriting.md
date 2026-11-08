---
title: Trace-Free+ Tool Description Rewriting
tags: [harness, pattern]
summary: "Trace-Free+ fine-tunes Qwen3-4B-Instruct to rewrite a tool's description from its schema alone, trained on descriptions derived from agent failure traces; it lifted multi-step StableToolBench query-level success from 33.5 to 44.6 with GPT-4.1 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-guo-2026-learning-rewrite-tool-descriptions-reliable.md
---

# Trace-Free+ Tool Description Rewriting

Guo et al. (Intuit AI Research, preprint under review) argue that descriptions written for human developers tolerate ambiguity an agent cannot resolve, and that the problem grows with catalogue size. Their example: a tool described as returning the publication year of a scientific paper made the agent supply a topic name as the title, until the description spelled out "full title".

## Method

Trace-Free+ is a small model trained by curriculum. Targets are descriptions built from agent failure traces; early training inputs include trace summaries and later inputs are the schema only (the best split was two stages, 0.1 then 0.9 trace-free). At use time it needs only the schema. The rewrites keep returning to five patterns: scope, dependencies between tools, output, parameter constraints, and dependencies between parameters.

## Results (self-reported, GPT-4.1 agent unless stated)

- Multi-step G2+G3, StableToolBench, 764 solvable queries, teacher-forced: query-level success 44.6 against 33.5 for the original description (D0) and 41.5 for a prompted-template rewrite (D1).
- Single-step G1: 60.7 against 61.6 for D1 and 59.2 for D0; D0 is near the ceiling there.
- Scaling to 0 to 150 extra tools: degradation reduced by 29.23% and average success up 60.89% against D0, with the extra candidates 90% random and read from a figure.
- RestBench (models trained only on StableToolBench tools): TMDB 74.9 against 49.5 for D0 and 58.0 for D1; Spotify 49.3 against 34.9.
- BFCLv2 Live: for GPT-4.1 the score moved from 79.28 to 80.63; for Claude Sonnet 4.5, from 52.40 to 53.45; for Gemini-3-pro-preview, from 84.98 to 86.41.
- Pattern coverage on Media and Finance tools: scope 3.3% to 97.2%, parameter constraints 9.9% to 94.2%, cross-parameter dependencies 0.3% to 17.1%.
- EasyTool scored below D0.

## Limits

- Authors concede: only Qwen3-4B-Instruct as generator; no gain over D1 on single-step queries; the rewriter may hallucinate constraints the server does not enforce, unmeasured.
- The extraction notes: run count not given; scaling gains read off a figure; random-padded candidates make selection easy; REST APIs only, with no MCP, code or database evidence; teacher forcing hides compounding selection errors; no human study; labels came from GPT-4.1 (96 of 100 checked correct); the prompted D1 template already gets most of the lift on short tasks.
- Other agent models appear only on BFCLv2.

## See Also
- [[Tool Design as Harness Surface]] — prerequisite-for
- [[Play2Prompt]] — alternative-to
- [[Dynamic Tool Discovery]] — related (description quality under large catalogues)
- [[Tool Design as Context Engineering]] — related
