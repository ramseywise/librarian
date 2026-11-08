---
title: Tool Design as Context Engineering
tags: [mcp, llm, agents, concept]
summary: Tools consume context twice — definitions sit in the window permanently, results enter per call — so token-efficient results, unambiguous boundaries, and terse routing descriptions are context decisions, not API aesthetics.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--10-tools-and-multi-agent.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--06-multi-agent-context.md
  - data/raw/repos/datathon_mcp/CLAUDE.md
  - data/raw/papers/2026-11-07-qin-2024-tool-learning-foundation-models.md
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

For enumerated arguments, make the error **list the valid values** (a read-only data-pool
MCP does this for every bad region, code or filter), so the model can correct itself in one
retry without a separate lookup tool.

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

## Evidence: tools can hurt, and examples help

Qin et al., "Tool Learning with Foundation Models" (arXiv 2304.08354, v3 of August 2024), is a
survey with one small experiment of its own: 18 tools in the BMTools repository, tried with
text-davinci-003 and ChatGPT (23 March 2023 version) under no-tool, zero-shot (API documentation)
and few-shot (documentation plus usage examples) prompting. Results are self-reported.

- ChatGPT on Calculator/ASDiv (266 items): 91.7 with no tool, 74.1 zero-shot and 92.5 few-shot.
- ChatGPT on Wikipedia/HotpotQA (200 sampled): 34.5 with no tool, but 8.5 zero-shot and 19.0 few-shot.
- ChatGPT on Search Engine/RealTimeQA (30 items): 50.0 with no tool, 43.3 zero-shot and 63.3 few-shot.
- Tools whose parameter is executable code stay hard: KGs (SPARQL, 64 curated questions) few-shot
  46.9 for davinci and 14.1 for ChatGPT.
- Six tools (Map, Weather, Slides, Tables, Cooking Assistant, AI Painting) reach satisfying
  completion with few-shot prompting; Weather scores 99.0 for both models.

The authors read this as zero-shot tool use sometimes scoring under no tool when the model has the
knowledge itself, and claim few-shot always beats no tool, which their own ChatGPT row on Wikipedia/HotpotQA
contradicts (34.5 with no tool against 19.0 few-shot). They prefer usage examples to descriptions alone.
They also recommend unifying tool interfaces, and adding a retrieval stage that selects tools once
the set outgrows the context window. The test sets are small (for example n=10 for 3D models, n=30 for
RealTimeQA) with no variance or repeated runs, and curated queries are scored by humans reading the API-call
trace, with no rubric or agreement given. Queries were expanded with ChatGPT, itself a model under test.
Per the extraction, the text and Table 1 disagree on Calculator datasets and Stock test size, the
few-shot claim conflicts with the HotpotQA row, and
the authors concede scores across tools are not comparable. The models predate native function calling.

## See Also
- [[Context Engineering]] — related (part of)
- [[Multi-Agent Context]] — related
- [[MCP Protocol]] — related
- [[Context Retrieval Strategies]] — prerequisite-for
- [[Tool Design as Harness Surface]] — related (same tools seen as a harness contract rather than a context cost)
- [[Curl-Bridge Context Injection]] — alternative-to (instructions to curl instead of tool definitions)
- [[Dynamic Tool Discovery]] — extends
- [[MCP Server Architecture Patterns]] — related (tool-count study)
