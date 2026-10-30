---
title: MemGPT / Letta Virtual Context Memory
tags: [memory, context-management, concept]
summary: "The LLM-as-operating-system memory design — the agent pages facts between a fixed in-context core block (RAM) and external archival/recall stores (disk) through its own tool calls, so it authors its context rather than just consuming it."
updated: 2026-10-30
sources:
  - data/raw/articles/2026-07-19-llms-as-os-agent-memory-letta.md
---

# MemGPT / Letta Virtual Context Memory

The MemGPT thesis (productised as Letta): treat the fixed context window like RAM and
external storage like disk, and let the **agent itself** do the paging. The model decides
what to move into and out of its own window, the way an OS pages virtual memory.

## Three tiers

| Tier | Analogy | Contents | Access |
|---|---|---|---|
| **Core memory** | RAM / scratchpad | Fixed-size key-value blocks (persona, user facts), always in context | Agent rewrites it with an edit tool |
| **Archival memory** | Disk | External vector store of long-term facts | Agent calls a search tool on demand |
| **Recall memory** | Swap / history | Conversation history, rolling-summarised | Searched or summarised back in |

This maps onto the semantic / episodic split in [[Agent Memory Types]]: core ≈ working
semantic facts, recall ≈ episodic, archival ≈ long-term semantic.

## The two non-obvious primitives

- **Self-editing memory.** The agent calls something like
  `memory_edit("core_memory", key, value)` to update its own beliefs. It modifies its
  *context*, not just its outputs — which is what lets behaviour adapt across a long
  conversation without a human re-seeding the prompt. (The revision-vs-accretion
  consequences of a self-editable persona block are covered in
  [[Identity Memory: Revision vs Accretion]].)
- **Retrieval as explicit tool use.** `search_archival_memory(query)` is a tool the agent
  chooses to call, with a query it forms itself. Retrieval is triggered by the agent's own
  reasoning about what it does not know, rather than passively on every turn — the same
  agentic-retrieval stance as the Self-RAG `[Retrieve]` decision.

## Shared memory blocks between agents

Agents can read and write each other's core blocks, so a supervisor can update a
subagent's beliefs without a message exchange. Cheaper than structured messages for
state synchronisation, but it is shared mutable state: concurrent writes need
coordination, and the coupling is implicit — the failure mode called out for hybrid
multi-framework systems in [[Framework Selection — LangChain vs LangGraph vs Deep Agents]].

## Relationship to LangGraph

The LangGraph equivalent is a [[LangGraph BaseStore]] namespace holding the "core" facts,
loaded into the prompt at turn start, plus memory-write tools (langmem) — with background
consolidation after the conversation instead of in-turn paging. The Letta version puts the
paging decision inside the agent loop; the LangGraph version usually puts extraction in a
post-session job so live latency is unaffected.

## See Also
- [[Agent Memory Types]] — extends (the taxonomy this architecture instantiates)
- [[Memory as Context]] — instance-of (write/select levers applied by the agent itself)
- [[Identity Memory: Revision vs Accretion]] — related (what a self-editable core block does to identity over time)
- [[LangGraph BaseStore]] — alternative-to (namespace store + post-session consolidation)
- [[Memory Store Operations]] — related
- [[Multi-Writer Agent Memory Systems Comparison]] — extends (Letta's agent-scoped model against shared multi-writer stores)
- [[Memory Architecture for VA Agents]] — prerequisite-for
