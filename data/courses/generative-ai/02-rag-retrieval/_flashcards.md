---
generated_by: src/librarian/slides/flashcards.py
decks:
- generative-ai/02-rag-retrieval/slides/deck.yaml
cards:
- front: What three costs does RAG add?
  back: RAG gives the model facts at inference time, in exchange for latency, an index to maintain and a new way to fail.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: What is the smallest possible RAG?
  back: A working RAG is a fetch plus an f-string, and every technique after this improves the fetch or the template.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
- front: How does Self-Route decide when to use the full context?
  back: Long context can win on quality with frontier models, but retrieval stays cheaper and is the only option for large corpora.
  lesson: generative-ai/02-rag-retrieval/notes/02-why-rag-and-the-augmented-prompt
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
  lesson: generative-ai/02-rag-retrieval/notes/01-rag-pipeline
- front: Which query kind does BM25 miss, and which does dense miss?
  back: BM25 misses paraphrases and dense misses exact codes, so hybrid raises recall even if it doesn't improve every metric.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: What does the k in RRF do?
  back: RRF combines retrievers using ranks alone, so it needs no calibration and rewards documents both lists agree on.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
- front: 'MRR, MAP or nDCG: when do you use each?'
  back: Track recall first because it caps everything downstream, then pick MRR, MAP or nDCG according to your task and labels.
  lesson: generative-ai/02-rag-retrieval/notes/03-keyword-semantic-and-hybrid-search
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
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
- front: Why rerank if recall is already fine?
  back: Over-retrieve cheaply, rerank with a cross-encoder, and pass few chunks, because a longer list can hurt the answer itself.
  lesson: generative-ai/02-rag-retrieval/notes/05-chunking-query-parsing-and-reranking
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
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
- front: On Balaguer et al.'s task, what were the three scores?
  back: Use retrieval for facts that change and fine-tuning for behaviour, and expect the two to add up rather than compete.
  lesson: generative-ai/02-rag-retrieval/notes/06-generation-for-rag
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
  lesson: generative-ai/02-rag-retrieval/notes/07-rag-in-production
- front: Why the max across expansions, and not the sum?
  back: PRINCE narrows from millions of vectors to seven chunks by filtering first, taking max scores and reranking on the original.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: Why did PRINCE remove the LLM SQL reviewer?
  back: Send counting questions to SQL with retrieved examples and mechanical checks, since an LLM reviewer cost more than it caught.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
- front: When should you avoid agentic RAG?
  back: Agentic RAG pays for broad questions over messy data, and when one pass works, its extra machinery just adds latency.
  lesson: generative-ai/02-rag-retrieval/notes/08-agentic-rag-prince
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
---
