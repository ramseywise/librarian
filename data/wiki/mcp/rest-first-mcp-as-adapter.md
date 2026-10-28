---
title: REST-First, MCP as Adapter
tags: [mcp, infra, decision]
summary: "Decision for a project scaffold: versioned REST is the standard service boundary, MCP servers are thin adapters over it containing no business logic and scaffolded only when an MCP host is an actual consumer, and a sidecar is a deploy-time transport detail — never the default."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-template-core-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-template-core-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-12-puffin-integration.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-12-puffin-integration.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/datathon_mcp/CLAUDE.md
  - data/raw/repos/datathon_mcp/README.md
---

# REST-First, MCP as Adapter

**Context.** The ai-project-template had to answer "REST vs sidecar vs MCP — which is
the standard?" while MCP was defaulting on for every agent-shaped project via a seeded
`agent_tools=[mcp]`.

**Decision.** Versioned REST is the service boundary. MCP is an adapter over it. A
sidecar is a deployment detail.

- Every long-running component exposes an app factory, `/health`, and `/api/v1/*`. REST
  is testable (pytest + httpx), observable, and already carries the auth story.
- **MCP servers contain no business logic.** Each tool is a thin client of a REST
  endpoint — the existing `search_articles` tool → `/api/v1/retrieval` behind
  `RAG_AGENT_URL` was the one place the template already did this, and it became the
  pattern to generalize. Protocol churn is isolated in one adapter layer; there is one
  surface to test and secure.
- **When to ship MCP:** the project *is* an MCP server, or the user declares an MCP host
  consumer (Claude Code/Desktop, an agent whose tools include `mcp`). Otherwise off.
- **Transport:** stdio for local/dev-tool hosts; streamable HTTP only when a hosted
  platform requires it — the only case resembling a sidecar, chosen at deploy time.

In the scaffold's DESIGN.md this ships as a pre-seeded Key Decision row, `Service
surface — Deferred(first external consumer identified)`, with the REST default recorded
(see [[Deferred Decision Status]]).

## Tradeoffs and supporting evidence

- **Server-side fidelity vs client demonstration.** An earlier integration kept the
  retrieval service as the thing the MCP server wraps over HTTP (server side), and
  demonstrated the *client* side — the part neither source repo had — in the two agents
  a user is most likely to copy: LangChain's `MultiServerMCPClient` and ADK's native
  `MCPToolset`, each using the framework's own library rather than custom protocol code.
- **MCP tools are JSON-schema-native.** `langchain-mcp-adapters` exposes `args_schema` as
  a plain JSON-schema dict, not a pydantic model — pass it straight into Anthropic's
  `input_schema`. Assuming pydantic and calling `.model_json_schema()` was caught only by
  testing against a live server.
- **Async ripple.** Adding a real tool-use loop made the generate node `async`, which
  forced `graph.invoke` → `await graph.ainvoke` in the FastAPI handler; the sync call
  does not run async nodes inside an already-running loop. Loop intermediates stayed
  local to the node, so graph state needed no change.
- **The same seam keeps backends swappable.** Every per-cloud retrieval implementation
  sits behind one factory with one return shape (`similarity_search(query, k) → [(id,
  title, text, score)]`); callers import the factory, never a backend, so swapping clouds
  is a flag, not an agent rewrite.
- **Same shape with a core library instead of REST.** A read-only data-pool prototype
  (datathon_mcp) puts every rule in one core API: validation, pagination caps, small-cell
  suppression and text sanitizing. MCP and REST are both thin facades that only translate
  transport. Adding a tool means one core method, one thin wrapper per facade, and a test.
  Tool errors list the valid values, so the calling model can self-correct
  (see [[Tool Design as Context Engineering]]).

## See Also
- [[MCP Protocol]] — prerequisite-for
- [[Tool Design as Context Engineering]] — related
- [[MCP Server Security Patterns]] — extends (one adapter surface to secure)
- [[Callable-By Integration Contract]] — related (the same "plain HTTP endpoint is the unit" stance for external services)
- [[Circular Core Justification]] — extends (why MCP stopped defaulting on)
- [[Deferred Decision Status]] — instance-of (shipped as a deferred decision row)
- [[Proxy Schema Overfits the Guess]] — related (schema failure in the same core-plus-facades prototype)
