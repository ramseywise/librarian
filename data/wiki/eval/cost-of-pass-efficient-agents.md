---
title: "Cost-of-Pass and Efficient Agent Design"
tags: [eval, concept]
summary: "Cost-of-pass divides the expected spend per attempt by the success rate, which lets an agent design be judged on cost per solved task instead of accuracy alone; a GAIA component study and a survey of cost levers both point toward simple memory, bounded steps and selective tool use, with the study's gaps listed in Limits."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wang-2025-efficient-agents.md
  - data/raw/papers/2026-11-06-yang-2026-toward-efficient-agents.md
  - data/raw/papers/2026-11-06-wang-2026-agentopia.md
---

# Cost-of-Pass and Efficient Agent Design

An agent that scores a few points higher can cost far more per task, so accuracy alone hides the price of reaching it. Cost-of-pass is the metric the Efficient Agents study uses to correct this: the expected cost of one attempt divided by the probability that the attempt succeeds. The extraction notes that the formula text reads as a ratio while the extracted symbol looks like a product, and that table values confirm the ratio (0.705 divided by 0.5333 is about 1.32). A design is more efficient when its cost-of-pass is lower, even if its raw accuracy is slightly behind.

## The component study

Efficient Agents (a preprint) varies one component of a general agent at a time on the GAIA dev set, which is about 165 tasks, with prices from May 2025. The default configuration the authors recommend reaches 51.52% accuracy at $0.285 per task and 127K tokens, against OWL at 53.33%, $0.398 and 189K tokens (self-reported, GAIA dev). Cost-of-pass is 0.55 for the lean configuration and 0.75 for OWL (self-reported). All figures in the list below are self-reported, from GAIA dev with one component changed at a time:

- **Backbone.** Qwen3-30B has accuracy 17.58% and cost-of-pass 0.13 (self-reported). GPT-4.1 has 53.33% and 0.98. Claude 3.7 has 61.82% and 3.54. The cheap small model has the lowest cost-of-pass of the three despite the lowest accuracy, which shows the metric alone does not say a design is good.
- **Reasoning effort.** Cost-of-pass rises with GAIA task level for reasoning models (self-reported, GAIA Level 1 to Level 3): Claude 3.7 Sonnet went from 1.69 to 9.04 and o1 from 1.96 to 12.66.
- **Best-of-N.** At N of 4 (self-reported), accuracy moved from 53.33 to 53.94 while cost-of-pass rose from 0.98 to 1.28 and tokens from 243K to 325K.
- **Step budget.** Maximum steps of 4, 8 and 12 gave (self-reported) accuracy 41.82, 52.73 and 53.33 with cost-of-pass 0.48, 0.70 and 0.98.
- **Memory.** A simple memory scored 56.36 with cost-of-pass 0.74 and 194K tokens; an LLM-summarised memory scored 51.52 with 1.52 and 367K (self-reported).
- **Tools.** Multi-source search lowered cost-of-pass from 1.32 to 0.81 and raised accuracy from 53.33 to 59.39 (self-reported).

## The survey view

Toward Efficient Agents is a survey with no experiments of its own. It treats efficiency as a property of the whole system and groups fourteen cost levers (the extraction's count) under memory, tools, planning and multi-agent design. Examples are bounded or compressed prompts, retrieving only a few tools, parallel calls, adaptive deliberation (it cites SwiftSage), plan caching and sparser multi-agent topologies. It argues that the right unit is end-to-end cost, counting token spend, elapsed time, outside actions, retried steps and the overhead of coordinating agents. Two cautions it records, both second-hand: compression has a quality cost, and memory maintenance is itself a cost, since synchronous LLM-managed updates add calls and latency. The quadratic-to-linear claim for multi-agent messages is asserted, not measured. The extraction flags an "exponentially" claim as unsupported.

## A scale footnote

Agentopia, a simulation paper, is a poor fit for this topic and contributes only a cost figure: its ten-year, 100-agent world consumed 13.7B tokens and 567K calls over roughly 186 hours (self-reported; single runs, no single-agent baseline). Input tokens were 13,347M against 352M output (self-reported), and the paper names memory growth as the bottleneck, with role-playing agents accounting for about 95% of input tokens (self-reported).

## Limits

- The study uses GAIA dev only, one run per cell and no confidence intervals; gaps of one to three points, such as 53.33 against 53.94, are within noise for about 165 tasks.
- One component is varied at a time; interactions between components are untested, and the combined recommended setup is not compared back against each single change.
- Framework comparisons are not matched on call counts; OWL and Smolagents run on their own defaults, with the backbone unstated.
- The tool study covers a web browser only, and the extraction notes a placeholder left in the conclusion text.
- Internal inconsistencies noted by the extraction: GPT-4.1 cost is $0.705 in some tables and $0.521 in others for the same configuration; the text says 96.7% retained where 51.52 over 53.33 is 96.6%; the headline 28.4% describes a drop in cost rather than in cost-of-pass; the lean configuration costs $0.285 in one place and $0.228 in another; and the "58.49 to 69.81" range is the Level 1 column.
- The abstract says the design adapts complexity to the task, but the configuration is fixed.
- The survey's numbers are second-hand and its 0/1 cost model is a simplification.

## See Also
- [[GAIA General-Assistant Benchmark]] — prerequisite-for (the benchmark the component study runs on)
- [[Budget Tracker and BATS]] — related (another cost-bounded agent design)
- [[Price Reversal in Reasoning-Model Costs]] — related
- [[Memory Lifecycle]] — related (memory maintenance as a cost)
