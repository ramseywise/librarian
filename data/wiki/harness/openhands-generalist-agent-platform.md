---
title: OpenHands Generalist Agent Platform
tags: [harness, concept]
summary: An open platform with an event stream, Docker runtime, skills library and agent delegation, plus a follow-up that gave the base agent a few general tools and raised GAIA results.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wang-2024-openhands.md
  - data/raw/papers/2026-11-06-soni-2025-coding-agents-multimodal-browsing-generalist.md
  - data/raw/papers/2026-11-06-xie-2023-openagents.md
  - data/raw/papers/2026-11-06-zhou-2023-agents.md
---

# OpenHands Generalist Agent Platform

OpenHands (Wang et al., ICLR 2025) is a community MIT-licensed platform for software-developer-style agents. Its hypothesis is that a single agent whose actions are general code (CodeAct) can hold its own across software, web and assistant tasks without task-specific prompts.

## Components

- An **event stream** records agent actions and environment observations; an agent turns the history of events into its next action.
- A **Docker runtime** per task session, reached through a REST server, offers bash, IPython and a Playwright browser. Isolation is asserted rather than security-tested.
- An **AgentSkills library** extends the interface; a skill is added only if the model cannot easily write the code itself or the skill calls an external model.
- **Delegation** lets one agent hand work to another through a delegate action.
- An evaluation framework integrates 15 benchmarks; integration tests mock model calls with scripted responses.

## Results

Authors' own numbers (self-reported); the baselines mix different models, and the paper does not say they were re-run.

- SWE-Bench Lite, 300 instances, no hints, CodeActAgent v1.8: 26.0% with claude-3-5-sonnet ($1.10 average cost), 22.0% with gpt-4o, 7.0% with gpt-4o-mini.
- HumanEvalFix Python (164): 79.3% with gpt-4o, below SWE-agent's 87.7% with a one-shot demonstration. ML-Bench subset (68): 76.5%. WebArena (812): 15.5% for the browsing agent. GAIA level-1 validation (53): 32.1% with gpt-4o.
- Setup quirks: GAIA comes from a different integrated agent, not CodeAct, and some benchmarks used subsets, and the agent versions were a mixture of v1.5 and v1.8.

## OpenHands-Versa follow-up

Soni et al. (2025) added code editing and execution, an API search tool, Set-of-Marks multimodal browsing and a multimodal file viewer to OpenHands v0.28.1, with a browsing condenser keeping only the latest browser observation and a planning prompt every 10 steps. Setup: pass@1 at temperature 0, with a single run in every cell, on the test splits (self-reported).

- With claude-3.7-sonnet against plain OpenHands on the same model: GAIA 37.21 to 51.16, TheAgentCompany full 26.29 to 30.86, SWE-Bench Multimodal 31.72 to 31.33.
- With claude-sonnet-4 the scores are 51.16 on GAIA, 34.43 on SWE-Bench M and 33.14 on TheAgentCompany.
- The one ablation varies the search API on GAIA validation, giving 56.96 for Brave, 58.18 for Exa and 64.24 for Tavily.
- No ablation of the individual added tools, so the GAIA gain is not attributed to any one of them.

## Limits

- No ablation ties a score to the event stream, runtime or skills; no variance, repeats or sandbox security test.
- Versa: Claude models only, single runs, and comparisons with published multi-agent baselines mix models, so the claim that specialist agents fail to generalise confounds architecture with tool coverage.
- Internal inconsistency in the extraction: the Versa abstract reports a TheAgentCompany gain of 9.1 points while the body gives 6.9 and 6.8.

## Two 2023 open platforms for comparison

**OpenAgents (Xie et al. 2023).** Three agents behind a web interface for non-expert users: a Data Agent (Python and SQL analysis with three tools that generate the code, Python in a Docker sandbox, SQL on SQLite), a Plugins Agent (over 200 plugins chosen by Instructor embeddings of plugin descriptions) and a Web Agent that controls the user's own Chrome through an extension. All follow a ReAct loop; the Data Agent prompt allows one tool per round, and at most 3 extra tool uses are allowed. Responses stream through a pushdown automaton parser, with a key pool for API limits and history truncation. The paper reports no quantitative evaluation, names failure modes without counting them, and the PDF does not state a venue.

**Agents library (Zhou et al. 2023).** A library built around an SOP, a graph of states, each with its own prompts and tools, where a controller model picks the next agent; three core classes are built from a JSON config. Memory follows RecurrentGPT, and an `_is_human` flag lets a person take an agent's role (this is not checkpointing). Automatic SOP generation is deferred to an unpublished paper. Limits: system description only, no task-quality evaluation; its feature table (Table 1) is scored by the authors; the loop has no turn limit.

## See Also

- [[Tool Design as Harness Surface]] — prerequisite-for
- [[SWE-agent Agent-Computer Interface]] — prerequisite-for
- [[TheAgentCompany]] — related (a benchmark used in the follow-up)
- [[Harness Orchestration]] — related
- [[CoAct-1 Coding Actions for Computer Use]] — related
- [[Multi-Agent Topology Patterns]] — related (the Agents library's SOP state graph)
