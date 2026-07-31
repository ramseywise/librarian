---
title: ACI (Agent-Computer Interface)
tags: [llm, concept]
summary: Tool design discipline for agents — the interface between agent and tools, analogous to HCI for humans. Good ACI determines whether the agent uses tools correctly or hallucinates parameters.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
---

# ACI (Agent-Computer Interface)

Coined by Anthropic. ACI is the discipline of designing tools so that agents use them correctly — description clarity, parameter naming, schema structure, and error messages. Poor ACI is the primary cause of tool-use failures that look like reasoning failures.

## The Core Insight

Agents use tools based on:
1. The tool's description (when to call it)
2. The parameter schema (what to pass)
3. The return format (what they get back)

If any of these are ambiguous, the agent either calls the wrong tool, passes wrong parameters, or misinterprets results. This is an interface design problem, not a model capability problem.

## ACI Design Rules

**Descriptions:**
- State the *when to use* condition, not just what the tool does
- Include what the tool does NOT do (disambiguation from similar tools)
- Example: "Use this to search the knowledge base. Do NOT use for real-time information."

**Parameters:**
- Use self-documenting names (`user_query` not `q`)
- Add `description` to every parameter in the schema
- Constrain with enums where the space is bounded
- Include examples in the description for ambiguous types

**Return values:**
- Return structured data the agent can act on (not free text)
- Include a `success: bool` or status field so the agent knows whether to retry
- Never return silent failures

**Error messages:**
- Return actionable errors, not stack traces
- "Query too long — max 200 tokens" beats `ValueError: token limit exceeded`

## In the Librarian Agent

All tools in the Librarian pipeline subclass `BaseTool Protocol` with explicit input/output schemas. The `description` field on each tool is the ACI surface — vague descriptions are the first place to debug when the agent misbehaves.

## See Also
- [[Agentic Workflow Patterns]]
- [[MCP Protocol]] — MCP tool schemas as a structured ACI standard
- [[Librarian RAG Architecture]]
