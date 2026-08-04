---
title: Agent Scaffolding Skill Layers
tags: [pattern, context-management]
summary: A three-layer Claude Code skill design for scaffolding agents — a generic parallel-subagent factory (L1), standalone capability add-skills that read the target before generating (L2), and a domain-specific bundle that orchestrates L2 skills in sequence (L3).
updated: 2026-07-14
sources:
  - raw/claude-docs/project-g/skills/agent-creation/new-agent/SKILL.md
  - raw/claude-docs/project-g/skills/agent-creation/new-support-agent/SKILL.md
  - raw/claude-docs/project-g/skills/agent-creation/add-rag/SKILL.md
  - raw/claude-docs/project-g/skills/agent-creation/add-guardrails/SKILL.md
  - raw/claude-docs/project-g/skills/agent-creation/add-hitl/SKILL.md
  - raw/claude-docs/project-g/skills/agent-creation/add-eval/SKILL.md
---

# Agent Scaffolding Skill Layers

A skill-design pattern for repos that build many similar agents: split scaffolding into three layers instead of one monolithic "create an agent" skill. Observed in project-g's `agent-creation/` skill family, but the layering itself is framework-agnostic and reusable in any repo that scaffolds recurring artifact types (agents, services, pipelines).

## The Three Layers

| Layer | Role | Example | Invocation |
|---|---|---|---|
| **L1 — Generic factory** | Framework-agnostic full scaffold from nothing — schema, state, graph/callbacks, infra, tests, eval harness, docs | `new-agent` | `/new-agent <name> --framework adk\|langgraph --capabilities rag,hitl,...` |
| **L2 — Capability add-ons** | Adds one capability to an *existing* agent, standalone and reusable | `add-rag`, `add-guardrails`, `add-hitl`, `add-eval` | `/add-rag <path>`, invoked directly or by an L3 skill |
| **L3 — Domain bundle** | An opinionated composition of L2 skills for one recurring agent archetype | `new-support-agent` | Orchestrates `add-rag` → `add-guardrails` → `add-eval` over a foundation skeleton |

**Key discipline: L3 does not reimplement L2's logic.** It builds the minimal foundation skeleton (schema, config, entry point) then *invokes* the L2 skills in sequence. This keeps the capability logic defined exactly once — a bug fix or pattern update to `add-rag` automatically benefits every path that uses it (standalone or via L3), instead of drifting across copies.

## L1: Parallel Subagent Dispatch for Speed

The generic factory's defining mechanism: instead of one sequential pass writing every file, it spawns one subagent per concern (schema-builder, agent-builder, infra-builder, test-scaffolder, eval-harness-builder, docs-builder, plus one per requested capability) **in a single message**, each with `isolation: "worktree"` and only its own spec slice (5–15 KB) — never the full conversation context. Total wall-clock time approaches single-subagent time; total token cost is `n_subagents × ~10K tokens` rather than one large sequential context.

This is a concrete instance of parallel fan-out for code generation — the same "avoid a single giant context" discipline that motivates [[Send API Fan-out]] in LangGraph, applied to skill/subagent orchestration rather than graph nodes.

**Capability tokens** (`--capabilities rag,hitl,streaming,...`) are the L1 factory's extension point: each token maps to a spec file (`cap-{capability}.md`) and, if present in the invocation, spawns one additional capability-builder subagent using the same prompt template as the core six.

## L2: Read-Target-Before-Generating Discipline

Every capability add-skill follows the same two-step shape regardless of what it adds:

1. **Read the ref docs** — the project's own architecture docs for that capability (e.g. `add-rag` reads the retrieval-improvements research doc and the KB reference doc before writing anything).
2. **Read the target agent** — the actual `agent.py`/`main.py`/`config.py` of the repo passed in `$ARGUMENTS`, to detect the framework (LangGraph vs ADK) and what's already wired, so generated code fits rather than duplicating or conflicting.

Only after both reads does the skill generate code — and it branches on framework at the wiring step (a LangGraph node vs. an ADK callback/`FunctionTool` for the same capability). This ordering (docs → existing code → generate) is the core transferable rule: **an L2 skill is a template plus two context-gathering reads, not a template alone.**

## L3: Orchestration Without Reimplementation

The domain-bundle skill (`new-support-agent`) demonstrates the composition contract:

1. Gather requirements (name, framework, domain, output dir).
2. Write the minimum-viable foundation skeleton — schema, config, entry point, prompts dir, empty tests. No capability code yet.
3. Invoke the L2 skills in a fixed order: RAG retrieval first, then guardrails, then eval harness — each L2 skill's own "read the target" step naturally picks up what the previous step just wrote.
4. Register the new agent (compose file / Makefile) and update any shared cross-agent tracking doc (e.g. a safeguards coverage table).
5. Smoke test.

**Anti-pattern this avoids:** an L3 skill that inlines its own copy of "how to wire Bedrock retrieval" — that copy drifts from the L2 skill's copy the first time either one is updated, and now there are two sources of truth for the same capability.

## When to Use This Pattern

Reach for the three-layer split when:
- The same capability (retrieval, guardrails, HITL, eval harness) needs to be addable to agents that already exist, not just new ones — L2 skills must work standalone.
- Multiple domain archetypes exist (support agent, forecasting agent, ops agent) that differ only in *which* capabilities they bundle and in what order — L3 skills are then thin compositions, not new logic.
- Scaffolding a full agent from scratch is common enough to be worth the parallel-subagent investment (L1) — for a one-off agent, a single sequential skill is simpler.

## See Also
- [[Multi-Agent Role Specialization]] <!-- auto-linked -->
- [[Skill Preloading via Agent Definition]] <!-- auto-linked -->
- [[VA Product Design Patterns]] <!-- auto-linked -->
- [[project-g Project]] — the concrete instance this pattern was extracted from (`agent-creation/` skill family)
- [[VA Bedrock KB Reference]] — the RAG capability's generated retrieval-module template
- [[project-g Safeguards Architecture]] — the guardrails capability's 5-layer target
- [[Send API Fan-out]] — the same parallel-dispatch discipline applied to LangGraph graph execution
- [[Multi-Repo Claude Organization]] — the broader skill-scope (global vs per-repo) decision this pattern lives inside
- [[SKILL.md Pattern]]
