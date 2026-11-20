# Wiki directories, domain tags, optional sections

Moved from CLAUDE.md. The routing rule (patterns vs subject vs interview) and the private rules stay in CLAUDE.md.

## Topics within a large directory

`data/wiki/_topics.yaml` lists the topics of each directory past about 100 pages (data-analytics,
data-engineering, eval, multimodal, llm on 2026-11-19; data-science on 2026-11-20). A page there carries exactly one as a tag;
`/lint` WARNs on none or two. Where a course module covers the directory, the topic is the module's
slug. A page with no fitting topic is a candidate to move, so it is left untagged and the WARN
stays. Tier ("introduced at") and modules are not tags: `courses/curriculum.py` derives them
from the notes that link a page.

## Subdirectories of `data/wiki/`

The top-level directory is the page's domain (its first tag). A subdirectory only files pages:
`frameworks/adk/x.md` has domain `frameworks`, with `adk` kept as a topic tag. The four subject
directories and `llm/` came from splitting the old `foundations/` on 2026-11-10 (routed by the
course that links each page); `patterns/`, `meta/`, `projects/` and `interview/` moved under
`private/` the same day.

Subjects (each its own area on the map):

  - `data/wiki/programming/` — Python, software design, testing, tooling, algorithms as a craft
  - `data/wiki/data-analytics/` — Statistics, experimentation, SQL, BI, applied analyses
  - `data/wiki/data-science/` — Classical ML, deep learning, NLP, model evaluation, MLOps
  - `data/wiki/data-engineering/` — Data systems, pipelines, storage formats, orchestration, data quality

Generative AI:

  - `data/wiki/llm/` — Transformer and LLM fundamentals: architectures, training, fine-tuning, inference, alignment, agents as a model capability
  - `data/wiki/frameworks/adk/` — Google ADK, SKILL.md, VA patterns, voice, orchestration
  - `data/wiki/frameworks/langgraph/` — LangGraph state machines, CRAG, checkpointers, reducers, streaming, Deep Agents
  - `data/wiki/rag/` — RAG, retrieval, chunking, embeddings, reranking, hybrid search
  - `data/wiki/eval/` — Evaluation harnesses, LLM judges, annotation pipelines, preference alignment
  - `data/wiki/memory/` — Agent memory patterns (in-context, episodic, semantic, procedural)

AI Engineering:

  - `data/wiki/prompting/` — Prompt engineering as a discipline: prompt construction, injection defence, structured output, few-shot design
  - `data/wiki/context/` — Context engineering: assembly, compaction, window budgeting, retrieval-into-context (distinct from `context-management` runtime tactics in `infra/`)
  - `data/wiki/harness/` — Agent harness engineering: harness anatomy and maturity, execution boundaries and guardrails, retry and termination design, verification loops, tool design, deployment anti-patterns
  - `data/wiki/loop/` — Loop engineering: the cycle that re-prompts, checks and stops an agent unattended (autonomy ladder, termination design, state files, evolve loop, self-modification, where lessons are stored)
  - `data/wiki/graph/` — Graph engineering and knowledge graphs: node, edge and state primitives, graph governance, entity resolution, text-to-Cypher, graph ML, graph retrieval, multi-agent topology and failure modes
  - `data/wiki/mcp/` — Model Context Protocol, tool schemas, A2A
  - `data/wiki/infra/` — Deployment, observability, caching, security, production hardening
  - `data/wiki/multimodal/` — Image, video and audio models: generation (GANs, diffusion, text-to-image and video), vision-language models and multimodal understanding, vision and speech encoders, embodied and robot policies built on them

Private (gitignored, never committed, never on the map, never in `_index.md`; same page format, still compiled and queryable locally):

  - `data/wiki/private/patterns/` — **Experiential knowledge: findings from your own build sessions.** Named, non-obvious mechanisms discovered while working (`silent-fallthrough-string-discovery`, `copier-re-entry-capability-path`), alongside the framework-agnostic classics (ReAct, CoT, ACI). This is the wiki's highest-value bucket and the core of the Karpathy use case — do not dilute it with textbook material. Externally-sourced concept knowledge belongs in a public subject directory above.
  - `data/wiki/private/meta/` — Wiki-about-wiki: Karpathy pattern, Claude workflow system, session knowledge
  - `data/wiki/private/projects/` — Per-project knowledge (librarian, listen-wiseer, etc.)
  - `data/wiki/private/interview/` — Coding-interview patterns (arrays/hashing, two pointers, sliding window, …), system design, prep references
  - `data/wiki/private/` (loose) — Company/project-specific pages with proprietary context, client names or internal details. Public pages never link into `private/` (`wiki check` blocks it): a public page that must cite a private finding repeats the point in its own words.

  - `data/wiki/_index.md` — Auto-generated TOC, updated after every ingest. Do not list `data/wiki/private/` entries here.
  - `data/wiki/_conflicts.md` — Flagged contradictions between sources

## Optional sections


`## What argues against it` and `## Open questions` go before `## See Also`. Both are optional and recommended for `private/patterns/` pages. Write them only when a source supports them, never to fill the slot. Existing pages are not backfilled.

## Domain tags


> The canonical domain list is derived from disk: directories under `data/wiki/`
> (excluding `private/`). The table below is illustrative, not normative.

| Tag | Covers |
|---|---|
| `programming`, `data-analytics`, `data-science`, `data-engineering` | The four subject directories; one each |
| `frameworks` | Agent frameworks; the directory tag of `frameworks/adk/` and `frameworks/langgraph/` |
| `adk` | Google Agent Development Kit — patterns, APIs, deployment (topic tag) |
| `langgraph` | LangGraph state machines, CRAG, checkpointers, edges (topic tag) |
| `rag` | Retrieval-augmented generation, embedders, rerankers, chunking |
| `memory` | Agent memory patterns — short-term, long-term, episodic, semantic |
| `mcp` | Model Context Protocol, MCP server design, tool schemas |
| `voice` | Voice agent patterns, BIDI streaming, session management |
| `eval` | Evaluation harnesses, LLM judges, golden sets, metrics |
| `infra` | Deployment, CI/CD, observability (LangFuse/LangSmith/Cloud Trace), caching |
| `llm` | Transformer and LLM fundamentals: architectures, training, fine-tuning, inference, alignment |
| `deep-agents` | Deep Agents harness — middleware, StateBackend, StoreBackend, skill format |
| `context-management` | Prefix caching, session compaction, history pruning, context windows |
| `interview` | Coding-interview patterns, algorithms, system design, prep material (private only) |
| `multimodal` | Image, video and audio generation, vision-language models, multimodal encoders and benchmarks |

## Domains index


Use `data/wiki/_index.md` to find pages by domain. The index is maintained automatically during ingest.

When searching for a page, check:
1. `data/wiki/_index.md` for the canonical list
2. The domain subdirectory directly: `data/wiki/rag/`, `data/wiki/frameworks/langgraph/`, `data/wiki/data-science/`, etc.
3. `data/wiki/private/projects/` for project-level pages (local only)

---
