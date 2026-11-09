---
title: Knowledge Graph Retrieval
tags: [rag, llm, concept]
summary: "Vector search finds things that sound like your question; graphs find things that are connected to your answer — but traversal depth compounds error, which makes entity resolution the load-bearing sub-problem."
updated: 2026-11-08
sources:
  - data/raw/articles/2026-07-19-knowledge-graphs-for-rag.md
  - data/raw/claude-docs/playground/docs/support-agents/accounting-knowledge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--README.md
  - data/raw/claude-docs/project-g/docs/support-agents/accounting-knowledge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--11-kg-rag-and-text-to-cypher.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--graph-engineering.md
  - data/raw/papers/2026-11-06-klein-2025-ark-v1.md
  - data/raw/papers/2026-11-06-dong-2026-wfm.md
  - data/raw/papers/2026-11-08-peng-2024-graph-retrieval-augmented-generation.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch07-creating-connecting-knowledge-graph-ai-agen.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch13-kg-powered-rag.md
---

# Knowledge Graph Retrieval

The **second sense** of graph in [[Graph Engineering]]: a graph as *retrieval structure*
rather than as execution topology. Nodes are entities (people, places, concepts), edges are
typed relationships, and the graph encodes structured world knowledge that a RAG pipeline
queries instead of — or alongside — a vector index.

Keeping the two senses distinct matters, because they share a word and almost nothing else:

| | Agent graph | Knowledge graph |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

## Why it beats vector-only

> **"Vector search finds things that sound like your question. Graphs find things that are
> connected to your answer."**

That is the whole case, and it is a case about **multi-hop** questions specifically.
No general graph-vs-vector accuracy number is quoted here: the widely repeated
"53.4% vs 42.9% multi-hop" figures trace to a vendor blog with no stated method. The primary
evidence is the GraphRAG paper below — LLM-judged comprehensiveness and diversity wins on
global sensemaking questions, with vector RAG winning on directness.

Single-hop lookups do not need a graph — semantic similarity already answers them. The
graph earns its cost where the answer requires following relationships the question does
not name.

### Where vector RAG breaks, and what a graph adds

Chunk-and-embed retrieval fails by **context fragmentation** (a fact split across chunks needs
every piece retrieved near the top), **embedding compression** (one vector per chunk loses
entity-level detail; rare terms embed poorly), **noise** and **misses** (similarity optimises
closeness, not coverage, so aggregate questions get partial answers). Near-identical cosine
scores do not guarantee that the named entity is even present in a chunk, and removing one
key passage can make the model **reverse its conclusion with the same confidence** — it can't
tell something is missing.

A graph adds multi-hop traversal, **entity-exact retrieval** ("documents mentioning *all* of
these entities"), **aggregation** over the whole graph instead of a top-k sample, metadata
routing (latest version, by source), **traceable answers** (return the path) and composed
retrieval (resolve an entity in the KG, then search documents for it). Make the graph
**text-attributed** (nodes and edges carry descriptive text) and **text-paired** (every node
and edge links back to its source documents).

### The evidence

The primary source is the GraphRAG paper (*From Local to Global*, arXiv 2404.16130): build an
entity graph, detect and pre-summarise communities, then answer **global sensemaking**
questions over ~1M-token corpora. Against vector RAG it reports comprehensiveness win rates of
72–83% (podcasts) and 72–80% (news), diversity win rates of 75–82% and 62–71% — while **vector
RAG wins on directness**. The judge was an LLM in head-to-head comparisons, not a ground-truth
accuracy measure: the result is "community summaries help whole-corpus questions", **not**
"graphs are more accurate than vectors".

## The compounding-error caveat

The number above comes with a caveat that is more useful than the number:

> At 85% per-hop accuracy, **"a 5-hop traversal is only 44% trustworthy."**

`0.85^5 ≈ 0.44`. **Traversal depth compounds error multiplicatively**, so deep traversal is
not a feature you turn on — it is a budget you spend. Two consequences:

1. **Bound traversal depth explicitly.** Unbounded traversal on a large graph produces
   confident nonsense at depth 5+.
2. **Entity resolution is the load-bearing sub-problem, not an implementation detail.**
   Per-hop accuracy *is* entity-resolution accuracy for most of the pipeline. Improving the
   retrieval model while entity resolution stays at 85% moves nothing.

## Retrieval modes

| Mode | How it retrieves | Use when | Fails when |
|---|---|---|---|
| Vector | Top-k chunks | Local lookups | Multi-hop, aggregates, exact entity constraints |
| Canned traversal | Fixed Cypher templates keyed by entities (k-hop, shortest path) | Known question shapes; production paths | A shape you didn't template |
| [[Text-to-Cypher]] | LLM writes Cypher from the schema | Open-ended structured questions over a well-named schema | Large or badly named schema; no validator |
| Hybrid | Vector finds entry chunks/entities, graph expands | Text-heavy corpora | Wrong entry points make expansion worse |
| Global (GraphRAG) | Pre-summarised communities, map-reduce | "Themes across everything?" | Specific lookups; high indexing cost |

**Default order:** start with vector; add canned traversals for the multi-hop shapes you can
name; add text-to-Cypher only for the long tail, and only with a validator.

**Triples lose meaning.** "If it rains next week I'll cancel the beach trip and go to the
museum" becomes `(user, plans, beach trip)` and `(user, backup, museum)` — the condition is
gone. *AI Agents in Depth* recommends keeping the core record in natural language and using
the graph as an **index** for domains that need multi-hop and disambiguation (medical, legal,
family relationships).

## Typed edges carry the knowledge

> **"The edge type IS the knowledge."**

An untyped edge asserts only that two things are related, which is barely more than
co-occurrence. See [[Graph Topology Primitives]] for the six-edge-type production minimum
(`SUPERSEDES`, `DEPENDS_ON`, `DECIDED_BY`, `CAUSED`, `IMPLEMENTS`, `REFERENCES`).

## You do not need a graph database

The community consensus on what actually matters:

> *"Small typed core, cheap indexing, hybrid retrieval, temporal supersession. **All four
> of those are implementable on markdown files you own.**"*

This wiki is an existence proof: `[[wikilink]]` edges with `— type` suffixes are a small
typed core; the relinker is cheap indexing; the MCP server's search is hybrid retrieval;
tombstone pages are temporal supersession. **The graph-database question is an
implementation detail downstream of getting those four right.**

## Hybrid, not replacement

Graph retrieval sits *alongside* vector search rather than replacing it — it is another
entry in the strategy table of [[RAG Retrieval Strategies]]: semantic similarity for "what
sounds relevant," graph traversal for "what is connected." Routing between them is a
decision the retrieval layer makes per query, not a global architecture choice.

## Where a graph earns its keep in support knowledge (playground notes)

An accounting-support corpus splits into three knowledge layers. **Procedural** how-to
content is served well by flat retrieval. **Regulatory rules** and **entity relationships**
(which form applies to which entity type under which threshold) are where multi-hop
questions live, and that is the only place a graph adds value. Design notes:

- The graph is small (hundreds of nodes), so a JSON adjacency file or a community-edition
  graph DB is enough. No graph platform is needed.
- Query it hybrid-style: Cypher for the structural hop, vector search for the text.
- Each jurisdiction is a separate graph, so every node needs a locale scope. Without one,
  a rule from one country answers a question about another.
- A graph adds nothing to the semantic cache. The cache keys on query similarity, not on
  structure.

## Course notes: construction noise, two-stage hybrid, GraphRAG

From a knowledge-graphs-for-RAG short course:

- **Construction is a noisy pipeline** — NER, relation extraction, coreference resolution,
  entity dedup, load — and every stage adds error, so retrieval quality is bounded by
  extraction quality. **Schema-constrained graphs** over a known entity schema (e.g.
  regulatory filings) outperform open-domain construction.
- **Two-stage hybrid:** vector search returns candidate chunks → entities extracted from
  those chunks anchor a Cypher query → the LLM receives both the unstructured chunks and the
  structured facts. This is the multi-hop pattern over heterogeneous data.
- **Know the relation types before querying.** A Cypher pattern like
  `MATCH (n:Entity)-[:RELATION]->(m)` is only useful if the schema's relation types are known.
- **GraphRAG (community summaries):** community detection over the graph produces
  summaries at several granularities; global questions are answered from community
  summaries, local questions from entity neighbourhoods — the synthesis-across-many-entities
  case flat vector search cannot serve.

## Paper evidence: agents and learned retrievers over graphs (2025-2026)

All figures are self-reported by preprints.

- **ARK-V1, a non-fine-tuned graph agent.** It loops through choosing an anchor entity, choosing an outgoing relation, retrieving triples and reasoning, then summarises and resets its context so only the system prompt, the query and the running summary remain. Setup: the CoLoTa set of 200 binary tasks, with Qwen3-30B sampled at temperature 0.7 over 30 runs: answer rate 76.98%, conditional accuracy 91.22%, overall 70.20%. The o1 chain-of-thought baselines (65 to 68% overall) are figures reported externally, so the comparison is not like for like. Small backbones abstain heavily (Qwen3-8B answer rate 57.67%, overall 48.42%).
- **WFM, a graph foundation model used as a retriever.** A text-augmented graph with dense passage nodes and a GAT-style encoder. Setup: 1,000 held-out questions per set, DeepSeek V4 Flash generator, DeepSeek V4 Pro judge. Accuracy in open and reject mode was 89.6 and 84.3 on HotpotQA, 90.2 and 82.4 on 2Wiki, and 69.8 and 52.6 on MuSiQue, ahead of Youtu-GraphRAG by 2.8 to 5.1 points. Replacing the passage-node graph with an entity-only graph cost 7.48 points of recall.
- **Prompt-only GraphRAG against plain RAG.** A-RAG and Graph-R1 both report graph methods that rely on prompting underperforming or not consistently beating chunk RAG; see [[Graph-R1 Agentic GraphRAG]].

## Surveys and book chapters on GraphRAG (2024-2025)

Method pages for named approaches: [[GraphRAG Local-to-Global Community Summaries]], [[Reasoning on Graphs]], [[MIRAGE Parallel Graph-Retrieval Reasoning Chains]], [[Graph Neural Prompting]], [[Knowledge Graph Prompting for Multi-Document QA]]; the KBQA benchmark behind several of them is [[GrailQA Three Levels of KBQA Generalization]].

- **Survey workflow (Peng and co-authors, J. ACM preprint).** The survey divides GraphRAG into three stages (G-Indexing, G-Retrieval, G-Generation) and describes it as fetching graph elements (nodes, triples, paths, subgraphs) in place of text chunks, aiming at three RAG weaknesses: ignored relationships, repetitive context and no global view. Its statements are qualitative, with no experiment of its own: hybrid indexing over graph, text and vector indices is preferred; non-parametric retrievers are cheap but may be inaccurate while LM and GNN retrievers cost more, so multi-stage designs are common; once-only retrieval suits real-time use and iterative retrieval is slower but can be more accurate; fine granularity suits simple or latency-bound queries and hybrid granularity complex ones; a graph language for the generator should be complete, concise and comprehensible, whereas graph embeddings avoid long input but lose exact entity names. It describes TIARA (constrained decoding over KB classes and relations) and UniOQA (a Cypher answer and a triplet answer, chosen by a selection step), and lists GRBench, 1,740 questions over 10 domain graphs, as described from its original authors. Open problems it names: most methods target graphs of thousands of entities while industrial graphs hold millions or billions, there is no unified benchmark, lossless compression of linearised graph context is unsolved, and retrievers trained on this task have no labelled retrieval targets, so they rely on distant supervision or RL.
- **Packt chapter 7 (Raieli and Iuculano).** It adopts the same three-step framing, citing the survey without naming its authors, and gives a five-stage construction path (creation, assessment, cleaning, enrichment, deployment). It states without data that a graph distilled from a small LLM by prompting for triplets is competitive with text-built ones, and relays MedGraphRAG, HybridRAG and a materials-science multi-agent graph with no scores. Its open problems include weaker GraphRAG results on abstractive questions and on questions that do not name an entity. It reports that LLMs read graphs as linear text and weight node labels over topology (one illustrative figure). The extraction notes that its graph-of-thoughts worked example mixes miles and kilometres.
- **Manning chapter 13 (Negro and co-authors).** A ReAct agent with three tools (a KG retriever, a KG-enhanced document retriever and a vector-search backup) runs over the Rockefeller Archive Center graph in Neo4j, with gpt-4o-mini at temperature 0. Setup: single illustrative runs, no accuracy measured. For a question about Lauritsen and cyclotron research, just one of the three best vector hits mentioned Lauritsen, even though all three scored almost the same cosine similarity; a question about Wrinch took four reasoning-action-observation steps; a Harvard versus Johns Hopkins aggregate was answered from a correct but clumsy Cypher query. Its advice: use parametrised, precanned Cypher tools for frequent question types, put the KG schema in tool descriptions, and test repeatedly with the same input.

## Limits

- WFM: the authors flag the new table cells and diagnostic sweeps as planning values they built, to be validated later, so the headline numbers are unverified. In its memory table the RHELM zero-shot full-context baseline (46.8) beats every retrieval method except WFM, and WFM without reflection (48.90) leads it by only 2.1. The ACM template is unfilled.
- ARK-V1: one dataset with binary tasks; large-backbone rows are single runs at temperature 0 with no variance.
- Surveys and chapters above: the Peng survey has no scores in its benchmark table, so no method comparison follows from it; chapter 7 shows partial tutorial code with LangChain classes since moved; chapter 13 is illustration only, calls itself not production-ready and names missing re-ranking and Cypher self-correction.

## See Also
- [[Graph Engineering]] — extends
- [[Knowledge Graph as Shared Agent Memory]] — prerequisite-for (the same structure used as write-path memory)
- [[Graph Topology Primitives]] — extends (typed edges)
- [[RAG Retrieval Strategies]] — alternative-to (similarity retrieval vs connection retrieval)
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for (fusing graph and vector result lists)
- [[Text-to-Cypher]] — prerequisite-for
- [[Knowledge Graph Entity Resolution]] — extends (the load-bearing sub-problem)
- [[Knowledge Graph Fundamentals and Cypher]] — extends
- [[Compiled-Prose KB vs Graph-Native Store]] — alternative-to
- [[Graph-R1 Agentic GraphRAG]] — instance-of (an RL-trained agent over a hypergraph)
- [[CorpusMap Entity Navigation for Agentic Search]] — alternative-to (entity navigation for an agent instead of a graph query)
- [[STAIR ToC-Constrained Generation Retrieval]] — alternative-to (a document's table of contents as the retrieval structure)
- [[GraphReader]] — instance-of
- [[LightPROF Knowledge Adapter for KGQA]] — related (a trained adapter encodes retrieved paths for a frozen LLM)
- [[CoAT Associative-Memory MCTS]] — related
- [[TANS Node Descriptions for Text-Free Graphs]] — related (LLM-generated node text for GNNs)
- [[Knowledge Graph Prompting for Multi-Document QA]] — instance-of
- [[Graph Neural Prompting]] — instance-of
