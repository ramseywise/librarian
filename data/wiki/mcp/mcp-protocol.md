---
title: MCP Protocol
tags: [mcp, concept]
summary: Model Context Protocol — how it separates tool definitions from agents, enabling independent deployment and runtime tool discovery; includes AWS Bedrock AgentCore deployment pattern from the Hypernova PoC.
updated: 2026-11-08
sources:
  - data/raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md
  - data/raw/claude-docs/playground/docs/archived/adk-samples-patterns-analysis.md
  - data/raw/web/2026-04-24-cloud-google-com-blog-topics-developers-practitioners-use-go-5e50e6e1.md
  - data/raw/web/2026-04-24-modelcontextprotocol-io-introduction-dd33377c.md
  - data/raw/notion/2026-06-04-hypernova-mcp-server-poc.md
  - data/raw/agent-skills/langchain-rag/references/advanced-patterns.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch07-enabling-agents-to-take-action.md
  - data/raw/papers/2026-11-08-ai-agents-with-mcp-ch01-agentic-ai-mcp.md
  - data/raw/papers/2026-11-08-ai-agents-with-mcp-ch02-introduction-model-context-protocol.md
  - data/raw/papers/2026-11-08-ai-agents-with-mcp-ch03-making-intelligent-application-agentic-mcp-clients.md
  - data/raw/papers/2026-11-08-ai-agents-with-mcp-ch04-mcp-clients-advanced-use-best-practices.md
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

The ADK samples repo uses a `[product]` MCP server (13 tools) with:
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

## Transport Protocols

Two transport mechanisms for MCP servers:

| Protocol | Description | Status |
|---|---|---|
| **SSE (Server-Sent Events)** | Two endpoints: HTTP POST for client→server requests, SSE GET for server→client streaming | Legacy; still widely used |
| **Streamable HTTP** | Single HTTP endpoint for both directions; server can optionally use SSE for streaming | Successor (released March 2025) |

ADK uses `MCPToolset.from_server` to connect to external MCP servers:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

# SSE transport
toolset = await MCPToolset.from_server(
    SseServerParams(url="http://localhost:8001/sse")
)
tools = await toolset.get_tools_async()
agent = LlmAgent(tools=tools)
```

For Streamable HTTP, use `StreamableHTTPServerParams` (same pattern, different params class).

**FastMCP** is the recommended server implementation for Python:
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("my-server")

@mcp.tool
def extract_wikipedia_article(query: str) -> str: ...
```

Debug MCP servers with `mcp dev server.py` (MCP Inspector UI).

Production auth: under active development in the MCP spec — refer to the MCP auth specification.

## AWS Bedrock AgentCore Deployment Pattern

AWS Bedrock AgentCore Runtime is a managed container runtime that simplifies deploying MCP servers to production. The assistant team's Hypernova PoC uses this pattern.

### How it works

```
bedrock-agentcore deploy
  → build container image
  → push to ECR
  → provision AgentCore Runtime endpoint
  → auto-configure CloudWatch + X-Ray observability
```

Single CLI command replaces manual ECS task definition, ECR push, CloudWatch log group setup, and X-Ray tracing instrumentation.

### Configuration (`.bedrock_agentcore.yaml`)

```yaml
name: [product]-mcp-server
entry_point: python src/server.py
observability: enabled       # auto-wires CloudWatch + X-Ray
auth:
  type: cognito              # JWT authorizer via Amazon Cognito
  user_pool_id: us-east-1_xxx
  client_id: xxx
```

### Authentication

Amazon Cognito JWT authorizer is the default auth pattern for Bedrock AgentCore MCP servers. The Runtime validates the JWT before forwarding to the container — no auth code required in the MCP server itself.

### Per-Organization Token Forwarding

When the MCP client (e.g., assistant-agents Next.js app) needs to pass organization-scoped credentials to the MCP server, the pattern is: forward the credential as an HTTP request header. The MCP server reads it from the request context on each call — no hardcoded or stored credentials.

Example (assistant-agents / [product].dk): the Next.js app sends the [product] API token (from the iframe) as a header on each MCP request. The [product]-mcp-server reads it and uses it for all [product] API calls in that request.

### Observability (auto-configured)

With `observability: enabled`:
- **CloudWatch**: all stdout/stderr captured automatically as log streams
- **X-Ray**: every MCP tool call is traced with a segment including input/output
- No SDK instrumentation required in the MCP server code

See Hypernova MCP for the full production deployment of this pattern.

## Limits stated in a 2025 book

Lakshmanan and Hapke (Generative AI Design Patterns, ch. 7) list three MCP limits as of May 2025 and flag them as likely to date: the protocol does not enforce authentication or authorisation; communication is mostly one-way, with agent-to-agent protocols arriving to fill it; and standard calls were terminated after 30-60 seconds depending on network setup, with streamable HTTP enabling longer streams. Their split of work: MCP eases supplying tool definitions, while a client framework eases invoking tools and returning results. Stdio transport suits Python-only clients and streamable HTTP other languages or machines.

## Client-side details from an early-release MCP book

Chapters 1 to 4 of an early-release book, AI Agents with MCP, cover the client side. The extraction describes it as a raw draft with no experiments, so these are the chapters' claims and worked examples, not measurements, and the SDK details are tied to one Python SDK version.

- **MxN to M+N.** With one connector per model-tool pair, 3 models and 4 tools need 12 connectors; under MCP every model gets a client and every tool a server, which makes 7 (a worked example).
- **Roots are advisory.** In the specification servers should respect them but are not required to, so roots cannot serve as a security control. The chapters advise validating URIs against path traversal and keeping access control in the host.
- **Rug pull.** A server that was safe when installed can be made malicious by its owner; the chapters say to treat servers as attack surface, local and remote.
- **Sampling and elicitation.** A client that offers sampling should have a human approve the request before the LLM is called and approve the reply before it goes back. Elicitation replies are accept, decline or cancel, and decline and cancel carry no content. A client must advertise each capability it supports.
- **Many servers.** Two primitives sharing a name cannot coexist in a ClientSessionGroup, so a name hook renames them to avoid collisions. Tool-choice accuracy may fall as tools accumulate (unquantified); the chapters suggest evaluating before and after adding a server.
- **Resumption and pagination.** Streamable HTTP connections resume from the last event id, and only list methods paginate, through nextCursor.
- **Transports and auth.** Always support stdio and add Streamable HTTP for remote use; transports that include authorisation must implement OAuth 2.1; do not pass all environment variables to a stdio server.
- **Ecosystem counts** (about 350 official and under 650 community servers listed, 4,800 specification-repo stars) are as of writing in 2025 and have dated.

Inconsistencies noted by the extraction: some figure numbering in chapter 2 is wrong (the sampling figure is cited as 2-3 but is 2-4), and the chapter 3 text ends after the prompts example although its introduction promises more. Code in the chapters is simplified and lacks the human approval the text says is required.

## See Also
- [[Karpathy LLM Wiki Pattern]]
- [[ADK Context Engineering]]
- [[Librarian RAG Architecture]]
- [[Agentic Workflow Patterns]]
- [[Integration Pattern Selection]] — alternative-to (MCP against Composio, direct clients, webhooks, and n8n)
- [[Tool Design as Context Engineering]] — extends (tool definitions and results as context surfaces)
- [[Agent Interoperability Protocol Stack]] — related (part of; MCP's place alongside A2A, A2UI, AP2, and UCP)
- [[REST-First, MCP as Adapter]] — extends (MCP servers as thin adapters over versioned REST)
- [[Dynamic Tool Discovery]] — extends (loading tool schemas on demand once servers multiply)
- [[LiveMCP-101]] — related (a benchmark of agents using live MCP tools)
- [[MCP Server Architecture Patterns]] — instance-of (five server patterns and a tool-count budget)
- [[Alita]] — related (generated tool scripts packaged as MCPs)
- [[Agent Communication Protocol Taxonomy]] — related
- [[EvoOntology Self-Evolving Ontology Layer]] — related (an ontology served to a data agent through browse and resolve MCP tools)
