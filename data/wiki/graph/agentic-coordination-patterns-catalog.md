---
title: Agentic Coordination Patterns Catalog
tags: [graph, agents, pattern]
summary: "Six coordination designs (router, supervisor, swarm, blackboard, contract-net, supervision tree) with their stated failure points and safeguards, from a pattern book that reports no measurements."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch04-agentic-ai-architecture-components-interacti.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch05-multi-agent-coordination-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch14-use-case-multi-agent-system-loan.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch15-agent-frameworks-multi-agent-loan-processing.md
---

# Agentic Coordination Patterns Catalog

Chapter 4 separates direct agent-to-agent messaging from indirect coordination through a shared medium (stigmergy), and stacks function calling, MCP and A2A as layers. Chapter 5 then lists coordination designs. Each is a design sketch with code; none is benchmarked.

## The patterns

- **Agent Router:** a capability graph decides which agent receives a request and acts as a whitelist, so an unlisted route is refused.
- **Supervisor:** one agent assigns work and collects results. The book names it a single point of failure and advises checkpointing after every step.
- **Swarm:** peers pick work from a task board without a central assigner.
- **Blackboard:** agents read and write typed, versioned facts on a shared board, and a controller decides who acts next.
- **Contract-Net:** a manager announces a task and agents bid. The weakness is overstated bids; the safeguards are deadlines and a reputation score.
- **Supervision Tree:** parents restart crashed children but stop after a repeat limit (the example is five crashes within one second) so a crash loop cannot run forever.
- Companion mechanisms: shared epistemic memory with provenance, consensus with a round cap, and explicit conflict resolution.

## Worked loan-processing builds

Chapters 14 and 15 rebuild a loan-processing flow as a supervisor with four specialist agents wrapped as tools, with the ADK version in chapter 14; chapter 15 reimplements the loan agent only in CrewAI and LangGraph. Those two implementations are not equivalent, so the framework comparison is qualitative.

## Limits

- No run is measured; chapter 14 logs two runs (one approved, one denied) and chapter 15 prints no output.
- The CrewAI and LangGraph versions differ in how risk is scored (a rule-based tool versus a model-driven node), and the risk scale is not defined in the text.
- Tool bodies are elided, so the safeguards cannot be checked against code.

## See Also
- [[Multi-Agent Topology Patterns]] — related (the wiki's topology view)
- [[Multi-Agent Failure Modes at Scale]] — related
- [[Multi-Agent Orchestration Patterns]] — related
- [[Shared Epistemic Memory]] — extends
