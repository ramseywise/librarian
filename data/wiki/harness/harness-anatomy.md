---
title: Harness Anatomy
tags: [llm, agents, infra, concept]
summary: "The nine harness components and the five subsystems they serve, why the filesystem is the foundational primitive (including state for sessionless agents), code as a meta-capability, the layered mental model, and the causal build order."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--02-harness-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--02-harness-anatomy.md
  - data/raw/papers/2026-11-06-jin-2024-llms-llm-based-agents-software.md
  - data/raw/papers/2026-11-06-ning-2026-code-as-agent-harness.md
---

# Harness Anatomy

The component inventory of [[Harness Engineering]]: what ships inside a harness, and which
primitives are foundational rather than optional.

## The Nine Components

### Knowledge and configuration

**1. System prompts and context policies** — behavioral framing, plus the *rules for what
gets assembled* per call. **The policy is harness; the assembled result is context.**

**2. Tools, skills, and MCPs — and their descriptions** — the action surface. Descriptions
are load-bearing: they are the *only* thing the model sees at selection time. Skills add
progressive disclosure so a large capability library does not flood the window at startup.
See [[Tool Design as Harness Surface]].

### Infrastructure

**3. Filesystem abstractions** — *"arguably the most foundational harness primitive."*
Durable storage, context offloading, cross-session persistence, and a shared medium for
multi-agent handoff.

**4. Bash and code execution** — the general-purpose escape hatch.

**5. Sandboxes** — safe execution environments with pre-configured tooling. See
[[Execution Boundaries and Guardrails]].

**6. Memory systems** — file-based standards (`AGENTS.md`, `MEMORY.md`) for continual
learning across sessions. See [[Memory as Context]].

### Orchestration and control

**7. Orchestration logic** — subagent spawning, handoffs, model routing, HITL feedback
loops. See [[Harness Orchestration]].

**8. Hooks / middleware** — deterministic control flow: compaction, continuation, lint
checks, verification gates. **The part of the harness that cannot be talked out of
enforcing itself.**

**9. Context management tools** — web search, retrieval, and MCP access for information past
the training cutoff; plus compaction and tool-output offloading.

Supporting: git versioning, planning files, test runners, self-verification hooks.

## The Five Subsystems

The nine components describe what ships; for **diagnosis**, group them into five subsystems —
**instructions** (1, 6), **tools** (2, 4, 9), **environment** (3, 5, `init.sh`), **state**
(plan file, progress log, feature list, git), and **feedback** (8, test runners, gates,
traces). Every failure attributes to exactly one, and removing one at a time (ablation)
shows which are load-bearing. See [[Harness Subsystem Attribution]].

## Why the Filesystem Is Foundational

It is the primitive the others lean on, because it solves four problems at once:

| Problem | Filesystem answer |
|---|---|
| Context window is finite | Offload large outputs to disk; keep a reference in-window |
| Sessions end | Plans, notes, and state survive as files |
| Subagents need to hand off | A file is a shared, inspectable medium |
| Work needs auditing | Git gives you history, diff, and rollback for free |

This is the mechanism behind **state externalization** ([[Long-Horizon Execution]]) —
progress lives in files, so the loop becomes re-entrant and independent of any single
context window.

It is also the mechanism behind **tool-call offloading**: keep the head and tail of a large
tool output in-window above a token threshold, write the full output to disk, and let the
model read it back only if needed. *A 2,000-line log becomes ~40 lines plus a path.*

**Git deserves separate mention: it is the only rollback mechanism most harnesses have.**
Branch-per-agent turns parallel experimentation into a safe operation with a free undo.

### State across messages

An always-on ("sessionless") agent reached over a chat app may get its next message minutes
or days later. Split the state in two (Li, *AI Agents in Depth*, ch. 5):

- **File state is persistent by construction** — mount the workspace on storage outside the
  sandbox.
- **Process state is kept warm, then rebuilt** — keep the sandbox and terminal alive while
  active; on idle timeout, write the serializable parts (working directory, env vars,
  background tasks) to a workspace file before destroying the sandbox, and rebuild from it
  on the next wake-up.

> **Persist auditable descriptions of state (files, scripts, manifests), never opaque
> long-lived processes.**

Within a single task the same idea is the **persistent terminal session**: `cd`, an
activated venv and env vars survive between commands instead of each command starting a
fresh shell.

### The environment status bar

Before every inference, append the working directory, git branch, recent commits and a
staged/unstaged summary **at the end of the context — never in the system prompt**, where
changing values would break the KV cache ([[Prefix Caching]]). Same rule as loading tools
mid-session in [[Dynamic Tool Discovery]].

## Bash as a General-Purpose Tool

The design bet: **you cannot pre-design every tool an agent will need.**

Harnesses ship a bash tool so the model can compose solutions by writing and executing
code, rather than being limited to the API surface someone anticipated. A curated tool set
handles known operations well; bash handles the long tail.

The tension is real — bash is maximally capable and maximally dangerous, which is exactly
why it must be paired with a sandbox and hooks. The **promote-from-bash heuristic**
resolves it:

> Start with shell; promote to a typed tool when you need a **gate**, a **rendered result**,
> an **audit record**, **parallelism**, or a **retry policy**.

### Code as a meta-capability

A minimal coding kit is seven tools — code interpreter, bash, read, write, edit, glob, grep
(compared in [[Coding-Agent Search and Edit Schemes]]). With them, **code becomes a way of
making the capabilities you didn't build**, applied in six directions:

1. **Thinking** — formalize math or logic for a symbolic or constraint solver.
2. **Rules** — encode policy as executable checks.
3. **Content** — slides, video and charts as code rather than through a GUI.
4. **Adapters** — glue for undocumented APIs or drifting log formats.
5. **UI** — forms and views generated on demand.
6. **Agents** — create or repair agents. Start from a known-good agent implementation and
   modify it; generating one from scratch reproduces outdated APIs and ad hoc context
   handling.

## The Layered Mental Model

```
┌─ Deterministic shell ──────────────────────────┐  hooks, permissions,
│  ┌─ Orchestration ──────────────────────────┐  │  schema validation
│  │  ┌─ The loop ─────────────────────────┐  │  │  (cannot be argued with)
│  │  │  ┌─ Context assembly ──────────┐   │  │  │
│  │  │  │   [ model call ]            │   │  │  │
│  │  │  └─────────────────────────────┘   │  │  │
│  │  │   tool execution · verification    │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │   subagents · handoffs · model routing   │  │
│  └──────────────────────────────────────────┘  │
│   sandbox · filesystem · git · observability   │
└────────────────────────────────────────────────┘
```

Two rules read straight off the diagram:

1. **Reliability requirements move outward.** Anything that must hold every time belongs in
   the deterministic shell, not in a sentence inside the model call. *A prompt can be
   ignored; a hook cannot.*
2. **Cost and blast radius grow outward too.** Adding a sentence is cheap and reversible;
   adding a subagent tier multiplies tokens and loses cross-agent context. **Reach for the
   innermost layer that can actually hold the requirement.**

## The Causal Build Order

A 38-lesson harness curriculum organized so that *"each step exists because the previous one
broke something."* That ordering is the best available answer to **what to build first**:

| # | Module | The break it answers |
|---|---|---|
| 1 | The agent loop | A chatbot can't act |
| 2 | Tool design | The model picks the wrong tool |
| 3 | System prompt | Behavior is inconsistent across runs |
| 4 | Sandbox abstraction | Execution is unsafe / environment-coupled |
| 5 | Context management | Tokens grow unbounded in long sessions |
| 6 | Subagent delegation | One context can't hold the whole task |
| 7 | Sandbox lifecycle | Cloud sandboxes cost money while idle |
| 8 | Human-in-the-loop | The agent guesses when it should ask |
| 9 | Planning and verification | Work is declared done without being checked |
| 10 | Surfaces | The same agent needs CLI and web |
| 11 | Extensibility | Adding a tool means editing the core |

Note the shape: **capability first (1–4), then the constraints that make capability
survivable at scale (5–9), then productization (10–11).** Teams that invert this — building
orchestration before verification — produce the Stage-0-claiming-Stage-2 failure in
[[Harness Maturity and Failure Modes]].

Two design principles worth lifting out:

- **"Swap the backend, the tools don't change."** The `Sandbox` interface is uniform; local
  `fs`/`child_process`, in-memory copy-on-write, and remote cloud sandboxes are
  interchangeable behind it. **Tools bind to the interface, never the backend.**
- **Extensibility without core edits.** Event buses, a tool registry, and progressive skill
  disclosure mean adding capability is *registration, not surgery*.

## Minimum Viable Harness

Cutting the inventory to what a first real harness needs:

1. A **tool loop** with typed schemas
2. A **sandbox** (even just a working-directory boundary)
3. A **filesystem** the agent can read and write
4. A **plan file** for anything past ~5 steps
5. One **verification gate** with a binary pass/fail
6. **Structured traces** of every step

Six items. Everything else here is elaboration on those.

## Survey views of what a harness and an agent are (self-reported counts from the surveys)

- **Code as Agent Harness (Ning et al., a May 2026 literature survey):** defines a harness as the software layer around a model that contains the tools, APIs, sandboxes, memory, validators and permission boundaries, along with the execution loops and feedback channels. It says the bottleneck of autonomy is the harness as well as the model, and splits the system into model-internal capability, system-provided infrastructure and agent-written code artifacts, calling the third underexplored. Its plan-execute-verify loop uses three permission tiers (read-only, sandbox-edit, full access with human approval for the last), and it says critique should interpret deterministic sensor output and not replace it. It notes that end-task success conflates model and harness, and cites studies reporting 14 to 53% best step-level failure attribution accuracy. Figures it quotes from other work are second-hand: 98%+ precision and recall for simulated execution on MBPP, and 16.9% of in-house issues resolved autonomously (43.3% with manual intervention) for one production agent.
- **LLM-based agents for software engineering (Jin et al., a 2024-2025 preprint survey):** proposes six criteria for calling a system an agent (a model as central reasoner, planning, autonomous tool use, choosing among candidate results, multi-turn context, autonomous learning), of which the first four are the basic level. It collected 139 papers from late 2023 to before December 2024, with 40.3% on arXiv. Its own analysis concedes that for test generation alone a plain model is enough and cheaper than an agent framework. It reports no experiments, and the results it cites are 2024-era (for example SWE-agent at 12.5% pass@1 on SWE-bench).

## Limits

- Neither survey runs a controlled experiment; "same model, different harness" appears in Ning et al. only as a qualitative remark, and the authors say reported planning gains may not reflect real improvement.
- Jin et al. internal inconsistencies: the text says 139 papers while Section X-A says 110; the topic figure sums to 153 instances because papers count in several topics; the year-trend figure sums to about 138. The agent criteria are a judgment call, and the extraction notes doubtful background claims (for example parameter counts for GPT-4) that should not be cited.

## See Also
- [[Skill Authoring Discipline]] <!-- auto-linked -->
- [[Eval Harness Anatomy]] <!-- auto-linked -->
- [[Harness Engineering]] — related (part of)
- [[Tool Design as Harness Surface]] — extends
- [[Execution Boundaries and Guardrails]] — extends
- [[Long-Horizon Execution]] — prerequisite-for
- [[Harness Subsystem Attribution]] — extends (the five-subsystem diagnostic cut)
- [[Coding-Agent Search and Edit Schemes]] — extends (the minimal coding kit's search and edit tools)
- [[Realtime Is UI Sync, Not the Event Bus]] — related (a realtime channel is not the event bus)
- [[DeepCode Information-Flow Management]] — related
- [[Natural-Language Agent Harnesses]] — extends
- [[Harness Effect on Token Economics]] — related
- [[Prime Agent State Hierarchy]] — related
- [[OpenDev Terminal Coding Agent]] — related
