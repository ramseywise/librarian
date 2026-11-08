---
title: AnyTool
tags: [harness, pattern]
summary: "AnyTool searches a pool of 16K+ APIs with a hierarchy of GPT-4 agents (meta-agent, category agents, tool agents) and a self-reflection loop, scoring 58.2% average pass rate on filtered ToolBench against 22.9% for the original ToolLLM pipeline (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-du-2024-anytool.md
---

# AnyTool

Du, Wei and Zhang (a 2024 preprint) address picking the right API from a very large pool. A meta-agent routes the query to category agents, which route to tool agents holding the API functions; the retrieved candidates go to a solver using DFSDT. The system uses GPT-4 function calling throughout.

## Mechanism

- **Self-reflection** triggers when the judge decides a proposed solution does not solve the query, or the solver gives up. The solver's give-up must name the failed or irrelevant APIs, which are pruned before the retry. Agents are re-activated bottom-up: tool, then category, then meta.
- Retrieval agents run in threads, each with its own history; agents that called their finish-search function are not re-activated.
- The authors also revise the ToolLLM pass-rate metric: they report that with random API candidates the original formula gave 99.0% because unsolvable queries counted as passed, and they use Solved/(Solved+Unsolved) plus a manual filter to solvable queries.

## Results (self-reported)

- Filtered ToolBench (16K+ RapidAPI APIs, GPT-4 judge, results reproduced by the authors): AnyTool 58.2 average pass rate, ToolLLM pipeline 22.9, GPT-4 given the gold APIs 38.9, a plain GPT-4 agent 15.2, AutoGen-RAG 13.1.
- AnyToolBench (400 queries the authors built, no reference APIs): AnyTool scored 73.8%; ToolLLM paired with a GPT-4 solver scored 36.6%, and a plain GPT-4 agent 14.0%.
- Ablation on G2-I and G3-I: removing the hierarchy gave 22.4 and 15.8 against 58.9 and 63.2; removing self-reflection gave 19.6 and 15.8.
- Re-activating more levels raised pass rate: tool agents only 43.9 and 44.7, plus category agents 55.2 and 55.3, all agents 58.9 and 63.2.
- Searchable pool size: 1K APIs 18.6 and 7.9, 5K 26.3 and 23.7, 10K 38.1 and 36.8, full pool 58.9 and 63.2.
- Cost per query averaged about 135K tokens and 43.3 OpenAI calls, with a 200,000-token cap.

## Limits

- Wall-clock time was not measured; the authors say it is infeasible given unstable GPT-4 server response.
- The judge is GPT-4 only and was validated on one subset (96.5% agreement). Filtered subsets are small (38 queries for G3-I). Ablations are single runs.
- The authors filtered ToolBench and built AnyToolBench with GPT-4-generated queries, which could favour GPT-4 agents. The baselines were implemented by the authors.
- The extraction notes the "self-reflection" step resembles a feedback-driven new search more than a verified correction.
- Internal inconsistency: the abstract says +35.4% over ToolLLM while the body reports +32.6 and +19.3 points against two different baselines.
- Performance in extremely complex scenarios is unverified by the authors' own account.

## See Also
- [[Dynamic Tool Discovery]] — prerequisite-for
- [[Tool Design as Harness Surface]] — related
- [[SkillWeaver Compositional Skill Routing]] — alternative-to
- [[APIGen]] — related (both build on ToolBench's API pool)
