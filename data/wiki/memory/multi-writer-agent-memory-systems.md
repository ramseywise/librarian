---
title: Multi-Writer Agent Memory Systems Comparison
tags: [memory, comparison]
summary: "Off-the-shelf agent memory layers compared on the question single-user surveys skip: can several people and agents write to one store safely? Scoping keys are not authorization, and multi-user modes are often opt-in."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_memory-survey.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_tencentdb.md
---

# Multi-Writer Agent Memory Systems Comparison

Most memory-layer comparisons assume one user and one agent. When the requirement is a
**team** store (several humans, several agents, one shared body of knowledge, and some
private slices), the deciding questions change. Who scopes a write? Who authorizes a read?
What happens when the isolation switch is left off? This page records a build-vs-adopt
survey run against exactly that requirement, at zero budget. Versions and pricing are as of
mid-2026 and will drift.

## The comparison

| System | Scoping model | Multi-writer? | Ops weight | Watch out for |
|---|---|---|---|---|
| **Letta** ([[MemGPT / Letta Virtual Context Memory]]) | Per **agent**. Each agent owns an isolated store. | No. "Multi-agent" means parallel agents with *separate* memories. Git-backed context repositories coordinate subagents of one agent, not separate people. | Moderate (Postgres + pgvector, Docker) | Shared-state coordination has to be built outside it |
| **Mem0** | Per **key**: `user_id`, `agent_id`, `run_id`, `app_id` filter every read and write | Yes, *if the app injects the key* | Low (FastAPI + Postgres, optional graph DB) | **No authentication or authorization.** The keys are filters, not security. A caller that can choose its `user_id` can read anyone's memory. |
| **Cognee** | Per **dataset**, with read/write/delete/share permissions | Yes, natively. Several agents can write one shared graph through MCP. | Low (embedded SQLite + LanceDB + Kuzu by default, Postgres for multi-process) | **Multi-user mode is opt-in.** If you forget to enable it, every user shares one space. |
| **Zep / Graphiti** | Per **`group_id`**: one team, one graph | Within a group, yes. Isolation between groups means a separate graph instance each. | High. You run a graph database (Neo4j/FalkorDB/Kuzu) and its backups. | Community edition is deprecated. The self-host image lagged releases. The hosted free tier only fits testing. |
| **Layered memory service** (L0 raw → L3 persona; chat, skill, wiki and code-graph assets) | Per **asset**, with private/team/restricted ACL, private by default | Yes. The asset-level ACL is the multi-writer primitive. | Moderate. Extraction needs an LLM API on every write. | Retrieval is BM25 + vector + RRF (k=60) with a small recall budget (5 items, 5 s timeout). Architecture comparison: [[Compiled-Prose KB vs Graph-Native Store]]. |

## Lessons that generalize

- **A scoping key is not an auth boundary.** `user_id`-style scoping only isolates when
  something *outside* the memory layer derives the key from an authenticated identity. Treat
  every key-scoped store as "trusted callers only" until the app layer binds key to session.
  This is the memory-store version of application-layer tenancy in
  [[ACL-Aware Retrieval and Tenant Isolation]].
- **Check the default, not the feature list.** "Supports multi-user" and "is multi-user
  out of the box" differ. Search results and summary docs both blurred the two. Only the
  mode's own doc page said it was optional. Test isolation by writing as user A and reading
  as user B before trusting it.
- **Private-by-default is the safe ACL default** for a mixed store. Anything shared is then
  an explicit act, and the failure mode is "teammate can't see it", not "client data leaked".
- **Agent-scoped memory answers a different question.** Letta-style isolation suits one
  long-lived coding agent and has no answer for "two people edited the same fact".
- **Graph-per-tenant scales in ops, not just storage.** One graph instance per team
  multiplies backups and schema migrations by the number of teams.

## See Also
- [[MemGPT / Letta Virtual Context Memory]] — extends (Letta's agent-scoped model compared against shared stores)
- [[Agent Memory Types]] — extends (which memory types a shared team store must hold)
- [[ACL-Aware Retrieval and Tenant Isolation]] — prerequisite-for (enforcement layers that key-scoped memory still needs)
- [[Compiled-Prose KB vs Graph-Native Store]] — alternative-to (compiled wiki instead of a memory service)
