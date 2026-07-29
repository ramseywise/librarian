---
title: Agents Interview Study Guide
tags: [interview, reference]
summary: Exam-prep reference for agent architecture questions — workflow vs agent distinction, composable patterns, ACI tool design, harness engineering, long-horizon reliability, and memory taxonomy.
updated: 2026-07-19
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--4-agents--interview-guide.md
  - raw/repos/learn-ai-engineering/interviewing--notes--agents-design.md
  - raw/repos/learn-ai-engineering/interviewing--notes--agent-harness.md
---

# Agents Interview Study Guide

Centerpiece topic for AIE/FDE loops. Interviewers test: (a) pick the simplest pattern that works, (b) design the system around the model (harness), (c) reason about reliability over long horizons and multiple agents.

## Workflow vs Agent — Always Open Here

- **Workflow**: LLMs + tools orchestrated through predefined code paths.
- **Agent**: the LLM dynamically directs its own process and tool use.

Anthropic's production guidance: start with the simplest thing — a single call with retrieval and examples is often enough. Add agency only when it measurably improves outcomes. Saying this first signals judgment, not weakness.

## Five Composable Workflow Patterns

| Pattern | Mechanism | Use when |
|---|---|---|
| Prompt chaining | sequential calls, gates between steps | fixed decomposition, accuracy > latency |
| Routing | classifier → specialized pipeline/model | distinct input classes |
| Parallelization | sectioning (independent) or voting (×N) | independence, or confidence via consensus |
| Orchestrator–workers | central LLM decomposes, delegates, synthesizes | subtasks unpredictable |
| Evaluator–optimizer | generator + critic loop | clear criteria + feedback demonstrably helps |

See [[Agentic Workflow Patterns]].

## Tool Design (ACI) — Highest-Leverage Detail

Treat the agent-computer interface like HCI. Tool descriptions written like docstrings for a junior dev: usage examples, edge cases, boundaries from neighboring tools. Careful parameter naming. Poka-yoke arguments so misuse is impossible (canonical: require absolute paths — one of the highest-impact fixes in Anthropic's SWE-bench agent).

Debugging heuristic: when the agent misuses a tool, fix the tool description before blaming the model. Tool quality beats tool quantity. See [[ACI (Agent-Computer Interface)]].

## Harness Engineering — "Agent = Model + Harness"

The harness is everything around the model that makes intelligence useful: system prompts/context policies, tools + skills + MCP servers, bundled infrastructure (filesystem, sandbox, browser), orchestration logic (subagents, routing, HITL), hooks/middleware for deterministic control, and a recovery path.

Four load-bearing parts to name: **acceptance baseline, execution boundary, feedback signals, rollback mechanism**.

Key moves:
- **Filesystem as durable state** — offload what doesn't fit in context; persist work across sessions; plan files as first-class artifacts.
- **Bash/code as the universal tool** — agents solve unforeseen problems by writing code, not by pre-designing every tool.
- **Sandbox + self-verification loops** — run tests, read logs, iterate; verification is the feedback signal that makes long runs converge.
- **Progressive disclosure (skills)** — load capability descriptions on demand; treat AGENTS.md/CLAUDE.md as a table of contents (~100 lines), details in on-demand docs.
- **Encode constraints, don't document them** — linters/types/CI enforce architecture.

Quotable thesis: **"a decent model with a great harness beats a great model with a bad harness."**

## Long-Horizon Reliability (Loop Engineering)

Long tasks outlive context windows. Pattern: externalize state to disk (task file, progress log), make the working loop reentrant so a fresh context can resume from the breakpoint, verify after every step. Rule of thumb: any task longer than ~30 minutes must have crash recovery — it's a requirement, not an option.

**Subagents as context firewall**: discrete noisy work (search, debugging) runs in isolated contexts that return only summaries, keeping the orchestrator thread coherent.

## Memory Taxonomy (Interviewers Expect This)

- **Working** — in-context
- **Episodic** — past interactions, conversation history
- **Semantic** — facts about the world/user
- **Procedural** — how-to, skills

Design points: curated MEMORY.md-style files + on-demand retrieval beats stuffing history. Memory writes should be reviewable/rollbackable. Caution: added memory can make chatbots sound smarter but reduce trust when it surfaces stale or misapplied facts — retrieval precision matters more than recall here.

See [[Agent Memory Types]].

## See Also
- [[Agentic Workflow Patterns]] — prerequisite-for
- [[ACI (Agent-Computer Interface)]] — instance-of
- [[ReAct Pattern]] — instance-of
- [[RAG Interview Study Guide]] — extends
- [[System Design Interview Study Guide]] — extends
