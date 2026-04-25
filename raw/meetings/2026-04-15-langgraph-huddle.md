# LangGraph Huddle — Meeting Notes

**Date:** 2026-04-15
**Source:** Google Drive — Gemini Notes (gemini-notes@google.com)
**File ID:** 1ocL1fdyvErAg8Raduvv62ACiNznbzKxL_s7D0ftZ5n0
**Attendees:** Ramsey Wise, Yan Zhang, Axel Simond, Marco Enrique Zimmermann, Jeremy Simon

---

## Summary

Initial LangGraph proof of concept, focused on RAG for a help assistant, sparked discussion for further development with two separate teams.

### Initial POC Reviewed

Yan Zhang presented a LangGraph POC originally built for a RAG help assistant interview. It handles two request types: simple Q&A and text execution (no external API). The system uses a planner agent to detect request type. For text execution, it includes a HITL component to clarify missing information, then a confirmation plan node before execution. The POC contains 4 agents and 2 functions — 6 graph nodes total.

### Deterministic Workflow Benefits

LangGraph supports deterministic workflows, resulting in faster speed compared to non-deterministic frameworks like Autogen. Yan found no difference in end-user experience between graph-based RAG and vanilla RAG, though LangGraph was easier to build.

### Feature Prioritization and Assignments

Two teams formed to fork the repository:
- **Team A (Yan + Axel):** Co-pilot agent POC — routing functionalities, action items, LangGraph design
- **Team B (Ramsey + Marco):** Enhance RAG features — reranker, specialized vector storage, chunking, indexing, embedding, storage refactoring

---

## Key Discussion Points

### Framework Choice: LangGraph vs ADK

There was an open question about whether to invest in LangGraph since Shine uses Google ADK for all their services — making LangGraph "potentially more effort to build." Decision deferred to higher pay grades; team continues learning/prototyping both.

### Node Architecture

- Nodes can be agents (with LLM) or simple functions
- No known node limit in LangGraph
- Node selection for a given request is handled by the planner agent
- Graph states serve as memory management — supports global memory and sub-memory within agent system
- Conditional edges determine whether HITL intervention is required

### RAG Enhancement Plan (Team B — Ramsey + Marco)

Current POC uses LangChain in-memory vector store with a single `similarity_search_with_score` function. No chunking (files small enough to embed whole).

Planned enhancements:
- Add proper chunking, indexing, embedding pipeline
- Retrieval: BM25 dense, hybrid, recursive, or multi-query approaches
  - Multi-query: LLM translates query to 2-3 variants → broader net for dense retrieval
- Reranker: listwise LLM ranking or Microsoft ms-marco cross-encoder
- Vector store: Chroma DB (OpenSearch access lost)
- LangSmith integration for metrics/observability
- Escalation path (missing from current POC)
- Confidence gates (missing from current POC)

**Task split (coin flip):**
- Ramsey → retriever component
- Marco → reranker component

Both add their component as a new node + update the graph design diagram.

### Co-pilot Agent POC (Team A — Yan + Axel)

Focus on routing and action items. LangGraph's stateful graph design suits chain-of-thought and continuous cross-checking for co-pilot scenarios.

### Presentation

Yan to present initial POC at knowledge sharing session. Question raised about whether presenting code structure is useful for non-programmers given the ADK vs LangGraph decision. Ramsey suggested Yan confirm scope with Anders.

---

## Next Steps

- **[Yan Zhang]** Ask Anders/Daniel about scope for knowledge sharing presentation
- **[Ramsey Wise]** Share repo link in Slack for collaboration
- **[Yan Zhang]** Schedule follow-up discussion on new POC project structure
- **[Axel + Yan]** Fork repo; build co-pilot agent POC with routing/action items
- **[Ramsey + Marco]** Fork repo; add reranker, retriever, chunking, indexing, embedding, storage refactoring
- **[Yan Zhang]** Obtain Shine data (articles, documentation) for preprocessing pipeline
- **[Yan Zhang]** Set up data preprocessing — cleaning, chunking strategy, embedding index
- **[Yan Zhang]** Select proper database for indexing/retrieval
- **[Ramsey Wise]** Integrate LangSmith into POC for metrics
- **[Ramsey Wise]** Implement retriever Python file; add nodes/edges to graph design
- **[Marco Enrique Zimmermann]** Implement reranker Python file; add nodes/edges to graph design

---

## Context Notes

- POC used synthetic data (LLM-generated) — no real Shine data available at interview stage
- LLM: OpenAI (all models in original POC)
- Bedrock considered as a status quo model source
- OpenSearch access lost; Chroma DB the local alternative
- Raptor-style RAG pipeline was the inspiration for Ramsey's playground implementation
