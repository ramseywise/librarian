---
title: '02 — RAG & Retrieval: multiple choice and worked problems'
summary: Interview-style questions on this module, 24 multiple choice and 3 worked problems with a numeric answer.
questions:
- id: d1
  prompt: 'The canonical pipeline, with optional stages in parentheses:'
  options:
  - Ingest → embed → chunk → index; query → retrieve → generate
  - Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  - Chunk → ingest → index → embed; query → rerank → retrieve → generate
  - Ingest → chunk → index → embed; query → retrieve → (verify) → generate
  answer: Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  explanation: 'Text has to be chunked before it can be embedded, and embedded before it can be indexed. Each optional
    stage sits where it acts: rewrite before retrieval, rerank after it, verify after generation.'
- id: d2
  prompt: 'Chunking priority order:'
  options:
  - Fixed-size windows, then semantic splitting as a refinement
  - Document structure (headings) first, then recursive paragraph/sentence boundaries, to a token budget
  - Semantic chunking first, falling back to fixed windows
  - Sentence-level always, merged upward to fill the budget
  answer: Document structure (headings) first, then recursive paragraph/sentence boundaries, to a token
    budget
  explanation: Headings mark where the author changed topic, which is the cheapest reliable boundary. A section
    over the budget is then split at paragraphs and sentences, so no chunk breaks in the middle of a thought.
- id: d3
  prompt: 'The course''s stance on semantic chunking:'
  options:
  - The recommended default for production corpora
  - Expensive at ingest and inconsistent — not the default
  - Required whenever documents lack headings
  - Equivalent to recursive splitting but faster
  answer: Expensive at ingest and inconsistent — not the default
  explanation: Semantic chunking embeds every sentence to find topic shifts, which adds cost at ingest, and where
    it cuts depends on a threshold that behaves differently from corpus to corpus. Structure-first splitting stays
    the default.
- id: d4
  prompt: 'Typical chunk token budget and overlap:'
  options:
  - ~256 tokens, ~32 overlap
  - ~512 tokens, ~64 overlap
  - ~1024 tokens, ~128 overlap
  - ~2048 tokens, ~256 overlap
  answer: ~512 tokens, ~64 overlap
  explanation: 'This is the bank''s starting point, not a law: a chunk long enough to hold one complete idea and
    short enough that its embedding is about one thing, with an overlap of about an eighth so a sentence cut at
    a boundary survives whole in one chunk. Tune both on your own corpus.'
- id: d5
  prompt: 'Parent/child chunking means:'
  options:
  - Index large chunks, generate from extracted sentences
  - Index small chunks, generate from their parent
  - Duplicate each chunk at two granularities in the same index
  - Chunk by document hierarchy only
  answer: Index small chunks, generate from their parent
  explanation: A small chunk has a precise embedding, so it matches the query well. Its parent section gives the
    model enough surrounding text to answer from.
- id: d6
  prompt: A `min_tokens` filter at ingest can cause which silent failure?
  options:
  - Oversized chunks are truncated mid-sentence
  - Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  - Embeddings drift toward the corpus mean
  - BM25 scores become incomparable with cosine
  answer: Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  explanation: 'A minimum length meant to drop stray headers also drops a complete one-line answer, and nothing
    raises an error: the question simply never retrieves it.'
- id: d7
  prompt: 'E5-family embedding models require:'
  options:
  - L2-normalized inputs
  - '`"query: "` / `"passage: "` prefixes'
  - Lowercased text
  - A fixed 512-token pad
  answer: '`"query: "` / `"passage: "` prefixes'
  explanation: E5 models were trained with those prefixes on each side, so leaving them out at inference quietly
    lowers retrieval quality.
- id: d9
  prompt: Vector-only search and BM25-only search fail in which way?
  options:
  - Vector misses paraphrases; BM25 misses exact tokens
  - Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  - Both miss exact tokens; only reranking recovers them
  - Vector misses short queries; BM25 misses long ones
  answer: Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  explanation: Embeddings capture meaning, so they match paraphrases but blur a rare exact string such as an error
    code. BM25 matches tokens, so it does the opposite. This is the case for hybrid search.
- id: d10
  prompt: Reciprocal Rank Fusion uses which constant?
  options:
  - k = 10
  - k = 60
  - k = 100
  - k is tuned per corpus
  answer: k = 60
  explanation: RRF scores a document as the sum of 1/(k + rank) over the result lists. k = 60 comes from the original
    paper (Cormack et al., 2009) and is the usual default; it flattens the gap between top ranks so one list cannot
    dominate.
- id: d11
  prompt: Why RRF instead of a weighted sum of BM25 and cosine scores?
  options:
  - RRF is provably optimal for hit rate
  - BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  - RRF is faster to compute
  - Weighted sums require normalized embeddings
  answer: BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  explanation: BM25 scores are unbounded and change with query length, while cosine similarities sit in a narrow
    band. A weighted sum needs a normalisation tuned per corpus; ranks can be compared as they are.
- id: d13
  prompt: 'CRAG vs Self-RAG, in one line:'
  options:
  - CRAG decides inside the LLM during generation; Self-RAG decides in the graph topology
  - CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during generation
  - Both decide before generation; CRAG adds a retry
  - Both decide during generation; Self-RAG adds a grader
  answer: CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during
    generation
  explanation: CRAG grades the retrieved documents in a separate step and routes on the grade before generating,
    which is control flow you write. Self-RAG trains the model to make those decisions itself while it generates.
- id: d14
  prompt: 'Self-RAG''s canonical mechanism (Asai et al.):'
  options:
  - LLM-driven query expansion into N paraphrases
  - Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  - A confidence gate on retrieved chunks with fallback
  - Entity-graph traversal alongside vector search
  answer: Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  explanation: The model is fine-tuned to emit special tokens that say whether to retrieve, whether a passage is
    relevant and whether the output is supported. The other options describe multi-query expansion, a CRAG-style
    gate and GraphRAG.
- id: d15
  prompt: 'Some blogs use "Self-RAG" to mean LLM query expansion. In an interview you should:'
  options:
  - Use the blog definition, since it is more common
  - Surface the ambiguity and name the canonical version — that itself scores
  - Avoid the term entirely
  - Correct the interviewer firmly and move on
  answer: Surface the ambiguity and name the canonical version — that itself scores
  explanation: The term is used loosely. Saying which meaning you intend stops you and the interviewer talking past
    each other, and shows you know the paper.
- id: d16
  prompt: 'HyDE works by:'
  options:
  - Embedding the question and expanding with synonyms
  - Generating a hypothetical answer and embedding *that* for search
  - Retrieving twice and fusing the ranks
  - Reranking with a cross-encoder on hypothetical pairs
  answer: Generating a hypothetical answer and embedding *that* for search
  explanation: A question and its answer are worded differently. A made-up answer, even with the facts wrong, is
    written like the documents, so its embedding lands nearer to them than the question's does.
- id: d17
  prompt: 'As an illustrative estimate rather than a benchmark, HyDE''s cost is:'
  options:
  - Roughly doubles total pipeline latency
  - One extra small-model call, ~100–200ms
  - Negligible — it reuses the main generation call
  - One extra embedding call only
  answer: One extra small-model call, ~100–200ms
  explanation: The hypothetical answer is one short generation by a small model before the search. It cannot reuse
    the main call, which runs after retrieval. The latency figure is the bank's estimate; measure it on your own
    stack.
- id: d18
  prompt: 'As illustrative rule-of-thumb figures rather than benchmarks, multi-query (RAG-Fusion) recall gain and
    its diminishing-returns point are:'
  options:
  - +5%, past 2 variants
  - +10–15%, past 3 variants
  - +20–25%, past 5 variants
  - +30%, past 10 variants
  answer: +10–15%, past 3 variants
  explanation: Each rewrite reaches documents the original wording missed, but later variants overlap with earlier
    ones while each still costs a retrieval. The figures are the bank's rule of thumb; measure on your own corpus.
- id: d19
  prompt: 'GraphRAG restraint — the course''s caution:'
  options:
  - GraphRAG is always preferable for enterprise corpora
  - It is overkill for factual lookup; for wiki-shaped corpora existing link structure already gives a
    traversable graph
  - It should replace vector search once entity extraction is available
  - It only works with proprietary graph databases
  answer: It is overkill for factual lookup; for wiki-shaped corpora existing link structure already gives
    a traversable graph
  explanation: Building an entity graph costs model calls over the whole corpus and pays off for questions that
    connect many documents. A single fact is answered by one chunk, and a wiki's links are already a graph.
- id: d20
  prompt: Debugging poor retrieval, what do you measure *first*?
  options:
  - Whether the LLM prompt includes the retrieved context
  - recall@k on a golden set
  - Cross-encoder reranker latency
  - Chunk overlap settings
  answer: recall@k on a golden set
  explanation: The order matters — golden-set recall@k, then embedding/corpus language match, prefix rules,
    chunk truncation, *then* hybrid + reranker, all before touching the LLM.
- id: d21
  prompt: 'RAGAS''s four standard metrics:'
  options:
  - precision, recall, F1, accuracy
  - faithfulness, answer_relevancy, context_precision, context_recall
  - groundedness, hallucination rate, MRR, nDCG
  - hit rate, coverage, calibration, naturalness
  answer: faithfulness, answer_relevancy, context_precision, context_recall
  explanation: Faithfulness asks whether the answer is supported by the context, and answer relevancy whether it
    addresses the question. Context precision asks whether the relevant chunks rank high, and context recall whether
    the context holds what was needed. Two score the generator and two the retriever.
- id: d22
  prompt: Which is *not* one of the three named cases for skipping RAG?
  options:
  - Stable narrow knowledge that fits the context window
  - Latency-critical paths
  - Poor-quality corpora
  - Corpora larger than 1M documents
  answer: Corpora larger than 1M documents
  explanation: Scale is a reason to change the index (ANN/HNSW), not to abandon RAG.
- id: r1
  prompt: What does an inverted index map?
  options:
  - Each document to the terms it contains
  - Each term to the documents that contain it
  - Each query to its cached results
  - Each document to its embedding
  answer: Each term to the documents that contain it
  explanation: A query looks up the posting list of each of its terms, so the search touches only documents that
    share a term with it.
- id: r2
  prompt: In BM25, what does the parameter b control?
  options:
  - How quickly repeated occurrences of a term stop adding score
  - The weight of rare terms
  - The number of results returned
  - How strongly the score is normalised for document length
  answer: How strongly the score is normalised for document length
  explanation: b = 0 ignores length and b = 1 normalises fully. Term-frequency saturation is the job of k1.
- id: r3
  prompt: When does embedding search beat keyword search?
  options:
  - The query and the document express the same meaning in different words
  - The query is an exact product code
  - The corpus is small
  - The query contains a rare name
  answer: The query and the document express the same meaning in different words
  explanation: Embeddings match on meaning. Keyword search wins on exact identifiers and rare names, which is why
    hybrid search runs both.
- id: r4
  prompt: What does reciprocal rank fusion need from each result list?
  options:
  - Scores on a common scale
  - A trained weight for each retriever
  - Only each document's rank
  - Relevance labels
  answer: Only each document's rank
  explanation: RRF sums 1/(k + rank) across lists. Ignoring the scores is what makes it robust when BM25 and cosine
    scores are on different scales.
- id: w33
  prompt: A term appears 3 times in a document and in 10 of the 1,000 documents in the corpus. With TF-IDF = count
    × log10(N / df), what is its score in that document?
  answer: '6'
  explanation: IDF = log10(1000 / 10) = 2, so TF-IDF = 3 × 2 = 6. A term in every document would score 0.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- id: w34
  prompt: A document is ranked 1st by keyword search and 4th by vector search. What is its reciprocal rank fusion
    score with k = 60, to 3 decimal places?
  answer: '0.032'
  explanation: 'RRF sums 1 / (k + rank) over the lists: 1/61 + 1/64 = 0.01639 + 0.01563 = 0.0320. Only ranks enter,
    so the two score scales never need reconciling.'
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- id: w35
  prompt: What is the cosine similarity of the vectors (1, 2, 2) and (2, 0, 1), to 3 decimal places?
  answer: '0.596'
  explanation: 'Dot product: 2 + 0 + 2 = 4. Lengths: √9 = 3 and √5 = 2.236. Cosine = 4 / (3 × 2.236) = 0.5963.'
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
---
