---
title: Wiki Index
tags: [index]
summary: Auto-generated table of contents for the obsidian-kb wiki. Updated after every ingest.
updated: 2026-04-24
---

# Wiki Index

> Maintained by Claude Code. Do not edit manually — updated automatically during `/ingest`.

---

## Concepts

*Technology and architecture concepts.*

| Page | Summary |
|---|---|
| [[Karpathy LLM Wiki Pattern]] | The compiler analogy for personal KBs — raw in, LLM compiles to wiki, no vector infra needed |
| [[LangGraph CRAG Pipeline]] | Deterministic CRAG graph with confidence gating, typed state, conditional retry loop |
| [[RAG Retrieval Strategies]] | Chunking, embedding, vector store, and hybrid search component choices and tradeoffs |
| [[RAG Reranking]] | Cross-encoder vs LLM listwise reranking, confidence scoring, CRAG gate integration |
| [[RAG Evaluation]] | Three-tier eval architecture — golden datasets, LLM-as-judge, failure clustering |
| [[Agent Memory Types]] | Four memory types (in-context, episodic, semantic, procedural) and LangGraph BaseStore |
| [[MCP Protocol]] | Tool definitions separated from agents — Resources, Tools, Prompts; runtime tool discovery |
| [[LangGraph Advanced Patterns]] | Subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints |
| [[Production Hardening Patterns]] | P0/P1/P2 checklist: embedder warmup, checkpointer, async I/O, SQL injection prevention, CORS, Docker |
| [[A2A Agent Protocol]] | Google's agent-to-agent specification — task lifecycle, agent cards, LangGraph mapping |
| [[Agentic Workflow Patterns]] | Anthropic's five composable workflow patterns (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and ACI tool design |
| [[PII Masking Approaches]] | Regex vs LLM-based vs hybrid masking — contextual PII is the hard problem; compliance sign-off is a hard gate |
| [[HITL Annotation Pipeline]] | Two-queue annotation workflow (random + edge case), inter-annotator agreement gate, feedback routing to eval dataset vs failure taxonomy |
| [[Reciprocal Rank Fusion]] | Score-free rank-position fusion algorithm for merging BM25 + dense vector results — k=60, no score normalization needed |
| [[HistoryCondenser]] | Haiku-based query rewriter that resolves coreferences before retrieval — zero latency on single-turn |
| [[LangGraph BaseStore]] | Cross-thread persistent KV store with optional vector search — backs episodic, semantic, and procedural memory |
| [[Prefix Caching]] | Claude's KV cache for repeated prompt prefixes — 90% cost/latency reduction on static system prompts and tool schemas |
| [[CRAG Retry Logic]] | Confidence-gated conditional back-edge that re-enters retrieval when reranker score falls below threshold |
| [[Send API Fan-out]] | LangGraph's runtime parallelism primitive — dynamically spawns N worker branches without knowing N at compile time |
| [[Summarization Node]] | 8-message trigger, 4-message overlap compaction using Haiku — same pattern in LangGraph and ADK (History Compaction) |
| [[ACI (Agent-Computer Interface)]] | Tool design discipline for agents — description, parameter, and return-value conventions that prevent tool-use failures |
| [[Embedder Warmup]] | Force-loads embedding model during app startup to prevent 3–8s cold-start spike on first production request |
| [[SKILL.md Pattern]] | ADK skill declaration format — YAML frontmatter + instruction body, three loading strategies, evaluation framework |

---

## Agents

*Agent patterns, framework comparisons, implementation decisions.*

| Page | Summary |
|---|---|
| [[Librarian RAG Architecture]] | Five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, Eval wired by LangGraph |
| [[ADK vs LangGraph Comparison]] | Side-by-side mental model, primitive mappings, and when to use each |
| [[ADK Context Engineering]] | SKILL.md pattern, three skill-loading strategies (A/B/C), history compaction |
| [[Plan and Execute Pattern]] | Separating planning from execution for multi-step tasks with HITL confirmation |

---

## Projects

*Per-project knowledge pages.*

| Page | Summary |
|---|---|
| [[Librarian Project]] | The Librarian RAG service — stack, architecture decisions, production status |
| [[Librarian KB — Build Plan]] | Revised phased plan — manifest dedup, Streamlit viz, focused ingest, then Chainlit + LangGraph agent |
| [[Listen-Wiseer Project]] | Spotify recommendation agent — ENOA taste map, LangGraph ReAct + Chainlit, LightGBM, DuckDB vss RAG, three-tier eval harness |
| [[VA Agent Project]] | Billy accounting VA agent — dual ADK+LangGraph implementations, 57 tools, MCP stub layer, all 9 phases complete |
| [[Evaluation & Improvement Project (VIR)]] | Shine Q2 2026 — Billy→Bedrock KB ingestion, CS annotation pipeline, ~50 conversation golden eval set targeting 2026-06-30 |

---

## Decisions

*Architecture decision records (ADRs).*

| Page | Date | Summary |
|---|---|---|
| [[ADK vs LangGraph Decision]] | 2026-04-12 | Keep LangGraph; Level 1 vocabulary alignment is the right scope |
| [[Bedrock KB vs LangGraph Decision]] | 2026-04-11 | Start Bedrock for TS prototype, migrate to Polyglot once eval validates quality |
| [[Orchestration Architecture Decision]] | 2026-04-12 | Three options (A/B/C): start A (Bedrock), migrate to C (Polyglot) |
| [[Observability — LangFuse vs LangSmith Decision]] | 2026-04-09 | LangFuse first — native ragas/deepeval, self-hostable, GDPR-friendly |

---

## Conflicts

Pages with unresolved conflicts between sources: see [[_conflicts]].

---

## Coverage Gaps (updated 2026-04-24 — post playground ingest)

*Sources in `raw/` not yet fully compiled into wiki pages.*

Remaining sources without full wiki coverage:
- `raw/claude-docs/playground/docs/archived/visualizer-improvements/` — Slide deck agent (distinct from RAG pipeline; low wiki priority)
- `raw/claude-docs/playground/docs/archived/docs-restructure/research.md` — Scope/Build/Archive docs lifecycle model (meta-pattern for `.claude/docs/`)
- `raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md` — Agentic RAG copilot topology (low priority)
- `raw/claude-docs/playground/docs/archived/skills-audit-research.md` — Skill quality patterns (partial via ADK Context Engineering)
- `raw/sessions/` — 54 session notes: first prompt + token stats only. **Skip.**
- `raw/claude-docs/playground/skills/` — 26 skill SKILL.md files (operational definitions; no new wiki knowledge)
