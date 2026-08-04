---
title: Agent Orchestration Patterns
tags: [llm, pattern, reference]
summary: Four levels of agent logic structure — single prompt, single agent + tools, multi-step graph, multi-agent — ordered by control and complexity, with a decision shortcut and the governing rule to start simple and escalate only on demonstrated need.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
---

# Agent Orchestration Patterns

How an AI system's logic is structured and executed. The choice determines how much
control you have over reasoning, how complex the implementation is, and which framework
dependencies you take on.

| Pattern | Control level | Complexity | Best for |
|---|---|---|---|
| [[Single Prompt Baseline]] | None (one LLM call) | Minimal | Classification, extraction, summarization |
| [[Single Agent With Tools]] | Medium (LLM decides) | Low–Medium | Straightforward tool-calling tasks |
| [[Multi-Step Graph Orchestration]] | High (you define flow) | Medium–High | Workflows with branching and gates |
| [[Multi-Agent Role Specialization]] | Variable (agents delegate) | High | Large systems with specialized roles |

The ordering is also an **escalation path**. Each pattern's limits are the next one's
entry condition: a single prompt that needs to act becomes an agent with tools; an agent
whose tool order needs controlling becomes a graph; a graph whose quality suffers across
distinct modes of thinking becomes multi-agent.

## Decision shortcut

| Question | Answer → Pattern |
|---|---|
| Does the AI need tools (search, APIs, databases)? | No → single prompt. Yes → continue. |
| How many tools, and is selection obvious? | 1–5, obvious → single agent. |
| Does the process have explicit phases with different logic? | Yes → multi-step graph. |
| Do you need human approval at specific checkpoints? | Yes → graph with interrupt nodes. |
| Does quality require genuinely different thinking modes? | Yes → multi-agent. No → single agent, better prompts. |
| How long do you have? | Weekend → single prompt. Multi-sprint → agent or graph. Semester → graph or multi-agent. |

The time question is a hard constraint, not a preference — it interacts with the
[[Complexity Floor]] of the chosen [[AI Project Archetypes|archetype]].

## Framework decision matrix

Pattern first, framework second:

| Decision | → Framework |
|---|---|
| Runtime is TypeScript, deploying to Vercel | Vercel AI SDK |
| GCP deployment, managed sessions, Gemini-first | Google ADK |
| Need graph control flow (branching, loops, HITL) | LangGraph |
| Multi-provider LLM support needed | LangGraph (via LangChain integrations) |
| Simple single agent, no preference | ADK (less boilerplate for simple cases) |

## The governing bias

Every pattern in this source carries the same warning in a different form:

- Single agent: *"Most DSSG projects need this level and no more. Resist the urge to build
  multi-agent systems when one agent with good tools would work."*
- Graph: *"Start with a single agent. If you find yourself writing 'if the tool result
  shows X, then call tool Y' — that's a graph wanting to exist. Refactor into LangGraph
  then, not before."*
- Multi-agent: *"Almost certainly overkill for a POC. Never start with multi-agent."*

This matches Anthropic's independent guidance in [[Agentic Workflow Patterns]] — add
agentic complexity only when it demonstrably improves outcomes.

## See Also
- [[Graph Engineering]] <!-- auto-linked -->
- [[ACI (Agent-Computer Interface)]] <!-- auto-linked -->
- [[Multi-Agent Orchestration Patterns]] <!-- auto-linked -->
- [[Agentic Workflow Patterns]] — related (composable workflow patterns from Anthropic)
- [[AI Project Archetypes]] — extends (archetype constrains the plausible orchestration)
- [[Project Discovery Conversation]] — prerequisite-for
- [[Complexity Floor]] — constrains
