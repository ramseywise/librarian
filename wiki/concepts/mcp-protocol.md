---
title: MCP Protocol
tags: [mcp, concept]
summary: Model Context Protocol — how it separates tool definitions from agents, enabling independent deployment and runtime tool discovery via MCP servers.
updated: 2026-04-24
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
  - raw/playground-docs/adk-samples-patterns-analysis.md
---

# MCP Protocol

Model Context Protocol (MCP, Anthropic 2024) separates *tool definitions* from the agent. Instead of baking tools into the agent at construction time, tools are served as MCP servers and the agent discovers them at runtime.

## Three Primitives

| Type | Purpose | Example |
|---|---|---|
| **Resources** | Read-only data the LLM can browse | Documents, schemas, session history |
| **Tools** | Actions with side effects | Retrieve, create, send, search |
| **Prompts** | Reusable prompt templates | System prompt variants, formatting templates |

## LangGraph MCP Client

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient({
    "librarian": {"url": "http://localhost:8001/mcp", "transport": "streamable_http"},
    "s3": {"url": "http://localhost:8002/mcp", "transport": "streamable_http"},
}) as client:
    tools = client.get_tools()
    graph = create_react_agent(llm, tools=tools, checkpointer=checkpointer)
```

Tools registered in the graph come from MCP at runtime. Swapping the retrieval backend doesn't require redeploying the agent — just update the MCP server it points to.

## ADK MCP Integration

The ADK samples repo uses a `billy` MCP server (13 tools) with:
- **Dual entry points:** REST API (FastAPI, port 8766) + MCP server (stdio/SSE, port 8765)
- **Shared database:** SQLite used by both
- Pure Python, no ADK dependency — completely decoupled from the agent

**Agent Gateway pattern:** per-session `Runner + SSE queue`, hot-switch between agents via `POST /agents/switch`.

## SKILL.md + MCP Tool Activation

In the ADK samples, `SKILL.md` frontmatter declares which MCP tools to activate per skill:

```yaml
---
name: invoice-skill
metadata:
  adk_additional_tools:
    - list_invoices
    - get_invoice
    - create_invoice
---
# Invoice Management Instructions
...
```

The frontmatter controls which tools load; the body is the instruction injected when the skill loads. This separates domain logic from agent orchestration code entirely.

## Librarian MCP Servers (current)

Playground already has MCP server implementations:
- `src/interfaces/mcp/librarian.py` — exposes RAG retrieval
- `src/interfaces/mcp/s3.py` — exposes S3 object listing/reading
- `src/interfaces/mcp/snowflake.py` — exposes Snowflake queries

These are MCP servers. The copilot can be an MCP *client* connecting to these.

## Why MCP Matters for the Copilot

The copilot doesn't need to know whether retrieval comes from ChromaDB, OpenSearch, or Bedrock. It calls the `librarian` MCP tool and gets chunks back. The retrieval strategy is entirely encapsulated in the MCP server. This is the factory pattern at the network boundary — enabling independent deployment and versioning of each capability.

Switching retrieval backends: update the MCP server, zero redeploy of the agent.

## Librarian Wiki MCP Server (planned)

The wiki repo needs an MCP server to expose wiki content to other agents:

```
Pratiyush/llm-wiki → 12 tools: query, search, lint, sync, export, ...
```

Start read-only; add write tools behind confirmation. The wiki MCP server will be the runtime interface for other agents to load wiki pages as context.

## See Also
- [[Karpathy LLM Wiki Pattern]]
- [[ADK Context Engineering]]
- [[Librarian RAG Architecture]]
