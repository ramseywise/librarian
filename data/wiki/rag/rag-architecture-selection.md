---
title: RAG Architecture Selection
tags: [rag, comparison]
summary: "The nine named RAG architectures as one selection space — what each buys, what it costs, and the decision cheat-sheet — plus Fusion RAG over heterogeneous sources, which is distinct from multi-query RAG-Fusion over one retriever."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--02-rag-retrieval--rag.md
---

# RAG Architecture Selection

The named RAG architectures are usually presented as a menu, which invites the wrong
question — *which one is best?* They are better read as **a baseline plus eight
modifications**, each buying one specific property at a specific cost. Nothing here
replaces standard RAG; each variant adds machinery to fix a failure mode standard RAG has.

**The recommended adoption path is deliberately conservative:** implement standard RAG as
the baseline, then prototype **exactly one** additional pattern against it, and A/B test to
confirm the lift is real. Stacking patterns before measuring is how a pipeline acquires
latency and cost it cannot justify.

## The nine, by what they change

| # | Architecture | Changes | Buys | Costs |
|---|---|---|---|---|
| 1 | **Standard RAG** | — | Baseline: retrieve top-k → inject → generate | — |
| 2 | **Conversational RAG** | Query, pre-retrieval | Multi-turn coherence via dialogue state + query condensation | Condensation call; state management |
| 3 | **Corrective RAG (CRAG)** | Post-generation | Evidence-backed answers, fewer factual errors | Higher latency and cost |
| 4 | **Adaptive RAG** | Routing | Speed on simple queries, depth where it matters | Intent classifier; routing must stay auditable |
| 5 | **Self-RAG** | Query generation | Handles vague input and heavy paraphrasing | Model-invented queries unless constrained |
| 6 | **Fusion RAG** | Source breadth | Evidence from vectors + web + DBs in one answer | Merge/rerank complexity; provenance tracking |
| 7 | **HyDE** | Pre-retrieval embedding | Large recall lift on vague queries vs dense docs | One extra LLM call before retrieval |
| 8 | **Agentic RAG** | Control flow | Retrieval as a tool in a planner/executor/verifier loop | Full agent-loop cost and failure surface |
| 9 | **GraphRAG** | Retrieval substrate | Multi-hop, entity-driven, traceable provenance | Entity-linking accuracy; graph maintenance |

Depth on most of these lives elsewhere: see [[Agentic RAG — Advanced Patterns]] for
Self-RAG, Adaptive, GraphRAG, and HyDE mechanics, [[CRAG Retry Logic]] for the corrective
loop, and [[Memory-Augmented Conversational RAG]] for the conversational variant.

Note that they modify **different stages**, which is why several compose cleanly — HyDE is a
pre-retrieval embedding trick and CRAG is a post-generation check, so running both is
coherent. Two that modify the *same* stage generally do not compose: Adaptive and Agentic
both own control flow, and running both means two routing authorities disagreeing.

## Decision cheat-sheet

| If | Reach for |
|---|---|
| Accuracy is critical | CRAG or GraphRAG |
| Workload is conversational | Conversational RAG + condensation |
| Workload is mixed | Adaptive or Fusion |
| Queries are paraphrase-heavy / docs are sparse | HyDE or Self-RAG |
| The product is automation, not Q&A | Agentic RAG |

The rows split on **what is unreliable**, not on what sounds sophisticated. Accuracy
problems get verification (CRAG, GraphRAG); vocabulary-mismatch problems get query-side
work (HyDE, Self-RAG); mixed-workload problems get routing (Adaptive, Fusion). Diagnosing
which of the three you have is the actual decision — the architecture follows from it. That
diagnosis is what the component gates in [[RAG Evaluation]] produce.

## Fusion RAG — one synthesizer, several retrievers

Fusion RAG pulls evidence from **structurally different sources** — a vector store, a web
search API, and a SQL database — then merges, reranks, and synthesizes a single answer with
**provenance labels** identifying which source each claim came from.

```
vector search ─┐
web API ───────┼─→ merge → rerank → LLM synthesize (with provenance)
SQL query ─────┘
```

**Use when** breadth of sources matters — enterprise settings where the answer legitimately
requires internal docs *and* live web *and* structured records.

### Not the same as multi-query RAG-Fusion

The naming collision is worth stating plainly, because the two are frequently conflated:

| | Varies | Merges |
|---|---|---|
| **Multi-query RAG-Fusion** | The *query* — N phrasings of one question | N ranked lists from **one** retriever |
| **Fusion RAG** (this pattern) | The *source* — vector, web, SQL | Ranked lists from **heterogeneous** retrievers |

Multi-query fusion is a recall technique against a single corpus, documented in
[[Agentic RAG — Advanced Patterns]]. Fusion RAG is an architecture for answering from
several corpora at once. They can be used together.

The harder problem is the merge. Multi-query fusion merges lists that are at least
commensurable — same retriever, same scoring. Fusion RAG merges lists whose scores mean
entirely different things: a vector cosine similarity, a web-search relevance rank, and a
SQL result that either matched or did not. **Rank-based fusion is the way out** — it uses
only position and is therefore scale-invariant, which is exactly the problem
[[Reciprocal Rank Fusion (RRF)]] was designed for.

Provenance labelling is not decoration here. When sources have different trust levels — an
internal policy document versus a web result — an answer that blends them without saying
which is which has destroyed the reader's ability to weigh it.

## Production checklist

Applies to any of the nine once it ships:

- **Semantic chunking with overlap**, sized within prompt-window limits — see
  [[RAG Knowledge Preparation]]
- **Cross-encoder reranker** over top-N retrieval results — see [[RAG Reranking]]
- **Incremental embedding refresh** for sources that change
- **Caching** for high-frequency and repeat queries — see [[Semantic Cache for RAG Agents]]
- **Token-budget enforcement**, with summarization for long contexts
- **Snapshot, backup, and rebuild plan** for the vector database
- **PII redaction and access controls** for private data
- **Human-in-the-loop review** for flagged outputs, feeding back into re-indexing

The refresh and rebuild items are the ones most often skipped, and they are infrastructure
rather than ML: an index is a build artifact with no natural expiry signal, so nothing fails
loudly when it goes stale. HyDE makes this sharper — its generated entries must be
regenerated whenever the model **or** the source documents change, or retrieval is running
against a hypothesis the current model would no longer produce.

## Monitoring

| Metric | What it catches |
|---|---|
| **Hallucination rate** | % of answers with ≥1 false claim (manual + automated) |
| **Precision@k / Recall@k** | Retrieval quality, independent of generation |
| **Latency p95** | UX viability |
| **Cost per query** | Tokens + API charges |
| **User trust score** | Human-review pass rate or NPS |
| **Claim-level accuracy** | CRAG systems specifically |

The pairing that matters is hallucination rate against precision@k: **a bad answer with good
retrieval and a bad answer with bad retrieval need opposite fixes**, and a single
end-to-end quality score cannot tell them apart. See [[RAG Evaluation]] and
[[RAG Eval Gate Contract]].

## See Also
- [[Agentic RAG — Advanced Patterns]] — extends (mechanics for Self-RAG, Adaptive, GraphRAG, HyDE, multi-query fusion)
- [[Reciprocal Rank Fusion (RRF)]] — depends-on (the scale-invariant merge Fusion RAG requires)
- [[RAG Evaluation]] — prerequisite-for (component gates produce the diagnosis that selects an architecture)
- [[CRAG Retry Logic]] — instance-of (the corrective variant, in depth)
- [[RAG Retrieval Strategies]] — complements (retrieval-layer choices within any of these architectures)
- [[Memory-Augmented Conversational RAG]] — instance-of (the conversational variant, in depth)
