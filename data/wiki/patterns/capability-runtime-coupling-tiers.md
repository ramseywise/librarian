---
title: Capability Runtime-Coupling Tiers
tags: [llm, patterns, pattern]
summary: Sorting agent capabilities into runtime-coupled (T1), runtime-adjacent (T2), and runtime-independent (T3) — because cross-runtime parity is a meaningful goal for T1/T2 and a category error for T3.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-20-consolidate-capability-reference.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-agents-skills-sync.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/adk-dev-guide.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/adk-dev-guide.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/adk-scaffold.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/adk-scaffold.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-a2a.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-a2a.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-batch.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-batch.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-cluster.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-cluster.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-compaction.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-compaction.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-finetune.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-finetune.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-forecast.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-forecast.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-genai.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-genai.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-guardrails.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-guardrails.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-hitl.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-hitl.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-kg.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-kg.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-langchain.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-langchain.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-mcp.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-mcp.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-observability.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-observability.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-rag.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-rag.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-rlhf.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-rlhf.md
  - data/raw/claude-docs/galactus/skills/new-agent/SKILL.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-search.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-search.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-streaming.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-streaming.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/cap-vision.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/cap-vision.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/core.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/core.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/docs.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/docs.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/eval.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/eval.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/framework-adk.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/framework-adk.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/framework-lg.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/framework-lg.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/infra.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/infra.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/langgraph-scaffold.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/langgraph-scaffold.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/test.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/test.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-research-A-capability-parity.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-research-A-capability-parity.md
---

# Capability Runtime-Coupling Tiers

A 14-capability code-gen payload looked like one flat collection of
framework-specific templates. Auditing it across four runtimes (Claude, ADK,
LangGraph, Vercel) found that **the 14 are three different kinds of thing**, with
radically different parity profiles:

| Tier | Name | Count | Parity question |
|---|---|---|---|
| **T1** | Runtime-coupled | 3 | Genuine — each runtime does it differently |
| **T2** | Runtime-adjacent | 5 | Real, needs a per-runtime table |
| **T3** | Runtime-independent | 6 | **A category error** |

## Why T3 is the load-bearing finding

Six of the fourteen are ordinary library code that happens to be called from an
agent. Asking "what is the LangGraph version of this?" is malformed — there
isn't one, because the capability never touched the runtime. For T3 the file
should carry an explicit *"host-language/library capability"* statement rather
than a parity table with four near-identical cells.

This reframes parity work: a matrix that dutifully fills in every cell for all 14
capabilities is manufacturing six rows of fake variance. The tier annotation is
what stops a future reader from trying to close a gap that does not exist.

A related classification error sat in the same list: **`langchain` is not a
capability — it is a competing framework.** It had been filed alongside things
like vision and batch because the payload's only organizing axis was "file in the
references directory."

## The missing contract layer

The audit's second finding was structural: **no contract layer existed anywhere
in the corpus.** Every file was code-first — a template with no prose stating
what the capability *means* independent of how it is implemented. That is not a
refactor; the contract has to be written from scratch.

The remedy shape, applied to all 14 files:

- an `## Agnostic contract` section at the top — what this capability is
- a `## Design notes` section — consolidated rationale
- declared tier membership
- for **T2**: a runtime-parity table across the four runtimes
- for **T3**: the explicit host-language statement
- surfaced flags for security issues, stale constants, and version-brittleness

The acceptance criterion that enforces it is negative and checkable: **no file is
code-first-only.**

## Tiers drive the ref layout

The tiering fed a three-layer documentation split — nine tooling-agnostic
`agent-*` convention refs holding the durable contracts, with framework refs
(`langgraph.md`, `google-adk.md`, `adk-vercel.md`) narrowed from prescriptive
walkthroughs to **bindings** that point into them (`"For X agents, read:
agent-architecture.md §5.1"`). The stated criteria: each binding under 300 lines,
and **no content duplication between binding and convention ref**.

An inversion the audit caught: `refs/adk-vercel.md` held the best
deployment-topology content in any store, *"buried under a framework ref where
nobody looks."* Content filed by framework when it is actually tier-independent
becomes unfindable — which is the same failure the tiering fixes at the payload
layer.

## Deferring the contested half

Roughly half the proposed canon sat on ground the research flagged as contested —
OTel GenAI attribute names, agent-memory backends, prompt-injection defense.
Writing those prescriptively *"ages badly."*

The sequencing decision: do the **mechanical migration first**. Once the payload
renders from canon, adding a contested doc later is a one-line sync change rather
than another hand-copy. Get the mechanism in place while the content is still
moving.

The same judgment ran the other way on pruning. Two capabilities were flagged as
an inversion — 30KB for the least-used capability — and deliberately **not**
deleted: they are *"written, synced, and cost only bytes; deleting working
payload to fix an aesthetic asymmetry trades a real asset for a tidier tree."*
Deprioritized in the routing table instead. See [[Complexity Floor]].

## Where the tiers are written down

In the `new-agent` skill's `references/cap-*.md` files (identical copies in two repos) each
capability opens with its tier, a runtime-agnostic contract, and a NATIVE / ASSEMBLABLE
matrix across Claude API, Managed Agents, ADK, LangGraph and Vercel. Two anomalies the
files record about themselves: `cap-langchain` is a framework, not a capability (a
modelling error kept for compatibility); and the framework-selection tree had no
realtime/duplex branch until the voice research added one — see
[[Duplex Voice Breaks Discrete-Turn Assumptions]].

## Traps the templates encode

The per-capability templates under `new-agent/references/` are mostly boilerplate. Each one
opens with an **agnostic contract** paragraph before any runtime table, and several carry
one non-obvious trap that is the real payload:

- **Streaming (T1).** The contract asks for ordered typed events, distinct content-type
  boundaries, terminal completion kept distinct from mid-stream error, and **client
  disconnect propagated back to cancel upstream generation**. That last clause "is the one
  implementations most often miss." Two surfaces from the same vendor can use different
  wire formats (`content_block_delta` vs `content_delta`), so don't conflate them.
- **Search (T2).** On runtimes with native server-side search, **server-tool errors come
  back as HTTP 200**: success `content` is a list, error `content` is an object, so branch
  before indexing. Long server-tool turns also need `pause_turn` handling. The custom
  search tool is only the fallback for runtimes without a native one.
- **Vision (T2).** Size and dimension limits are provider constants that go stale. Each was
  re-verified with a date: a high-resolution long-edge ceiling costs about 3× the image
  tokens of the old 1568 px ceiling, so the lower ceiling stays available as an option when
  fidelity won't change the answer. Extend the `provider` branch rather than replacing the
  file.
- **Eval.** Warning-only graders (drift) must be **excluded by name from `all_passed`**, or
  an advisory signal blocks the loop. A drift score should not accept `None`.
- **Tests.** Always smoke-test `max_cycles` enforcement, because the most common LangGraph
  state bug is control-flow keys (`cycle_count`, `max_cycles`, `terminate`) **silently
  dropped between nodes when they are not declared in the TypedDict**. Also run the full
  agent against the generated synthetic schema (column-availability assumption), and run
  tiny fixtures through the all-noise clustering path, where the result must never be zero
  segments.
- **Prompt changes bump `PROMPT_VERSION`**, or old and new prompt runs mix in one
  experiment and ablations become unreadable.
- **LangGraph has no official scaffolder.** The scaffold skill hand-writes the file set from
  a DESIGN_SPEC. Its rules: a checkpointer is mandatory if HITL is requested
  (`interrupt()` fails without one), never leave an in-memory saver where the spec needs
  production persistence, and ask before choosing the deployment shape.

## Gaps a parity matrix hides (2026-07-19 research)

A capability-parity research pass over the template's payload surfaced gaps that a
framework × capability grid cannot express:

- **"Claude" is four runtimes, not one.** The raw Messages API, the Tool Runner, the Agent
  SDK, and Managed Agents give different verdicts for the same capability — HITL and A2A
  in particular are native on some and hand-rolled on others. A single "Claude" column
  averages them into a meaningless cell. The recommendation was to default to the Tool
  Runner and escalate to Managed Agents only when the capability needs it.
- **Delegation and peer A2A are conflated.** Sub-agent delegation (a parent hands a task
  to a child it owns) and peer agent-to-agent calls (two independent services) were one
  row; they likely need to be separate capabilities with separate parity verdicts.
- **The response schema is the de facto contract.** The shared `AssistantResponse` /
  `FailureReason` shape is what actually crosses every capability boundary — populate
  fields like citations natively where the runtime supports it rather than synthesizing
  them uniformly.
- **Undeclared cloud coupling.** The infra package's dependency list pulled in every
  framework unconditionally (and omitted the Anthropic SDK entirely), so the "framework
  choice" toggle did not actually narrow the install.

## See Also
- [[Capability Parity Audit]] — alternative-to (have/partial/gap axis vs runtime-coupling axis)
- [[Sync as Render, Not Copy]] — prerequisite-for (how the tiered canon reaches the template)
- [[AI Project Template Scaffold]] — instance-of
- [[Complexity Floor]] — related (constrains; a flagged asymmetry is not automatically work)
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — extends (the framework-vs-capability distinction)
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (the missing first row of the selection tree)
- [[Multi-Modal Agent Response]] — related (the response schema as cross-capability contract)
