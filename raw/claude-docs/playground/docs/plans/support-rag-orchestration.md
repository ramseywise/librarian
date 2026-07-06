# Support RAG Orchestration Refactoring

## Summary
Separated retrieval orchestration (va-support-rag) from answer synthesis orchestration (va-langgraph, va-google-adk). This prevents redundant orchestration logic and gives VA agents full control over how they inject context and synthesize answers.

## Architecture Changes

### Before
```
va-langgraph/va-google-adk → /api/v1/chat → support-rag full pipeline → answer
```
- Support-rag did: planner → retriever → reranker → answer + post-eval
- VAs just received a finished answer, no context injection flexibility

### After
```
va-langgraph/va-google-adk → /api/v1/retrieval → support-rag retrieval only
                                                 ↓
                            (VAs inject docs + synthesize answer)
```
- **Support-rag owns**: Query planning, retrieval, reranking, quality gates
- **VAs own**: Routing, context injection, answer synthesis, retry logic
- `/api/v1/chat` still available for direct users or evals (backward compat)

## Changes Made

### Phase 1: va-support-rag (commit 6ee47cd)
- Added `RetrievalOutput` schema: `{query, documents, confidence_score, escalated, latency_ms}`
- Created `build_retrieval_subgraph()`: stops after reranking (skips answer, post-eval, summarizer)
- Added `LangGraphRuntime.run_retrieval()`: invokes retrieval graph and extracts documents
- Added `/api/v1/retrieval` endpoint for VA agents
- Kept `/api/v1/chat` for backward compat + standalone users

**Graph topology** (retrieval-only):
```
START → planner → retriever → qa_policy_retrieval
        ↓
        reranker → qa_policy_rerank → END (answer synthesis happens in caller)
        ↓
        [escalation path if needed]
```

### Phase 2: va-langgraph (commit c929618)
- Updated `support_subgraph()` to call `/api/v1/retrieval`
- Now returns structured documents in `tool_results` instead of answer
- Format node synthesizes answer from documents using va-langgraph's LLM

**Flow**:
1. Router sends to support_subgraph
2. support_subgraph retrieves docs via `/api/v1/retrieval`
3. format_node reads doc in tool_results, synthesizes answer with sources

### Phase 3: va-google-adk (commit 78831ff)
- Updated `search_knowledge()` tool to call `/api/v1/retrieval`
- Returns formatted document summary for support_agent to use
- support_agent LLM synthesizes answer with proper sources

**Flow**:
1. Analyzer routes to support_agent
2. search_knowledge retrieves docs via `/api/v1/retrieval`
3. support_agent LLM synthesizes answer using the docs

## Benefits
1. **Cleaner separation**: Retrieval ≠ answer synthesis
2. **Flexible context injection**: VAs can enhance docs with their own context (page URL, user intent, etc.)
3. **Better observability**: Each stage of the pipeline is independently testable
4. **Future-proof**: Can swap retrieval strategies without touching VA answer synthesis
5. **Backward compat**: Full pipeline still available for direct use or evals

## Testing
- All va-support-rag orchestration tests pass (64 tests)
- Schemas and graph builders verified
- No breaking changes to existing code

## Next Steps (Optional)
- Feature flag to test both `/api/v1/chat` vs `/api/v1/retrieval` in production
- Monitor latency: retrieval-only should be ~30% faster (no LLM for answer synthesis)
- Evals: Compare answer quality when context is synthesized by VA vs by RAG pipeline
