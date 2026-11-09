---
title: MemGPT / Letta Virtual Context Memory
tags: [memory, context-management, concept]
summary: "The LLM-as-operating-system memory design — the agent pages facts between a fixed in-context core block (RAM) and external archival/recall stores (disk) through its own tool calls, so it authors its context rather than just consuming it."
updated: 2026-11-08
sources:
  - data/raw/articles/2026-07-19-llms-as-os-agent-memory-letta.md
  - data/raw/papers/2026-11-07-packer-2023-memgpt.md
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

## The 2023 paper's design and results

In the original preprint (Packer et al., arXiv 2310.08560) the prompt has three parts: read-only system instructions, a working context the model can read and write, and a FIFO queue holding a recursive summary. Through function calls the model edits its memory and queries recall and archival stores (PostgreSQL with pgvector); a warning signals memory pressure and triggers a queue flush. A request_heartbeat flag allows several calls in a row before control goes back to the user. The authors add three tasks, deep memory retrieval, conversation openers and nested key-value retrieval, and release the data along with 20M Wikipedia embeddings. The models tested were GPT-4, GPT-4 Turbo and GPT-3.5 Turbo, each against fixed-context baselines.

Results (self-reported):

- Deep memory retrieval (sessions 1 to 5 of Multi-Session Chat, question in session 6, LLM judge): GPT-4 Turbo with MemGPT reached 93.4% accuracy against 35.3% for the baseline; GPT-3.5 Turbo 66.9% against 38.7%. ROUGE-L recall for GPT-4 rose from 0.296 to 0.814.
- Nested key-value retrieval (140 UUID pairs, about 8k tokens, levels 0 to 4, 30 orderings): the GPT-3.5 baseline hit 0% accuracy at a single nesting level, with GPT-4 and GPT-4 Turbo hitting it by three. MemGPT on GPT-4 showed no effect from nesting (read from a figure), while on GPT-4 Turbo and GPT-3.5 it fell off at two levels.
- Document QA (50 NaturalQuestions-Open questions, up to about 200 documents): the baseline's accuracy stays bounded by the retriever, whereas MemGPT is not affected by retrieving more documents. No accuracies are printed, only a figure, and GPT-3.5 degraded significantly from weak function calling.

## Limits

- No variance, seeds or significance tests, and document QA uses only 50 questions.
- The deep memory retrieval baselines are given only a lossy summary of earlier sessions, whereas MemGPT can search the entire history; the authors state this, and it makes the comparison uneven.
- MemGPT frequently quits paging before the retriever's results run out, and results hinge on function-calling ability. Neither the judge model nor the decoding settings are given.
- Only fixed-context baselines are compared; there is no retrieval-with-paging or other memory system. The context-length table is dated January 2024.

## See Also
- [[Agent Memory Types]] — extends (the taxonomy this architecture instantiates)
- [[Memory as Context]] — instance-of (write/select levers applied by the agent itself)
- [[Identity Memory: Revision vs Accretion]] — related (what a self-editable core block does to identity over time)
- [[LangGraph BaseStore]] — alternative-to (namespace store + post-session consolidation)
- [[Memory Store Operations]] — related
- [[Multi-Writer Agent Memory Systems Comparison]] — extends (Letta's agent-scoped model against shared multi-writer stores)
- [[Memory Architecture]] — prerequisite-for
- [[AIOS]] — related (an OS kernel view of agent memory and scheduling)
- [[JAZ Invoke Loop]] — alternative-to (history searched by code instead of a memory store; compared against Letta)
- [[Agent S Hierarchical GUI Agent]] — alternative-to
