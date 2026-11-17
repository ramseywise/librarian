---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/02-rag-retrieval/slides/deck.yaml
cards:
- front: What are the five parts of this lecture, in order?
  back: The lecture follows one wrong answer from the pipeline's map, through search and generation and real stacks, to deciding which fix to build.
  lesson: generative-ai/02-rag-retrieval/readme
- front: Name four things this lecture teaches you to do with a RAG system.
  back: You will be able to say which stage let the wrong page through, fix it, and show on your own queries that the fix worked.
  lesson: generative-ai/02-rag-retrieval/readme
- front: Name Gao's three RAG paradigms.
  back: Naive, advanced and modular name how much machinery surrounds retrieval, so start naive and add what the eval justifies.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why rerank against the original question after expansion?
  back: Order stages so each narrows the set for the next, and always rerank against what the user actually asked.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why does ingestion set the ceiling?
  back: Inspect what the parser produced first, because no retriever or reranker can recover text that ingestion lost.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: What is the difference between Self-RAG and FLARE?
  back: Route aggregates to SQL, add agent loops only for questions that decompose, and treat retrieval timing as a design choice.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What three costs does RAG add?
  back: RAG gives the model facts at inference time, in exchange for latency, an index to maintain and a new way to fail.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: What is the smallest possible RAG?
  back: A working RAG is a fetch plus an f-string, and every technique after this improves the fetch or the template.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: How does Self-Route decide when to use the full context?
  back: Long context can win on quality with frontier models, but retrieval stays cheaper and is the only option for large corpora.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: What are the five ways to train the two halves of a RAG system?
  back: There are five ways to train the pair (training-free, independent, retriever first, LLM first, joint), and most production RAG stays training-free because joint training forces both to be retrained together.
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: What goes wrong when you train a retriever and reader together?
  back: Keep the index fresh while a retriever trains, read language-modelling multipliers as such, and leave near-duplicates of the answer out of the prompt.
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: Which query kind does BM25 miss, and which does dense miss?
  back: BM25 misses paraphrases and dense misses exact codes, so hybrid raises recall even if it doesn't improve every metric.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: What does the k in RRF do?
  back: RRF combines retrievers using ranks alone, so it needs no calibration and rewards documents both lists agree on.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: 'MRR, MAP or nDCG: when do you use each?'
  back: Track recall first because it caps everything downstream, then pick MRR, MAP or nDCG according to your task and labels.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: What do M, efConstruction and ef control?
  back: HNSW walks stacked graphs to get roughly logarithmic search, giving up exact results for tunable, measurable recall.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: What goes wrong with post-filtering under a selective filter?
  back: Choose a database when you need updates, filters and persistence, and check whether its filters run before the search.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: What goes wrong at each extreme of chunk size?
  back: Chunk size trades meaning against precision, and the common overlap numbers are conventions to test on your own corpus.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: Where did semantic chunking's big win come from?
  back: Fixed-size chunking is a strong baseline, while structure-aware chunking pays on table-heavy documents, so measure before you switch.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: 'Which adds query latency: HyDE or hypothetical questions?'
  back: Generated text can bridge queries and documents, and doing it at index time avoids adding latency to each request.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Why rerank if recall is already fine?
  back: Over-retrieve cheaply, rerank with a cross-encoder, and pass few chunks, because a longer list can hurt the answer itself.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Why split an eval by query kind?
  back: Label queries, split them by kind, score each retriever, and change one thing at a time so you know what helped.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: How does top-p differ from temperature?
  back: Low temperature and low top-p reduce variety for factual answers, while truth still has to come from retrieved documents.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Why include a refusal instruction and dates?
  back: A grounded prompt limits, cites and allows refusal, which gives you something to check even though it guarantees nothing.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Which retrieved passages hurt most?
  back: A model can overrule good context or answer without any, and the worst passage scores highly while lacking the answer.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: On Balaguer et al.'s task, what were the three scores?
  back: Use retrieval for facts that change and fine-tuning for behaviour, and expect the two to add up rather than compete.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: Who calibrates code checks and LLM judges?
  back: Cross scope with evaluator so that cheap code checks run everywhere, judges cover meaning and humans calibrate both.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What does a RAG trace need to show?
  back: Trace every span so that real failures become datasets, and let experiments on those datasets decide which fix ships.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What do you cut first to lower cost?
  back: Cut tokens before changing models, since most of the money and latency is in the LLM, and keep only stages that pay.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: How do you stop one customer seeing another's documents?
  back: Enforce permissions at retrieval and treat the corpus as an attack surface, because instructions in prompts protect nothing.
  lesson: generative-ai/02-rag-retrieval/notes/07b-security-changing-text-multimodal-and-live-indexes
- front: Why the max across expansions, and not the sum?
  back: PRINCE narrows from millions of vectors to seven chunks by filtering first, taking max scores and reranking on the original.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Why did PRINCE remove the LLM SQL reviewer?
  back: Send counting questions to SQL with retrieved examples and mechanical checks, since an LLM reviewer cost more than it caught.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: When should you avoid agentic RAG?
  back: Agentic RAG pays for broad questions over messy data, and when one pass works, its extra machinery just adds latency.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: What breaks when you change embedders?
  back: Vector count, dimensions and hybrid needs pick the store, and an embedder change means re-embedding wherever you are.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: What does a semantic cache risk that an exact cache doesn't?
  back: A cache lookup is a matrix multiply that skips the whole pipeline, and a wrong match goes to the user unchecked.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: Why not always use 0.95?
  back: Sweep the threshold on hard near misses for your own embedder, and invalidate rows whenever a source document changes.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: Why was CRAG judged marginal?
  back: Ablations expose costs and interactions, like a loop that buys almost nothing and a setting that helps one agent only.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: Why is a paired test tighter?
  back: Before you believe a gain on a small eval set, run a paired bootstrap on per-query differences and read the interval.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: Why can 32 queries and 5 configs never give 200 DPO pairs?
  back: More annotated queries unblock DPO, not more configs, because pairs from one question are not independent examples.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: What did trained retrievers, filters and loops gain over prompting?
  back: Training a retriever, filter, trigger or loop can help, but retrieval itself is most of the gain and each result is one run, so measure on your own queries first.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: What can't a managed RAG service do for you?
  back: A managed backend takes the index off your hands, while the eval and the decision about what goes in stay yours.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What differs in who owns generation?
  back: Managed services differ in how much they hide, and the evaluation row reads the same across every option.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Where does the score threshold get applied?
  back: Bedrock's two modes differ by one config object, and the score threshold you rely on is your own client-side code.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What doesn't a grounding score tell you?
  back: A score only means something within its own mode, so compare backends by running them on the same eval set.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: When would you leave Vertex's :answer endpoint?
  back: Buy unless your eval shows you need control, and when you build, budget for owning each line of the pipeline.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What do you fix first in a weak RAG system, what is the default, and how do you prove a change?
  back: Fix ingestion and recall first, default to hybrid plus reranking, and prove each change on your own eval set.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Name the three RAG paradigms in Gao et al.
  back: Naive (index, retrieve, read). Advanced (adds pre- and post-retrieval). Modular (swappable stages composed into patterns).
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: What order do the query-time stages run in, and why?
  back: Filter, search, rerank, dedupe, compress, inject memory, format. Each stage narrows the set, so cheap stages go first and expensive ones see fewer items.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why not sum BM25 and cosine scores?
  back: They are on different scales, so the larger range swamps the other. Normalise and weight, or fuse ranks with RRF.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: How does RRF work?
  back: Each list contributes `1/(k + rank)` per document, usually with k=60, and documents are sorted by the sum. It needs no score calibration, and it discards score magnitude.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why rerank against the original query after expansion?
  back: Expansion is a recall device. The user's question remains the relevance target, and reranking against a rewrite would compound its drift.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why is Text-to-SQL a retrieval strategy?
  back: Embedding similarity cannot count, sum or compare, so aggregation questions go to a query against structured data. Choosing that path is a routing decision.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: How do you keep an index in sync?
  back: Start with scheduled batches and a change-detection method, and make writes idempotent with content-derived ids and source-scoped deletes.
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Why do flat chunks fail on aggregation questions?
  back: Each chunk is retrieved on its own similarity, and the answer is a pattern across many chunks. Structure built at index time (summaries, graphs, schemas) gives the retriever something to match at that level.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What does RAPTOR build?
  back: 'A tree: leaf chunks are clustered, each cluster is summarised into a parent, and the process recurses to a root. Retrieval can then match at any level of abstraction.'
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What do knowledge graphs lose, and how do you keep it?
  back: 'Conditions and nuance: a conditional sentence becomes separate triples. Use the graph as an index beside the natural-language text, not instead of it.'
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What did CorpusMap find about entity pages?
  back: On three enterprise-style benchmarks, entity pages as files raised an agent's quality by 6.4 to 11.7 points over raw files with 34–57% fewer input tokens. Entity-to-entity edges added nothing.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What is multi-representation indexing?
  back: Embed one thing (a summary, a description) and return another (the full document) under a shared id. Search runs over the short form and the model gets the original.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: Why add a similarity floor to nearest-neighbour lookup?
  back: Top-k always returns something while the index holds any vector. Without a threshold the fallback for "nothing relevant" never fires.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: When is agentic RAG worth the cost?
  back: When questions decompose into sub-questions or need several sources compared. For narrow questions a single pass matches it at lower latency.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What does IRCoT do?
  back: It uses each chain-of-thought sentence as the next retrieval query. It raised gold-paragraph recall by 11.3–22.6 points over one-step retrieval on multi-hop QA, at up to 8 extra LLM calls.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What changes in multi-turn RAG?
  back: The corpus includes the conversation, follow-ups need intent resolution, and the system decides whether to retrieve on each turn.
  lesson: generative-ai/02-rag-retrieval/notes/01b-index-structures-and-agentic-rag
- front: What problem does RAG solve?
  back: The model lacks private, real-time and hard-to-access facts. Retrieval supplies them in the prompt at inference time, with no retraining.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: Why is updating an index better than retraining?
  back: Lewis et al. swapped a 2016 Wikipedia index for 2018 and the model named 2018 world leaders correctly 68% of the time. With the wrong year's index it fell to 4–12%, and no retraining was involved.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: What does RAG cost you?
  back: A retrieval step of added latency, an index to keep in sync, and a new failure surface.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: Does RAG reduce hallucination?
  back: 'In Shuster et al.''s dialogue setup, hallucinated responses dropped from 68.2% to 8–21%. More documents can push it back up: 7.9% to 19.8% going from 5 to 25 with FiD-RAG.'
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: Long context or RAG?
  back: Long context can beat top-5 RAG on quality with frontier models, at much higher token cost. Li et al.'s Self-Route answers with RAG and falls back to full context only for "unanswerable" outputs. When the corpus doesn't fit the window, retrieval is the only option.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: How much retrieved context is optimal?
  back: It depends on the model and data. Yu et al. saw Llama3.1-70B peak at 48K tokens on one benchmark, and document order alone added 6 F1 at 16K.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: Name the training paradigms for retriever and generator.
  back: Training-free, independent, sequential in either order, and joint. Most production systems stay training-free because joint training ties the pair together.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: Why keep source metadata through prompt formatting?
  back: Citations need it, and so does debugging. If formatting strips the source from a chunk, nobody can trace a claim in the answer back to where it came from.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: What are the ways to train the two halves of RAG?
  back: Training-free, independent, sequential (retriever first or LLM first) and joint. Most production RAG is training-free
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: How can a retriever learn without question–passage labels?
  back: Izacard and Grave use the reader's cross-attention as the target. RPT uses a scoring LM's likelihood gain on the next chunk. Both need a decent starting retriever
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: What did REALM show about joint training?
  back: The index goes stale as the retriever updates. A 30× staler index cut NQ dev EM from 38.2 to 28.7
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: Why is kNN-LM's gain not all retrieval?
  back: 'Xu et al.: a separate trained output matrix recovers about 55% of it, and the kNN softmax temperature changes results by up to 3.7%'
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: What does InstructRetro show?
  back: Retrofitting a 43B GPT with retrieval for 100B tokens, then instruction tuning, beat instruction-tuned GPT with RAG by 7% on average zero-shot. The gap on NQ was 38.9 against 37.0
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: Does RETRO's multiplier carry over to QA?
  back: No. It is a language-modelling result, and RETRO scored 45.5 EM on NQ against FiD's 51.4
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: What does ALCUNA say about readers?
  back: Few-shot models misuse in-context new knowledge, mostly when linking it to existing knowledge and when the parent entity is also in the prompt. It does not test a retriever
  lesson: generative-ai/02-rag-retrieval/notes/02b-training-the-retriever-and-the-reader
- front: What does IDF do?
  back: It discounts terms that appear in many documents. A term in every document contributes nothing in classic TF-IDF, while a rare code dominates.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: What do BM25's `k1` and `b` control?
  back: '`k1` saturates term frequency, so repeats give diminishing returns. `b` sets how much long documents are penalised: 0 ignores length, 1 normalises fully.'
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: When does keyword search beat embeddings?
  back: Exact identifiers, names and jargon, especially when many documents are semantically near-identical.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: Cosine similarity or dot product?
  back: Cosine ignores length. They are the same on unit vectors, so normalise and use the faster one.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: What are good unsupervised baselines for text retrieval?
  back: TF-IDF and BM25, which need no trained model. BM25 is TF-IDF with two tunable fixes, `k1` and `b`, and it is still the default keyword scorer.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: Why fuse ranks and not scores?
  back: BM25 and cosine live on different scales. RRF needs no calibration, at the cost of discarding score magnitude.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: Which retrieval metric first, and why?
  back: Recall@k. A document that was not retrieved can't be used, so low recall caps the system.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: MRR, MAP or nDCG?
  back: MRR when one good document is enough. MAP when you want all relevant documents ranked high with binary labels. nDCG with graded labels.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: Do human relevance labels predict RAG quality?
  back: 'Weakly in Salemi and Zamani''s tests: tau around 0.18 for provenance MRR on NQ, against 0.50 for eRAG, which scores each document by what the system''s LLM does with it.'
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: Why do filters not replace search?
  back: A filter is a hard yes or no with no ranking. It enforces constraints but does not order what remains by relevance.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: What are precision and recall at k?
  back: Precision is relevant retrieved over retrieved. Recall is relevant retrieved over total relevant. At k, both are counted on the top k only, which makes systems comparable.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: What is mean average precision (MAP)?
  back: Average precision takes the precision at each relevant hit in one query's ranking. MAP is its mean over queries, and it is high when relevant documents rank near the top.
  lesson: generative-ai/02-rag-retrieval/notes/03b-metadata-filters-hybrid-search-and-evaluating-a-retriever
- front: Why not just scan every vector?
  back: KNN cost grows linearly with the corpus, so each query at 1B vectors computes 1B distances.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: What does ANN give up?
  back: The guarantee of the true top k. You trade a measurable loss in recall for far fewer distance calculations.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: How does HNSW search?
  back: It walks stacked proximity graphs from a sparse top layer down to the full bottom layer, greedily moving closer to the query at each level, for roughly logarithmic cost.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: What are `M`, `efConstruction` and `ef`?
  back: Links per node, the beam width while building, and the beam width at query time. Higher values raise recall and cost memory, build time or latency respectively.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: When would you use IVF, PQ or LSH instead?
  back: IVF to probe a few k-means clusters, PQ to shrink memory with approximate distances, LSH for fast cheap builds with lower recall. FAISS commonly combines IVF and PQ.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: What does a vector database add over FAISS?
  back: Create, update and delete, metadata filters, persistence and backups, plus keyword, hybrid and reranked search in many cases.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: Pre-filter or post-filter?
  back: Post-filter can return fewer than k results under a selective filter. Pre-filter keeps k but needs index support.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: When is pgvector enough?
  back: 'When your data is already in Postgres and scale is modest: one system and one transaction. Check its dimension and scale limits against your load.'
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: How do you compare ANN indexes?
  back: On recall, queries per second, build time and index size, as ANN-Benchmarks does.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: How do you make ingestion idempotent?
  back: Derive object IDs deterministically from the content, such as `generate_uuid5`, so a rerun overwrites instead of duplicating.
  lesson: generative-ai/02-rag-retrieval/notes/04-vector-databases-and-ann
- front: Why chunk at all?
  back: A whole document's vector averages its meaning, retrieval returns too much text, and embedders silently truncate past their limit.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: What overlap should you use?
  back: Start at 10–20% and test it, because it is a convention. Book examples range from 1% to 20% and none measures it.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: Does semantic chunking beat fixed-size?
  back: 'Not on real long documents in Qu et al.: HotpotQA F1@5 was 90.59 fixed vs 87.37 breakpoint. Its big win came only on synthetic stitched documents, and the embedder mattered more.'
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: When does element-based chunking pay?
  back: On structured, table-heavy documents. Jimeno Yepes et al. got 53.2% vs 48.2% on FinanceBench with about half the chunks.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: What is contextual retrieval?
  back: An index-time LLM writes a 50–100 token context for each chunk, prepended before the chunk is indexed. It adds no query latency.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: HyDE vs hypothetical questions?
  back: HyDE generates a fake answer at query time. Hypothetical questions are generated at index time and matched against the user's question, so they add no query latency.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: Multi-query vs RAG-Fusion?
  back: Both search with several versions of the question. Multi-query unions the results and RAG-Fusion merges them with RRF.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: How do you make a chat turn searchable?
  back: Rewrite it into a standalone query with a small LLM. Concatenating history is cheap, and it drags old topics into retrieval.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Bi-encoder vs cross-encoder vs ColBERT?
  back: 'Bi-encoder: one vector per text, precomputable and fast. Cross-encoder: scores each pair jointly, best and slowest, so reranking only. ColBERT: per-token vectors with MaxSim, near cross-encoder quality and heavy storage.'
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Why rerank if recall is fine?
  back: Zhao et al. found answer quality falls as the list grows even when the gold passage is present, and gold first beats gold last. Fewer and better chunks also cut cost.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: What is the standard reranking recipe?
  back: Over-retrieve 20–50 with hybrid search, rerank the pairs, return the best 3–10.
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Can search be framed as a classification problem?
  back: 'Yes, pointwise: a classifier scores each (query, passage) pair for relevance and you sort by score, as monoBERT does after BM25 retrieval. duoBERT then compares passages in pairs.'
  lesson: generative-ai/02-rag-retrieval/notes/05b-query-parsing-conversational-retrieval-and-reranking
- front: Temperature vs top-p?
  back: Temperature reshapes the distribution. top-p restricts which tokens are eligible, keeping the smallest set whose cumulative probability reaches p, so it adapts to the model's confidence.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Settings for factual RAG?
  back: Temperature near 0 and a low top-p, with an "only from the documents, cite, say if absent" prompt.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: How would you order the context?
  back: Put the strongest chunks at the edges (lost in the middle), or nearest the question (Cuconasu et al.). It matters most with a wide top-k.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Why does RAG work at all?
  back: Attention lets every generated token look at the retrieved documents, so the context can change the output without changing the weights.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: How many passages should the reader get?
  back: Depends on the reader. FiD, trained to fuse, gained from 10 to 100 passages; a reader that only concatenates loses quality as text is added, even with the gold sentence in.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Why use a JSON schema over a prompt request?
  back: The schema makes output parseable and gives you a validator. It doesn't make the content true.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: Why can a model still ignore good context?
  back: Its weights can pull harder than the context. Wu et al. show that the further a context departs from the model's prior, the more it trusts itself.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: What is pseudo-helpfulness?
  back: Zhao et al.'s term for models answering when the gold passage is absent, using loosely related context or invention. Nine prompt variants made no salient difference.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: Are citations proof of attribution?
  back: No. Appending all retrieved sources records what the model saw. Per-claim matching such as ContextCite records what it used.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: What do RAGAS relevancy and faithfulness measure?
  back: 'Relevancy: generate prompts that could have produced the answer and compare with the real prompt. Faithfulness: the share of extracted claims supported by the documents. Both lean on an LLM judge.'
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: RAG or fine-tuning?
  back: 'RAG for knowledge and freshness, fine-tuning for behaviour and format. Balaguer et al.: GPT-4 went 75% → 81% fine-tuned and 86% with RAG on top. RARE trains with retrieved documents in the prompt to get both.'
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: When do you split one call into a workflow?
  back: When small steps such as routing and relevance checks can run on a cheap model, or the task needs branches or loops. Start simple and validate each output.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: What can a no-LLM check catch, and what does it miss?
  back: Missing or invalid `[DOC n]` ids, uncited claims, and numbers absent from the cited text. It misses unsupported claims attached to a correct number, which still need a judge.
  lesson: generative-ai/02-rag-retrieval/notes/06b-hallucinations-evaluation-and-fine-tuning
- front: How do you evaluate a RAG system?
  back: 'By scope and evaluator: component and system, each with code checks, LLM judges and humans. Code runs on everything, judges cover the rest, and humans calibrate both.'
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What does a trace need to show?
  back: The original and rewritten query, retrieved chunks with scores, reranker output, the final prompt, the response, and tokens and latency per span.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What is the flywheel?
  back: Traces to failure cases to datasets to fixes to experiments to deployment, then round again.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: How do you reduce memory for vectors?
  back: float32 to int8 is 4× smaller. 1-bit is 32× smaller and needs rescoring at higher precision. Matryoshka embeddings can be truncated.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: Where does the money go?
  back: Mostly LLM tokens, so cut prompt size and `top_k` first. Huyen reports vector-database spend at a fifth to a half of model API spend at some companies, so it's not negligible either.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: Where does the latency go?
  back: Mostly the transformer. Then measure each component (the course estimates reranker ~50 ms, rewriter ~300 ms, router ~200 ms) and keep those that move a metric.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What does ARES add?
  back: Lightweight judges fine-tuned on synthetic data, corrected with about 150 human labels through prediction-powered inference.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: Which production metrics do you watch?
  back: Hallucination rate, precision and recall at k, p95 latency, cost per query, user trust, and claim-level accuracy for CRAG systems.
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: What is knowledge poisoning?
  back: Crafted documents in the corpus get retrieved for a target question and steer the answer, as in PoisonedRAG. Separate ingestion from the app and sanitise retrieved chunks.
  lesson: generative-ai/02-rag-retrieval/notes/07b-security-changing-text-multimodal-and-live-indexes
- front: Are injection regexes enough?
  back: No. They miss paraphrases and over-block benign text. Use them as a first filter, log drops, and add a model-based classifier.
  lesson: generative-ai/02-rag-retrieval/notes/07b-security-changing-text-multimodal-and-live-indexes
- front: How do you retrieve from rules that change over time?
  back: Store published, effective-from and effective-to dates on each version, and filter on the effective dates with the as-of date in the query. Resolve cross-references and check quotes against the same date.
  lesson: generative-ai/02-rag-retrieval/notes/07b-security-changing-text-multimodal-and-live-indexes
- front: Why two pipelines inside one agent?
  back: Similarity search finds passages. It cannot filter, count or compare, so structured questions go to Text-to-SQL.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: What does the clarify step buy?
  back: It fixes tools and scope before retrieval, and it fails fast on queries that name nothing to search for.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Walk through PRINCE's query-time funnel.
  back: Keywords, a metadata filter and 5 expansions; 5 pre-filtered hybrid searches at 0.7 kNN and 0.3 keyword; the max score per chunk to k about 20; `bge-reranker-large` to k = 7; the answer with citations.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Why pre-filter inside the vector query?
  back: It shrinks millions of vectors to tens or hundreds before similarity runs, so results are all valid and k does not get used up on the wrong study.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Why the max across expansions, not the sum?
  back: Paraphrases are not independent votes. The max asks whether any phrasing found the chunk strongly.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: What is the rerank target?
  back: The original question, never an expansion. PRINCE and the LLM Twin both follow this.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: How does dynamic few-shot work?
  back: Question and SQL pairs live in their own vector collection; the nearest pairs go into the prompt; new pairs are added when a pattern fails.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: What is SELECT-only validation missing?
  back: It allows reads of sensitive tables and long-running queries. Add a read-only role, an allowed table list and a timeout.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Name five kinds of router.
  back: Logical, keyword, zero-shot classifier, function calling, semantic.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: What happens as tools multiply?
  back: They overlap and selection accuracy falls. PRINCE added Think & Plan, then domain sub-agents with their own tools and prompts.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: How does PRINCE repair metadata safely?
  back: 'NER with a per-field confidence score: high confidence updates Athena, low confidence goes to a human quarantine queue.'
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: What runs daily without references?
  back: Live-traffic evals for faithfulness and answer relevancy. Reference-based dataset evals run on every significant change.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: Why is a semantic router a retrieval problem?
  back: It embeds route descriptions and picks the nearest, so it misroutes the way a retriever misranks. Score it on labelled queries; TURA lifted Recall@5 from 0.42 to 0.83 by embedding synthetic queries per route and splitting multi-intent queries.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: What context does each PRINCE agent get?
  back: Think & Plan gets the goal, progress and tools; the Text-to-SQL researcher gets only the relevant schema slice; reflection gets the question and evidence; the writer gets curated chunks with citation constraints.
  lesson: generative-ai/02-rag-retrieval/notes/08b-routing-sub-agents-and-evaluation
- front: What three questions pick a store?
  back: How many vectors, how many dimensions, and does a query need keyword and dense together.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: When is exact search enough?
  back: 'When the scan is small next to the model call and concurrency is modest: on this machine, around 100k vectors at a few hundred dimensions. It also has perfect recall and no parameters.'
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: What is pgvector's dimension limit?
  back: HNSW and IVFFlat index up to 2,000 dimensions for `vector` and 4,000 for `halfvec`. A column can hold 16,000, searched exactly.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: How do you get hybrid search on a dense-only store?
  back: Run a separate keyword search and fuse the ranked lists with RRF in the application.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: HNSW or Annoy for a live corpus?
  back: HNSW, because it takes incremental inserts. Annoy needs a full rebuild, so stale content lingers until the next one.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: When is OpenSearch or Elasticsearch worth the operations?
  back: At scale, when one query must combine BM25, dense and metadata, or if you already run a cluster.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: What does a managed service cost you?
  back: 'Visibility: Discovery Engine is a black box, and Bedrock KB hides the raw score. You trade calibration and chunk control for zero operations.'
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: Name retrieval levers that apply to any store.
  back: Hybrid search, reranking, multi-query, parent-child chunking, CRAG.
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: Do you embed queries and documents the same way?
  back: 'Not with every model. E5 is trained on prefixed text, so queries start with `query: ` and passages with `passage: `, and its model card warns of degraded performance without them.'
  lesson: generative-ai/02-rag-retrieval/notes/09-vector-database-comparison
- front: What does a semantic cache save?
  back: 'The whole retrieval and generation path on a hit: in the production agent about 3 to 6 s and two or more LLM calls, for the price of one embedding and a matrix multiply.'
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: How does it differ from an exact cache?
  back: It matches on meaning, so it catches paraphrases, and it can match wrongly. An exact cache never serves the wrong answer.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: What is the main risk?
  back: 'A false hit: a near-identical question with a different meaning gets a confident wrong answer, and no later stage checks it.'
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: How do you set the threshold?
  back: Sweep it on labelled paraphrases and hard near misses for your model, then choose on the relative cost of a wrong answer and a miss.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: Does a threshold transfer across embedders?
  back: No. Cosine scales differ by model and by language.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: What goes in a cache row?
  back: The question vector, the answer, the source ids, the build date, a quality score, and the scope if not public.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: How do you handle staleness?
  back: Invalidate rows when a source document changes, with an age limit as a backstop.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: Do you need an ANN index for it?
  back: Not at a few hundred rows. A matrix multiply is enough.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: What is a centroid router?
  back: The mean embedding of example queries per intent; a query takes the closest one, or falls to flat search below a floor. It reuses the embedding with no LLM call.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: How do you decide between keyword, centroid and LLM routing?
  back: Run an ablation on source precision, MRR, quality and latency. Ship the cheapest variant that ties.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: What should block a merge?
  back: Regression on the miss path, a hit subset below baseline quality, or hit latency above budget.
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: Where does a semantic cache sit in the request path?
  back: 'In this support agent it is Tier 1, ahead of any LLM or retrieval call: embed the query, cosine match against the golden seed, and return the cached answer on a hit of 0.85 or more.'
  lesson: generative-ai/02-rag-retrieval/notes/10-semantic-cache
- front: What is an ablation?
  back: Change one component at a time, score each configuration on the same queries, and compare. It separates each change's effect and shows interactions.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: What interaction did the ablation find?
  back: A thinking budget gained +0.165 MRR on the tool-loop agent but hurt the graph agent with CRAG, because thinking changed citation style and broke the grader's alignment.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: How would you judge a +0.03 MRR on 32 queries?
  back: Not yet real. Worst-case SE of one mean is 0.088. Compute a paired bootstrap interval on per-query differences.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: Why a paired test?
  back: The same queries go through both systems, so per-query difficulty cancels and the comparison is tighter.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: How does multi-query help, and what does it cost?
  back: 'It covers lexical variance by retrieving for 2 or 3 reformulations and merging. Cost: one LLM call and one retrieval per variant. It helps keyword search most.'
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: How does HyDE differ?
  back: It embeds a generated hypothetical answer in place of the query. At least one LLM call, one long bet on the corpus's vocabulary. The paper tested it only with pure vector search.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: Why did the LLM planner lose to a regex?
  back: -0.031 MRR and +4 s. For a narrow edge-case vocabulary the rule was simply better, so test before assuming an LLM wins.
  lesson: generative-ai/02-rag-retrieval/notes/11-retrieval-improvements
- front: What is a coverage gap?
  back: A gold document that was never indexed. It lowers scores and no ranker can fix it, so filter or report it separately.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: Why keep URL mapping in a data file?
  back: KB migrations become a data change, not a redeploy, and agents stay KB-agnostic.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: Why not alias the product glossary?
  back: It has no canonical article equivalent, so it is excluded from coverage. Definition queries use it for context only.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: Why is DPO last?
  back: It needs 200+ pairs and golden responses. 32 queries with 5 configs cap out at 192 correlated pairs, and none were stored.
  lesson: generative-ai/02-rag-retrieval/notes/11b-training-the-pieces-and-the-pipeline-eval
- front: What does a managed RAG service give you?
  back: Crawling, parsing, chunking, indexing and search as a service, and optionally reranking and generation.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What can't you hand over?
  back: The eval set, the decisions about what goes in the index, and interpreting scores.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Bedrock's fast and reranking modes?
  back: 'Fast: 5 results, cosine threshold 0.4, no reranker, for the agent tool. Reranking: 15 candidates to 5 with `amazon.rerank-v1:0`, threshold 0.05, for eval and complex queries.'
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Can you compare a 0.4 cosine with a 0.2 reranker score?
  back: No. Different scales, per mode and per backend. Compare systems on eval metrics.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: When is Bedrock's hybrid search not hybrid?
  back: When the vector store isn't one of the supported types with a filterable text field. It uses semantic search instead.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What do `AMAZON_BEDROCK_TEXT_CHUNK` and `AMAZON_BEDROCK_TEXT` hold?
  back: The leaf chunk that matched, and the larger parent context the LLM reads.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Why fire multi-query with `asyncio.to_thread`?
  back: boto3 is synchronous, so threads give parallel calls without blocking the event loop.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: How do you deduplicate across query variants?
  back: Sort by score, fingerprint `url` plus the first 200 characters, and keep the first occurrence.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Main differences between Bedrock and Vertex?
  back: Bedrock is stateless, explicit and leaves generation to you. Vertex is more opaque, has sessions, and `:answer` can own retrieval and generation.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: What is a grounding score, and what doesn't it tell you?
  back: How well the source passages support the answer. It doesn't tell you the sources were correct or current.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: When would you leave `:answer`?
  back: When you need correction loops or control over synthesis, since you can't intercept its retrieval step.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: When is pgvector right?
  back: Local dev, or a stack already on Postgres. You give up managed hybrid and reranking and take on the infrastructure work.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Why keep a pipeline deterministic?
  back: 'Retrieve once, rerank, generate: predictable latency and easier to debug. Loops live in the graph agent, and leaked config was removed.'
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Why does the delta gate exist?
  back: A borderline top score with a clear gap to the runner-up is more trustworthy than a tie.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
- front: Why `[^\S\n]+` and not `\s+`?
  back: It normalises horizontal whitespace and keeps the newlines that heading-aware chunking needs.
  lesson: generative-ai/02-rag-retrieval/notes/12-managed-rag
---
