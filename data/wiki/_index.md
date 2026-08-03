---
title: Wiki Index
tags: [meta, reference]
summary: Auto-generated table of contents for every page in data/wiki/, grouped by domain directory.
updated: 2026-08-03
sources:
  - data/wiki/
---

# Wiki Index

Canonical list of all wiki pages, grouped by domain (the primary retrieval axis).
Regenerate after every ingest. `data/wiki/private/` is deliberately excluded.

**164 pages** across 13 domains.


## Foundations

- [[Batch Normalization]] — Batch Normalization (Ioffe & Szegedy, 2015) normalizes layer inputs using mini-batch statistics during training to reduce internal covariate shift — enables higher learning rates, reduces sensitivity to initialization, and acts as a regularizer. Rethinking BatchNorm (Wu & Johnson, 2021) exposes pitfalls with EMA population statistics, train/inference inconsistency, and domain shift.
- [[Dialogue Transformers — TED Policy]] — Transformer Embedding Dialogue (TED) policy (Rasa, 2020) applies self-attention at the discourse level — over dialogue turns rather than tokens — outperforming LSTM-based policies on sub-dialogue handling while being simpler and faster than REDP.
- [[DIET Architecture]] — Dual Intent and Entity Transformer (Rasa, 2020) — a multi-task NLU architecture for joint intent classification and entity recognition that outperforms fine-tuned BERT while being 6x faster to train, using plug-and-play pre-trained embeddings with sparse features.
- [[HDBSCAN with KMeans Fallback]] — Clustering selection strategy that tries density-based HDBSCAN first and falls back to KMeans when silhouette drops below 0.25 — plus the diagnostic discipline that treats a fallback as a feature-quality signal rather than a resolved choice.
- [[Dilated Causal Convolutions]] — Convolutions with exponentially increasing dilation factors that preserve temporal causality while growing the receptive field exponentially with depth — the key architectural innovation in WaveNet for modeling long-range audio dependencies efficiently.
- [[Neural Probabilistic Language Model]] — Bengio et al. (2003) introduced the idea of learning distributed word representations (embeddings) jointly with a neural network language model — fighting the curse of dimensionality by mapping words to a continuous vector space where semantically similar words have nearby representations.
- [[Open-Domain Dialogue Systems]] — Survey of frameworks for open-domain conversation — retrieval-based (score candidates), generation-based (seq2seq/PLM), and hybrid methods — with two key goals (informative via knowledge grounding, controllable via persona/strategy/safety).
- [[Positional Encoding]] — Sinusoidal or learned position signals injected into Transformer input embeddings — required because self-attention is permutation-invariant and has no inherent notion of sequence order.
- [[Self-Attention Mechanism]] — Self-attention (intra-attention) relates different positions of a single sequence to compute a representation — the core primitive enabling Transformers to model long-range dependencies in O(1) path length.
- [[Transformer Architecture]] — The Transformer model architecture (Vaswani et al., 2017) — encoder-decoder stacks of self-attention and feed-forward layers that replaced RNNs/CNNs for sequence transduction, enabling parallelized training and constant-length dependency paths.
- [[WaveNet — Autoregressive Audio Generation]] — WaveNet (van den Oord et al., 2016) is a deep autoregressive generative model for raw audio waveforms using dilated causal convolutions — achieved state-of-the-art TTS naturalness (MOS >4.0) and demonstrated multi-speaker conditioning, music generation, and speech recognition from raw audio.

## Patterns

- [[ACI (Agent-Computer Interface)]] — Tool design discipline for agents — the interface between agent and tools, analogous to HCI for humans. Good ACI determines whether the agent uses tools correctly or hallucinates parameters.
- [[Agent Quality Review Checklist]] — Nineteen agent-system-specific review checks across six families — prompt/LLM smells, tool safety, workflow state, retrieval/context, memory write-back, and accountability — of which "safeguard in prose only" is named the highest-value finding.
- [[Agent Scaffolding Skill Layers]] — A three-layer Claude Code skill design for scaffolding agents — a generic parallel-subagent factory (L1), standalone capability add-skills that read the target before generating (L2), and a domain-specific bundle that orchestrates L2 skills in sequence (L3).
- [[Agentic Workflow Patterns]] — Anthropic's five composable workflow patterns for LLM agents — when to use each, and the ACI principle for tool design.
- [[AI Project Archetypes]] — Four archetypes — Information Retrieval, Document Generation, Workflow Automation, Conversational Interface — that cover most nonprofit AI projects, each with a complexity floor, disambiguating questions, and a mapping to concrete scaffold parameters.
- [[AI Project Template Scaffold]] — A generic, framework-agnostic starter repo pattern for standing up new AI agent projects — modeled on a mature reference project's skills/docs/infra layout plus a conventional data-science project skeleton (`.github`, `project_init.sh`, `.vscode`, `data/`, `docs/`, `infrastructure/`), kept as its own repo rather than nested under the reference project.
- [[Asked vs Derived Scaffold Variables]] — A scaffold interview that splits ~20 template variables into six asked out loud, eight derived-then-confirmed, and the rest left silently defaulted — with the split decided by blast radius of a wrong guess, not by how many variables exist.
- [[Branch Naming Convention Pattern]] — Ticket-linked, type-prefixed branch naming (`type-TICKET-slug`) with per-repo type taxonomies and a `hotfix` escape hatch for production-blocking bugs.
- [[Chain of Thought]] — Inference-time technique where the LLM is prompted to show its reasoning before answering — improves accuracy on multi-step logic, arithmetic, and routing decisions with no training cost.
- [[Copier Re-Entry as Capability Path]] — Treating `.copier-answers.yml` as durable scaffold state so that flipping a template answer and re-rendering is the *only* sanctioned way a component enters a generated repo — which turns "scaffold the MVP now, add later" into a real guarantee rather than advice.
- [[Copier Upstream Update Workflow]] — Pulling template changes into an already-scaffolded project — a clean-tree gate, a mandatory `--pretend --diff` preview, impact-categorized change review, and conflict resolution that preserves local intent over template defaults.
- [[Data Pipeline Pattern Selection]] — Four ways data reaches an AI system — batch ingest, event-driven, streaming, hybrid — chosen by one question about where the data comes from, with hybrid treated as a phase-2 evolution rather than a phase-1 option.
- [[Deferred Decision Status]] — A three-value status for design decisions — Resolved / Open / Deferred(trigger) — where a deferral must name the concrete event that reopens it, and a triggerless deferral silently degrades to Open so it still blocks the gate.
- [[Deterministic Review Substrate]] — Review steps that are mechanical (diff scoping, dedup clustering, schema validation, report rendering) are pushed into a CLI the agent shells out to, so the only work left to LLM judgment is the part that actually needs judgment.
- [[Evidence Classification Model]] — A four-state classification (verified / supported / hypothesis / question) every review finding must carry before it is returned, with self-verification assigned to the producing subagent rather than the orchestrator.
- [[Integration Pattern Selection]] — Five ways an AI system connects to external services — MCP tools, Composio connectors, direct httpx clients, webhook receivers, n8n glue — and the single discriminating question that picks each one.
- [[Merge Impact and Evidence State]] — A two-axis finding schema that separates how much a problem matters (merge_impact) from how sure the reviewer is (evidence_state) — so an uncertain critical finding and a certain trivial one stay distinguishable.
- [[Multi-Repo Claude Organization]] — How to organize .claude/, .agents/, and docs/ across related repos — avoiding skill sprawl, maintaining canonical sources, and sharing context between parallel workspaces.
- [[Shared Context Brief]] — A structured brief the orchestrator fills in exactly once and passes to every dispatched subagent, so N parallel reviewers share one grounding pass instead of each re-deriving repository context from the same diff.
- [[Skill Preloading via Agent Definition]] — A skill file is inert until an agent definition names it in a `skills:` field — the two-file split that turns checklist content into context actually loaded at subagent startup.
- [[Read-Only by Default with Explicit Authorization]] — A review agent's safety model: an enumerated safe-command allowlist plus one authorization gate at the write boundary, so subagents get real shell access while every mutating action stops at proposing.
- [[Verified Runtime Capability Constraint]] — A control may only be specified if the runtime demonstrably enforces it — three Parallax mechanisms were dropped on discovering the harness had no way to make them real.
- [[Corrective Follow-Up Dispatch]] — Gated subagents that a signal-detection pass failed to trigger get dispatched in a second round when always-on subagents report out-of-dimension signal — treating reviewer observations as a recovery path for missed conditional dispatch.
- [[Parallel Dimension Scanner Architecture]] — Code review decomposed into independent single-concern scanner agents dispatched in parallel — each owns one dimension, one ID prefix, and one severity mapping — so review breadth scales by adding agents rather than lengthening one prompt.
- [[Project Discovery Conversation]] — A guided pre-design conversation that turns a volunteer's pain point into a Project Profile — deliberately withholding all technology vocabulary so the artifact commits to outcomes and constraints, not framework choices.
- [[ReAct Pattern]] — Reasoning + Acting loop — the foundational single-agent pattern where the LLM alternates thought and tool calls until it has enough information to answer. Implemented via create_react_agent in LangGraph.
- [[Scope-POC Design Interview]] — A five-tier system-design interview that produces a DESIGN.md answering *what* to build — idempotent over its own output, ratifying rather than adopting inherited decisions, and treating "I don't know" as a recordable answer instead of a blocker.
- [[Silent Fallthrough in String-Keyed Discovery]] — When a tool finds its working target by grepping a literal string, renaming that string doesn't crash — it selects a different target with no error, making the rename a flag-day change whose only defence is a call-site checklist.
- [[Source Severity vs Merge Impact]] — When a review aggregates findings from external tools, each tool's native severity is preserved unrewritten and a separate merge-impact field answers the different question of whether this particular PR should merge.
- [[Specification by Example]] — The classical practice (ATDD/SBE) of expressing a requirement as a concrete example rather than prose, producing an executable specification that cannot drift from the code.
- [[TDD as Coding-Agent Harness]] — Using a failing test to constrain the agent that writes code — the clearest goal you can give it — plus the guardrail neither popular source addresses: an agent that writes both test and implementation can satisfy itself.
- [[Template Migrations for Structural Moves]] — A file-level merge cannot express "this module moved" — template `_migrations` supply the missing structural edit, and degrade to a loud WARN rather than a silent overwrite when the file being moved was hand-edited.
- [[Track2Vec Playlist Co-Occurrence Embeddings]] — Item2vec-style technique — treat playlists as "sentences" and item IDs as "words", train Word2Vec over co-occurrence to get dense embeddings that capture human curation intent rather than content similarity.
- [[Wander — Question-Generating Review Agent]] — A review agent that produces 3–5 pointed questions instead of findings — surfacing intent, edge cases, walked-past decisions, blast radius, and the conspicuously absent thing — as the "yin" complement to defect scanners.
- [[Webhook Handler Idempotency]] — Every inbound webhook handler must tolerate the same event arriving more than once — at-least-once delivery is the sender's contract, so deduplication is unambiguously the receiver's responsibility.

## RAG

- [[Agentic RAG — Advanced Patterns]] — Self-RAG vs CRAG distinction, Adaptive RAG complexity tiers, GraphRAG for relationship traversal, HyDE for lexical gap, Multi-Query RAG-Fusion, agentic latency budgets, and A2A protocol mapping to LangGraph.
- [[Bedrock KB vs LangGraph Decision]] — Decision framework for Bedrock Knowledge Bases vs. LangGraph CRAG pipeline — quality, observability, cost, and migration path analysis.
- [[Conversation Repository Pattern]] — Two-table PostgreSQL schema for persisting multi-turn conversation state — conversations table for sessions, messages table for turns with JSONB trace and sources columns enabling trace-linked retrieval debugging.
- [[CRAG Retry Logic]] — The confidence-gated conditional back-edge in a CRAG pipeline that re-enters retrieval when the reranker's top score falls below threshold — preventing low-confidence answers from reaching the user.
- [[Embedder Warmup]] — Force-loading the embedding model during application startup (before the first request) to prevent a 3–8s cold-start spike on the first query in production.
- [[GCP Vertex AI Search vs AWS Bedrock KB]] — Head-to-head comparison of GCP Discovery Engine and AWS Bedrock Knowledge Bases as managed RAG backends — covering search semantics, session state, answer ownership, and when to consider switching.
- [[Librarian RAG Architecture]] — The five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, and Eval agents wired by a LangGraph StateGraph with CRAG retry loop.
- [[RAG API Design Patterns]] — Three design patterns for exposing a RAG service cleanly — multi-query surface (LLM sends 2-3 query variants), fingerprint-based global deduplication, and typed Pydantic response contract at the HTTP boundary.
- [[RAG Evaluation]] — Three-tier evaluation architecture for RAG pipelines — golden datasets, LLM-as-judge, failure clustering, ragas vs deepeval, and retrieval lift measurement.
- [[RAG Knowledge Preparation]] — The process of transforming human-readable documentation into machine-retrievable knowledge units — chunking, metadata tagging, rewriting for self-containment, and enforcing consistency.
- [[RAG Reranking]] — Reranking strategies for RAG pipelines — cross-encoder vs LLM listwise, confidence scoring, and when each is appropriate.
- [[RAG Retrieval Strategies]] — Comprehensive reference for chunking, embedding, vector store, and hybrid search strategies — component choices, tradeoffs, and swap paths used in the Librarian pipeline.
- [[Reciprocal Rank Fusion (RRF)]] — Score-free fusion algorithm that combines multiple ranked lists by position — the standard method for merging BM25 and dense vector retrieval results, and for amplifying cross-query agreement in multi-query retrieval.
- [[Semantic Cache for RAG Agents]] — Zero-retrieval-cost path for RAG agents — embed the query, cosine-match against a grader-validated golden seed, and short-circuit the full CRAG pipeline on high-similarity hits.
- [[VA vs HCA Retrieval Evaluation]] — Benchmarking results comparing VA, HCA (Bedrock), and local RAG baselines across 935 Danish support questions — VA outperforms HCA on all dimensions (MRR 0.286 vs 0.248), but 47% corpus ceiling means data-ops fixes dominate model-level improvements.
- [[Vector Database Comparison]] — Side-by-side of vector stores used across RAG pipelines — DuckDB (embedded local), ChromaDB, pgvector, OpenSearch (Bedrock), Pinecone, GCP Discovery Engine — with when-to-use guidance and migration notes.

## LangGraph

- [[HistoryCondenser]] — LangGraph node that rewrites the latest user query into a self-contained form given prior turns — prevents retrieval degradation on coreference-heavy multi-turn conversations.
- [[LangChain Agent Middleware]] — LangChain's create_agent() middleware API — HumanInTheLoopMiddleware for tool-call approval, wrap_tool_call/before_model/after_model hooks for custom logic, and Command-based resume — the mechanism Framework Selection means when it says "LangGraph has no middleware."
- [[LangChain Dependency Management]] — Package structure and version policy for the LangChain ecosystem — langchain/langchain-core/langgraph/langsmith as the required core, provider/tool packages installed a la carte, and the langchain-community non-semver trap.
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]] — LangChain 1.0's core agent-building primitives — the create_agent() loop, the @tool decorator, checkpointer-based persistence, and structured output — the foundation layer beneath LangGraph and Deep Agents.
- [[LangChain RAG Implementation Patterns]] — LangChain-specific RAG implementation surface — document loaders, RecursiveCharacterTextSplitter, vector store classes (Chroma/FAISS/Pinecone), similarity/MMR search, metadata filtering, and wrapping a retriever as an agent tool; the API layer beneath the conceptual choices in RAG Retrieval Strategies.
- [[LangGraph Advanced Patterns]] — Advanced LangGraph patterns beyond the basics — subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints/interrupts, error handling, and Plan-and-Execute.
- [[LangGraph BaseStore]] — LangGraph's cross-thread persistent key-value store with optional vector search — the standard backend for episodic, semantic, and procedural agent memory.
- [[LangGraph CRAG Pipeline]] — The Corrective RAG pattern implemented as a LangGraph StateGraph — deterministic graph with conditional retry loop, confidence gating, and typed state schema.
- [[LangGraph State Reducers]] — Functions that define how parallel node outputs merge into shared state — preventing collisions when multiple nodes write to the same field simultaneously.
- [[Orchestration Architecture Decision]] — Three architecture options for the Librarian service deployment — full Bedrock, full LangGraph, or polyglot — with tradeoffs and the recommended migration path.
- [[Runtime Topology and Checkpointer Alignment]] — Critical rule — checkpointer backend must match runtime hosting model. MemorySaver fails silently in Lambda and multi-worker deployments. Covers trigger patterns, observability tool choice (LangSmith vs Langfuse/GDPR), and key production signals.
- [[Send API Fan-out]] — LangGraph's Send API enables dynamic map-reduce parallelism — fan out to N workers at runtime without knowing N at graph compile time.
- [[Summarization Node]] — A LangGraph node that compresses conversation history when it exceeds a trigger threshold — keeps context window usage bounded while preserving conversational continuity.

## Google ADK

- [[ADK Context Engineering]] — How the ADK samples repo manages context — SKILL.md pattern, three skill-loading strategies, static vs dynamic instruction, and history compaction.
- [[ADK Deployment Patterns]] — ADK deployment targets (Agent Engine vs Cloud Run vs GKE), CI/CD with WIF, service account architecture, event-driven triggers, and Terraform patterns.
- [[ADK Eval Guide]] — ADK evaluation methodology — the eval-fix loop, 8 built-in criteria, evalset schema, tool trajectory gotchas, multimodal eval, and user simulation for dynamic testing.
- [[ADK JS TypeScript Patterns]] — Google ADK TypeScript SDK (@google/adk 0.5.0) — LlmAgent, FunctionTool, structured Zod output, streaming NDJSON, and pitfall patterns for Next.js agent integration.
- [[ADK Observability]] — Four-tier observability for ADK agents — Cloud Trace (always-on), prompt-response logging, BigQuery Agent Analytics plugin, and third-party platforms (AgentOps, Phoenix, MLflow, etc.).
- [[ADK Python API Reference]] — Quick reference for the Google ADK Python SDK — agent types, tools, state, callbacks, plugins, artifacts, memory, context caching, and context compaction.
- [[ADK Scaffold Patterns]] — Agent Starter Pack CLI patterns for scaffolding ADK agent projects — templates, deployment options, prototype-first workflow, DESIGN_SPEC.md contract, and development phase guidelines.
- [[ADK User Simulation Eval]] — Dynamic conversation testing in ADK using ConversationScenario and a user simulator LLM — replaces static turn sequences when agent response order is unpredictable.
- [[ADK vs LangGraph Comparison]] — Side-by-side mental model comparison of Google ADK and LangGraph — primitive mappings, weighted scoring (LangGraph 716/845 for AWS/ADK-compatible context), VA team production findings, and the recommended vocabulary alignment approach.
- [[ADK vs LangGraph Decision]] — Decision to keep Librarian on LangGraph — ADK's strengths don't address Librarian's core requirements; vocabulary alignment (Level 1) is the right refactor scope.
- [[ADK Workflow Agents]] — ADK's three deterministic workflow agents — Sequential, Parallel, and Loop — which provide control flow without LLM orchestration.
- [[HITL and Interrupt Patterns]] — Six HITL patterns for LangGraph agents — static breakpoints, dynamic interrupt(), clarification loop (budget-bounded), scheduler confirmation gate, tool approval for irreversible actions, and time-travel/replay/fork.
- [[Multi-Agent Orchestration Patterns]] — Multi-agent architecture patterns — supervisor/handoff/parallel swarm trade-offs, try-agent history for fallback routing, tool count budget, and the [client] ADK POC selection rationale.
- [[Multi-Modal Agent Response]] — Agent response pattern where output can include text, data visualizations, interactive UI components, and full task surfaces — moving beyond chat to structured elicitation and guided execution.
- [[Plan and Execute Pattern]] — Separating planning from execution for multi-step agent tasks — Planner, Executor, Replanner, and Responder nodes with HITL confirmation gate.
- [[SKILL.md Pattern]] — ADK skill declaration format — YAML frontmatter listing tools + natural language instruction body, enabling dynamic skill loading without hardcoding capabilities into the system prompt.
- [[System Design — Serverless Agent Backends]] — Interview-format system design writeup of running agent systems on serverless (Vercel Functions / Next.js API routes) — stateless invocations, session state in Postgres, streaming within platform timeouts, and the designed handoff to a stateful phase 2.
- [[VA Product Design Patterns]] — Product design patterns for embedded VA agents — three interaction levels, structured output as UI contract, page context awareness, escalation triggers, and tool count budget for routing quality.
- [[Voice Agent Patterns]] — Patterns for real-time voice agents — hard latency constraints, BIDI streaming session management, ADK Strategy C preloading, LangGraph flat tool node, and mandatory history pruning.

## Deep Agents

- [[Deep Agents Framework]] — Opinionated agent harness built on LangChain/LangGraph — create_deep_agent() wraps planning, file management, subagent delegation, and HITL into configurable middleware with no boilerplate.
- [[Deep Agents Memory Backends]] — Pluggable backend system for Deep Agents file operations and memory — StateBackend (ephemeral), StoreBackend (cross-thread), FilesystemBackend (local disk), and CompositeBackend (routing).
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — Decision guide for choosing between LangChain, LangGraph, and Deep Agents — layered frameworks where higher layers add planning, memory, and middleware on top of lower ones.

## Memory

- [[Agent Memory Types]] — Three-tier memory taxonomy (semantic/episodic/procedural) with storage patterns, context window strategies, reflection pattern, and SQLite preference store for VA agents — backed by LangGraph BaseStore.
- [[Memory Architecture for VA Agents]] — Three-tier cognitive memory model (semantic/episodic/procedural), SQLite implementation pattern, context window management strategies, and self-improving reflection pattern for VA agents.
- [[Self-Learning Agents]] — Four-level improvement stack for production agents — inference-time (ReAct, CoT, self-critique), session-time (reflection, procedural memory), operational (learning loop, HITL), and training-time (DPO). Most agents need the first three; DPO is a late-stage investment.

## MCP

- [[A2A Agent Protocol]] — Google's Agent-to-Agent open specification for inter-agent communication — task lifecycle, agent cards, and how it maps to LangGraph primitives.
- [[MCP Protocol]] — Model Context Protocol — how it separates tool definitions from agents, enabling independent deployment and runtime tool discovery; includes AWS Bedrock AgentCore deployment pattern from the Hypernova PoC.
- [[MCP Server Security Patterns]] — Security patterns for MCP servers — read-only invariant, sandbox isolation, secrets handling, and what to never expose over MCP.

## Evaluation

- [[Agentic KPI Trees]] — KPI tree pattern for agentic products — goal completion rate, no-touch rate, and transaction match accuracy as the primary success metrics for VA, document processing, and reconciliation agents.
- [[Anthropic Three-Tier Eval Taxonomy]] — Practical agent evaluation framework from Anthropic — three tiers (unit/trajectory/e2e) mapped to cost, determinism, and failure coverage. Unit covers ~70% of regressions cheaply; trajectory checks routing paths; e2e is sparingly used for quality gates.
- [[Copilot Learning Loop]] — "The operational process for improving agent systems over time — signal capture from real usage, knowledge refinement workflows, and controlled autonomy expansion. Not automatic: requires deliberate instrumentation and tooling."
- [[Direct Preference Optimization]] — Training-time technique that fine-tunes a model on human preference pairs (preferred vs rejected responses) without a reward model — replaces PPO/RLHF for preference alignment. Not applicable to API-only models.
- [[Eval vs Test Distinction]] — A test tells you your code is broken; an eval tells you your product got worse — two different instruments with different targets, graders, cadences, and failure semantics.
- [[Eval-Driven Development (EDD)]] — Writing the eval suite before the agent exists — ATDD reconstructed for non-deterministic systems, where first-ness buys honesty rather than design pressure.
- [[Forecast Grader Thresholds]] — The pass/fail contract for time-series forecast evaluation — MASE against a naïve baseline, SMAPE, directional accuracy, and prediction-interval coverage — with the diagnostic each failure points to and the drift ratio that triggers retraining.
- [[Golden Set Mechanics]] — The shape of a golden case (input/expected/metadata), sizing by purpose (20–50 at spec time, 100–1000 for CI), sourcing priority, and the anti-staleness practices that keep a set measuring.
- [[Grounding Claim Methodology]] — Claims-based grounding — the "yellow highlighter" approach to RAG verification, where the agent extracts verbatim supporting quotes from retrieved documents before writing the final answer, creating a verifiable paper trail.
- [[HITL Annotation Pipeline]] — Human-in-the-loop annotation workflow for conversation data — two-queue structure (random + edge case), inter-annotator agreement as quality gate, and feedback routing to eval dataset vs failure taxonomy.
- [[LightGBM vs CatBoost Comparison]] — Methodology for comparing calibrated GBM rerankers head-to-head — fixing train/inference feature-distribution mismatch before comparing, native categorical handling, and Brier score/log-loss as the metrics that matter for calibrated probability scores.
- [[LLM Grader Calibration Insights]] — Calibration evidence for LLM-as-judge graders in the project-g eval pipeline — custom v3 grader outperforms DeepEval defaults (+0.214 score delta vs +0.086), domain-shift is the main failure pattern, passage context is required for grounding accuracy. Grounding cross-check vs DeepEval shows near-zero agreement until article text is wired in.
- [[Observability & Evaluation Glossary]] — Canonical vocabulary for agent observability and evaluation — the observability/tracking/tracing/monitoring/alerting hierarchy, offline vs online evaluation modes, heuristic vs LLM-judge metric types, dataset terminology, and rank-based retrieval metrics (MRR/precision@k/recall@k/ndcg@k/hit@k).
- [[project-g Eval Architecture]] — Routing vs domain eval distinction (Strand A/E/F), grader interface contract, three-tier eval coverage, calibration methodology for the project-g HC agent eval pipeline, and ADK vs LangGraph parallel evaluation approach.
- [[RAG Eval Gate Contract]] — Eight-gate ownership contract for RAG evaluation pipelines — each gate answers a distinct question about corpus quality, retrieval, generation, and grader calibration, with strict handoff contracts between gates.
- [[RAG Eval Metrics Suite]] — Eight-metric RAG evaluation framework covering stakeholder quality (faithfulness, naturalness, completeness, relevance), retrieval quality (contextual relevance, recall, document precision), and system calibration — split between runtime-compatible and offline-only metrics.
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — Three-agent pipeline for A/B testing Claude Code skills — a blind comparator scores two outputs on a rubric without knowing which skill produced them, a grader checks explicit expectations pass/fail with cited evidence, and a post-hoc analyzer unblinds the result to explain why the winner won and suggest concrete improvements to the loser.
- [[Skill Pipeline Dryrun Testing]] — Regression-testing a chain of conversational skills by simulating a user through fixed scenarios with unambiguous expected outcomes — asserting not only what the pipeline produces but which questions it correctly skips and which it must still ask.
- [[Synthetic Dataset Generation for RAG Eval]] — Four-mode pipeline for generating and maintaining a versioned synthetic test dataset from a knowledge base — article fingerprinting drives incremental refresh, stable content-derived IDs make Langfuse upserts idempotent, and four query categories cover the full quality surface.
- [[System Design — Unified Eval Harness]] — Interview-format system design writeup of playground's eval harness — golden set → heuristic graders → LLM judges → gate, shared across three agent implementations, with HTML reporting and threshold governance.
- [[VA Eval Harness]] — "Agent evaluation harness for VA agents — four eval suites (routing, quality, behavioral, error handling), JSON evalset schema, tool_trajectory_avg_score metric, LLM-as-judge, Makefile flow, and CI regression gate. Production golden dataset: ~100 questions from 700-question Intercom set, Langfuse pipeline live, CS agent validated."

## Infrastructure

- [[Cloud Run + Cloud SQL Pattern]] — Single-container Cloud Run service (FastAPI + SPA) connected to Cloud SQL via the built-in Auth Proxy unix socket — no public IP, no SSL config, private GCP-internal networking by default.
- [[Input Guardrails Pipeline]] — 7-stage deterministic safety pipeline (normalise → size check → domain classify → injection detect → PII redact → XML envelope → advisory) that runs before every LLM call — LLM-free by design.
- [[Langfuse ADK Tracing Patterns]] — Two-layer Langfuse instrumentation for ADK agents — OpenTelemetry auto-instrumentation plus manual @observe decorators produce a single unified trace tree; session grouping, RAG path tagging, and first-class Scores are the critical operational additions.
- [[Langfuse Platform]] — Langfuse is an open-source LLM engineering platform for tracing, prompt management, and evaluation — chosen by [client]'s AI teams as the observability standard, with SSO and governance pending before production rollout. Instrumentation patterns vary by framework (lf.trace() for ADK, CallbackHandler for LangGraph, @observe for FastAPI).
- [[Observability and Runtime Patterns]] — Observability tool choice (LangSmith vs Langfuse), tracing architecture, runtime topology and checkpointer alignment rules, trigger patterns, and key signals to monitor for VA agents.
- [[Observability — LangFuse vs LangSmith Decision]] — Decision to use LangFuse first for RAG observability — native ragas/deepeval integrations, self-hostable, GDPR-friendly, and highest weighted score (8.58/10) for [client]'s AWS-hosted, high-compliance context.
- [[PGVector Migration Pattern]] — Migrating a vector store from in-memory NumPy arrays to PostgreSQL + pgvector — preserving the public API, using cosine distance operator, adding an IVFFlat index, and moving embeddings to Cloud SQL without re-embedding.
- [[PII Masking Approaches]] — Regex vs LLM-based vs hybrid PII masking for conversation data pipelines — contextual PII is the hard problem; compliance sign-off is a hard gate before data moves.
- [[Prefix Caching]] — Claude's automatic KV cache reuse for repeated prompt prefixes — cuts latency and cost by 90% for static system prompts and long tool schemas.
- [[Presidio PII Redaction for Langfuse]] — Presidio orchestration layer with spaCy fr_core_news_lg + CamemBERT NER + custom regex recognizers for French financial PII — wired into Langfuse via the SDK mask hook as a single interception point before traces leave the process.
- [[Production Hardening Patterns]] — Checklist of production hardening fixes for the Librarian service — P0/P1/P2 issues, async I/O safety, SQL injection prevention, CORS, and Docker packaging.
- [[Production Readiness Backlog]] — The pre-launch gap checklist for a RAG service going to managed cloud hosting — auth, CORS, structured logging, tests, CI gate, staging separation, probes, retries, migrations — each stated as current-state vs required.
- [[Safeguards Architecture — Five Protection Layers]] — Five-layer runtime safety pipeline for production agents — input guardrails, routing confidence, retrieval quality (CRAG), post-generation grounding check, and escalation routing — each with distinct latency cost and failure mode.
- [[System Design — Shared Code-Index Service]] — Interview-format system design writeup of the DSSG shared indexer — centralized indexer + query API with MCP as a thin read-only client, DuckDB single-writer risk, and the pgvector escape hatch.

## Interview Prep

- [[Agents Interview Study Guide]] — Exam-prep reference for agent architecture questions — workflow vs agent distinction, composable patterns, ACI tool design, harness engineering, long-horizon reliability, and memory taxonomy.
- [[Evals and Observability Interview Study Guide]] — Exam-prep reference for eval and observability questions — vocabulary, grader types, three-tier taxonomy, pass@k vs pass^k, and the tracing-first discipline.
- [[LLM Fundamentals Interview Study Guide]] — Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes.
- [[RAG Interview Study Guide]] — Exam-prep reference for RAG architecture questions — component choices, architecture variants, production judgment, measured benchmarks, and terminology traps.
- [[System Design Interview Study Guide]] — Method guide for the ML/LLM/agent system design round — 5-step process, trade-off narration formula, LLM reference architecture, bottleneck table, and failure mode reflexes.

## Meta

- [[Agile Workflow Definitions]] — Definition of Ready, Definition of Done, WIP limits, weekly cadence, and ceremony-to-skill mapping for the Claude Code workflow system.
- [[Claude Code Hook Architecture]] — Claude Code lifecycle hooks — PreToolUse/PostToolUse events, exit-code protocol (0=pass, 2=block), and the hook suite pattern used to enforce code quality automatically without mid-task reminders.
- [[Claude Workflow System]] — Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints, and session notes — that automates context management across multi-phase engineering workflows.
- [[Code Review Drill — SANYI]] — Code-review interview drill using a real SANYI review as the worked example — a two-line diff that lints clean but violates the change contract, and the reviewing method that catches it.
- [[Documentation Boundary — Machine vs Human Docs]] — Who writes what — machine-consumed docs (CLAUDE.md, skills, plans) vs human-consumed docs (READMEs, wiki, design docs), with the akira dao exception.
- [[Karpathy LLM Wiki Pattern]] — The compiler analogy for personal knowledge bases — raw sources in, LLM compiles them into structured interlinked wiki pages, no vector infra needed.
- [[No-Placeholder Plan Discipline]] — A plan handed to an implementing agent carries every file's content in full, and a gap is treated as a defect in the plan rather than license for the agent to invent — with verification steps that check structure, not behavior, when the deliverable is markdown.
- [[Plan-Doc Status Enum]] — Nine-member Status enum for plan docs (7 in-flight, 2 terminal) with a forbid-and-relocate suffix policy — the Status line carries exactly one token, everything else moves to named fields.
- [[Puffin Consciousness Development Skills]] — A chained Claude Code skill family in the `guacamayo` project (renamed from `puffin` 2026-07-17) (genesis → wake → grow → reflect → synthesize → dream) that walks a user and Claude through a staged, multi-session self-development process — grounded in "user seed material" collected from prior conversations.
- [[SANYI Change-Contract System]] — Three-layer change-contract system (变易/简易/不易) for agent architectures — classifies every component into ever-changing, simple, or invariant, then enforces cross-layer discipline via init/review/audit modes.
- [[Session Insights]] — Compiled insights from 42 facet-analyzed Claude Code sessions — friction patterns, recurring themes, skill candidates, and learning outcomes.
- [[Session Knowledge Capture Patterns]] — Patterns for capturing, enriching, and classifying session knowledge — output type taxonomy, pre-compact enrichment, and the session-as-source-of-truth approach.
- [[Skill-Knowledge Information Flow]] — How knowledge flows between the four parallel systems — global skills, ai-project-template, learn-ai-engineering, and the librarian wiki — and the sync contracts between them.

## Projects

- [[Atlas Project]] — Time-series forecasting and customer-segmentation agent system — Planner/Forecaster/Evaluator/Learner loop over ARIMA and Chronos models, an HDBSCAN-with-KMeans-fallback segmentation pipeline, and a Neo4j knowledge graph linking customers to segments and merchants.
- [[Change-Contracts Rollout]] — 2026-07-17 decision record — SANYI promoted to the global skills reservoir, SANYI.md contracts drafted for playground/librarian/atlas, contract checks wired into review skills, template seeds contracts at scaffold time; akira rollout blocked on hardcoded scan paths.
- [[Librarian Graph Explorer]] — Local React Flow wiki graph explorer — multi-dimensional edge types (wikilink/semantic/tag-shared), UMAP semantic layout, and agent chat with graph highlighting and wikilink write-back. Addresses the gap where Obsidian cannot do multi-edge toggling or embedding-based spatial layout.
- [[Librarian KB — Build Plan]] — Phased build plan for the Librarian KB — Phases 1–5 complete, Phase 6 (connectors) active, Phase 8A+B (React Flow UI) done, Phases 9–15 future.
- [[Librarian Project]] — The Librarian service — a LangGraph CRAG-based RAG pipeline for knowledge retrieval, deployed as a Python FastAPI service with evaluation harness.
- [[Listen-Wiseer Project]] — Spotify recommendation agent with ENOA taste-map personalisation — LangGraph ReAct + Chainlit UI, LightGBM classifiers, DuckDB vss RAG, and three-tier eval harness.
- [[Parallax]] — Evidence-driven PR review system for general and agentic changes — the judging third of the Akira (observes) / SANYI (governs) / Parallax (judges) triad, deliberately optimizing against comment count.
- [[NYC-DSSG Project]] — NYC Data Science for Social Good — platform engineering for a nonprofit serving 600+ nonprofits via 300 volunteers; building knowledge base, project templates, and PM agent.
