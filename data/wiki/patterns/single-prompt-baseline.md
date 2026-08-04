---
title: Single Prompt Baseline
tags: [llm, pattern]
summary: One LLM call with no tools, state, or framework — the simplest orchestration, correct for classification/extraction/summarization, and the baseline any agent must beat to justify its complexity.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
---

# Single Prompt Baseline

Input → prompt → output. No tools, no state, no framework. The simplest possible AI
system, and the baseline against which every more complex orchestration should be judged.

**Use when** the task is classification, extraction, or summarization; no external tools
are needed; each request is independent; the timeline is a weekend sprint.

**Avoid when** the AI must take actions, multiple steps are required, conversation history
matters, or streaming/real-time interaction is needed.

## Complexity

**Weekend sprint** — literally one API call with a well-crafted prompt. This is the only
orchestration pattern that fits inside a [[Complexity Floor|weekend floor]] with room to
spare.

## Example

An arts nonprofit reformats grant reports from an internal template into each funder's
required format. Input: raw report plus funder requirements. Output: reformatted text.
One call, no tools.

## Scaffold mapping

| Parameter | Value | Rationale |
|---|---|---|
| `project_type` | `prototype` or `ai_backend` | No agent framework needed |
| `primary_chat_agent` | `none` | Build on rag_agent infra without a chat agent |

## Trade-offs

**Pro:** simplest implementation, cheapest to run, easiest to evaluate, fastest to build.
**Con:** no tools, memory, or complex reasoning — limited to what one call can do.
**Upgrade path:** when you hit the limits, add tool-calling → [[Single Agent With Tools]].

Anthropic's independent guidance agrees: *"Single LLM calls with retrieval and in-context
examples are often enough"* — see [[Agentic Workflow Patterns]].

## See Also
- [[Multi-Step Graph Orchestration]] <!-- auto-linked -->
- [[Chain of Thought]] <!-- auto-linked -->
- [[Agent Orchestration Patterns]] — part-of
- [[Single Agent With Tools]] — upgrade-path
- [[Agentic Workflow Patterns]] — related
