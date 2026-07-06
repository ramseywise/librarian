# VA Agent Research

Accumulated research on building production-grade virtual assistant agents. These docs cover patterns, trade-offs, and design decisions — not implementation plans. Useful as a reference before starting a new agent build or adding a major capability.

---

## Agentic AI

Patterns for agent architecture, safety, and product design.

| Doc | What it covers |
|-----|---------------|
| [orchestration-patterns.md](agentic-ai/orchestration-patterns.md) | Supervisor vs handoff vs parallel swarm; subgraph routing; try-agent history; ADK vs LangGraph decision matrix |
| [memory-architecture.md](agentic-ai/memory-architecture.md) | Three-tier memory taxonomy (semantic/episodic/procedural); SQLite store; context window strategies; reflection pattern |
| [guardrails-pipeline.md](agentic-ai/guardrails-pipeline.md) | 7-stage deterministic safety pipeline: normalise → size check → domain classify → injection detect → PII redact → envelope → advisory |
| [hitl-and-interrupts.md](agentic-ai/hitl-and-interrupts.md) | Static vs dynamic `interrupt()`; bounded clarification budget; time travel and fork patterns |
| [adk-skill-loading-patterns.md](agentic-ai/adk-skill-loading-patterns.md) | SKILL.md pattern; three skill-loading strategies (proxy/native/preloaded); history pruning; agent gateway; ADK↔LangGraph mapping |
| [va-product-patterns.md](agentic-ai/va-product-patterns.md) | Three interaction levels; structured output as UI contract; page context awareness; escalation path; tool count budget |

---

## RAG

Retrieval patterns, component decisions, and API design for knowledge-grounded agents.

| Doc | What it covers |
|-----|---------------|
| [rag-integration-strategy.md](rag/rag-integration-strategy.md) | RAG as a service vs subgraph; integration patterns with VA agents |
| [agentic-rag-patterns.md](rag/agentic-rag-patterns.md) | Self-RAG vs CRAG; adaptive RAG; GraphRAG; HyDE; multi-query RAG-Fusion; global dedup; agentic eval; A2A protocol |
| [rag-component-tradeoffs.md](rag/rag-component-tradeoffs.md) | Chunking, embeddings, vector stores, retrieval strategies, reranking — decision log with production benchmarks |
| [rag-api-design.md](rag/rag-api-design.md) | Multi-query API surface; fingerprint-based deduplication; typed response contract |

---

## Evaluation and Learning

How to measure agent quality and improve it over time.

| Doc | What it covers |
|-----|---------------|
| [eval-harness.md](evaluation-and-learning/eval-harness.md) | Four eval suites; JSON evalset schema; `tool_trajectory_avg_score`; LLM judge; Makefile flow; CI regression gate |
| [self-learning-agents.md](evaluation-and-learning/self-learning-agents.md) | ReAct; chain-of-thought; self-critique; corrective RAG subgraph; reflection; DPO vs RLHF; maturity stack |
| [observability-and-runtime.md](evaluation-and-learning/observability-and-runtime.md) | LangSmith vs Langfuse (incl. GDPR); trigger patterns; runtime topology; checkpointer alignment |

---

## Team Workflow

Standards and quick references for working as a team on this codebase.

| Doc | What it covers |
|-----|---------------|
| [git-workflows.md](git-workflows.md) | Branch naming, commit style, rebase vs merge, conflict resolution, undoing mistakes, interactive rebase — with Linear ticket conventions |
