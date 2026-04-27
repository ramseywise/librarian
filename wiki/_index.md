---
title: Wiki Index
tags: [index]
summary: Auto-generated table of contents for the obsidian-kb wiki. Updated after every ingest.
updated: 2026-04-27
---

# Wiki Index

> Maintained by Claude Code. Do not edit manually — updated automatically during `/ingest`.

---

## RAG

*Retrieval-augmented generation — chunking, embeddings, vector stores, hybrid search, reranking.*

| Page | Summary |
|---|---|
| [[RAG Retrieval Strategies]] | Chunking, embedding, vector store, and hybrid search component choices and tradeoffs |
| [[RAG Reranking]] | Cross-encoder vs LLM listwise reranking, confidence scoring, CRAG gate integration |
| [[RAG Evaluation]] | Three-tier eval architecture — golden datasets, LLM-as-judge, failure clustering |
| [[RAG Knowledge Preparation]] | Transforming human-readable documentation into machine-retrievable knowledge units |
| [[RAG API Design Patterns]] | Multi-query surface, fingerprint-based global dedup, typed Pydantic response contract |
| [[Reciprocal Rank Fusion (RRF)]] | Score-free rank-position fusion algorithm for merging BM25 + dense vector results |
| [[Embedder Warmup]] | Force-loads embedding model at startup to prevent 3–8s cold-start spike on first request |
| [[CRAG Retry Logic]] | Confidence-gated conditional back-edge that re-enters retrieval below reranker threshold |
| [[Librarian RAG Architecture]] | Five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, Eval wired by LangGraph |
| [[Bedrock KB vs LangGraph Decision]] | Decision framework for Bedrock KBs vs LangGraph CRAG pipeline — quality, cost, migration path |

---

## LangGraph

*LangGraph state machines, CRAG, checkpointers, reducers, streaming, context management.*

| Page | Summary |
|---|---|
| [[LangGraph CRAG Pipeline]] | Deterministic CRAG graph with confidence gating, typed state, conditional retry loop |
| [[LangGraph Advanced Patterns]] | Subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints |
| [[LangGraph State Reducers]] | Functions that define how parallel node outputs merge into shared state |
| [[LangGraph BaseStore]] | Cross-thread persistent KV store with optional vector search — backs episodic and semantic memory |
| [[Send API Fan-out]] | LangGraph's runtime parallelism primitive — dynamically spawns N worker branches |
| [[Runtime Topology and Checkpointer Alignment]] | Checkpointer must match runtime — MemorySaver fails silently in Lambda/multi-worker |
| [[Summarization Node]] | 8-message trigger, 4-message overlap compaction using Haiku — same pattern in LangGraph and ADK |
| [[HistoryCondenser]] | Haiku-based query rewriter that resolves coreferences before retrieval |
| [[Orchestration Architecture Decision]] | Three architecture options (A/B/C) for Librarian deployment with migration path |

---

## ADK

*Google Agent Development Kit — SKILL.md, context engineering, VA patterns, voice, decisions.*

| Page | Summary |
|---|---|
| [[ADK Context Engineering]] | SKILL.md pattern, three skill-loading strategies (A/B/C), history compaction |
| [[ADK vs LangGraph Comparison]] | Side-by-side mental model, primitive mappings, and when to use each |
| [[SKILL.md Pattern]] | ADK skill declaration format — YAML frontmatter + instruction body, three loading strategies |
| [[Voice Agent Patterns]] | Real-time voice agent patterns — <400ms latency budget, ADK Strategy C, BIDI streaming |
| [[Multi-Agent Orchestration Patterns]] | Four patterns evaluated for Shine ADK POC — Agent with Skills & Compaction selected |
| [[VA Product Design Patterns]] | Three interaction levels, structured output as UI contract, tool count budget |
| [[Multi-Modal Agent Response]] | Agent response combining text, charts, interactive UI, and task surfaces |
| [[Plan and Execute Pattern]] | Separating planning from execution for multi-step tasks with HITL confirmation |
| [[ADK vs LangGraph Decision]] | Decision to keep Librarian on LangGraph — vocabulary alignment is the right scope |

---

## Infra

*Deployment, observability, caching, security, production hardening.*

| Page | Summary |
|---|---|
| [[Production Hardening Patterns]] | P0/P1/P2 checklist: embedder warmup, checkpointer, async I/O, SQL injection prevention |
| [[PII Masking Approaches]] | Regex vs LLM-based vs hybrid masking — contextual PII is the hard problem |
| [[Prefix Caching]] | Claude's KV cache for repeated prompt prefixes — 90% cost/latency reduction |
| [[Input Guardrails Pipeline]] | 7-stage deterministic safety pipeline — LLM-free by design |
| [[Observability — LangFuse vs LangSmith Decision]] | LangFuse first — native ragas/deepeval, self-hostable, GDPR-friendly |

---

## Patterns

*Framework-agnostic agentic design patterns.*

| Page | Summary |
|---|---|
| [[ReAct Pattern]] | Reasoning + Acting loop — alternating thought and tool calls until answer is ready |
| [[Chain of Thought]] | Inference-time technique to show reasoning before answering; improves multi-step logic |
| [[ACI (Agent-Computer Interface)]] | Tool design discipline — description, parameter, and return-value conventions |
| [[Agentic Workflow Patterns]] | Anthropic's five composable workflow patterns and ACI tool design |

---

## Eval

*Evaluation harnesses, LLM judges, annotation pipelines, preference alignment.*

| Page | Summary |
|---|---|
| [[Copilot Learning Loop]] | Operational process for improving agent systems — signal capture, knowledge refinement |
| [[HITL Annotation Pipeline]] | Two-queue annotation workflow, inter-annotator agreement gate, feedback routing |
| [[Direct Preference Optimization]] | Training-time preference alignment using preference pairs — not applicable to API-only models |
| [[VA Eval Harness]] | Four eval suites, tool_trajectory_avg_score, LLM judge, Makefile flow, CI regression gate |

---

## Deep Agents

*Deep Agents harness — middleware, state/store backends, framework selection.*

| Page | Summary |
|---|---|
| [[Deep Agents Framework]] | create_deep_agent() harness — planning, file management, subagent delegation, HITL |
| [[Deep Agents Memory Backends]] | Pluggable backends — StateBackend, StoreBackend, FilesystemBackend, CompositeBackend |
| [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] | Decision guide for choosing between LangChain, LangGraph, and Deep Agents |

---

## Memory

*Agent memory patterns — in-context, episodic, semantic, procedural.*

| Page | Summary |
|---|---|
| [[Agent Memory Types]] | Four memory types and LangGraph BaseStore — when to use each |
| [[Self-Learning Agents]] | Four-level improvement stack — inference-time, session-time, operational, training-time |

---

## MCP

*Model Context Protocol, tool schemas, agent-to-agent communication.*

| Page | Summary |
|---|---|
| [[MCP Protocol]] | Tool definitions separated from agents — Resources, Tools, Prompts; runtime tool discovery |
| [[A2A Agent Protocol]] | Google's agent-to-agent specification — task lifecycle, agent cards, LangGraph mapping |

---

## Meta

*Wiki-about-wiki — Karpathy pattern, Claude workflow system, session knowledge.*

| Page | Summary |
|---|---|
| [[Karpathy LLM Wiki Pattern]] | The compiler analogy for personal KBs — raw in, LLM compiles to wiki, no vector infra needed |
| [[Claude Workflow System]] | Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints |
| [[Session Log]] | Chronological index of all Claude Code and Codex sessions — what was worked on |
| [[Session Insights]] | Friction patterns, recurring themes, skill candidates from 84 facet-analyzed sessions |

---

## Projects

*Per-project knowledge pages.*

| Page | Summary |
|---|---|
| [[Librarian Project]] | The Librarian RAG service — stack, architecture decisions, production status |
| [[Librarian KB — Build Plan]] | Phased build plan — Phases 1–5 complete, Phase 6 active, Phases 9–15 future |
| [[Listen-Wiseer Project]] | Spotify recommendation agent — ENOA taste map, LangGraph ReAct + Chainlit, DuckDB vss RAG |
| [[VA Agent Project]] | Billy accounting VA agent — dual ADK+LangGraph implementations, 57 tools, 9 phases complete |
| [[Evaluation & Improvement Project (VIR)]] | Shine Q2 2026 — Billy→Bedrock KB ingestion, CS annotation pipeline, golden eval set |
| [[Shine Copilot Architecture]] | Shine's embedded guidance/orchestration/execution layer — VA team owns coordination |
| [[Shine Knowledge Agent]] | Shine's Help Center RAG system — knowledge retrieval for Copilot, ≥60% self-service target |

---

## Conflicts

Pages with unresolved conflicts between sources: see [[Conflicts]].

---

## Coverage Gaps

*Sources in `raw/` not yet fully compiled into wiki pages.*

- `raw/claude-docs/playground/docs/archived/visualizer-improvements/` — Slide deck agent (low wiki priority)
- `raw/claude-docs/playground/docs/archived/docs-restructure/research.md` — Scope/Build/Archive docs lifecycle model
- `raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md` — Agentic RAG copilot topology (low priority)
- `raw/claude-docs/playground/docs/archived/skills-audit-research.md` — Skill quality patterns (partial via ADK Context Engineering)
- `raw/claude-docs/playground/skills/` — 26 skill SKILL.md files (operational definitions; no new wiki knowledge)
