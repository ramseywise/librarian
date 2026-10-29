---
imported_hash: dcf137c7c5a5751c
title: Preparing Text Data for RAG
summary: ''
order: 14
kind: reading
section: Notebooks / Knowledge graphs for rag / Notes
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/notes/Lesson_3.md
---

# Preparing Text Data for RAG

- RAG systems are using text embeddings to match prompt to relevant sections within the unstructured data.
- Similarly to find text in knowledge graph, we'll need to create embeddings of the text fields in the graph.
- First step to enable vector search is to create vector index.

## Notebook

- [Jupyter Notebook](../code/l3-prep-text-for-rag.md)
- This notebook uses the movie database used in [previous lesson](lesson-2.md#notebook).
- [Pre-requisite](https://neo4j.com/docs/cypher-manual/current/genai-integrations/#_prerequisites): OpenAI account
- Signature for `genai.vector.encode()` is described in [GenAI integrations documentation](https://neo4j.com/docs/cypher-manual/current/genai-integrations/#single-embedding).
  - `genai.vector.encode(resource :: STRING, provider :: STRING, configuration :: MAP = {}) :: LIST<FLOAT>`
