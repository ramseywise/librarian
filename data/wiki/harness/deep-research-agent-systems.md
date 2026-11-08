---
title: Deep Research Agent Systems
tags: [harness, concept]
summary: How search and deep-research agents are built, from a survey's three-layer taxonomy to concrete systems (Open Deep Search, MindSearch, Baidu's multi-agent search); what each reports and how little of it is comparable across papers.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-huang-2025-deep-research-agents.md
  - data/raw/papers/2026-11-06-alzubi-2025-open-deep-search.md
  - data/raw/papers/2026-11-06-chen-2024-mindsearch.md
  - data/raw/papers/2026-11-06-li-2025-towards-ai-search-paradigm.md
---

# Deep Research Agent Systems

A deep-research agent plans, searches, reads and writes over many turns. Four sources are folded here; deeper pages cover the named methods linked at the bottom. All numbers are the papers' own (self-reported).

## Survey taxonomy (Huang et al.)

The survey sorts systems by three layers: workflow (static pipelines against dynamic replanning), planning strategy for dynamic systems (planning only, intent then planning, unified), and composition (single agent in a ReAct-style loop against multi-agent coordination). It says single agents suit end-to-end RL while multi-agent coordination makes RL hard. On retrieval it contrasts API search (fast, weak on JavaScript pages and logins) with browser-based retrieval (reaches dynamic content, costs latency) and suggests hybrids. For long context it lists three strategies: larger windows, compression of intermediate steps, and external structured storage. Its benchmark tables are compiled from other papers rather than controlled comparisons.

## Open Deep Search (ODS)

A search tool (query rephrasing, SERP retrieval, page scraping with chunk re-ranking) plus a reasoning agent over any base model. ODS-v1 uses chain-of-thought, ReAct and dynamic few-shot examples; ODS-v2 uses a code-writing agent. With DeepSeek-R1, ODS-v2 scores 88.3 on SimpleQA (4,326 questions) and 75.3 on FRAMES (824) where bare R1 gets 82.4 and 30.1; GPT-4o Search Preview scores 90.0 and 65.6. ODS-v2 averages 3.39 searches per FRAMES query and 1.45 per SimpleQA query. SimpleQA is judged by GPT-4o-mini.

## MindSearch

A planner writes Python that builds a search graph step by step; each node spawns a searcher, nodes added together run in parallel, and each searcher sees only its parent node's answer and the root question. On HotpotQA with InternLM2.5-7b-chat, graph planning scores 64.0 against 58.0 for ReAct and 61.3 for CodeAct. Closed-set averages: 59.8 against 55.1 for ReAct (GPT-4o) and 49.2 against 42.9 (InternLM2.5-7b). Mean DAG depth is 1.1, 1.2 and 1.6 for 2, 3 and 4 hops.

## Baidu AI search paradigm

A blueprint of Master, Planner, Executor and Writer agents. The Master chooses among three team setups according to query complexity; the Planner emits a whole task DAG once, which the Executor runs layer by layer; failures trigger re-planning of the affected subgraph only; tools are narrowed to about a dozen by retrieval first. Against the legacy engine, blind side-by-side net win rate was 0.00% on simple queries, +5.00% on moderately complex and +13.00% on complex ones (sample size not stated); a 1% traffic A/B test showed daily active users +1.85%.

## Limits

- The survey itself names, in a closing limitation paragraph, weak generalisation across varied tasks, rigid workflows, trouble wiring in fine-grained external tools, and heavy compute for advanced planning and optimisation. Its open challenges add narrow information sources, linear planning, single-agent designs, benchmarks that models can answer from memory, and underdeveloped self-evolution.
- Its tables are compilations. The extraction notes no controlled comparison of static against dynamic or single against multi-agent designs, no cost or latency figures, no survey method, and rows it could not verify (an OpenAI DR GAIA average below its level scores, and an H2O.ai row appearing under both test and dev with different models).
- ODS: no cost, latency or variance; closed systems score higher on SimpleQA; ablation SimpleQA uses 500 questions. The extraction notes inconsistencies: ODS-v1 with Llama3.1-70B is 83.4 in Table 2 and 84.0 in Table 3, and the text names OpenPerplex in one place and serper.dev in another.
- MindSearch: the extraction notes that the text says multi-query generation matters most, but Table 3 shows removing page selection costs more (58.0 against 60.6, self-reported); the open-set human study has 100 queries and 5 raters; speed claims lack hardware details.
- Baidu: a blueprint with no ablation of the DAG against ReAct or a single agent, and no cost data; the extraction notes that its win-rate labels (WTL and NWR) are used inconsistently.

## See Also
- [[WebThinker Deep Research Agent]] — instance-of
- [[DeepDive Knowledge-Graph Search Agent Training]] — instance-of
- [[Harness-1 State-Externalizing Search Agent]] — instance-of
- [[AgentIR Reasoning-Aware Retrieval]] — instance-of
- [[Task Decomposition Patterns]] — related
- [[FINDER and DEFT (Deep Research Agent Failures)]] — related
- [[AgentRxiv Shared Preprint Server]] — instance-of
- [[CodeScientist Semi-Automated Discovery]] — instance-of
- [[AutoScientists Self-Organizing Teams]] — instance-of
