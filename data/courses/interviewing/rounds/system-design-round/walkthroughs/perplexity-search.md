---
imported_hash: a1537cc744d57f1e
title: Design a real-time LLM-powered search engine (like Perplexity.ai)
summary: perplexity-search-walkthrough · rag · hard
order: 98
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/perplexity-search.md
---

# Design a real-time LLM-powered search engine (like Perplexity.ai)

`perplexity-search-walkthrough` · rag · hard

## 1. clarify

**Interviewer:** What do you clarify first? Frame freshness, grounding, scale, and how this differs from closed-corpus RAG.

<details><summary>Reference</summary>

This is RAG, but over the LIVE WEB, not a fixed corpus — that changes everything.
Clarify: (1) Freshness: how fresh must answers be? A news/search product needs
near-real-time crawling and indexing, not a nightly batch — Perplexity ingests tens
of thousands of index updates per second. (2) Grounding bar: is the answer required to
cite sources and say nothing it didn't retrieve? For a search engine, yes — that's the
core promise. (3) Scale: web-scale index (Perplexity indexes ~200B URLs, 400+PB hot
storage, ~400M queries/month) and high QPS. (4) Latency: fast TTFT with streaming, a
few seconds to full answer. (5) Conversation: follow-ups keep context. (6) Cost per
query at that volume. State assumptions and confirm before designing. [bytebytego-perplexity, vespa-perplexity, igotanoffer]

</details>

## 2. high-level

**Interviewer:** Sketch the end-to-end pipeline from question to cited answer.

<details><summary>Reference</summary>

A five-stage online pipeline (Perplexity's shape): (1) QUERY UNDERSTANDING — an LLM
parses intent semantically, not by keywords, possibly rewriting/expanding the query.
(2) RETRIEVAL — search a live web index for candidate pages. (3) SNIPPET EXTRACTION —
pull the most relevant passages/chunks from those pages. (4) GENERATION — an answer
model synthesizes a response STRICTLY from the retrieved snippets, attaching inline
citations to each claim. (5) REFINEMENT — follow-up questions trigger new searches
while keeping dialogue context. Behind it: an OFFLINE crawl+index path keeping the web
index fresh, plus cross-cutting layers — a query-complexity router, caching, guardrails,
and observability. Stream tokens for fast perceived latency. [bytebytego-perplexity, chip-huyen-platform]

</details>

## 3. deep-dive

**Interviewer:** The live index: how do you crawl and index the web for freshness at scale?

<details><summary>Reference</summary>

This is the hard, non-RAG-101 part: a continuously updated web index, not a static
vector DB. Crawl the web continuously and, on each page, store it in ONE engine as
(a) its text (for lexical/BM25 search), (b) vector embeddings (for semantic search),
and (c) structured metadata (URL, domain authority, publish/last-seen time) — Perplexity
does this on Vespa. Support REAL-TIME UPDATES and continuous deployment so fresh pages
become answerable within seconds and stale ones age out; the system sustains tens of
thousands of index-update requests per second while serving queries at thousands of QPS
with ~100ms per-query processing latency. Freshness signals (recency) feed ranking so
breaking topics surface new pages. [vespa-perplexity, bytebytego-perplexity]

</details>

## 4. deep-dive

**Interviewer:** Retrieval & ranking: how do you find the right pages, and why hybrid + ML ranking?

<details><summary>Reference</summary>

Use HYBRID retrieval: lexical/BM25 nails exact terms, names, and rare identifiers;
dense vector search captures semantics and paraphrase. Retrieve a broad candidate set
combining both (high recall), then apply a MACHINE-LEARNED RANKER that scores
candidates on features like lexical relevance, vector similarity, DOMAIN AUTHORITY,
FRESHNESS, and user-engagement signals — reordering for precision. This mirrors
two-stage retrieval: cheap recall then expensive precision, sending only the best few
passages to the LLM (LLM answer quality degrades as you stuff more context). Vespa
unifies vector + lexical + structured filtering + ML ranking in one engine so this
happens in ~100ms. [bytebytego-perplexity, pinecone-rerank, chip-huyen-platform]

</details>

## 5. deep-dive

**Interviewer:** Generation & grounding: how do you produce a trustworthy cited answer and avoid hallucination?

<details><summary>Reference</summary>

The rule: the model may say NOTHING it didn't retrieve. Feed the top extracted snippets
to the answer model and instruct it to synthesize ONLY from that context, attaching an
inline CITATION to every claim so users can verify each statement against its source.
Never treat the LLM as the source of truth — grounding + citations are the core
hallucination defense. When retrieval is weak (few or low-relevance sources), don't
fabricate: say the sources are thin or ask to narrow the question. Stream the answer
with citations as it generates. This grounding contract is exactly what makes it a
search engine rather than a chatbot guessing from memory. [bytebytego-perplexity, igotanoffer, chip-huyen-platform]

</details>

## 6. tradeoffs

**Interviewer:** Cost & latency at web scale: how do you keep both in check?

<details><summary>Reference</summary>

Route by complexity: a CLASSIFIER decides query difficulty and sends simple queries to
a cheap, fast model and only complex ones to a powerful frontier model — Perplexity
routes this way, using its own fine-tuned Sonar models plus third-party frontier models
(GPT/Claude via Bedrock) behind a gateway. Cache aggressively: exact cache for repeated
popular queries, semantic cache for near-duplicates (flag its false-match risk), and
cache retrieval results for hot topics. Keep the context sent to the LLM small via
ranking + snippet extraction to cut tokens. Stream for fast TTFT. Track cost-per-query
and latency per model and per stage. [bytebytego-perplexity, chip-huyen-platform, igotanoffer]

</details>

## 7. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does it degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Stale/lagging index: with real-time freshness a
slow crawl serves outdated answers — monitor index-update lag and coverage of fresh
URLs. (2) Hallucination / uncited claims: run a groundedness/faithfulness check that
every claim maps to a source; degrade by abstaining when sources are thin. (3) Low-
quality or spammy sources / misinformation: weight domain authority in ranking, and
diversify sources. (4) Latency or cost spikes under load: monitor p95, TTFT, cost/query,
cache hit rate; degrade to a smaller model, fewer sources, or shorter answers. (5)
Prompt injection from a malicious page steering the answer: sanitize retrieved content
and constrain generation. Close with the biggest risks (freshness lag, grounding) and
what you'd measure and improve first. [bytebytego-perplexity, vespa-perplexity, igotanoffer]

</details>

## Sources

- [ByteByteGo — How Perplexity Built an AI Google](https://blog.bytebytego.com/p/how-perplexity-built-an-ai-google)
- [Vespa Blog — Perplexity builds AI Search at scale on Vespa.ai](https://blog.vespa.ai/perplexity-builds-ai-search-at-scale-on-vespa-ai/)
- [Chip Huyen — Building a Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html)
- [Pinecone — Rerankers and Two-Stage Retrieval](https://www.pinecone.io/learn/series/rag/rerankers/)
- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
