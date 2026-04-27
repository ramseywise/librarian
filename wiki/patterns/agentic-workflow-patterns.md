---
title: Agentic Workflow Patterns
tags: [llm, pattern]
summary: Anthropic's five composable workflow patterns for LLM agents — when to use each, and the ACI principle for tool design.
updated: 2026-04-24
sources:
  - raw/web/2026-04-24-www-anthropic-com-engineering-building-effective-agents-7d24e5fa.md
---

# Agentic Workflow Patterns

From Anthropic's production experience: the most successful agent implementations use simple, composable patterns rather than complex frameworks.

## Workflows vs Agents (Anthropic's Distinction)

| Type | Definition |
|---|---|
| **Workflow** | LLMs and tools orchestrated through predefined code paths |
| **Agent** | LLM dynamically directs its own processes and tool usage |

Start with the simplest solution. Single LLM calls with retrieval and in-context examples are often enough. Add agentic complexity only when it demonstrably improves outcomes — it trades latency and cost for task performance.

## The Five Workflow Patterns

### 1. Prompt Chaining

Task → sequential LLM calls, each processing the previous output. Programmatic gate checks can validate intermediate steps.

**Use when:** task cleanly decomposes into fixed subtasks, and trading latency for accuracy is worthwhile.

**Examples:** generate marketing copy → translate; write outline → validate → write document.

### 2. Routing

Classifier LLM → routes input to specialized downstream tasks. Enables separation of concerns and targeted prompts.

**Use when:** inputs fall into distinct categories better handled separately, and classification can be done accurately.

**Examples:** customer service query type → different processes; easy questions → Haiku, hard → Sonnet.

### 3. Parallelization

Two variations:
- **Sectioning** — break task into independent subtasks run simultaneously
- **Voting** — run the same task multiple times for diverse outputs

**Use when:** subtasks are independent (sectioning), or high-confidence results require multiple perspectives (voting).

**Examples (sectioning):** guardrails model runs in parallel with response model. **Examples (voting):** multiple prompts each review code for vulnerabilities.

### 4. Orchestrator-Workers

Central LLM dynamically breaks down tasks and delegates to worker LLMs; synthesizes results. Workers' subtasks are not pre-defined — the orchestrator determines them from the input.

**Use when:** task requirements can't be predicted in advance (e.g. multi-file code changes, open-ended research gathering).

This is topographically similar to [[Plan and Execute Pattern]] but with dynamic rather than pre-planned subtask creation.

### 5. Evaluator-Optimizer

One LLM generates a response; another evaluates and provides feedback in a loop.

**Use when:** there are clear evaluation criteria, and iterative refinement provides measurable value. Two signals of good fit: (1) LLM responses improve with feedback, (2) an LLM can provide that feedback.

**Examples:** literary translation with nuance critique; complex search requiring multiple rounds.

## Three Core Agent Principles (Anthropic)

1. **Maintain simplicity** in agent design
2. **Prioritize transparency** — explicitly show the agent's planning steps
3. **Carefully craft the ACI** — agent-computer interface via thorough tool documentation and testing

## ACI — Agent-Computer Interface

Invest in ACI design the same way you invest in HCI. Key practices:

- Put yourself in the model's shoes — if *you* would need to think carefully about how to use a tool, the model will too
- Write tool descriptions like docstrings for a junior developer: include example usage, edge cases, input format requirements, and clear boundaries from other tools
- Think carefully about parameter names and descriptions
- Test with many example inputs; iterate on what mistakes the model makes
- **Poka-yoke your tools** — change arguments to make mistakes harder (e.g. always require absolute filepaths instead of relative ones)

> From Anthropic's SWE-bench agent: more time was spent optimizing tools than the overall prompt. Changing relative to absolute filepaths was one of the highest-impact fixes.

## Framework Guidance

Frameworks (Claude Agent SDK, Strands, Rivet, Vellum) help get started but add abstraction layers that obscure prompts/responses and make debugging harder.

**Recommendation:** start with LLM APIs directly. Most patterns can be implemented in a few lines. Use frameworks if needed, but understand what's underneath — incorrect assumptions about framework internals are a common error source. Reduce abstraction layers as you move to production.

## See Also
- [[Plan and Execute Pattern]]
- [[LangGraph Advanced Patterns]]
- [[MCP Protocol]]
- [[ADK vs LangGraph Comparison]]
- [[RAG Evaluation]]
- [[ACI (Agent-Computer Interface)]]
- [[Send API Fan-out]]
