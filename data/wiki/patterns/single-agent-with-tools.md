---
title: Single Agent With Tools
tags: [llm, pattern]
summary: One agent with a tool set, where the LLM chooses which tools to call and when to stop — the level most real projects need, and the recommended default before any graph or multi-agent escalation.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
---

# Single Agent With Tools

One agent with access to tools (search, database, calendar, APIs). The LLM decides which
tools to call, in what order, and when it has enough information to respond. The framework
handles the tool-calling loop.

**Use when** the AI must look things up or take actions to answer; tool selection is
straightforward; one role suffices; the happy path is *understand → call 1–3 tools →
synthesize*.

**Avoid when** there's complex branching logic, multiple specialized roles are needed,
human approval gates are required at specific points, or the process has retry loops.

## Complexity

**Multi-sprint** — needs agent framework setup, tool definitions with schemas, error
handling, and evaluation of tool-selection quality.

## Example

A workforce development org's case managers ask *"What programs is this client eligible
for?"* The agent searches the eligibility database, checks the client profile,
cross-references program requirements, and returns a ranked list. One agent, three tools.

## Framework choice

| Framework | Runtime | Best when |
|---|---|---|
| LangGraph | Python | Explicit state management; already using LangChain tools |
| Google ADK | Python | Deploying to GCP; managed session service; Gemini-first |
| Vercel AI SDK | TypeScript | Agent lives in a TS/Node backend; deploying to Vercel |

## Scaffold mapping

| Parameter | Value |
|---|---|
| `project_type` | `agent` or `chat_app` |
| `primary_chat_agent` | `lg_agent` (Python) or `ts_agent_framework: vercel_ai_sdk` (TS) |
| `agent_tools` | `[mcp, custom]` |
| `agent_memory` | `conversation` |

## Trade-offs

**Pro:** handles most real-world tasks; frameworks provide structure; good evaluation story
(grade tool selection and final answer separately).
**Con:** the LLM decides tool order and sometimes gets it wrong; needs good tool
descriptions; framework lock-in.

**Key insight:** *"Most DSSG projects need this level and no more. Resist the urge to build
multi-agent systems when one agent with good tools would work."*

Because tool-selection quality is the dominant failure mode here, tool description quality
is the dominant lever — see [[ACI (Agent-Computer Interface)]].

## See Also
- [[Agent Orchestration Patterns]] — part-of
- [[Single Prompt Baseline]] — upgrade-from
- [[Multi-Step Graph Orchestration]] — upgrade-path
- [[ACI (Agent-Computer Interface)]] — extends (tool descriptions drive selection quality)
