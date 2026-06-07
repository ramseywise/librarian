---
title: VA Hypernova MCP
tags: [mcp, adk, infra, project]
summary: Hypernova is the VA team's MCP server PoC — extracts 18 Billy.dk tools from va-agents into a standalone Python MCP server on AWS Bedrock AgentCore Runtime, adapted from a sevdesk production deployment (March 2026).
updated: 2026-06-05
sources:
  - raw/notion/2026-06-04-hypernova-mcp-server-poc.md
---

# VA Hypernova MCP

**Repo:** https://github.com/ageras-com/va-hypernova  
**Language:** Python (migrated from TypeScript)  
**Based on:** sevdesk production deployment `SV-2520-http-mcp` (live March 2026)

The Hypernova project extracts the 18 Billy.dk tool integrations from the va-agents Next.js app and deploys them as a standalone MCP server on AWS Bedrock AgentCore Runtime. Agent reasoning logic stays in the Next.js app; tools are called over HTTP.

---

## Why MCP for va-agents?

va-agents currently bundles all 18 Billy.dk API integrations inside the Next.js app alongside the agent logic. This creates coupling: changing a tool requires deploying the entire agent app.

MCP solves this by **separating the tool layer from the reasoning layer**:
- Tools (how to talk to Billy.dk) live in `billy-mcp-server`
- Agent (how to reason about a user's request) stays in Next.js
- Each can be developed, deployed, and updated independently

---

## Layered Architecture

```
Layer 1 — Auth & Security
  JWT/OAuth validation, RBAC, audit logging, rate limits

Layer 2 — Agent Orchestration (Next.js app)
  Google ADK + Gemini reasoning, conversation state, response formatting

Layer 3 — MCP Server (billy-mcp-server on Bedrock AgentCore)
  Standard MCP tool interface over HTTP — no business logic, no agent reasoning

Layer 4 — Agentic Tools (Billy.dk domain capabilities)
  18 tools: invoices, quotes, customers, products, emails, invitations, support knowledge lookup
```

The separation makes each layer independently evolvable: swap the reasoning model, add/remove tools, change auth — without rewriting adjacent layers.

---

## Current vs Proposed Architecture

| Component | Current (va-agents) | Proposed (Hypernova) |
|---|---|---|
| Agent framework | Google ADK + Gemini | Unchanged |
| Tool hosting | Inside Next.js app | Standalone `billy-mcp-server` on Bedrock AgentCore |
| Tool protocol | In-process function calls | HTTP via MCP protocol |
| Authentication | Internal ECS trust model | Amazon Cognito JWT authorizer |
| Deployment config | Jsonnet task definition | `.bedrock_agentcore.yaml` (single YAML) |
| Session state | PostgreSQL on RDS | Unchanged (MCP server is stateless) |
| RAG | Bedrock Knowledge Base | Unchanged — becomes one of the MCP tools |
| Observability | N/A | CloudWatch + X-Ray (auto-configured by AgentCore) |

---

## `billy-mcp-server` Details

- Standalone container: exposes all 18 Billy.dk tools as MCP endpoints
- No agent logic — only Billy.dk API calls + domain-specific error handling
- Stateless: no session history; org token + context passed with each request from Next.js
- Deployed via `bedrock-agentcore deploy` CLI (build → push ECR → provision Runtime in one step)

### Per-Organization Token Handling

Va-agents passes a different Billy API token per organization (from the Billy iframe as a request header). The MCP server reads the token from the incoming request context and uses it to authorize Billy API calls — no credentials hardcoded or stored.

---

## Observability

AgentCore auto-configures CloudWatch logging and X-Ray tracing when `observability: enabled` is set in the deployment YAML. No application-level instrumentation code required. Every tool call is logged and traceable.

---

## Repo Structure (va-hypernova)

The repository is explicitly structured as two layers:
- **Tool layer**: Billy-facing domain tools (the actual capabilities)
- **MCP layer**: MCP server/transport wrapper that exposes those tools via MCP protocol

This matches the separation-of-concerns model above and enables tools to evolve independently of the MCP transport and orchestration.

---

## MCP SDK

- **TypeScript** (va-agents is a Next.js app): `@modelcontextprotocol/sdk` (official Anthropic npm package)
- **Python** (va-hypernova): `FastMCP` — becoming the standard for Python agent-tool development
- No language change required in the Next.js app — it connects to the MCP server over HTTP

---

## See Also
- [[MCP Protocol]]
- [[VA Agent Project]]
- [[AI Engineering Chapter @Shine]]
- [[Shine Chat Agent]]
- [[ADK vs LangGraph Comparison]]
