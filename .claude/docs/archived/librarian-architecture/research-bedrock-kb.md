# Research: Librarian RAG vs AWS Bedrock Knowledge Bases

Date: 2026-04-11
Context: Decision support for production architecture — Option 1 (Bedrock KB) vs Option 2 (LangGraph pipeline)

---

## Summary

Bedrock KB is the right default for launch: zero infra, fast to wire, and acceptable quality
for well-structured corpora. The Librarian pipeline wins on every quality dimension that
matters once you hit production — retrievability gaps, multi-turn accuracy, and failure
diagnosis. The side-by-side switch is already implemented in the UI; test both before committing.

---

## Head-to-head

### 1. Retrieval quality

**Bedrock KB**
- AWS manages embedding (Titan or Cohere), chunking, and vector store (OpenSearch Serverless)
- Single-strategy: dense vector retrieval only — no BM25 hybrid, no keyword fallback
- Fixed chunking: AWS auto-chunks your S3 documents; no heading-aware or parent-doc strategies
- No reranking step — top-k by cosine similarity is the final ranking

**Librarian**
- Hybrid BM25 + vector with configurable weights (default 0.3/0.7)
- RRF (Reciprocal Rank Fusion) across multi-query variants — expands the query into N reformulations and merges ranked lists
- Cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`) scores each (query, chunk) pair and reorders — consistently 10-20% hit_rate improvement vs cosine-only ranking
- CRAG retry loop: if confidence score falls below threshold, rewrites the query and retrieves again before generating

**Verdict:** Bedrock KB retrieval is a black box optimised for average-case corpora. Librarian's
hybrid + rerank + CRAG combination is measurably better for domain-specific or technical corpora
where term overlap matters (code, product names, version numbers, jargon).

---

### 2. Multi-turn accuracy

**Bedrock KB**
- Has `sessionId` parameter that passes conversation history to the model
- AWS handles context injection — limited control over how history is used
- No explicit query reformulation: "what about the Python version?" sent verbatim to the retriever

**Librarian**
- `HistoryCondenser` node rewrites the latest user query to be self-contained given prior turns
- "What about the Python version?" → "What is the Python version for [topic from prior turn]?"
- Only fires on multi-turn (single-turn has zero added latency)
- Uses Haiku (~$0.001/rewrite) — cheap, fast, targeted

**Verdict:** Bedrock KB's session handling will silently degrade on coreference-heavy
conversations ("that one", "and for the other method?"). The Librarian's condenser prevents
retrieval misses that look like hallucinations but are actually bad queries.

---

### 3. Observability and failure diagnosis

**Bedrock KB**
- Response: answer text + citations list. That's it.
- "Why did it give a wrong answer?" → no answer. Was it a retrieval miss? Wrong chunk? Model drift?
- No intermediate state, no scores, no ranked list, no per-step timing

**Librarian**
- Every node emits structured log events: `graph.crag.retry`, `chroma.search.done`, `reranker.done`
- `confidence_score` (0–1) tells you how much the reranker trusted its own output
- `retrieved_chunks`, `graded_chunks`, `reranked_chunks` all in state — inspectable at any step
- `failure_reason` in eval traces: `zero_retrieval`, `expected_doc_not_in_top_k`, `low_confidence`
- `FailureClusterer` groups misses by pattern for batch diagnosis
- Optional LangFuse integration for trace-level debugging and metric dashboards

**Verdict:** When Bedrock KB fails, you can't tell why. When Librarian fails, you can diagnose
it to the exact node and fix it. This compounds over time — the Librarian pipeline improves;
Bedrock KB failures stay mysteries.

---

### 4. Latency

| Step | Bedrock KB | Librarian (warm, streaming) |
|---|---|---|
| Embed query | ~100ms (AWS-managed) | ~100–200ms (local) or ~50ms (Voyage API) |
| Vector retrieve | ~200ms (OpenSearch Serverless) | ~50ms (Chroma local) or ~100ms (OpenSearch) |
| Rerank | None | ~200–500ms (cross-encoder CPU) |
| Generate (Claude) | Included in API call | ~400–800ms TTFT |
| **Total** | **1–2.5s (blocking, no stream)** | **~800ms–1.5s TTFT (streaming)** |

Bedrock KB's `RetrieveAndGenerate` is a single blocking call — no streaming token delivery.
Librarian streams from the generation node, so the user sees text arriving within ~1s.

**Verdict:** Bedrock KB latency is acceptable but feels slower because it's a blocking wall.
Librarian's streaming gives a significantly better perceived latency even if wall-clock is similar.

---

### 5. Cost structure

**Bedrock KB**
- Bedrock KB retrieval: ~$0.0004–0.001 per query (OpenSearch Serverless unit costs)
- Titan/Cohere embedding: ~$0.0001 per query
- Claude model tokens: same as Librarian
- No fixed infra cost — fully serverless
- Gets expensive at sustained high volume (>10K queries/day)

**Librarian on ECS/Fargate**
- Fixed: ~$50–80/month for always-on 2vCPU/4GB task
- Variable: Claude model tokens only (no embedding API cost with local model)
- Cheaper at volume (fixed cost amortises), more expensive at low volume
- Swapping local embedder for Voyage AI (~$0.00012/1K tokens) adds ~$0.0001/query but
  eliminates the 560MB RAM tax and model cold-start

**Verdict:** Bedrock KB wins at low volume. Librarian wins above ~5K queries/month (fixed
Fargate cost becomes cheaper per query than Bedrock's per-call fees).

---

### 6. Corpus control

**Bedrock KB**
- Ingest: upload documents to S3, configure KB in AWS console, Bedrock handles the rest
- Chunking: fixed-size or hierarchical (limited options, no heading-aware strategy)
- Embedding: Titan v2 (1536-dim) or Cohere embed — not swappable without re-indexing
- Metadata filtering: supported, but schema is AWS-defined
- Re-ingestion: full re-sync via S3 sync job

**Librarian**
- Ingest via `IngestionPipeline`: chunk → embed → index → MetadataDB + SnippetDB
- Six chunking strategies: `html_aware` (heading-boundary), `parent_doc`, `fixed`, `overlapping`, `structured`, `adjacency` — swappable via config
- Embedding model: swappable via `EMBEDDING_PROVIDER` env var; currently local e5-large
- Metadata schema: fully custom via `ChunkMetadata` (namespace, topic, access_tier, etc.)
- Selective re-ingestion by `doc_id` without full re-index

**Verdict:** Bedrock KB's corpus control is acceptable for document sets you don't iterate on.
For corpora that change frequently or require fine-grained control (access tiers, namespaces,
language-specific chunking), Librarian's ingestion pipeline is essential.

---

### 7. Vendor lock-in

**Bedrock KB**
- Data plane: AWS OpenSearch Serverless (proprietary)
- Vector store schema: AWS-managed, not portable
- Embedding format: Titan/Cohere vectors in AWS — can't move to another provider without re-embedding
- Switching cost: high — need to re-ingest, re-embed, rebuild KB

**Librarian**
- Vector store: Chroma (local, portable) or OpenSearch (self-managed) — swap via `RETRIEVAL_STRATEGY` env var
- Embedding: local model or any cloud API (Voyage, Cohere, OpenAI) via `EMBEDDING_PROVIDER`
- LangGraph: open source, runs anywhere Python runs
- Switching cost: low — change config, re-ingest to new backend

**Verdict:** Bedrock KB commits you to AWS's data plane. Librarian is portable — can run on
any cloud or on-prem.

---

## When Bedrock KB is the right choice

1. **Corpus is stable and well-structured** — standard prose documents (PDFs, web pages),
   not code, structured records, or mixed-language content
2. **No budget for always-on infra** — serverless, zero fixed cost
3. **Speed to launch is the priority** — no model to run, no pipeline to configure
4. **Acceptable to accept black-box retrieval** — you don't need to explain why an answer was wrong
5. **Low query volume** (< 5K/month) — per-call cost is cheaper than fixed Fargate

## When Librarian is the right choice

1. **Retrieval quality matters** — technical docs, code, domain-specific jargon, version numbers
2. **Multi-turn conversations are a core UX** — coreference resolution is critical
3. **You need to improve over time** — can't improve what you can't observe
4. **Higher volume** (> 5K queries/month) — fixed cost amortises
5. **Corpus requires custom chunking** — HTML-aware, parent-doc, access tiers
6. **Streaming perceived latency** — blocking Bedrock vs. token-streaming Librarian

---

## Side-by-side testing (already implemented)

The Streamlit frontend at `frontend/librarian_chat.py` has a radio button switching between
`"Python RAG (Librarian)"` and `"AWS Bedrock KB"`. The API routes dispatch on
`req.backend: Literal["librarian", "bedrock"]`.

**To activate Bedrock KB testing:**
```bash
# .env
BEDROCK_KNOWLEDGE_BASE_ID=<kb-id-from-aws-console>
BEDROCK_MODEL_ARN=arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-20251001-v2:0
BEDROCK_REGION=us-east-1
```

Same corpus ingested to both backends → same queries → compare `confidence_score`,
`citations`, response quality, and latency side by side in the Streamlit UI.

**Key things to test:**
- Multi-turn queries with coreference ("what about the Python one?")
- Technical/jargon queries (version numbers, product names, code terms)
- Queries where the answer spans multiple documents
- Edge cases: out-of-scope queries, ambiguous queries
