---
title: Budget Tracker and BATS
tags: [harness, pattern]
summary: "Showing a tool-using agent its remaining tool-call budget each turn (Budget Tracker), and the fuller BATS loop that adds budget-aware planning and answer verification, changed how a ReAct agent spent search calls on BrowseComp (all self-reported, mostly Gemini-2.5-Pro)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-liu-2025-budget-aware-tool-use-enables.md
---

# Budget Tracker and BATS

Liu et al. (a Google and academic team) study agents that search and browse the web under a cap on tool calls. They report that a plain [[ReAct Pattern]] agent does not use extra budget when given it: on BrowseComp, Gemini-2.5-Pro averaged 13.77 search calls at a cap of 30 and 14.24 at a cap of 100, with accuracy 10.5% and 12.6% (self-reported). The authors say the agent stops early because it believes it has an answer.

## Budget Tracker

The Budget Tracker is a plug-in with no training. After every tool response it appends a short block giving, per tool, the budget used and the budget remaining. Results with 100 calls allowed per tool, mean of 3 runs (self-reported): on BrowseComp, Gemini-2.5-Pro went from 12.6 to 14.6 and Claude-Sonnet-4 from 12.2 to 14.0; Gemini-2.5-Pro on BrowseComp-ZH went from 31.5 to 32.9 and on HLE-Search from 20.5 to 21.8. At a budget of 10 with the tracker, Gemini-2.5-Pro scored 12.8% against 12.6% for plain ReAct at 100, while search calls fell 40.4%, browse calls fell 19.9% and cost fell 31.3% (6.8 cents per question against 9.9; self-reported).

Outside web search (appendix results, global budget): Gemini-2.5-Flash on tau2-bench retail, budget 10, moved Avg@4 from 47.8 up to 55.5 (self-reported). On SWE-bench Verified with Gemini-3-Flash-Preview and mini-swe-agent, 500 tasks, budget 50, the resolve rate rose from 36.8% to 55.4% at near-equal tool calls (self-reported). At budget 70 the baseline scored 63.0 against 55.1 for the tracker.

## BATS

BATS adds a planning step that builds a tree of sub-questions, and a verifier that judges each proposed answer as SUCCESS, CONTINUE or PIVOT. PIVOT summarises and resets the context and abandons the direction. The loop ends when any one budget is used up, and a judge picks among verified answers. With Gemini-2.5-Pro at 100 per tool (self-reported): BATS reached 24.6 on BrowseComp where ReAct reached 12.6; on BrowseComp-ZH it reached 46.0 where ReAct reached 31.5, and on HLE-Search 27.0 where ReAct reached 20.5. In the BrowseComp ablation, dropping the planner left 17.0, dropping the verifier left 15.4, and dropping both left 14.6, from a full score of 24.6. A trained system, OpenAI Deep Research, scores 51.5 on BrowseComp, well above BATS.

The authors' reading is that budget awareness changes strategy, broad when budget is plentiful and precise when scarce, rather than just spending more. Their browse-to-search ratio was 9.6% for ReAct and 12.9% with the tracker.

## Limits

- Only tool-call budgets were studied, not token, latency or joint limits; the authors list allocation of the budget by the agent as unstudied, say context management was kept simple, and say compute cost prevented repeated runs.
- The budget is a signal visible in the prompt, so it relies on the model's cooperation; no test covers an agent that ignores or tampers with it, and the extraction notes the paper is silent on whether anything outside the model enforces the cap.
- Results mostly come from one model family on three web-search benchmarks. The appendix holds the tau2 and SWE-bench numbers, and SWE-bench runs on a different model.
- Tracker-only gains in the main table are 1 to 3 points on low accuracies.
- The authors write that models often underestimate their own resource use (App. G).

## See Also
- [[Context Window Budgeting]] — prerequisite-for
- [[ReAct Pattern]] — prerequisite-for
- [[Verification Loops]] — related (the verifier step in BATS)
- [[Loop Detection and the Two-Retry Rule]] — related (another cap on agent loops)
- [[Effective Feedback Compute]] — related
- [[Cost-of-Pass and Efficient Agent Design]] — related
