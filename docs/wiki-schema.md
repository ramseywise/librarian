# Wiki directories, domain tags, optional sections

Moved from CLAUDE.md. The routing rule (patterns vs subject vs interview) and the private rules stay in CLAUDE.md.

## Subdirectories of `data/wiki/`

  - `data/wiki/rag/` — RAG, retrieval, chunking, embeddings, reranking, hybrid search
  - `data/wiki/langgraph/` — LangGraph state machines, CRAG, checkpointers, reducers, streaming
  - `data/wiki/adk/` — Google ADK, SKILL.md, VA patterns, voice, orchestration
  - `data/wiki/infra/` — Deployment, observability, caching, security, production hardening
  - `data/wiki/patterns/` — **Experiential knowledge: findings from your own build sessions.** Named, non-obvious mechanisms discovered while working (`silent-fallthrough-string-discovery`, `copier-re-entry-capability-path`), alongside the framework-agnostic classics (ReAct, CoT, ACI). This is the wiki's highest-value bucket and the core of the Karpathy use case — do not dilute it with textbook material. Externally-sourced concept knowledge belongs in a subject directory below.
  - `data/wiki/eval/` — Evaluation harnesses, LLM judges, annotation pipelines, preference alignment
  - `data/wiki/deep-agents/` — Deep Agents harness, middleware, state/store backends
  - `data/wiki/memory/` — Agent memory patterns (in-context, episodic, semantic, procedural)
  - `data/wiki/mcp/` — Model Context Protocol, tool schemas, A2A
  - `data/wiki/prompting/` — Prompt engineering as a discipline: prompt construction, injection defence, structured output, few-shot design
  - `data/wiki/context/` — Context engineering: assembly, compaction, window budgeting, retrieval-into-context (distinct from `context-management` runtime tactics in `infra/`)
  - `data/wiki/foundations/` — ML/DS/data-engineering fundamentals: classical ML, deep learning, NLP, data systems, MLOps
  - `data/wiki/interview/` — Coding-interview patterns (arrays/hashing, two pointers, sliding window, …), system design, prep references
  - `data/wiki/meta/` — Wiki-about-wiki: Karpathy pattern, Claude workflow system, session knowledge
  - `data/wiki/graph/` — Graph engineering and knowledge graphs: node, edge and state primitives, graph governance, entity resolution, text-to-Cypher, graph ML, graph retrieval, multi-agent topology and failure modes
  - `data/wiki/harness/` — Agent harness engineering: harness anatomy and maturity, execution boundaries and guardrails, retry and termination design, verification loops, tool design, deployment anti-patterns
  - `data/wiki/loop/` — Loop engineering: the cycle that re-prompts, checks and stops an agent unattended (autonomy ladder, termination design, state files, evolve loop, self-modification, where lessons are stored)
  - `data/wiki/multimodal/` — Image, video and audio models: generation (GANs, diffusion, text-to-image and video), vision-language models and multimodal understanding, vision and speech encoders, embodied and robot policies built on them
  - `data/wiki/projects/` — Per-project knowledge (generic, public — librarian, listen-wiseer, etc.)
  - `data/wiki/private/` — Company/project-specific pages; **gitignored, never committed**. Move pages here when they contain proprietary context, client names, or internal project details. Use the same page format — they are still compiled and queryable locally.
  - `data/wiki/_index.md` — Auto-generated TOC, updated after every ingest. Do not list `data/wiki/private/` entries here.
  - `data/wiki/_conflicts.md` — Flagged contradictions between sources

## Optional sections


`## What argues against it` and `## Open questions` go before `## See Also`. Both are optional and recommended for `patterns/` pages. Write them only when a source supports them, never to fill the slot. Existing pages are not backfilled.

## Domain tags


> The canonical domain list is derived from disk: directories under `data/wiki/`
> (excluding `private/`). The table below is illustrative, not normative.

| Tag | Covers |
|---|---|
| `adk` | Google Agent Development Kit — patterns, APIs, deployment |
| `langgraph` | LangGraph state machines, CRAG, checkpointers, edges |
| `rag` | Retrieval-augmented generation, embedders, rerankers, chunking |
| `memory` | Agent memory patterns — short-term, long-term, episodic, semantic |
| `mcp` | Model Context Protocol, MCP server design, tool schemas |
| `voice` | Voice agent patterns, BIDI streaming, session management |
| `eval` | Evaluation harnesses, LLM judges, golden sets, metrics |
| `infra` | Deployment, CI/CD, observability (LangFuse/LangSmith/Cloud Trace), caching |
| `llm` | LLM API patterns, prompt engineering, context management |
| `deep-agents` | Deep Agents harness — middleware, StateBackend, StoreBackend, skill format |
| `context-management` | Prefix caching, session compaction, history pruning, context windows |
| `foundations` | ML/DS/data-engineering fundamentals — classical ML, deep learning, NLP, data systems, MLOps |
| `interview` | Coding-interview patterns, algorithms, system design, prep material |
| `multimodal` | Image, video and audio generation, vision-language models, multimodal encoders and benchmarks |

## Domains index


Use `data/wiki/_index.md` to find pages by domain. The index is maintained automatically during ingest.

When searching for a page, check:
1. `data/wiki/_index.md` for the canonical list
2. The domain subdirectory directly: `data/wiki/rag/`, `data/wiki/langgraph/`, `data/wiki/adk/`, etc.
3. `data/wiki/projects/` for project-level pages

---
