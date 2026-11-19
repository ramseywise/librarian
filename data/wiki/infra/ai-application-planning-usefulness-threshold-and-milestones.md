---
title: "AI Application Planning: Usefulness Threshold and Milestones"
tags: [infra, concept]
summary: "Huyen's planning checklist for a foundation-model product: why to build, critical versus complementary AI, Crawl-Walk-Run automation, a usefulness threshold across quality, latency and cost, milestones from existing models and the last-mile gap, with the figures she relays."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch01-introduction-building-ai-applications-foundation-model.md
---

# AI Application Planning: Usefulness Threshold and Milestones

Chip Huyen's *AI Engineering* (O'Reilly), chapter 1, defines AI engineering as building applications on top of foundation models and describes three layers of the stack: application development, model development and infrastructure. This page keeps the planning guidance. Most figures are reported from other sources.

## Before building

- Decide why: existential threat, opportunity or hedge, and whether to build or buy.
- Settle how central AI is (critical or complementary), when it acts (reactive or proactive), whether it is dynamic or static, and where humans fit.
- Automation grows in steps under Microsoft's Crawl-Walk-Run framework. Her illustration: if human agents accept the AI's output around 95% of the time on simple requests, customers could be let to talk to it directly (claim).

## Setting expectations

- Set business metrics and a usefulness threshold, meaning how good the product must be to count as useful, spanning quality, latency (TTFT, TPOT, total), cost and more. Worked example: 10 ms per token makes a 100-token answer take a second, whereas she notes ordinary internet apps expect roughly 100 ms.
- Test existing models first so milestones are realistic: reaching 60% is easier for a chatbot already handling 30% of tickets than for one handling none.
- Plan for the last mile. LinkedIn (2024) took a month to get to 80% of the experience it wanted and four further months to pass 95%; she cites the UltraChat paper (Ding et al. 2023) for going from 60 to 100 being far harder than 0 to 60.

## Adapting a model

She orders techniques by data and effort: prompt engineering needs the least, then finetuning, then training from scratch. An illustrative comparison (no study cited): about ten examples and a weekend to adapt, versus a million examples and half a year to build. Pre-training takes up to 98% of InstructGPT's compute and data resources (reported). Comparing models under equal prompting matters: changing the technique raised Gemini Ultra's MMLU from 83.7% to 90.04% (Gemini technical report, December 2023; 5-shot against CoT@32). See [[Benchmark Prompt Format Sensitivity]].

## Maintenance and sequencing

She advises keeping versioning and evaluation infrastructure so that swapping models is painless, and building the product first, investing in data and models once it shows promise.

## Figures she relays

- Noy and Zhang 2023, 453 professionals, writing tasks, half randomly given ChatGPT: writing time down 40%, quality up 18%. A McKinsey developer study: AI roughly doubles developer productivity on documentation, 25 to 50% gains on code generation and refactoring, minimal gain on highly complex tasks.
- GitHub Copilot passed $100 million annual recurring revenue two years after launch; Midjourney reached $200 million by late 2023.
- Scribd's estimate of its AI costs for these use cases dropped by two orders of magnitude between April 2022 and April 2023 (personal communication).
- Her own informal research covered 50 company interviews, over a hundred case studies and 205 open-source apps; 920 AI repositories with 500 or more stars in March 2024; 20 practitioners surveyed on the name AI engineering.

## Limits

- An overview chapter that only lightly touches many topics. Most numbers come from surveys, press and company reports, several uncited or by personal communication.
- The author's tallies are informal, with no stated way the samples were chosen. Costs, model sizes and market data date from 2023 and 2024.
- The extraction records the book as disputing the idea that ML knowledge is merely nice to have.

## See Also
- [[Evaluation-Driven Model Selection]] — related (the next step: choosing a model by criteria)
- [[Goodput and Inference Metrics]] — related (TTFT and TPOT in depth)
- [[Cheap-First Gating and Model Cascades]] — related
- [[LLM Inference Economics]] — related
