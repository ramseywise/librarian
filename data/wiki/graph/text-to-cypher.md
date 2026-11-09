---
title: Text-to-Cypher
tags: [graph, rag, pattern]
summary: "LLM-generated Cypher over a knowledge graph is reliable only as a generate-then-verify loop: an annotated LLM-ready schema, relationships-before-query output ordering, intent detection, a pre-execution EXPLAIN validator and a bounded retry edge — and it belongs last in the retrieval order, after vector search and canned traversals."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--11-kg-rag-and-text-to-cypher.md
  - data/raw/papers/2026-11-08-kg-and-llms-in-action-ch14-natural-language-kg-questions.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch15-qa-agent-with-langgraph.md
---

# Text-to-Cypher

Text-to-Cypher lets a model answer open-ended structured questions over a knowledge graph by
writing a graph query from the schema. It is the graph analogue of
[[Text-to-SQL as a Retrieval Strategy]], and it fails the same way: plausible-looking schema
mistakes. Treat it as a **generate-then-verify loop**, never as a single call.

## Where it sits in the retrieval order

Start with vector search; add **canned traversals** (fixed Cypher templates keyed by entities
extracted from the question: shortest paths, k-hop neighbourhood) for multi-hop question
shapes you can name; add text-to-Cypher only for the long tail, and only with a validator. A
book-length treatment of KG-powered RAG makes the same call: its ReAct agent's tools use
precanned Cypher because free-form generation fails too often, with vector search as a
fallback. This is "structure what you know, leave agency where you don't" applied to
retrieval (see [[Knowledge Graph Retrieval]] for the full mode table).

## Schema first: think like the domain expert

An expert does not read paragraphs; they know the schema and build a constrained traversal:

1. **Parse** the question into entities, relationships and constraints (colour, model, area,
   time window).
2. **Map** them onto schema labels and relationship types.
3. **Construct** the Cypher, with constraints as parameters (`$startTime`, `$areaRadius`).

### An LLM-ready schema

Raw `apoc.meta.schema` output is the wrong input. Transform it:

- **Filter** with a skip list: internal labels, embeddings, housekeeping properties.
- **Annotate** labels, relationship types and properties with `/* comments */`: value
  encodings (`status: 1 = open`), direction semantics, units.
- **Name things well upstream.** A model cannot use a relationship called `REL_7`.

## Prompt and output shape

The reference prompt has nine parts: task and question; annotated schema; intent-dependent
requirements (a map needs coordinates, a graph view needs named relationships); few-shot
examples; the user's current selection; KG-specific notes; the question restated; the
requirements restated; the output format.

Order the output fields so the model commits to the schema before writing the query:

```json
{ "relationships": ["..."], "reasoning": "...", "query": "<Cypher>", "success": true }
```

Listing `relationships` first reduces invented relationship types — chain-of-thought ordering:
an answer written before its reasoning is a guess the reasoning then rationalises. Few-shot
examples must use the same format.

### Two-level intent detection

Before generating anything, classify (1) the **request type** — data question, question about
the system, or feedback/complaint; only data questions go to Cypher — and (2) the **output
form** — graph, table, chart or map — which changes what the query must `RETURN`.

## The failure to expect

A LangChain `GraphCypherQAChain`, told to follow the schema, still summed a `value` property on
a `Company` node; the property actually lived on the `OWNS_STOCK_IN` relationship. **One
few-shot example with the right pattern fixed it.** These are exactly the errors a schema check
catches.

## The QA agent as a graph

The reference implementation is a LangGraph pipeline:

```
START → intent_detection → schema_extraction → text_to_cypher → query_execution
                                  ▲                                   │
                                  └────────── retry (≤3) ─────────────┤
                                                    summarize → generate_summary → END
```

```python
def post_query_execution(state):
    if state["results_error"] is not None:
        return "retry" if state["retries"] < 3 else "END"
    return "summarize" if state["output_type"] in ("map", "graph") else "END"
```

- **Generate-then-verify:** the database is the verifier; its error message is fed back into
  the next prompt.
- **Bounded back-edge:** three retries, then stop.
- **Typed state as audit trail:** `output_type_reason`, `query_reasoning`, `results_error` are
  kept, which also yields a free dataset of failures and few-shot candidates.
- **Checkpointer** at compile time.

**What it lacks — add it:** a validator that runs *before* execution. `EXPLAIN` checks the
query parses and plans without running it; compare the labels and relationship types it uses
against the schema. Wrong queries are caught before they reach a live database, and the repair
is cheaper.

Summaries are generated only for graph or map outputs where analysis was asked for, and should
point out what the visualisation does not make obvious rather than restate it.

## Evidence from the Manning book chapters

The Manning book *Knowledge Graphs and LLMs in Action* devotes chapters 14 and 15 to this design (read here through extractions); they present a demonstration, not an evaluated system.

- **Why not plain RAG.** The chapter's illustration is five invented witness statements in a detective prompt: removing a single statement turned the model's verdict on whether the perpetrator is left-handed from probably yes to probably no. It is one anecdotal run with an unnamed model.
- **Intent detection.** One question was classified as Data-Related by a smaller or quantized model but as System-Related or Documentation-Related by a full-scale model (models unnamed, no accuracy). The chapter recommends a reason field in the classifier output to debug misclassifications and to harvest boundary cases as new few-shot examples, and biasing the fallback class toward graph output.
- **Schema as YAML.** A YAML file with skip lists (classes, relationships, properties) and descriptions turns `apoc.meta.schema` output into the conceptual schema. The implementation's schema provider reads the entire database through `apoc.meta.schema`, with no sampling.
- **Reasoning-first output.** The authors assert (self-reported) that listing relationships before the reasoning and query significantly reduces relationship hallucination, and that reasoning-first beats answer-first because the model commits to an early answer (they call this semantic consistency). Both are shown qualitatively on one path-finding task, not measured. For classification they put the answer first, since the reasoning there is for diagnosis.
- **Pipeline behaviour (chapter 15).** When a query fails, the text-to-Cypher node is run again with the error attached, at most three times. A summary step exists only for graph and map results; a table ends the run. Events are streamed as (type, payload, state) tuples to a Streamlit front end. A five-step investigation on a crime and ANPR-camera KG is shown with screenshots only.
- **Future work.** The authors cite studies that in-context learning underperforms task-specific adaptation and propose fine-tuning; for large KGs they suggest agents that enrich the schema, and layered schemas.

### Limits of these chapters

- The extraction notes no quantitative evaluation anywhere (accuracy, latency, cost), no model identity or temperature for the pipeline, and the law-enforcement data is invented, so generality is asserted.
- The chapters compare against no schema-free or alternative text-to-Cypher approach, and their hallucination-reduction claims go unmeasured. The authors call the code a foundation rather than a turnkey solution.
- The extraction notes that chapter 15's listings are inconsistent (a state key named `output_reason` against `output_type_reason`, a misspelt `summary_analisys`, an undefined `self.memory`), and that the code catches only `ClientError`, which means an empty result never triggers a retry.
- The reference list is not in the chapter 14 extraction.

## See Also
- [[Knowledge Graph Retrieval]] — extends
- [[Text-to-SQL as a Retrieval Strategy]] — alternative-to
- [[Knowledge Graph Fundamentals and Cypher]] — prerequisite-for
- [[Graph Topology Primitives]] — instance-of
- [[Multi-Agent Failure Modes at Scale]] — extends
- [[Knowledge Graph Entity Resolution]] — prerequisite-for
- [[Degree-Weighted Path Count (DWPC)]] — related (LLM-drafted metapath Cypher)
- [[GrailQA Three Levels of KBQA Generalization]] — related
