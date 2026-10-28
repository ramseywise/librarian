---
title: Provenance-Tracked Agent Beliefs
tags: [mcp, memory, pattern]
summary: "A design proposal for agent-to-agent knowledge exchange — every belief carries its source and contradictions, each agent keeps a PeerModel of what others know, and a compressed AttentionBrief is the default message so full provenance stays in an external store until a reasoning step needs it."
updated: 2026-10-17
sources:
  - data/raw/playground-docs/2026-07-13-puffin-multiagent-knowledge-schema.md
  - data/raw/playground-docs/2026-07-13-puffin-agentic-protocols-general-vs-specific.md
---

# Provenance-Tracked Agent Beliefs

*Status: working design (playground, 2026-07), not yet built or measured.*

Most A2A protocols treat knowledge transfer as message passing: the receiver learns
*what* the sender believes but not *why*. This proposal applies the wiki's own ingest rule
to agent communication — every belief has a source, contradictions are flagged and never
silently overwritten, and knowledge received from another agent is tracked as such.

## Schema

- **Belief** — `content`, `confidence`, `timestamp`, plus `source`, `contradicts: [belief_id]`
  and `derived_from: [belief_id]`.
- **Source** — `type ∈ {observation, agent_message, inference, tool_result}`, `agent_id`
  (if received from a peer), `task_id`, `step`.
- **PeerModel** — agent A's model of agent B: the beliefs and capabilities A thinks B has,
  `last_synced`, and a `confidence` in that model's currency. Theory of mind as data.
- **MetaState** — the agent's model of itself: known gaps, uncertain beliefs, stale
  beliefs, and an attention budget splitting context into high-value vs compressible.

## Message types (general layer)

| Message | Use |
|---|---|
| `AttentionBrief` | **Default.** Compressed state slice optimised for what the receiver needs |
| `KnowledgePush` | Beliefs + full provenance — only when the source chain matters to the receiver's reasoning |
| `BeliefCorrection` | "I told you X, now believe Y — here's why"; always carries the reason |
| `TaskHandoff` | Subtask + scoped context slice, not full state |
| `CapabilityNegotiation` | "Can you handle X?" before delegating — prevents bad handoffs |
| `ScopeNegotiation` | "I take A–C, you take D–E" — prevents duplicate work |
| `FailurePropagation` | "I tried X and it failed, because…" — closes feedback loops |
| `ObservationSharing` | Raw observations before they become beliefs (grounding layer) |
| `PeerModelSync` / `BeliefQuery` | Check or pull another agent's state before a decision that depends on it |

## The load-bearing trade-off

Full provenance is expensive in tokens. The resolution is a split: `AttentionBrief`
carries most traffic, full belief chains live in an **external provenance store**, and an
agent pulls from the store only when provenance actually changes the reasoning step. The
store is shared transport; domain protocols decide what is stored, not how it moves.

## Domain layers on top

Repo-specific protocols specialise the general layer without changing transport:

- **Knowledge-graph enrichment** (music recommender): typed-edge proposals, and a
  `GraphConflict` message when two agents disagree on an edge type. Two similarity signals
  from different sources (listener behaviour vs musical structure) are stored side by side
  with their source rather than merged — the disagreement is itself useful output.
- **Multi-agent wiki compilation**: `DomainClaim`, `WikiPageProposal` (passes a
  contradiction check before merge), `ContradictionFlag`, `OrphanAlert`. The policy here
  is explicitly *flag, don't auto-resolve* — a human stays in the loop.
- **Phase pipelines** (research → plan → execute → review): `PhaseHandoff` records what
  was decided and assumed, and `ContractCheck` verifies invariants at each phase boundary
  rather than only at commit time.

## Open questions recorded with the design

- Who arbitrates contradictions — the receiver, an orchestrator, or voting agents?
- How does a `DomainClaim` expire if the claiming agent goes offline?
- PeerModel drifts as the peer acts; how is that uncertainty represented (probabilities, not
  just "B knows X")?
- What granularity should an `AttentionBrief` have, and how does it map onto LangGraph
  checkpoints?

## See Also
- [[Protocol-Driven Multi-Agent Collaboration]] — extends (adds belief provenance to the protocol's message layer)
- [[A2A Agent Protocol]] — complements (transport and task lifecycle this sits above)
- [[Knowledge Graph as Shared Agent Memory]] — alternative-to (shared store instead of per-agent belief state)
- [[Karpathy LLM Wiki Pattern]] — instance-of (flag-not-overwrite contradiction policy applied to agents)
- [[Multi-Agent Context]] — complements (scoped context slices on handoff)
