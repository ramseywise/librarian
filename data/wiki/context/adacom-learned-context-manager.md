---
title: "AdaCoM Learned Context Manager"
tags: [context, pattern]
summary: "AdaCoM trains a small RL manager to edit a frozen agent's context through JSON edits; on BrowseComp-Plus it lifted four agents by 39.0% on average over ReAct (self-reported), and the learned edit style differs per agent."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yi-2026-learning-agent-compatible-context-management.md
---

# AdaCoM Learned Context Manager

The manager is a separate model that sits beside a frozen agent and rewrites the agent's context between steps, trained with reinforcement learning against that agent's task outcome. A separate manager is trained per agent.

## Setup and results (self-reported)

BrowseComp-Plus, 680 train and 150 test tasks, 35 iterations max, an embedding retriever, a GPT-4o judge, mean of 3 runs. The manager is Qwen3-4B-Instruct. The managed agents were DeepSeek-V3, Qwen3-Max, GLM-4.5-Air and Kimi-K2. Context is capped at 32K under AdaCoM.
- Average accuracy 24.17 for ReAct against 33.60 for AdaCoM (+39.0% relative); the Kimi agent gained +95.0% (self-reported).
- A trained summarize-only manager (SumCoM) averaged 29.39 (+21.6%) and lowered GLM from 32.56 to 26.44; an untrained manager averaged 22.01 (self-reported).
- Agent-side self-management (SumAgent 22.06, MemAct 25.72) did not reliably beat ReAct (self-reported).
- Mean context after management differed by agent: about 1.9K tokens under DeepSeek, then Kimi at 3.4K, Qwen at 5.2K and GLM at 7.0K. Stronger agents received later, lighter compression; weaker ones got near-every-round distillation. The paper calls this the Fidelity-Reliability trade-off.
- On MCP-Bench-Wiki (150 tasks, two agents) the average gain was +15.2% (self-reported). Managers transferred: 23 of 28 cross-agent pairs improved, with a mean gain of 25.0% over all 32 pairs (self-reported).
- The manager learned, unprompted, to keep a compact state note after the task message listing requirements, evidence, leads and failed queries. 42.6% of the Kimi agent's tool-use steps were repetitive under ReAct.

## Limits

- The 32K cap is below the agents' native windows (128-256K), so part of the gain may come from the cap itself rather than from learned editing; the claim that extra raw context hurts beyond an effective length is the authors' inference.
- Style mismatch caused failures: a 4B manager may not paraphrase losslessly, and aggressive compression hurt GLM. Process rewards helped in two agents only.
- A manager is trained per agent, and only a handful of agents and two task families were tested.

## See Also
- [[Context Compaction]] — prerequisite-for
- [[Learned Proactive Compaction]] — alternative-to
- [[AgentFold Context Folding]] — alternative-to
- [[Context-Aware Compression]] — related
