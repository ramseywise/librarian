# Hypernova: MCP Server PoC by the Virtual Assistant Team

**Source:** Notion — Virtual Assistant Team Documents
**URL:** https://app.notion.com/p/359f148b3ab78046a596dcd9b2ba5d04
**Last updated:** 2026-06-04
**Based on:** internal production deployment SV-2520-http-mcp (vendor-a team, live March 2026)

---

## Overview

Proposed architectural change to va-agents — the product-a.dk virtual assistant chatbot. Goal: extract the 18 product-a.dk tool integrations from the Next.js app and deploy them as a standalone MCP server on AWS Bedrock AgentCore Runtime, keeping agent reasoning logic in place.

---

## What is MCP?

Model Context Protocol (MCP) is an open standard maintained by Anthropic for exposing tools as a standalone HTTP service that any AI agent or client can connect to. Tools live in their own container (an MCP server) and are called over HTTP. The agent connects, discovers available tools, and calls them as needed.

**Core benefit:** Separation of concerns — tools (how to talk to product-a.dk API) decoupled from agent (how to reason). They can be developed, deployed, and updated independently. Plug-and-play for AI capabilities: one standard connection replacing dozens of custom connectors.

---

## Layered Architecture (Separation of Concerns)

### Layer 1 — Auth & Security
- Validates identity (JWT/OAuth), enforces RBAC
- Central place for audit logging, rate limits, allow-lists
- Only verified/authorized requests reach the agent/tool layer

### Layer 2 — Agent Orchestration (reasoning layer)
- Routes requests to the right workflow/agent
- Plans multi-step tasks, manages tool-call order
- Owns conversation state and response formatting for UI (separate from tool execution)

### Layer 3 — MCP Server (tool transport + registry)
- Exposes a standard tool interface (MCP) over HTTP
- Registers tools, handles MCP protocol/transport
- Free of business/domain logic and free of agent reasoning

### Layer 4 — Agentic Tools (domain capabilities)
- Implements actual domain actions (invoices, quotes, customers, etc.)
- Encapsulates product-a.dk API calls, validation, domain-specific error handling
- Designed to be reusable across multiple clients and orchestration strategies

---

## Current Architecture (va-agents)

- **Framework**: Next.js app deployed on AWS ECS
- **Agent**: Google ADK with Gemini (via Google Vertex AI)
- **Tools**: 18 product-a.dk tool integrations live directly inside the Next.js app alongside agent logic
- **Session history**: PostgreSQL on AWS RDS
- **RAG**: AWS Bedrock Knowledge Base for product-a support documentation

---

## Proposed Architecture

Tools are extracted from the Next.js app and deployed as a standalone MCP server on AWS Bedrock AgentCore Runtime. The Next.js app becomes the MCP client — continues to handle agent reasoning and structured response formatting, but calls tools over HTTP.

### New: `product-a-mcp-server`
- Standalone container exposing all 18 product-a.dk tools as MCP endpoints
- Tools: invoices, quotes, customers, products, emails, invitations, support knowledge lookup
- No agent logic — only knows how to call product-a.dk API and return results
- Deployed to AWS Bedrock AgentCore Runtime (manages container lifecycle, auth, observability automatically)

### New: Amazon Cognito Authorizer
- AgentCore Runtime endpoint protected by Cognito JWT authorizer
- Next.js app authenticates with Cognito before calling MCP server
- Replaces implicit trust model of internal ECS service communication

### Deployment
- Defined in `.bedrock_agentcore.yaml` (single YAML config, not Jsonnet task definition)
- `bedrock-agentcore deploy` CLI: builds, pushes to ECR, provisions Runtime in one step

### Session State
- MCP server is stateless — no conversation history stored
- Session context managed by Next.js app; product-a organization token + context passed with each request
- PostgreSQL session tables can eventually be removed once client-side context management is confirmed

---

## What Stays the Same

| Component | Status |
|---|---|
| React frontend (product-a.dk iframe) | Unchanged |
| Agent reasoning logic (Google ADK + Gemini) | Unchanged |
| Rich structured output schema (forms, charts, nav buttons) | Unchanged |
| Bedrock Knowledge Base (support docs RAG) | Unchanged — becomes one of the MCP tools |
| product-a.dk API integration logic | Unchanged — moves into the MCP server |
| Feedback storage (PostgreSQL) | Unchanged |
| AWS ECR (container registry) | Unchanged |
| AWS region (eu-north-1) | Unchanged |

---

## Stack Overview

| Layer | Technology |
|---|---|
| Frontend | React 19, Next.js (unchanged) |
| Agent framework | Google ADK with Gemini, or optionally Anthropic SDK with Claude |
| MCP server SDK | `@modelcontextprotocol/sdk` (TypeScript, npm) |
| MCP runtime | AWS Bedrock AgentCore Runtime |
| Container registry | Amazon ECR |
| Authentication | Amazon Cognito (JWT authorizer) |
| Support knowledge | AWS Bedrock Knowledge Base (RAG) |
| Observability | Amazon CloudWatch + AWS X-Ray (auto-configured by AgentCore) |
| Feedback storage | PostgreSQL on Amazon RDS (unchanged) |
| Secrets | AWS Secrets Manager (unchanged) |

---

## Implementation Status

The va-agents toolset + MCP server have been migrated from TypeScript to Python in the **va-hypernova** repository: https://github.com/ageras-com/va-hypernova

Repo structure:
- **Tool layer**: product-a-facing domain tools (actual capabilities)
- **MCP layer**: MCP server/transport wrapper exposing those tools via MCP protocol

The TypeScript equivalent (`@modelcontextprotocol/sdk`) is the official Anthropic npm package providing the same tool-definition model in Node.js — no language change required if staying in TypeScript.

---

## Per-Organization Token Handling

Va-agents passes a different product-a API token per organization (sent as request header from product-a iframe). The proposed approach keeps this intact: Next.js app forwards the org token as a header when calling the MCP server via AgentCore. MCP server reads the token from request context and uses it to authorize product-a API calls. No credentials hardcoded or stored in the container.

---

## Observability

CloudWatch logging and X-Ray tracing are enabled automatically by AgentCore when `observability: enabled` is set in the deployment config. No application-level instrumentation code required. Every tool call is logged and traceable without changes to tool implementation.
