---
title: RAG Knowledge Preparation
tags: [rag, infra, concept]
summary: The process of transforming human-readable documentation into machine-retrievable knowledge units — chunking, metadata tagging, rewriting for self-containment, and enforcing consistency.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-huyen-ai-engineering-ch06-rag-agents.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch06-advanced-rag-techniques-information-retriev.md
  - data/raw/meetings/2026-06-26-final-checkin.md
  - data/raw/meetings/2026-06-23-onboarding-bedrock-data-sources.md
  - data/raw/claude-docs/chat-agent/docs/kb-analysis/intercom_kb_analysis.md
  - data/raw/notion/2026-04-07-support-knowledge-agent.md
  - data/raw/notion/2026-04-13-rag-pipeline-requirements.md
  - data/raw/papers/2026-11-06-chan-2025-retrieval-augmented-reasoning-lean-language.md
  - data/raw/papers/2026-11-08-building-ai-agents-llms-rag-kgs-ch05-extending-your-agent-rag-prevent-hallucinat.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch03-building-context-aware-multi-agent-.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch03-adding-knowledge-bass.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch07-high-fidelity-rag-defense-nasa-insp.md
---

# RAG Knowledge Preparation

Existing documentation is typically written for human reading, not machine retrieval. Before content can serve as a reliable RAG knowledge source, it must be restructured.

This is an operational discipline distinct from chunking strategy (which is a retrieval engineering concern) — knowledge preparation happens before ingestion and involves editorial decisions about content quality and structure.

---

## Core Preparation Steps

### 1. Chunk Long Articles Into Smaller Knowledge Units

Long articles written for sequential reading contain multiple topics, introductory context, and caveats that become noise in retrieval. Split into topic-scoped units where each unit answers exactly one type of question.

Rule of thumb: if a chunk requires prior context to understand, it is not self-contained.

### 2. Remove Redundant and Outdated Content

Duplicate coverage of the same topic across multiple articles leads to conflicting retrieval results. Outdated articles create factual errors — the retriever doesn't know the content is stale.

### 3. Rewrite Sections for Self-Containment

Each knowledge unit should stand alone as an answer. A section like "As described above, the VAT rate is..." fails when retrieved without the article context. Rewrite to: "The VAT rate for [scenario] is..."

### 4. Attach Structured Metadata

Metadata is critical for retrieval accuracy. Without it, the system may retrieve technically correct information that is irrelevant to the user's context.

**Key metadata fields:**
- `product_area` — which product domain (invoices, expenses, banking, etc.)
- `feature` — specific feature or workflow
- `market` — which country/regulatory market applies (Denmark, Germany, France, etc.)
- `language` — content language
- `object_type` — the system object being described (invoice, expense, transaction, etc.)

Metadata enables **runtime filtering** — retrieval can narrow to market-relevant content rather than returning globally similar chunks.

---

## The Market and Language Filtering Problem

In multi-market financial software, accounting rules differ significantly across jurisdictions:
- Chart of accounts varies by country
- VAT rules differ
- Regulatory reporting obligations differ

A retrieval system that ignores market context may return content that is factually correct for one market but incorrect for another. **For financial software, incorrect regulatory guidance is the highest-risk failure mode.**

Every knowledge unit must include explicit market and language metadata. At query time, the retriever must include the user's market context as a filter — not as a ranking preference.

---

## Documentation Consistency

Multiple articles describing the same process differently create conflicting explanations. When retrieved together, these produce ambiguous or contradictory answers.

Preparation should include a consistency pass:
- Identify articles covering the same topic
- Reconcile conflicting claims
- Flag genuine regulatory ambiguity explicitly (don't silently merge)

---

## Support Conversations as Knowledge Source

Support conversations are a rich signal for identifying knowledge gaps — they represent real user questions that the current documentation fails to answer. However, they are NOT ideal direct retrieval sources:

- Frequently contain partial explanations
- Include edge cases not representative of typical behavior
- Contain corrections made mid-conversation (earlier turns may be wrong)
- Use informal language not matching documentation style

**Use support conversations for:** identifying documentation gaps, improving existing articles, building golden eval datasets. NOT as direct retrieval chunks.

---

## When to Do Knowledge Preparation

Knowledge preparation is a prerequisite before loading content into a vector store. Skipping it doesn't make RAG fail immediately — it makes RAG fail in subtle ways:

- Inconsistent retrieval quality across question types
- High hallucination rate on market-specific questions
- Conflicting answers when multiple articles cover the same topic
- Low recall on specific question types (chunk too broad, splits dilute signal)

---

## Corpus Hygiene Lessons from a Managed-KB Web Crawl

Defects found in the first EDA of a web-crawled managed KB for a support assistant:

- **Tables break hierarchical chunking.** A pricing page's table structure produced child
  chunks too small to hold a full price row, so pricing answers came back truncated — a
  known failure mode, fixed in parsing, not in retrieval.
- **Crawlers ingest what the regex does not exclude.** Spreadsheet templates linked from
  articles were crawled as documents; URL-regex filters belong in the crawler config.
- **Partial translations are duplicates in the wrong market.** Second-language copies of
  the same articles were dropped, along with encyclopedic marketing pages that produced
  false-positive retrievals for support questions.
- **Boilerplate duplication is a storage cost, not a retrieval cost.** Repeated
  image/copyright chunks were deprioritised after duplication analysis showed they did not
  surface in retrieval.
- **Add a sentence-fragmentation check** to the corpus quality checklist — chunks that
  start or end mid-sentence are a cheap-to-detect chunker defect.
- **Parsing beats chunk tuning for simple dense retrieval.** With a single dense retriever,
  changing chunking strategy moved results little; cleaning and parsing the source was the
  higher-leverage work.
- **Ground-truth coverage limits citation checks.** When only ~10% of historical answers
  cite a source URL, URL-level grounding covers a small slice, and instructing the model to
  cite in the prompt is not enough — a delivery-time gate (retrieval score threshold or a
  citation-presence check) is the safeguard.

## Paper evidence: indexing summaries instead of pages

A technical report on a medical-advice RAG (Qwen2.5-32B summaries, all-mpnet-base-v2 and Chroma, 1,000 synthetic queries, 989 condition pages) found that indexing LLM-written summaries retrieved better than indexing full pages: p@1 0.51 against 0.47, p@5 0.76 against 0.68 (self-reported). The summarizer was told to retain just symptoms and next steps, which suits the query type, and the authors advise indexing full pages for a more general system. Retrieval capped accuracy: with k=5 the ceiling is the 76% precision at 5. Summaries also cut the average reasoning-training example from 74,641 tokens to 7,544.

## Book-chapter practices: chunking, embedding and dual namespaces

Two practitioner book chapters (Packt, read via O'Reilly) give guidance rather than experiments.

- **Chunk and embed (a RAG chapter in a book on agents with LLMs, RAG and knowledge graphs).** Keep chunks within the embedder's context, since truncation loses information; chunks that are too small lose context, while ones that are too large turn non-specific and raise inference cost. The chapter advises a small overlap relative to chunk size, because overlap enlarges the database. The chapter says no chunker is universal, so each strategy should be evaluated; it names recursive and propositions-based chunking. Common fixed sizes it lists are 100 tokens, 256 tokens or 500 characters; its demo uses 1,500 characters. For embedders, test several on your own data rather than trusting MTEB alone (the chapter calls leaderboard results self-reported and generic-domain). It prefers int8 over float32 before binary quantization, which it says cuts memory up to 32x at some performance cost (an assertion; no experiment given), and it describes Matryoshka embeddings as truncatable with limited loss. Query and documents should use the same encoder.
- **Vector store choice (same chapter).** Weigh licence, language support, maturity, insert and query speed, privacy, integration and cost. By the chapter, FAISS fits immutable indexes better than systems with heavy create-read-update-delete traffic; SQL vector extensions fit internal projects, and dedicated vector databases fit performance needs.
- **Dual RAG namespaces (Rothman, Context Engineering for Multi-Agent Systems, ch. 3).** The demo keeps facts in a KnowledgeStore namespace and procedural instructions ("semantic blueprints") in a ContextLibrary namespace of one Pinecone serverless index, so either can be updated independently. The embedding covers only the blueprint's description, and the JSON blueprint itself is stored as metadata. The Librarian agent retrieves the top blueprint (top_k=1) and falls back to a neutral default when nothing matches; the Researcher takes the top 3 chunks. Chunking is by tokens (400 with 50 overlap, cl100k_base); text-embedding-3-small gives 1,536-d vectors with cosine. Because namespace deletion can be asynchronous, the notebook polls the vector count to zero before upserting.

## Chunking, metadata, embedding lifecycle and tables (Lakshmanan and Hapke, ch. 3)

The chapter is illustrative, with no retrieval metrics. Points it makes:
- Match the chunking method to the document: fixed length with overlap, sentence, paragraph, structural or semantic-shift boundaries; never embed a whole book as one vector. Embedding vectors of 768 to 4,096 dimensions are an information bottleneck.
- Documents up to about 200,000 tokens (about 500 pages) may skip RAG and sit in the context window with server-side caching (June 2025 claim).
- Keyword retrieval is brittle to synonyms: on one equipment manual (BM25, top 5, 200-character chunks), asking about a "broken" diaphragm instead of a "ruptured" one returned a different action. One query pair, no scores.
- Tabular data: a 512-dim text vector extended by two numeric columns gives 514 dims, and the text part swamps the numbers; in a toy catalogue, a metadata prefilter on creation date removed a duplicate older product.
- Metadata (document, chunk, domain, access control) filters stale content, prunes the store, and helps detect contradictions; the authors prefer pruning old content over filtering since a smaller index is faster. Freshness examples: CDC isolation guidance changed twice; hypertension thresholds differ between guideline bodies, so adding sources makes answers contradict.
- Embedding lifecycle: a deprecated embedding model forces a full reindex (the patent example is about 350,000 new patents a year), so prefer long support life or open weights; split indexes by domain and index incrementally. MTEB ranks quoted are a June 2025 snapshot.

## Ingestion with source metadata, sanitising and citations (Rothman, ch. 7)

A practitioner chapter, with one toy run and no metrics. It keeps ingestion separate from the engine and stores the source filename in every chunk's metadata, then verifies with a probe query that the metadata comes back. At query time the Researcher takes the top 3 chunks, passes each through a regex gateway of six case-insensitive patterns (for example "ignore previous instructions" and "act as") and drops any chunk that matches. The sources list is appended programmatically from the retrieved chunks' metadata, so it records what was retrieved, not what the answer used. On an Apollo 11 query against a store holding only two other documents, the Researcher said the information was missing instead of inventing it (one run, qualitative). The author calls the sanitiser basic and recommends moderation APIs or guardrails in production. Limits: two toy documents, single runs, regex-only defence.

## Further book-chapter practices (chapter 6 notes)

One chapter gives a chunking example of 2,048 characters with 20 characters of overlap and says inverted-file indexes group vectors into clusters of roughly 100 to 10,000. Another reports that embedding inversion recovered over 70% of words from stored vectors and notes a 32K-token limit for one embedder (dated); it also cites a 2024 best-practice guideline without numbers. None of these chapters reports an experiment of its own.

## Limits

- One domain and one query type. A 32B model fine-tuned on reasoning traces scored 0.56 against 0.54 with retrieval alone, within about 2 standard deviations (the extraction's caution), so most of the gain came from retrieval.
Limits of this section:
- Chapter 3 has no experiments of its own; MTEB ranks and context sizes have dated. Fig 3-11 (degradation with index size) is a schematic with no data. The chapter's pattern numbering is inconsistent, and its table example uses StandardScaler though the text says min-max.
- Book-chapter section (Packt chapter and Rothman ch. 3): the extraction notes the first has no experiments (its formulas are images) and that the demo has no evaluation; the second's demo has 2 knowledge chunks and 3 blueprints, and it neither measures retrieval quality, latency or cost nor sets a score threshold on retrieval.

## See Also
- [[Librarian RAG Architecture]] <!-- auto-linked -->
- [[Agentic RAG — Advanced Patterns]] <!-- auto-linked -->
- [[RAG Retrieval Strategies]]
- [[RAG Evaluation]]
- [[[client] Knowledge Agent]]
- [[LangGraph CRAG Pipeline]]
- [[PII Masking Approaches]]
- [[Data Pipeline Pattern Selection]] — extends (batch ingest as one of four data-arrival patterns)
- [[Canonical Document IR for Ingest]] — extends (source-blind typed Document schema with provenance threaded from ingest)
- [[Consequence-Flagged KB Audit]] — extends (per-article four-field audit with financial-consequence flag and corpus defect taxonomy)
- [[Lucene HNSW and Pyserini Dense Retrieval]] — related
