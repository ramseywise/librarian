---
title: WebThinker Deep Research Agent
tags: [harness, pattern]
summary: A reasoning model that decides for itself when to search, delegates page exploration to a sub-agent, and drafts a report section by section; trained with iterative online DPO.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-li-2025-webthinker.md
---

# WebThinker Deep Research Agent

WebThinker wraps a large reasoning model (QwQ-32B in the main runs) in a loop that emits tool calls inline. A search call triggers a **Deep Web Explorer**: a sub-loop of search and link clicks that returns a short block of findings, so the main model does not read raw pages. In report mode an **Autonomous Think-Search-and-Draft** loop writes sections through a separate assistant model, checks only an outline, and edits on request, so the main model never holds the full report text. Training is two rounds of iterative online DPO over about 3k questions the base model fails when answering directly; smaller R1-distilled backbones first need a cold-start SFT on 7.8k trajectories. Numbers are the paper's (self-reported). Setup: Pass@1, Qwen2.5-72B-Instruct judge, Bing API with k=10, one run, no error bars.

## Reported results

- **Problem solving, QwQ-32B backbone.** WebThinker-32B-RL scores GPQA 70.7, GAIA 48.5 (text-only validation, 103 questions), WebWalkerQA 46.5 (680 questions), against Search-o1-32B at 67.2, 39.8 and 34.1 and direct QwQ-32B at 64.1, 22.3 and 4.3.
- **HLE** (500 sampled text-only questions): 15.8 for RL and 13.0 for the training-free base, against 10.8 for Search-o1, 14.0 for o3-mini (High, official figure) and 26.6 for OpenAI Deep Research (official figure).
- **Report generation** (30 Glaive questions, LLM judges, citations not scored): average 8.1 against 7.9 for Gemini Deep Research and 6.5 for Grok3 DeeperSearch.
- **Ablations.** Problem-solving average 45.4 full, 38.3 without the explorer, 42.6 without link clicking; reports 8.1 full against 6.6 without autonomous drafting. RL average 45.4 against 43.2 for offline DPO and 42.1 for the base, with almost no report gain.

## Limits

- No images, video or GUI browsing; single-run Pass@1 with no error bars; no cost, latency or tool-call counts.
- Report evaluation is 30 synthetic Glaive questions with LLM judges only. OpenAI Deep Research is far ahead where reported (GAIA 67.4 against 48.5).
- The extraction notes that headline gains over Search-o1 mix relative and absolute figures, and the intro and results give different numbers.
- The extraction notes an internal inconsistency: Section 4.7 gives 44.9 for the RL model's average, Table 3 gives 45.4.

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[GAIA General-Assistant Benchmark]] — related
- [[Task Decomposition Patterns]] — related
- [[Search-o1 Reason-in-Documents]] — alternative-to
