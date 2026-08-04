---
title: Memory-Augmented Conversational RAG
tags: [rag, memory, llm, pattern]
summary: "Multi-turn retrieval breaks because the query is under-specified — the fixes are query rewriting against history, a when-to-retrieve policy, and asking a clarifying question instead of retrieving on an ambiguous turn."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
---

# Memory-Augmented Conversational RAG

Standard RAG assumes a **self-contained query**. Conversational RAG does not get one. This
is the multi-turn case of stage C in [[Memory Lifecycle]], and the failure is specific:

> "What about the second one?" retrieves nothing useful, because the embedding of that
> string is not near anything in the index.

Three distinct fixes, addressing three distinct failures.

## 1. History-aware query rewriting

Rewrite the user's turn into a standalone query using conversation history *before*
embedding it. `"What about the second one?"` → `"What are the side effects of
metformin?"` — the rewritten query is what hits the retriever.

**CONQRR** is the notable implementation: a query-rewriting model trained with
**reinforcement learning against retrieval performance directly**, rather than against
human-written rewrites.

> That objective choice is the interesting part. Supervised rewriting optimizes for
> *looking like* a good rewrite; RL against retrieval optimizes for *retrieving the right
> documents*, which is what you actually wanted. Rewrites that read awkwardly but retrieve
> well are correct answers under the second objective and errors under the first.

## 2. A when-to-retrieve policy

Not every turn needs retrieval. `"thanks!"` and `"can you rephrase that?"` should not hit
the index — retrieval on a conversational turn injects irrelevant context and can actively
derail the response.

The decision is a **policy, not a default**: retrieve when the turn introduces new
informational need; skip when it is meta, social, or answerable from what is already in
context. This is the same discipline as the tool-call gating in
[[Execution Boundaries and Guardrails]] — an always-on retriever is an ungated tool.

## 3. Mixed-initiative clarification

When the query is genuinely ambiguous, the correct move is to **ask** rather than to
retrieve on a guess.

> Retrieving on an ambiguous query produces a confident answer to a question the user
> didn't ask, which is worse than a clarifying question — the user has no signal that the
> system misread them.

This is the retrieval-layer instance of the general principle that **an agent uncertain
about intent should surface the uncertainty rather than resolve it silently.**

## Azure agentic retrieval

The shipped form of all three: the agent **decomposes a complex query into focused
subqueries**, runs them in parallel, and merges the results — while using conversation
history to determine what each subquery should actually be.

Decomposition is the natural extension of rewriting: rewriting produces one standalone
query, decomposition produces several. See [[Knowledge Graph Retrieval]] for why multi-hop
questions are the ones that need this, and [[Send API Fan-out]] for the parallel-execution
mechanism.

## Benchmarks

Conversational retrieval has its own evaluation set, distinct from single-turn RAG
benchmarks:

| Benchmark | Focus |
|---|---|
| **CAsT** (TREC) | Conversational search, multi-turn |
| **QReCC** | Question rewriting in conversational context |
| **TopiOCQA** | Topic-switching conversational QA |
| **CORAL** | Conversational RAG |
| **mtRAG** | Multi-turn RAG |
| **InSCIt** | Mixed-initiative, clarification-seeking |
| **OR-ShARC** | Open-retrieval conversational reading comprehension |

Note that **InSCIt exists specifically to score clarification behavior** — evidence that
asking-instead-of-guessing is treated as a measurable capability, not a UX preference. If
you build fix #3, that is the benchmark shape to evaluate it against.

## See Also
- [[Memory Lifecycle]] — extends (stage C in the multi-turn case)
- [[RAG Retrieval Strategies]] — extends (adds the conversational-query problem)
- [[Agent Memory Types]] — complements (history is the rewriting input)
- [[Knowledge Graph Retrieval]] — complements (multi-hop questions need decomposition)
- [[Execution Boundaries and Guardrails]] — complements (retrieval as a gated tool call)
