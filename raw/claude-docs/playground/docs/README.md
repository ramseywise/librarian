# .claude/docs

Reference documentation for this project. Curated for anyone wanting to understand the
architecture, key decisions, and tooling — not a dump of every planning artifact.

---

## architecture/

Design decisions, framework comparisons, and system-level research. Start here if you're
new to the project.

| Doc | What it covers |
|---|---|
| [va-adk-implementation.md](architecture/va-adk-implementation.md) | How the VA is structured with Google ADK — why two layers (agents/ and gateway/), the sub-agent pattern, what's confusing about the current layout, and what a cleaner structure would look like |
| [langgraph-vs-adk.md](architecture/langgraph-vs-adk.md) | Side-by-side mental model comparison: agent-centric/event-driven (ADK) vs. graph/state-machine (LangGraph). Covers primitives mapping, state management, observability, callback hooks, and when each framework is the right choice |
| [custom-rag-vs-managed-kb.md](architecture/custom-rag-vs-managed-kb.md) | Build vs buy for RAG: custom LangGraph pipeline vs AWS Bedrock Knowledge Bases across 7 dimensions (retrieval quality, multi-turn accuracy, observability, latency, cost, corpus control, vendor lock-in) |
| [architecture-decisions.md](architecture/architecture-decisions.md) | The three design options considered (full Bedrock / full LangGraph / polyglot), with tradeoffs, verdicts, and the recommended migration path |
| [rag-patterns.md](architecture/rag-patterns.md) | Comprehensive RAG research reference: all chunking and retrieval strategies evaluated, CRAG implementation, reranker comparison, intent classification, multi-agent vs single-graph design, observability platform selection, production benchmarks from RAPTOR v1 |

---

## tooling/

How the project's dev tooling is configured.

| Doc | What it covers |
|---|---|
| [hooks-architecture.md](tooling/hooks-architecture.md) | How the Claude Code hook suite works — lifecycle events, exit codes, per-hook responsibilities, how to add a new hook |
| [eval-harness.md](tooling/eval-harness.md) | The `va-langgraph` eval framework — 278 real Clara fixtures, 4 graders (routing, safety, schema, message_quality), how to run and extend it |
| [observability-setup.md](tooling/observability-setup.md) | How tracing is wired for both VA implementations (LangSmith for both; Langfuse as the commented-out alternative). Also documents how to switch to Langfuse |
| [adk-js.md](tooling/adk-js.md) | Google ADK JS patterns and conventions |
| [demo.md](tooling/demo.md) | Demo setup and walkthrough |
| [nextjs-16-app-router.md](tooling/nextjs-16-app-router.md) | Next.js App Router conventions used in this project |

---

## What is and isn't tracked in git

| Directory | Tracked | Notes |
|-----------|---------|-------|
| `research/` | ✅ yes | Permanent knowledge base — architecture decisions, evaluated patterns |
| `tooling/` | ✅ yes | Curated reference for dev tooling |
| `plans/` | ❌ no (gitignored) | Local-only implementation specs — delete after execution |
| `reviews/` | ❌ no (gitignored) | Local-only code review artifacts — ephemeral |

Active plans live in `plans/` (local only). When a plan is complete, promote the key decisions into a `research/` doc and delete the plan file.
