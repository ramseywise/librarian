---
imported_hash: 1cdd26069c5fe8a8
title: Design a Document Q&A / RAG system for 10M+ articles
summary: rag-10m-walkthrough · ai-system-design · hard
order: 99
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/rag-10m.md
---

# Design a Document Q&A / RAG system for 10M+ articles

`rag-10m-walkthrough` · ai-system-design · hard

## 1. clarify

**Interviewer:** What do you ask before designing anything? Frame users, scale, freshness, quality bar, and guardrails.

<details><summary>Reference</summary>

Don't jump to a solution. Clarify first (the #1 interview mistake). Ask:
(1) Users & use case: internal employees or public? factual lookup or open-ended
synthesis? Is a cited, grounded answer required (yes for a knowledge base)?
(2) Scale: 10M articles is roughly 10s of millions of chunks after chunking,
~50 QPS peak. How fast does the corpus grow? (3) Freshness: new articles
answerable within minutes means near-real-time indexing, not a nightly batch.
(4) Quality/NFRs: grounding/faithfulness bar, p95 latency (few seconds), and a
cost-per-query budget. (5) Guardrails: access control (can every user see every
article?), PII, prompt injection, and the behavior when nothing relevant is
retrieved. State assumptions and confirm before drawing. [igotanoffer]

</details>

## 2. high-level

**Interviewer:** Sketch the end-to-end architecture. Name both the offline and online paths and the cross-cutting layers.

<details><summary>Reference</summary>

Two paths. OFFLINE ingest/index: article -> parse/clean -> chunk (with overlap)
-> embed -> upsert into a vector index plus a metadata store (article id, ACL,
timestamp, source URL for citations). ONLINE query/generate: query -> API
gateway/auth -> input guardrails -> optional query rewrite -> embed -> hybrid ANN
retrieve top-k -> rerank down to a few -> build a grounded prompt -> model
gateway/router -> LLM generate -> output guardrails -> answer WITH inline
citations. This mirrors Perplexity's five-stage pipeline (intent parse -> retrieve
-> snippet extract -> generate-with-citations -> refine). Cross-cutting: model
gateway, multi-layer cache, guardrails, and observability/eval. Keep it stateless
RAG: pass all context per request so the model retains nothing (privacy + more
relevant answers). [bytebytego-perplexity, slack, chip-huyen-platform]

</details>

## 3. deep-dive

**Interviewer:** Chunking & embeddings: how do you split 10M articles and represent them for retrieval?

<details><summary>Reference</summary>

Chunk so each unit is a coherent, retrievable idea. Semantic/paragraph-aware
chunking with modest overlap beats naive fixed windows because it avoids cutting
mid-thought and preserves citation granularity. Pick an embedding model matched to
the domain and index those vectors. Store rich metadata (article id, section, ACL,
published/updated time, URL) alongside each chunk so you can filter, enforce
permissions, and cite the exact source. Chunk size is a trade-off: smaller chunks
= sharper retrieval but more chunks and more calls. Larger chunks = more context
per hit but noisier and more tokens. [igotanoffer, chip-huyen-platform]

</details>

## 4. deep-dive

**Interviewer:** Retrieval at 10M+ vectors: which index and search strategy, and why not brute force?

<details><summary>Reference</summary>

Brute-force / flat search over tens of millions of vectors is too slow for a
few-second p95. You need approximate nearest neighbor (ANN). Default to HNSW: best
recall-per-latency while the index fits in RAM. Once the index outgrows memory,
move to IVF or IVF-PQ (cluster + product-quantize) to trade a little recall for a
much smaller memory/cost footprint. Use HYBRID search: sparse/lexical (BM25) nails
exact terms, rare identifiers, and names. Dense/vector captures semantics. Combine
them (as Perplexity does with an ML ranking layer). Apply metadata filters and
enforce the requesting user's ACLs at query time so retrieval never returns docs
the user can't see. [bigdataboutique, chip-huyen-platform, bytebytego-perplexity, slack]

</details>

## 5. deep-dive

**Interviewer:** Why add a reranker, and how does it change how many chunks you retrieve vs send to the LLM?

<details><summary>Reference</summary>

Two-stage retrieval. The bi-encoder ANN stage is fast but lossy (a whole chunk is
squeezed into one vector), so retrieve MANY candidates (e.g. top 50-100) to
maximize recall. Then a cross-encoder reranker reads each query-chunk pair jointly
(less information loss) and reorders by true relevance. That way you send only the
top few (e.g. 3-8) to the LLM. LLM recall degrades as the context grows, so
maximize retrieval recall, then minimize tokens reaching the model. The
cost is reranker latency, which is why it runs on a shortlist, not the whole
corpus. [pinecone]

</details>

## 6. deep-dive

**Interviewer:** Grounding, citations, and empty retrieval: how do you keep answers faithful and handle 'nothing relevant'?

<details><summary>Reference</summary>

Instruct the model to answer STRICTLY from the retrieved context and attach inline
citations/provenance to each claim so users can verify. Never let the LLM be the
source of truth. When retrieval is empty or low-confidence (low similarity /
sparse hits), don't hallucinate: abstain, say you don't know, or ask a clarifying
question. Add an output-side faithfulness/hallucination check (e.g. an LLM judge or
SelfCheckGPT-style verification) before returning. This is the core hallucination-
mitigation approach: retrieval grounding + confidence estimation + source
transparency. [interviewnode, bytebytego-perplexity, chip-huyen-platform]

</details>

## 7. deep-dive

**Interviewer:** How do you evaluate this system offline and online?

<details><summary>Reference</summary>

Offline: build a golden question/answer set with known source passages. Run
adversarial and red-team prompts. Score RAG-specific metrics like context
relevance/precision (did retrieval pull the right chunks?), groundedness/
faithfulness (is the answer supported by context?), and answer quality, often with
LLM-as-judge (acknowledge its bias/limits). Online: A/B tests plus feedback signals
(thumbs up/down, click/citation-follow, escalations) feeding a continuous
improvement loop. Segment metrics by prompt version, model, and time. Skipping an
eval/monitoring plan reads as not production-ready. [igotanoffer, interviewnode, chip-huyen-platform]

</details>

## 8. tradeoffs

**Interviewer:** How do you keep cost and latency in check at 50 QPS without hurting quality too much?

<details><summary>Reference</summary>

Bend the curve with caching and tiering rather than brute GPU spend. Caching:
prompt cache for shared system-prompt/instruction prefixes, exact cache for
repeated identical questions, and semantic cache for near-duplicate queries (flag its
false-match risk, because a wrong similarity hit returns a wrong answer). Model tiering /
routing: a small classifier sends easy queries to a cheap small model and only
hard ones to a premium model (Perplexity routes this way). Stream tokens to improve
perceived latency (TTFT), budget prompt tokens (rerank keeps context small), and
parallelize independent steps. Track per-token cost and latency continuously via
the model gateway. [chip-huyen-platform, interviewnode, bytebytego-perplexity, uber]

</details>

## 9. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does the system degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection: (1) Hallucination on empty retrieval: detect via
groundedness eval + low-similarity thresholds, and degrade by abstaining. (2) Stale or
missing index: with minute-level freshness, a lagging ingestion pipeline serves old
answers, so monitor index-update lag and doc coverage. (3) Cost/latency blowup under
traffic spikes: monitor per-query cost, QPS, p95, cache hit rate, and degrade via
throttling, smaller model, or shorter context. (4) Prompt injection / data leakage:
a malicious article or query manipulates the model, so defend with input/output
guardrails, ACL-scoped retrieval, and PII redaction at the gateway. (5) Context
overflow: cap and rerank. Provider outage: fall back through the model gateway to
an alternate model. Close with the biggest risks and what you'd improve next.
[igotanoffer, chip-huyen-platform, uber, slack]

</details>

## Sources

- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- [Chip Huyen — Building a Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html)
- [ByteByteGo — How Perplexity Built an AI Google](https://blog.bytebytego.com/p/how-perplexity-built-an-ai-google)
- [Slack Engineering — How We Built Slack AI to be Secure and Private](https://slack.engineering/how-we-built-slack-ai-to-be-secure-and-private/)
- [Pinecone — Rerankers and Two-Stage Retrieval](https://www.pinecone.io/learn/series/rag/rerankers/)
- [BigDataBoutique / Milvus — HNSW vs IVF vector index tradeoffs](https://bigdataboutique.com/blog/hnsw-vs-ivfflat-how-to-choose-the-right-vector-index)
- [InterviewNode — GenAI System Design Interview Patterns](https://www.interviewnode.com/post/generative-ai-system-design-interview-patterns-you-should-know)
- [Uber — GenAI Gateway](https://www.uber.com/blog/genai-gateway/)
