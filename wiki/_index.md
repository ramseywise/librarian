---
title: Wiki Index
tags: [index]
summary: Auto-generated table of contents for the obsidian-kb wiki. Updated after every ingest.
updated: 2026-07-19
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
| [[Agentic RAG — Advanced Patterns]] | Self-RAG vs CRAG, Adaptive RAG, GraphRAG, HyDE, Multi-Query RAG-Fusion, A2A protocol mapping, latency budgets |
| [[Reciprocal Rank Fusion (RRF)]] | Score-free rank-position fusion algorithm for merging BM25 + dense vector results |
| [[Embedder Warmup]] | Force-loads embedding model at startup to prevent 3–8s cold-start spike on first request |
| [[CRAG Retry Logic]] | Confidence-gated conditional back-edge that re-enters retrieval below reranker threshold |
| [[Librarian RAG Architecture]] | Five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, Eval wired by LangGraph |
| [[Bedrock KB vs LangGraph Decision]] | Decision framework for Bedrock KBs vs LangGraph CRAG pipeline — quality, cost, migration path |
| [[VA vs HCA Retrieval Evaluation]] | Production benchmarking (MRR 0.286 vs 0.248, n=754), 47% corpus ceiling analysis, failure taxonomy, and two-lever improvement framework |
| [[Conversation Repository Pattern]] | Two-table PostgreSQL schema for multi-turn conversation state — conversations + messages with JSONB trace and sources columns |
| [[Semantic Cache Pipeline]] | 3-tier zero-retrieval-cost path for paraphrase queries — cache lookup → source router → CRAG fallback, with offline seed build and threshold sweep |
| [[Vector Database Comparison]] | Side-by-side of DuckDB, ChromaDB, pgvector, OpenSearch, Pinecone, and GCP Discovery Engine across cost, scalability, search modes, and migration notes |
| [[GCP Vertex AI Search vs Bedrock KB]] | Architecture and behavioral comparison of GCP Vertex AI Search vs AWS Bedrock KB — score semantics, language handling, session state, and when to switch |

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
| [[LangChain Fundamentals — create_agent, Tools, Structured Output]] | LangChain 1.0's create_agent() loop, @tool decorator, checkpointer persistence, and structured output — the foundation layer beneath LangGraph and Deep Agents |
| [[LangChain Agent Middleware]] | LangChain's create_agent() middleware API — HumanInTheLoopMiddleware, wrap_tool_call/before_model/after_model hooks, Command-based resume |
| [[LangChain Dependency Management]] | Package structure and version policy for the LangChain ecosystem — core packages, provider packages, the langchain-community non-semver trap |
| [[LangChain RAG Implementation Patterns]] | LangChain-specific RAG API surface — document loaders, text splitters, vector store classes, similarity/MMR search, RAG as an agent tool |

---

## ADK

*Google Agent Development Kit — SKILL.md, context engineering, VA patterns, voice, decisions.*

| Page | Summary |
|---|---|
| [[ADK Python API Reference]] | Quick reference for the ADK Python SDK — agents, tools, state, callbacks, plugins, artifacts, memory, context caching, and compaction |
| [[ADK Workflow Agents]] | Sequential, Parallel, and Loop agents — deterministic control flow without LLM orchestration |
| [[ADK Deployment Patterns]] | Agent Engine vs Cloud Run vs GKE decision matrix, CI/CD with WIF, service account architecture, event-driven triggers, Terraform patterns |
| [[ADK Eval Guide]] | Eval-fix loop, 8 built-in criteria, evalset schema, tool trajectory gotchas, multimodal eval, user simulation |
| [[ADK User Simulation Eval]] | Dynamic conversation testing using ConversationScenario and user simulator LLM |
| [[ADK Observability]] | Four observability tiers — Cloud Trace, prompt-response logging, BigQuery Agent Analytics, third-party platforms |
| [[ADK Scaffold Patterns]] | Agent Starter Pack CLI, templates, DESIGN_SPEC.md contract, prototype-first workflow |
| [[ADK Context Engineering]] | SKILL.md pattern, three skill-loading strategies (A/B/C), history compaction |
| [[ADK vs LangGraph Comparison]] | Side-by-side mental model, primitive mappings, and when to use each |
| [[SKILL.md Pattern]] | ADK skill declaration format — YAML frontmatter + instruction body, three loading strategies |
| [[Voice Agent Patterns]] | Real-time voice agent patterns — <400ms latency budget, ADK Strategy C, BIDI streaming |
| [[Multi-Agent Orchestration Patterns]] | Four patterns evaluated for [client] ADK POC — Agent with Skills & Compaction selected |
| [[VA Product Design Patterns]] | Three interaction levels, structured output as UI contract, tool count budget |
| [[Multi-Modal Agent Response]] | Agent response combining text, charts, interactive UI, and task surfaces |
| [[Plan and Execute Pattern]] | Separating planning from execution for multi-step tasks with HITL confirmation |
| [[ADK vs LangGraph Decision]] | Decision to keep Librarian on LangGraph — vocabulary alignment is the right scope |
| [[HITL and Interrupt Patterns]] | Six HITL patterns — static/dynamic breakpoints, clarification loop, scheduler gate, tool approval, time-travel/fork |
| [[ADK JS TypeScript Patterns]] | Google ADK TypeScript SDK (@google/adk 0.5.0) — LlmAgent, FunctionTool, Zod structured output, NDJSON streaming, pitfalls |
| [[System Design — Serverless Agent Backends]] | Interview-format writeup — stateless invocations, session state in Supabase, streaming inside timeout budgets, designed phase-2 handoff |

---

## Infra

*Deployment, observability, caching, security, production hardening.*

| Page | Summary |
|---|---|
| [[Production Hardening Patterns]] | P0/P1/P2 checklist: embedder warmup, checkpointer, async I/O, SQL injection prevention |
| [[PII Masking Approaches]] | Regex vs LLM-based vs hybrid masking — contextual PII is the hard problem |
| [[Prefix Caching]] | Claude's KV cache for repeated prompt prefixes — 90% cost/latency reduction |
| [[Input Guardrails Pipeline]] | 7-stage deterministic safety pipeline — LLM-free by design |
| [[Observability — LangFuse vs LangSmith Decision]] | LangFuse first — native ragas/deepeval, self-hostable, GDPR-friendly; [client] weighted score 8.58/10 |
| [[Langfuse Platform]] | Open-source LLM observability — tracing, prompt management, eval; [client] adoption status (legal cleared, SSO pending) |
| [[Observability and Runtime Patterns]] | LangSmith vs Langfuse choice, tracing architecture, checkpointer alignment rules, trigger patterns, key monitoring signals |
| [[Langfuse ADK Tracing Patterns]] | Two-layer ADK + Langfuse tracing — OTel auto-instrumentation + @observe decorators; session grouping, RAG path tagging, first-class Scores, error visibility |
| [[Cloud Run + Cloud SQL Pattern]] | Single Cloud Run container + Cloud SQL Auth Proxy (unix socket) — sizing rationale, --workers 1, KB update workflow |
| [[PGVector Migration Pattern]] | NumPy .npz → pgvector migration — schema, cosine distance operator, IVFFlat index, pg_dump/restore via Auth Proxy |
| [[Presidio PII Redaction for Langfuse]] | Presidio + spaCy fr_core_news_lg + CamemBERT + custom regex for French financial PII — wired via Langfuse SDK mask hook |
| [[System Design — Shared Code-Index Service]] | Interview-format writeup — centralized indexer + query API, MCP as thin read-only client, DuckDB single-writer risk, pgvector escape hatch |

---

## Patterns

*Framework-agnostic agentic design patterns.*

| Page | Summary |
|---|---|
| [[ReAct Pattern]] | Reasoning + Acting loop — alternating thought and tool calls until answer is ready |
| [[Chain of Thought]] | Inference-time technique to show reasoning before answering; improves multi-step logic |
| [[ACI (Agent-Computer Interface)]] | Tool design discipline — description, parameter, and return-value conventions |
| [[Agentic Workflow Patterns]] | Anthropic's five composable workflow patterns and ACI tool design |
| [[Multi-Repo Claude Organization]] | Organizing .claude/, .agents/, and docs/ across related repos — avoiding skill sprawl |
| [[Branch Naming Convention Pattern]] | Ticket-linked, type-prefixed branch naming (`type-TICKET-slug`) with per-repo type taxonomies and a `hotfix` escape hatch |
| [[AI Project Template Scaffold]] | Generic starter-repo pattern for new AI agent projects — reference-project skills/docs/infra + DS-template skeleton, kept as its own repo |
| [[Agent Scaffolding Skill Layers]] | Three-layer Claude Code skill design for agent scaffolding — generic parallel-subagent factory (L1), standalone capability add-skills (L2), domain-specific orchestrator bundle (L3) |
| [[Track2Vec Playlist Co-Occurrence Embeddings]] | Item2vec-style Word2Vec-over-playlists technique — dense track embeddings that capture curation intent rather than audio similarity |

---

## Eval

*Evaluation harnesses, LLM judges, annotation pipelines, preference alignment.*

| Page | Summary |
|---|---|
| [[Copilot Learning Loop]] | Operational process for improving agent systems — signal capture, knowledge refinement |
| [[Anthropic Three-Tier Eval Taxonomy]] | Three-tier agent eval framework (unit/trajectory/e2e) — 70% regression coverage from deterministic unit evals, RAGAS+DeepEval for e2e |
| [[HITL Annotation Pipeline]] | Two-queue annotation workflow, inter-annotator agreement gate, feedback routing |
| [[Direct Preference Optimization]] | Training-time preference alignment using preference pairs — not applicable to API-only models |
| [[VA Eval Harness]] | Four eval suites, tool_trajectory_avg_score, LLM judge, Makefile flow, CI regression gate |
| [[project-g Eval Architecture]] | Routing vs domain eval (Strand A/E/F), grader interface, three-tier coverage, ablation methodology, GT pipeline |
| [[LLM Grader Calibration Insights]] | Custom v3 grader vs DeepEval defaults, domain-shift failure pattern, passage context requirement |
| [[Agentic KPI Trees]] | KPI tree pattern — goal completion rate, no-touch rate, auto-reconciliation accuracy for VA/accounting/matching agents |
| [[RAG Eval Metrics Suite]] | Eight-metric RAG eval framework — runtime (faithfulness, naturalness, relevance, contextual relevance) vs offline (completeness, recall, document precision, calibration) |
| [[Synthetic Dataset Generation for RAG Eval]] | Four-mode pipeline (init/refresh/regenerate/export) with article fingerprinting, stable content-derived IDs, and four query categories |
| [[Eval Gate Contract]] | 8-gate RAG eval pipeline (Corpus QA → Index Readiness → Retrieval Optimization → Model/Runtime → Agent Retrieval → Generation Quality → Grader Calibration → Report) with canonical row pools and failure taxonomy |
| [[Grounding Claim Methodology]] | Yellow highlighter metaphor for citation verification — four-tier grounding, quote word-boundary check, Tier 1–3 hard fails, Tier 4 log-only diagnostics |
| [[Observability & Evaluation Glossary]] | Canonical vocabulary — observability/tracking/tracing/monitoring/alerting hierarchy, offline vs online eval modes, heuristic vs LLM-judge metrics, dataset terminology, rank-based retrieval metrics |
| [[Skill Eval Pipeline (Blind Comparison + Grading)]] | Three-agent pipeline for A/B testing Claude Code skills — blind comparator (rubric scoring), grader (PASS/FAIL with evidence + eval critique), post-hoc analyzer (unblinds winner, suggests loser improvements) |
| [[LightGBM vs CatBoost Comparison]] | Methodology for comparing calibrated GBM rerankers — fixing train/inference feature mismatch first, native categorical handling, Brier score/log-loss as the right metrics |
| [[System Design — Unified Eval Harness]] | Interview-format writeup of playground's harness — golden set, two-tier grading (heuristic → LLM judge), regression vs capability harnesses, threshold governance |

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
| [[Memory Architecture for VA Agents]] | Three-tier cognitive model (semantic/episodic/procedural), SQLite pattern, context window management, reflection pattern |

---

## MCP

*Model Context Protocol, tool schemas, agent-to-agent communication.*

| Page | Summary |
|---|---|
| [[MCP Protocol]] | Tool definitions separated from agents — Resources, Tools, Prompts; runtime tool discovery |
| [[A2A Agent Protocol]] | Google's agent-to-agent specification — task lifecycle, agent cards, LangGraph mapping |
| [[MCP Server Security Patterns]] | Read-only invariant, sandbox isolation, secrets handling, and what not to expose over MCP |

---

## Meta

*Wiki-about-wiki — Karpathy pattern, Claude workflow system, session knowledge.*

| Page | Summary |
|---|---|
| [[Karpathy LLM Wiki Pattern]] | The compiler analogy for personal KBs — raw in, LLM compiles to wiki, no vector infra needed |
| [[Claude Workflow System]] | Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints |
| [[Claude Code Hook Architecture]] | Lifecycle hooks (PreToolUse/PostToolUse/Stop), exit-code protocol, current hook suite, pattern for adding new hooks |
| [[SANYI Change-Contract System]] | Three-layer change contract (变易/简易/不易) for agent architectures — init/review/audit modes, violation codes |
| [[Session Knowledge Capture Patterns]] | Output type taxonomy, pre-compact enrichment, and session-as-source-of-truth approach |
| [[Session Log]] | Chronological index of all Claude Code and Codex sessions — what was worked on |
| [[Session Insights]] | Friction patterns, recurring themes, skill candidates from 84 facet-analyzed sessions |
| [[Puffin Consciousness Development Skills]] | Chained skill family (genesis → wake → grow → reflect → synthesize → dream) for staged self-development across sessions |
| [[Code Review Drill — SANYI]] | Code-review interview drill from a real contract-check run — the two-line diff that lints clean but violates the change contract |

---

## Projects

*Per-project knowledge pages — public, reusable.*

| Page | Summary |
|---|---|
| [[Librarian Project]] | The Librarian RAG service — stack, architecture decisions, production status |
| [[Librarian KB — Build Plan]] | Phased build plan — Phases 1–5 complete, Phase 6 active, Phases 9–15 future |
| [[Librarian Graph Explorer]] | Local React Flow wiki graph explorer — multi-edge toggling (wikilink/semantic/tag-shared), UMAP semantic layout, agent chat + write-back |
| [[Listen-Wiseer Project]] | Spotify recommendation agent — ENOA taste map, LangGraph ReAct + Chainlit, DuckDB vss RAG |
| [[Change-Contracts Rollout]] | 2026-07-17 decision record — SANYI global promotion, per-repo contracts, review-skill enforcement, template seeding; akira blocked on hardcoded scan roots |

> **Private project pages** (company-specific) live in `wiki/private/` — gitignored, available locally.

---

## Interview

*Coding-interview patterns, algorithms, system design, prep references for ML/AI-engineering/DS/FDE roles.*

| Page | Summary |
|---|---|
| [[RAG Interview Study Guide]] | Exam-prep reference for RAG architecture questions — component choices, architecture variants, production judgment, measured benchmarks, and terminology traps |
| [[Agents Interview Study Guide]] | Exam-prep reference for agent architecture questions — workflow vs agent distinction, composable patterns, ACI tool design, harness engineering, long-horizon reliability, and memory taxonomy |
| [[System Design Interview Study Guide]] | Method guide for the ML/LLM/agent system design round — 5-step process, trade-off narration formula, LLM reference architecture, bottleneck table, and failure mode reflexes |
| [[Evals and Observability Interview Study Guide]] | Exam-prep reference for eval and observability questions — vocabulary, grader types, three-tier taxonomy, pass@k vs pass^k, and the tracing-first discipline |
| [[LLM Fundamentals Interview Study Guide]] | Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes |

---

## Foundations

*ML/DS/data-engineering fundamentals — classical ML, deep learning, NLP, data systems, MLOps.*

*(Empty — pending M2 distillation of data-science/ and data-engineering/ material from learn-ai-engineering.)*

---

## Conflicts

Pages with unresolved conflicts between sources: see [[Conflicts]].

---

## Coverage Gaps

*Sources in `raw/` not yet fully compiled into wiki pages.*

- `raw/articles/2026-07-19-*.md` — 13 coursera-reference articles written 2026-07-19; awaiting full wiki compile (M4)
- `raw/repos/learn-ai-engineering/interviewing--rounds--*.md` — 9 round-type files (behavioral, case-study, coding-challenge, etc.); awaiting compile into interview/ wiki pages
- `raw/repos/learn-ai-engineering/interviewing--guides--*.md` — remaining guides (foundations, context-cost, security-safety, data-eng-mlops, product-delivery); awaiting compile
- `raw/repos/learn-ai-engineering/interviewing--notes--*.md` — 16 cleaned Notion notes; awaiting compile (high value: deep-agents, context-engineering, loop-engineering, reliable-agents)
- `raw/claude-docs/playground/docs/archived/visualizer-improvements/` — Slide deck agent (low wiki priority)
- `raw/claude-docs/playground/docs/archived/docs-restructure/research.md` — Scope/Build/Archive docs lifecycle model
- `raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md` — Agentic RAG copilot topology (low priority)
- `raw/claude-docs/playground/docs/archived/skills-audit-research.md` — Skill quality patterns (partial via ADK Context Engineering)
- `raw/claude-docs/playground/skills/` — 26 skill SKILL.md files (operational definitions; no new wiki knowledge)
- `learn-ai-engineering/data-science/`, `data-analytics/`, `data-engineering/` — books/courses for foundations/ domain; pending curated distillation into raw/books/
