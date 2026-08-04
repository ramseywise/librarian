---
title: Agent Interoperability Protocol Stack
tags: [mcp, infra, concept]
summary: "The five open protocols standardizing agent integration — MCP for data, A2A for agent-to-agent, A2UI for generative UI, AP2 and UCP for machine-to-machine commerce — and why the layer exists at all."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--agents-google-adk.md
---

# Agent Interoperability Protocol Stack

Custom tool integrations are technical debt with a combinatorial growth rate: *N* agents
against *M* systems is *N×M* bespoke connectors, each independently maintained. The
interoperability protocols exist to make that *N+M*.

The framing worth keeping: these are the **industry standards** — the uniform screw sizes,
data formats, and communication channels — that let one team's machinery safely interact
with everyone else's. The claim attached to them is that software's next evolution *"isn't
written, it's orchestrated by interoperable agents."*

## The five protocols

| Protocol | Connects | Purpose |
|---|---|---|
| **MCP** (Model Context Protocol) | Model → data sources | Tool and resource access over a uniform schema |
| **A2A** (Agent2Agent) | Agent → agent | Cross-framework, cross-vendor task delegation |
| **A2UI** (Agent-to-User Interface) | Agent → UI | Generative UI — agents emitting structured interface, not just text |
| **AP2** (Agent Payments Protocol) | Agent → payment rail | Secure machine-to-machine payment authorization |
| **UCP** (Universal Commerce Protocol) | Agent → commerce system | Machine-to-machine commerce transactions |

They partition by **what sits on the other end of the boundary**, which is the useful way
to hold them: data (MCP), another agent (A2A), a human (A2UI), or money (AP2/UCP). An
agent architecture that reaches all four ends touches all five.

The maturity gradient is steep. MCP and A2A have real adoption and reference
implementations — [[MCP Protocol]] and [[A2A Agent Protocol]] cover them in depth. A2UI
appears in working systems ([[Multi-Agent Orchestration Patterns]] documents an A2UI MCP
translation layer). AP2 and UCP are the newest and least proven; treat them as direction
rather than as available infrastructure.

## MCP adoption notes

The practical guidance, ordered as encountered:

**Discovery — security is the first consideration, not a later one.** Public community
servers should not be passed credentials. Where an untrusted server must be used, put a
mediation layer in front of it (Google's Model Armor is the named example).

**Configuration checklist:**

1. Check prerequisites
2. Identify scope and access criteria
3. Include the specifications in the coding agent's context
4. Authentication

Step 2 is the one that carries weight — an MCP server's access criteria define the blast
radius of every tool call the agent subsequently makes, and it is far cheaper to scope at
configuration time than to constrain at call time. See
[[MCP Server Security Patterns]].

## Why this layer is separate from the harness

A harness constrains, informs, verifies, and corrects *one* agent
([[Harness Engineering]]). These protocols govern what happens at that agent's boundary
when the thing on the other side is not under the same control.

The distinction has a practical consequence: harness guarantees do not cross a protocol
boundary. A sandboxed, hook-guarded, rollback-capable agent that delegates a task over A2A
to a remote agent has just handed work to something with an unknown harness — which is
exactly why agent cards advertise capabilities and authentication schemes rather than
assuming them.

## See Also
- [[MCP Protocol]] — part-of (the data-access protocol, in depth)
- [[A2A Agent Protocol]] — part-of (the agent-to-agent protocol, in depth)
- [[MCP Server Security Patterns]] — extends (scoping and credential handling at the boundary)
- [[Harness Engineering]] — complements (single-agent control versus cross-boundary standards)
- [[Multi-Agent Orchestration Patterns]] — instance-of (A2UI applied in a working system)
