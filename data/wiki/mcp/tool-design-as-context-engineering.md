---
title: Tool Design as Context Engineering
tags: [mcp, llm, agents, concept]
summary: Tools consume context twice — definitions sit in the window permanently, results enter per call — so token-efficient results, unambiguous boundaries, and terse routing descriptions are context decisions, not API aesthetics.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--06-multi-agent-context.md
---

# Tool Design as Context Engineering

Tools consume context **twice**: their **definitions** sit in the window permanently, and
their **results** enter it per call. Both are [[Context Engineering]] surfaces, which makes
tool design a context discipline rather than only an API-design one.

## Token-Efficient Results

A tool returning 50k tokens of raw output **defeats just-in-time retrieval** — you have
reintroduced the bulk-loading problem through the tool layer. See
[[Context Retrieval Strategies]].

Tools should return what the agent needs to **decide**, not everything they could produce.

- Paginate or truncate large outputs with an explicit continuation affordance
- Return structured summaries with **drill-down identifiers** rather than full payloads
- **Filter at the tool boundary**, where filtering is cheap and deterministic — not in the
  model, where it costs attention

## Tool Overlap

**Tool overlap** — multiple tools covering similar functionality — creates ambiguous
decision points. The agent must spend attention choosing, and may choose inconsistently
across runs.

> **Test:** given this task, is there exactly one obviously correct tool?

If two plausibly apply, either merge them or sharpen their descriptions until the boundary
is unambiguous.

## Self-Contained and Robust to Error

Each tool should be usable without knowledge of the others, handle its own errors, and
return **structured errors the agent can act on**.

```json
{"error_code": "not_found", "is_fatal": false}
```

That is actionable. A stack trace is 500 tokens of noise the agent cannot use — and those
tokens sit in the window for the rest of the session.

## Descriptive Parameters

Parameter names and descriptions should be unambiguous and play to model strengths.

| Weak | Strong |
|---|---|
| `query: str` | `search_query: natural-language description of the code you're looking for` |

The first tells the model nothing about what to generate; the second specifies the shape of
the value.

## Descriptions Are Routing Logic

Tool descriptions follow the same discipline as skill descriptions:

- When should I use this?
- When should I **not** use this?
- What are the outputs and success criteria?

**Terse beats verbose — these tokens are resident in every window.**

```yaml
# bad (~45 tokens)
description: |
  This skill handles the complete deployment process to production.
  It covers environment checks, rollback procedures, and post-deploy
  verification. Use this before deploying any code to production.

# good (~9 tokens)
description: Use when deploying to production or rolling back.
```

Negative examples reduce misfires: *"Don't call this when…"* plus what to do instead.

## See Also
- [[Context Engineering]] — part-of
- [[Multi-Agent Context]] — complements
- [[MCP Protocol]] — implements
- [[Context Retrieval Strategies]] — depends-on
- [[Tool Design as Harness Surface]] — complements (same tools seen as a harness contract rather than a context cost)
