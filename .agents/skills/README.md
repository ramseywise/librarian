# `.agents/skills/` — Skill Index

Agent skills loaded on demand by the Deep Agents harness. Each skill injects reference
material and patterns into agent context when invoked. Not slash commands — loaded at runtime.

> **Also useful for Claude coding sessions** when building or modifying agent code in this repo.
> Claude can read any of these skill files directly for framework reference.

---

## Entry Point

| Skill | One-line summary |
|-------|-----------------|
| `framework-selection` | **Start here.** Decides whether to use LangChain, LangGraph, or Deep Agents for a given task. |

---

## Google ADK Skills

For building agents with the Google Agent Development Kit (Python).

| Skill | One-line summary | References |
|-------|-----------------|------------|
| `adk-cheatsheet` | API quick reference — agent types, tools, orchestration, callbacks, state management. | `python.md`, `docs-index.md` |
| `adk-dev-guide` | Development lifecycle: project layout, mandatory conventions, testing, iteration workflow. | — |
| `adk-scaffold` | Scaffold a new ADK agent project — directory layout, pyproject.toml, Makefile, .env. | — |
| `adk-deploy-guide` | Deploy ADK agents to Agent Engine, Cloud Run, GKE, or event-driven triggers with Terraform. | `agent-engine.md`, `cloud-run.md`, `event-driven.md`, `terraform-patterns.md` |
| `adk-eval-guide` | Evaluation methodology — evalset schema, LLM-as-judge, metrics, multimodal evals. | `criteria-guide.md`, `builtin-tools-eval.md`, `multimodal-eval.md`, `user-simulation.md` |
| `adk-observability-guide` | Observability — Cloud Trace, Cloud Logging, BigQuery analytics for production traffic. | `cloud-trace-and-logging.md`, `bigquery-agent-analytics.md` |

---

## Deep Agents Skills

For building with the Deep Agents harness (LangChain + LangGraph + opinionated middleware).

| Skill | One-line summary | References |
|-------|-----------------|------------|
| `deep-agents-core` | Harness architecture, `create_deep_agent()`, SKILL.md format, configuration options. | — |
| `deep-agents-memory` | Pluggable storage: `StateBackend` (ephemeral), `StoreBackend` (persistent), `CompositeBackend`, `FilesystemMiddleware`. | — |
| `deep-agents-orchestration` | Sub-agents, task planning (`TodoListMiddleware`), human-in-the-loop approval flows. | `langgraph-compat.md` |

---

## LangChain / LangGraph Skills

Framework reference for the layers Deep Agents is built on.

| Skill | One-line summary | References |
|-------|-----------------|------------|
| `langchain-dependencies` | Package versions, installation order, and dependency pinning for LangChain projects. | — |
| `langchain-fundamentals` | `create_agent`, tool definitions, chains, and basic middleware setup. | — |
| `langchain-middleware` | Human-in-the-loop approval, custom middleware, structured output patterns. | — |
| `langchain-rag` | Full RAG pipeline — loaders, chunking, embeddings, vector stores (Chroma/FAISS/Pinecone). | `rag-strategies.md`, `advanced-patterns.md` |
| `langgraph-fundamentals` | `StateGraph`, nodes, edges, `Command`, `Send`, state schemas, invocation patterns. | — |
| `langgraph-persistence` | Checkpointers, thread IDs, time travel, `Store`, subgraph persistence scoping. | — |
| `langgraph-human-in-the-loop` | Interrupt, pause-for-approval, error recovery, and human feedback patterns. | — |

---

## Research → References mapping

The following research docs from `.claude/docs/` contain evergreen knowledge that should live
as `references/` files here, so agents and Claude coding sessions can load them on demand.

| Research doc | Proposed location | Covers |
|---|---|---|
| `.claude/docs/in-progress/librarian-architecture/research-adk-orchestration.md` | `deep-agents-orchestration/references/langgraph-compat.md` | ADK vs LangGraph mental model, primitive mapping, vocabulary translation |
| `.claude/docs/backlog/rag-agent-template/research.md` | `langchain-rag/references/rag-strategies.md` | Multi-turn, CRAG, chunking, reranking, intent routing — patterns from help-assistant + listen-wiseer |
| `.claude/docs/backlog/agentic-rag-copilot/research.md` | `langchain-rag/references/advanced-patterns.md` | Self-RAG, GraphRAG, A2A protocol, Plan-and-Execute, agentic evaluation |

The research docs stay in `.claude/docs/` as planning artifacts. The reference copies here
are distilled for agent consumption.

---

## Claude Code relevance

These skills are all useful when Claude is **coding** in this repo, not just when agents run:

- `adk-cheatsheet` — read before writing any ADK agent code
- `adk-dev-guide` — conventions to follow in this project
- `framework-selection` — before choosing which layer to build on
- `deep-agents-core` — before modifying the harness or creating new agents
- `langchain-rag` + `langgraph-persistence` — before touching retrieval or memory code
