---
title: Multi-Agent Role Specialization
tags: [llm, pattern]
summary: Multiple agents with distinct roles and tool sets coordinated by an orchestrator — the highest-complexity orchestration, justified only when quality genuinely requires different modes of thinking, and explicitly never a starting point.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
---

# Multi-Agent Role Specialization

Multiple agents, each with a specific role (researcher, writer, reviewer, coordinator),
working together. An orchestrator delegates to specialists; each has its own tools, system
prompt, and expertise.

**Use when** the task genuinely requires different *modes* of thinking (research vs.
writing vs. critique); a single agent can't maintain quality across all subtasks; the
system has 5+ distinct responsibilities; you want to scale by adding specialists.

**Avoid when** one agent with good tools can handle it (most cases); the team is under
four engineers; the "roles" are just different prompts for the same task; or the timeline
is weekend/multi-sprint.

## The role test

The sharpest disqualifier in the source: *"the 'roles' are just different prompts for the
same task."* Naming a prompt "Researcher" does not make it a specialist. The test is
whether the modes of thinking genuinely differ — a critic that only reruns the writer's
prompt with harsher wording is one agent wearing two hats, and pays multi-agent cost for
single-agent capability.

## Complexity

**Semester** — needs agent-to-agent communication protocol, shared state management,
orchestration logic, per-agent evaluation, and failure handling when one agent fails.
These are prerequisites, not refinements, which is why the [[Complexity Floor]] here is
categorical.

## Example

A research nonprofit producing policy briefs: orchestrator receives a topic → Researcher
searches academic databases and news → Analyst identifies themes, contradictions, gaps →
Writer drafts in house style → Editor checks citations, tone, factual claims → polished
brief returned.

## Scaffold mapping

| Parameter | Value |
|---|---|
| `project_type` | `agent` |
| `primary_chat_agent` | `lg_agent` or `both` |
| `agent_tools` | `[search, mcp, custom]` |
| `deployment_target` | `cloud` |

## Trade-offs

**Pro:** highest quality for genuinely complex tasks; modular (add/remove specialists);
each agent evaluable independently.
**Con:** highest complexity; expensive (multiple LLM calls per task); hardest to debug —
*which agent caused the error?*; slowest (sequential agent calls).

**Recommendation:** *"Almost certainly overkill for a POC. Start with a single agent. If
quality suffers because one agent can't handle all roles, add one specialist at a time.
Never start with multi-agent."*

## See Also
- [[Agent Orchestration Patterns]] — part-of
- [[Multi-Step Graph Orchestration]] — upgrade-from
- [[Complexity Floor]] — constrains
- [[Agentic Workflow Patterns]] — related (orchestrator-workers)
