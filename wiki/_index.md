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

## Coverage Gaps

*Sources in `raw/` not yet fully compiled into wiki pages.*

Remaining sources without full wiki coverage:
- `raw/playground-docs/py-copilot-research.md` — Python copilot multi-agent topology (partial coverage in [[ADK Context Engineering]])
- `raw/playground-docs/librarian-ts-parity-research.md` — TS parity patterns (partial coverage in [[Librarian Project]])
- `raw/playground-docs/research-agent-refactor-research.md` — Research agent note quality (covered in [[Librarian Project]])
- `raw/claude-docs/playground/docs/archived/visualizer-improvements/` — Slide deck agent (distinct from RAG pipeline; low wiki priority)
- `raw/claude-docs/playground/docs/archived/docs-restructure/research.md` — Scope/Build/Archive docs lifecycle model (meta-pattern for `.claude/docs/`)
- `raw/claude-docs/playground/docs/archived/librarian-restructure/plan.md` — Superseded directory restructure (no action needed)
- `raw/sessions/` — 54 session notes: first prompt + token stats only; actual knowledge captured in playground-docs and archived plans. **Skip.**
- `raw/claude-docs/playground/skills/` — 26 skill files (pending ingest — will populate skill reference stubs in `.agents/skills/`)
