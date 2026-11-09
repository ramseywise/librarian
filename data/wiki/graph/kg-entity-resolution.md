---
title: Knowledge Graph Entity Resolution
tags: [graph, rag, pattern]
summary: "Building a KG from text with LLMs: extraction is the easy part — the graph is only as good as entity resolution, so keep raw mentions in a reversible metagraph, resolve with relational evidence (WCC, LLM clustering with descriptions, ontology NED), and gate loads on false-merge rate weighted above false-split."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--10-building-kgs-with-llms.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch05-extracting-domain-knowledge.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch06-building-kgs-with-llms.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch07-named-entity-disambiguation.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch08-ned-open-llms-ontologies.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-appendix-c-kgs-from-structured-sources.md
---

# Knowledge Graph Entity Resolution

One false merge silently joins two people, and every multi-hop answer passing through the join
is wrong. Extraction is the easy part of building a knowledge graph; **resolution is the
load-bearing step**.

## Why: errors compound with depth

If each hop is independently correct with probability *p*, an *n*-hop answer is correct with
*pⁿ*. At 85% per hop: 72% at 2 hops, 61% at 3, **44% at 5**. Hops aren't truly independent, but
the shape holds, and most per-hop errors are resolution errors (two entities merged, or one
split). Deep traversal is only worth it when resolution is good — see
[[Knowledge Graph Retrieval]].

## The pipeline

```
chunk → extract (mentions) → normalise → resolve (ER / NED) → assemble (+provenance) → evaluate (gate) → load
```

A model tier per stage, as in Anthropic's KG-construction cookbook: a small fast model
(Haiku-class) extracts into Pydantic models, a stronger model (Sonnet-class) resolves and
queries, assembly is deterministic (a NetworkX `MultiDiGraph` with `source_docs` on nodes and
`source_doc` on edges), and entity P/R is scored against a gold set. Use the model only where
judgement is needed — "spend agency per node" from [[Graph Topology Primitives]].

## Extraction lessons

- **Type names are instructions.** Renaming an entity type from "Topic" to "Occupation" improved
  extraction.
- **Schema-constrained output** (structured outputs, tool schemas, Pydantic), not free text plus
  a parser.
- **Temperature 0, then test stability**: run the same document several times; instability means
  an ambiguous prompt.
- **Prompt unit tests** on small inputs with known outputs, run on every prompt change.
- **Build a mini-KG from ~10 documents and look at it** before scaling; missing edge types and
  junk hubs are obvious.
- **Don't trust LLM character offsets** — recompute spans deterministically.
- **Fine-tune only when prompting plateaus**, and only once the evaluation gold set exists.

Traditional pipelines (spaCy/scispaCy) are cheap, deterministic and come with domain linkers
(UMLS IDs, which an LLM cannot assign by itself) but are weak at relations; LLMs are strong at
relations and new types. A common hybrid: a traditional linker where a domain KB exists, an LLM
for relations and long-tail types.

## ER vs NED

- **Entity resolution (ER):** which mentions are the same thing?
- **Named-entity disambiguation (NED):** which entry in a reference knowledge base does a mention
  denote? Use NED when an ontology exists (medicine, law, finance identifiers), ER when it
  doesn't.

### Keep mentions; resolution is reversible

```
(:Document)-[:HAS_PAGE]->(:Page)-[:MENTIONS]->(:Entity)    ← metagraph: raw mentions
(:Entity)-[:META_SIMILAR]->(:Entity)                        ← resolution evidence
(:Entity)-[:RESOLVES_TO]->(:Canonical)                      ← the KG proper
```

Extraction writes mentions; resolution writes similarity edges and canonical nodes on top.
Nothing is deleted, so the KG can be rebuilt whenever resolution changes. This reversibility is
what [[Knowledge Graph as Shared Agent Memory]] depends on.

### Graph-based ER

1. Normalise names (titles, case, punctuation).
2. Collect evidence: string similarity (obvious and risky) plus **relational signals** — same
   employer, same topics, same Louvain community, embedding proximity.
3. Write `META_SIMILAR` where evidence is strong enough.
4. Run **WCC** over `META_SIMILAR`; each component becomes one canonical entity.
5. Send borderline clusters to a **human review queue**. In the worked archive example, a
   physiologist turned up inside a physics subgraph because the extractor had respelled his
   surname to match a physicist on the same page — only a person looking at the graph caught it.

String similarity alone causes false merges; relational evidence tells two same-named people
apart.

### LLM-based ER

Give the model the unique names of one type **with their extraction descriptions** and ask for
`{canonical, aliases[]}` clusters. The descriptions are what prevent merging two different
people who share a surname. Failure modes: **dropped names** (fall back to a singleton cluster)
and **over-merging** (a numbered mission folded into its parent programme).

### NED against an ontology

1. **Candidate selection** via fuzzy full-text search over the ontology, filtered by NER type —
   **no LLM here**: candidates must come from the ontology, not model memory.
2. **Ranking:** find shortest paths between candidates and the document's other entities,
   **dropping hub nodes** that connect everything, verbalise and summarise the paths, then let
   the LLM choose. "Zika" next to "microcephaly" resolves to congenital Zika infection.
3. **Integration:** the resolved entity gains its ontology neighbourhood.

### Measure what normalisation did

Compare WCC counts and shortest-path distributions before and after. Three spellings of one
disease had split it into three nodes; after normalisation related nodes sit closer. If
resolution has no measurable structural effect, it probably isn't doing anything.

## Evaluation gate

Hand-label a gold set (50–100 mentions to start) and measure entity P/R, edge P/R over
(subject, type, object), **false-merge rate**, false-split rate and run-to-run stability.
**Weight false merges above false splits**: a split loses a connection; a merge invents
connections that traversal then follows confidently. Gate the load step on these the way CI
gates a deploy ([[Run-Then-Assert Eval CI]]).

## Assembly and integration

- **`MERGE` on a shared identity key is how sources are fused** — and only works once identities
  are resolved. Pair it with uniqueness constraints ([[Knowledge Graph Fundamentals and Cypher]]).
- **Curate before you scale**: a few task-relevant sources beat many loosely related ones.
- Structured-source integration swaps extraction for **identity mapping** onto shared codes
  (UMLS, Disease Ontology), **schema alignment** of edge semantics, and **validation** (counts,
  orphans, degree distributions) after each load.
- Generic clustering (WCC, Louvain) and domain-subgraph metrics (largest component, density,
  conductance) answer different questions; raw path counts favour hubs, which DWPC discounts
  ([[Graph Machine Learning and GNNs]]).

## Worked examples from the Manning book chapters

Reading extractions of chapters 5 to 8 and appendix C of *Knowledge Graphs and LLMs in Action* give the concrete runs behind the lessons above. All are single-corpus demonstrations judged by eye or by counts; none reports precision, recall or F1.

- **Extraction prompts (chapter 5).** On one paragraph of a Rockefeller Archive Center diary with GPT-4o mini at temperature 0, a generic first prompt split one relation concept into four relation types and gave the four research topics of one professor three different node labels. Running the identical prompt and settings a second time produced different output, so results were unstable even at temperature 0. The book reports that renaming the class Topic to Occupation gave more comprehensive, stable results, with no numbers. It recommends temperature 0 for fact extraction (about 0.2 for code), and says OpenAI charged 10 times more for a custom fine-tuned model than for the base one at the time of writing.
- **Three layers (chapter 6).** The graph is built as document, metagraph and KG layers so normalisation and resolution happen before the final KG, which can be rebuilt from the metagraph. The baseline links mentions by string similarity plus relatedness, runs WCC and names each group by its longest member; occupations are grouped through GPT or SentenceBERT embeddings and agglomerative clustering, which the chapter praises without giving a metric. The example uses 150 pages of a 1939 diary from a project of more than 10,000 pages (self-reported setup). A cyclotron influence query surfaced a researcher only through a respelled name, which the chapter uses to argue for an analyst feedback loop; a duplicate node was left unresolved.
- **NED with scispaCy (chapter 7).** On an EU health-document KG (Zika, dengue and SoHO, built with scispaCy, UMLS 2022AA, SNOMED CT 2022-09-01 and HPO in Neo4j), scispaCy ranks a distinct UMLS identifier first for each of three Zika mentions in one 3-sentence passage, while one informal ChatGPT prompt gave back surface terms and declined to assign UMLS identifiers. A repeated bulletin header inflates the co-occurrence counts (Communicable Diseases leads Zika's disease co-occurrences with 606, self-reported). Dropping the 350 highest-degree nodes reduced the shortest paths linking two SNOMED concepts from 11,185 down to 9 (self-reported), though those that remained still ran through generic nodes.
- **NED with an open LLM (chapter 8).** The pipeline runs LLM NER with categories taken from SNOMED first-level nodes, full-text candidate selection, then disambiguation by hub-filtered shortest paths that are verbalised and summarised, served by Llama 3.1 8B through Ollama at temperature 0. For one Zika and microcephaly sentence it picks Congenital Zika virus infection (762725007); the chapter gives no gold labels or comparison beyond that passage. It notes that scispaCy ranks Zika Virus Infection first for bare "Zika" and finds no candidate for "Zika disease" without cue words. Offsets are computed in Python because the LLM gives them poorly.
- **Normalising structured sources (appendix C).** In a miRNA-disease KG built from three association datasets (4,874 miRNAs, 118,806 connections and 1,144 diseases, against 1,207, 18,732 and 849 from HMDD alone), disease names were normalised to UMLS with scispaCy into separate NormalizedDisease nodes so the step could be reviewed and reset. WCC showed a giant component of 5,010 nodes before and 6,033 after, with no significant change. All-pairs shortest paths showed miRNA pairs at distance 1 up 4.5%, at distance 2 down 18.7% and at distance 5 down 52.1% (all appendix C figures self-reported) (a single distance-6 pair vanished). The chapter argues shorter paths give better embeddings but runs no link prediction to test it.

### Limits of these chapters

- Illustrated on one corpus each (150 pages in chapter 6, one passage in chapters 7 and 8); no accuracy figures, gold labels or sensitivity checks; hub threshold 350 is hand-chosen.
- Chapter 5 tested GPT-4o mini only and shows neither the final prompt nor the fine-tuning run; chapter 6 gives no models, prompts or thresholds. Chapter 8's results are from October 2024 and vary with model version, and candidate selection is full-text only.
- Chapter 7 results vary slightly by environment, indexing, ingestion order and scispaCy nondeterminism.
- Appendix C covers construction and exploration only: LLM-based normalisation is discussed, not run, and the all-pairs shortest path algorithm was still alpha-tier in Neo4j GDS when the book was written.

## See Also
- [[Knowledge Graph Fundamentals and Cypher]] — extends
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Knowledge Graph as Shared Agent Memory]] — prerequisite-for
- [[Memory Lifecycle]] — extends
- [[Text-to-Cypher]] — related
- [[Degree-Weighted Path Count (DWPC)]] — related (hub-damped path scoring on integrated graphs)
