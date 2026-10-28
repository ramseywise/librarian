---
title: Stub Backend Is Permanent Dev Infrastructure
tags: [patterns, infra, pattern]
summary: "Treat the tool interface as the dev/prod seam: the stub backend behind it (a seeded MCP server over SQLite) is permanent dev, CI and staging infrastructure, not a placeholder to replace later; production is a second implementation of the same signatures, and a \"replace stubs with the real API\" phase is a planning error."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/plans/va-agent-improvements.md
  - data/raw/claude-docs/playground/docs/plans/va-infra.md
  - data/raw/claude-docs/playground/docs/plans/va-agent-systems.md
---

# Stub Backend Is Permanent Dev Infrastructure

From the playground repo's virtual-assistant plans (2026-04). The VA ran on two runtimes
(ADK and LangGraph) against an accounting product's data. A revised plan corrected an
earlier build order, and that correction is the learning.

## The correction

The earlier plan had a final phase called "replace stubs with real API". The revision
called that phase **wrong**. The tool layer is the abstraction boundary: function
signatures and docstrings never change, and only the backend that executes them does.

```
Tool interface (signatures + docstrings)
        |                              |
  Dev / CI / staging              Production
  MCP stub server                 thin httpx wrapper over the real REST API
  (FastMCP -> seeded SQLite)      (OAuth token from session, org id per request)
```

- **The stub is never deleted.** It keeps serving tests (110 of them already passed
  against it), CI, local development and demos after production exists. It is seeded
  and persistent, and a reset script reloads the full fixture.
- **Production is a separate implementation of the same interface.** An env var selects
  it (`<PRODUCT>_BACKEND=api`), and it gets built once real API access exists. It does
  not block dev work.
- Calling the stub a "placeholder" makes it look like debt and starves it of
  maintenance. Calling it infrastructure keeps its fixtures realistic.

The stub's contract still has to match production's wire shape. A stub that drifts
reproduces the problem in [[A Fake That Conforms to a Broken Seam]]: tests go green
against a seam the real adapter does not honour.

## The companion decision: runtime is a library, MCP is only tools

The infra plan separated two questions that often get merged:

| Layer | Decision | Why |
|---|---|---|
| Gateway + agent runtime | FastAPI **in-process** with the ADK or LangGraph runner. One image, and a `VA_BACKEND` env var picks the runtime | No network hop on the streaming path. The agent runtime is a library import, not a microservice |
| Tools | MCP server as a **separate container** | Stable signatures and a swappable backend (the stub above) |

MCP is strictly the tool layer. The gateway calls it for data, never for orchestration.
Both runtimes sit behind the same gateway contract and share one structured
`AssistantResponse` schema and SSE event types, so the frontend doesn't care which
runtime answered.

## SSE through a load balancer

Getting streaming right through an AWS ALB took three settings. Set them in Terraform
before the first deploy:

- `idle_timeout` above the longest expected SSE turn (300s here).
- Sticky sessions (`lb_cookie`) for session affinity.
- An `X-Accel-Buffering: no` response header so proxies flush events instead of
  buffering them. Check that uvicorn flushes.

HTTP/1.1 keep-alive is enough for SSE, so no NLB is needed. WebSocket voice is a
different matter and needs NLB or upgrade support.

## See Also
- [[A Fake That Conforms to a Broken Seam]] — related (what goes wrong when the stub's shape drifts from production)
- [[Stated Seams Drift, Enforced Seams Hold]] — extends (the tool interface is a seam worth enforcing)
- [[VA Eval Harness]] — related (evals run against these runtimes and the stub backend)
- [[Streaming Output Scrubbing]] — related (the other half of shipping SSE responses)
