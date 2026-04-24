---
title: ADK vs LangGraph Decision
tags: [adk, langgraph, decision]
summary: Decision to keep Librarian on LangGraph — ADK's strengths don't address Librarian's core requirements; vocabulary alignment (Level 1) is the right refactor scope.
updated: 2026-04-24
sources:
  - raw/playground-docs/adk-orchestration-research.md
  - raw/playground-docs/orchestration-rollout-plan.md
  - raw/playground-docs/orchestration-rollout-review.md
---

# ADK vs LangGraph Decision

**Date:** 2026-04-12  
**Status:** Decided — keep LangGraph, apply Level 1 vocabulary alignment

## Decision

Librarian stays on LangGraph. ADK is **not** worth porting to for the retrieval pipeline. The gap is vocabulary, not architecture. Level 1 vocabulary alignment (~2 days) achieves full readability for ADK/CrewAI/LangChain engineers without any behavior change.

## Why Not ADK (Level 3 — Full Port)

| Blocker | Detail |
|---|---|
| Claude support | ADK is Gemini-native; Anthropic Claude requires LiteLLM adapter or custom model class — neither production-proven |
| CRAG loop | ADK's `LoopAgent` can't model Librarian's surgical conditional back-edge — loop would restart full condense → analyze sequence |
| Type safety | Typed `LibrarianState` → untyped session dict. Debugging regressions becomes harder |
| Observability | LangFuse integration is LangGraph-specific; would need replacement |
| Strategy dispatch | `factory.py` DI pattern (chroma vs opensearch, cross-encoder vs llm-listwise) has no ADK equivalent |

**Verdict:** migration cost is high; the gain is vocabulary only — which Level 1 achieves for free.

## What Level 1 Vocabulary Alignment Does (~2 days)

1. Rename SubGraph classes → `*Agent` naming (RetrieverAgent, RerankerAgent, etc.)
2. Add `name` and `description` properties to each agent class
3. Extract `instruction` (system prompt snippets) into agent classes
4. Expose `as_node()` method on each agent class (replaces `_make_*_node()` helpers)
5. Document graph topology in `graph.py` matching ADK's `sub_agents=[...]` self-documenting style

**Result:** codebase readable to any engineer who has used ADK, CrewAI, or LangChain agent code.

## Risk Scorecard: Level 1

| Risk | Assessment |
|---|---|
| Behavior change | None — rename + add properties only |
| Test breakage | Low — public API surfaces keep same interface |
| Observability regression | None — LangFuse wiring unchanged |
| Migration cost | ~2 days |
| Transferability gain | High |
| Reversibility | Trivially reversible — pure rename |

## ADK is Worth Prototyping (Separately)

Two prototype hypotheses worth testing against the existing LangGraph pipeline:

**Option A: ADK + LangGraph hybrid (~1–2 days)** — wrap the compiled LangGraph graph as a single ADK `BaseAgent`. Tests: does ADK's session management add value over the existing `conversation_id` pattern?

**Option B: ADK + custom RAG tools (~1 day)** — fresh ADK agent where Gemini drives retrieval decisions via tools. Tests: does LLM-driven retrieval close quality gaps vs. Librarian's fixed pipeline? This is the more interesting research question — test Option B first.

**Implemented:** all four variants (LangGraph vocab alignment, ADK+Bedrock, ADK+CustomRAG, ADK+LangGraph hybrid) completed per the orchestration rollout plan. Tests: 412 PASSED.

## Orchestration Rollout — Known Gaps (post-review)

Three blocking issues found in the review of the orchestration rollout implementation:

1. **Missing tools in ADK custom_rag agent** — only `search_knowledge_base` + `rerank_results`. No `condense_query` or `analyze_query`. The LLM can't do query understanding or multi-turn condensation — this would make the ADK agent under-perform the Librarian pipeline in eval, not because ADK is worse, but because it wasn't given the same capabilities.

2. **No tracing/observability in ADK agents** — `BedrockKBAgent`, `CustomRAGAgent`, and `LibrarianADKAgent` have zero observability integration. ADK provides `before_tool_callback`/`after_tool_callback` — these should log to structlog + optionally LangFuse.

3. **`_extract_latest_query` duplicated 3 times** — should be one shared utility in `orchestration/adk/utils.py`.

## See Also
- [[ADK vs LangGraph Comparison]]
- [[LangGraph CRAG Pipeline]]
- [[Librarian RAG Architecture]]
- [[Bedrock KB vs LangGraph Decision]]
