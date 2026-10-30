---
title: Index-Time Distillation
tags: [context, rag, pattern]
summary: "Naive chunk-and-retrieve fails on aggregation and rule-induction questions however good the retriever, because attention is soft retrieval, not a summariser — spend compute at index time to turn cases into statistics, rules and hierarchy (RAPTOR, GraphRAG, L0/L1/L2 filesystem tiers, factor discovery)."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
---

# Index-Time Distillation

The [[Agent Status Bar]] idea — *distill, don't retrieve* — applied to a corpus. Instead of
indexing raw documents and hoping retrieval assembles an answer, precompute the
conclusions the questions will need.

## Two Question Shapes Naive RAG Cannot Answer

- **Aggregation.** 100 case files, 90 of one class and 10 of another; ask for the ratio.
  Top-k truncation, uneven scores and the basic mismatch ("count across everything" vs
  "find the few most relevant") leave the model reasoning from a sample of ~18. One
  indexed summary ("100 cases: 90 A (90%), 10 B") answers it in a single retrieval.
- **Rule induction.** Three cases: two professions granted a discount, a third refused. A
  fourth profession asks. Its embedding sits near one granted case, the refusal is
  missed, and the model concludes it qualifies. The indexed *rule* ("discount for X and Y
  only") answers every profession.

**Attention is soft retrieval, not a summariser.** No retriever improvement fixes these;
the corpus must be pre-digested.

## Structures

| Structure | Built by | Answers | Caveat |
|---|---|---|---|
| **RAPTOR** | Cluster leaf chunks, summarise each cluster as a parent, recurse to a root | Drill-down from concept to detail at any abstraction level | Up-front LLM cost |
| **GraphRAG** | LLM-extracted entities/relations, community detection, community summaries | Multi-hop and disambiguation (two people with the same name are two nodes) | Triples lose conditions ("if it rains, cancel X and do Y"); use as an index *alongside* natural-language text, not instead of it. See [[Knowledge Graph Retrieval]] |
| **Filesystem tiers** | Each resource gets L0 (~100-token abstract), L1 (~2k overview), L2 (full text), with per-directory abstracts | Navigation; most queries resolve at L1 | Progressive disclosure for a corpus. Needs wiki-style cross-links and index pages — weaker models append orphan files unless the writing prompt requires linking and index updates |
| **Knowledge discovery** | Extract a schema per case, cluster into prototypes, rank the factors | "What decides outcomes here?" | Ranked factors also tell the agent which questions to ask, in order |

**When to use it:** if questions are "find the passage that says X", hybrid retrieval is
enough ([[Context Retrieval Strategies]]). If they need cross-document synthesis or
multi-level navigation, structured indexing is worth its large up-front LLM cost.

The filesystem-tiers row is the shape of the [[Karpathy LLM Wiki Pattern]] — and its
orphan-file failure is why this wiki's ingest protocol blocks on missing backlinks.

## See Also
- [[Agent Status Bar]] — extends (distill-don't-retrieve, at corpus scale)
- [[Context Retrieval Strategies]] — extends
- [[Knowledge Graph Retrieval]] — instance-of (the GraphRAG row)
- [[RAG Architecture Selection]] — extends
- [[Contextual Retrieval]] — alternative-to (enrich each chunk rather than add summary levels)
