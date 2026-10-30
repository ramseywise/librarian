---
title: Deep Agent Pillars
tags: [llm, agents, deep-agents, concept]
summary: "What separates a deep agent from a shallow tool-calling loop — explicit planning, an orchestrator with clean-context sub-agents, external memory with agentic search, and verification — all sitting on context engineering, and convergent across coding agents, agent SDKs, and deep-research products."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--deep-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--README.md
---

# Deep Agent Pillars

A **shallow** agent runs a tool-calling loop inside one context window and falls apart on
long, multi-step work. A **deep** agent adds four things. The framing is the DAIR agents
guide's; coding agents, agent SDKs, the LangChain Deep Agents SDK, and deep-research
products all converge on it — the same convergence argument made in [[Harness Engineering]].

| Pillar | What it means | Harness page |
|---|---|---|
| **Explicit planning** | A living to-do list the agent updates, retries and recovers from — not ad-hoc reasoning in context | [[Long-Horizon Execution]] (plans as first-class artifacts) |
| **Orchestrator + sub-agents** | An orchestrator delegates to specialists (search, code, retrieval, verification), each with a clean context, then integrates the results | [[Harness Orchestration]] |
| **External memory / agentic search** | Intermediate work goes to files, notes or stores rather than conversation history; the agent retrieves what it needs | [[Memory as Context]] |
| **Verification** | A judge, verifier sub-agent, or human checks outputs before they are accepted | [[Verification Loops]] |

On the memory pillar, the source points to *ReasoningBank* (arXiv 2509.25140) and *Agentic
Context Engineering* (arXiv 2510.04618) for how that external memory is built and curated.

## Underneath: Context Engineering

All four pillars sit on [[Context Engineering]]. **Underspecified instructions are the most
common deep-agent failure** — a deep loop amplifies a vague brief rather than correcting it.

## Deep vs. Classic Decomposition

The pillars look like the classic *agent = LLM + planning + tools + memory* decomposition
plus verification. The difference [[Harness Engineering]] draws: the classic framing
describes what the *model* does; the harness's four parts (acceptance baseline, execution
boundary, feedback, rollback) describe what the *system* must guarantee. The deep-agent
pillars are halfway between — they name architecture, and verification is the pillar that
reaches into guarantees.

A concrete implementation of all four is [[Deep Agents Framework]]: `write_todos`
(planning), the `task` tool (sub-agents), a pluggable virtual filesystem (external memory),
and HITL interrupts.

## See Also
- [[Deep Agents Framework]] — instance-of
- [[Harness Engineering]] — part-of
- [[Harness Orchestration]] — extends
- [[Long-Horizon Execution]] — depends-on
