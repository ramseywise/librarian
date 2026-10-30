---
title: Harness Maturity and Failure Modes
tags: [llm, agents, infra, reference]
summary: "A five-stage maturity ladder, the six-stage per-task pipeline, and the five ways teams fool themselves — the first of which hides the other four — plus the two records a mature harness keeps and the silent builder gotchas of harness runtimes."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--08-maturity-and-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--08-maturity-and-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Harness Maturity and Failure Modes

Where a harness sits today, what to build next, and the five ways teams fool themselves.

## The Five-Stage Maturity Model

| Stage | Name | What exists |
|---|---|---|
| **0** | Ad-hoc | Scripts, manual tool invocation, no registry, no structured logging |
| **1** | Basic | Schema-first tool specs, simple registry, minimal verification via unit tests |
| **2** | Verified | Static verification in CI, sandboxed execution, structured tracing, behavioral evals, **branch-per-agent** |
| **3** | Observability-first | End-to-end tracing, LLM-as-judge scoring, composable middleware, versioned memory |
| **4** | Self-healing | Automated remediation, cost-aware orchestration, policy-as-code governance |

Stage 4 remains **emerging as of 2026** — treat it as direction, not a target.

Reading the ladder:

> **Stage 1 makes the agent work. Stage 2 makes it trustworthy. Stage 3 makes it
> improvable.**

Most production value lands at **2→3**, and **most teams claiming 3 are at 1** — see failure
mode 1.

Reference implementations: **LangChain DeepAgents** (Stage 2→3, branch-per-agent A/B
testing), **Claude Code** (opinionated commercial starter with visible orchestration),
**Goose** (Block; model-agnostic, MCP-native, open source). See [[Deep Agents Framework]].

## The Canonical Six-Stage Pipeline

The per-task shape a mature harness runs:

```
Preflight → Plan → Approve → Tasks → Verify → Finish
```

| Stage | What happens |
|---|---|
| **Preflight** | Gather context; establish current state |
| **Plan** | Decompose into steps |
| **Approve** | **Mandatory human gate** on the plan |
| **Tasks** | Execute, documenting as you go |
| **Verify** | Quality gate — binary pass/fail |
| **Finish** | Export artifacts, log outcome |

Three gates constrain behavior throughout: **scope boundary, permissions, responsibility
boundary.**

**The Approve gate is the one teams skip and the one that pays best.** It costs one human
review of a *plan* — cheap, fast, high-information — and prevents plan errors from
propagating through an entire expensive execution.

> Reviewing a wrong plan takes two minutes; reviewing the code produced by a wrong plan takes
> an hour.

An **incident memory** captures problems for future reference, enabling compound learning —
the ratchet from [[Harness Engineering]] as a **persistent artifact rather than a habit**.

## Three Parallel Branches, Not a Progression

A common category error: treating these as an evolutionary ladder. They are **choices to
make on problem fit.**

| | **Pipelines** | **Agents** | **Self-improvers** |
|---|---|---|---|
| Who orchestrates | Code orchestrates LLM calls | LLM orchestrates tool calls | Agent modifies its own prompts from evals |
| Strength | Observability, cost control, determinism | Handles unpredictable task shapes | Compounds without human tuning |
| Cost | Lowest | Higher | Highest |
| Precondition | Known task shape | Task shape varies | **Binary evals** + team accepts unreadable prompts |

**If the task shape is known, a pipeline is *better* than an agent, not less advanced.**
Self-improvers only earn their cost with binary evals in place — without them the system
optimizes against a distorted signal.

## Core Practices

### KISS discipline

> **The dumbest variant that works outperforms elaborate prompts under production noise.**

Elaborate scaffolding is tuned to conditions observed during development. Production has
different noise, and complexity fails in ways nobody anticipated. **Complexity should be
pulled in by an observed failure, never pushed in by anticipation.**

### Diagnose in order

When an agent fails, audit:

1. **Orchestration layer** — tool descriptions, retry budgets, handoff schemas
2. **Context layer** — data quality, coverage, recency
3. **Model** — last, and rarely the answer

*"The model itself is rarely the bottleneck in mature setups."* **Reaching for a model
upgrade before auditing tool descriptions is the field's most expensive reflex.**

### Sequence accuracy before cost

> **Get it right, then get it cheap. Optimizing cost before accuracy compromises both.**

One production system deliberately ate high inference costs during its early phase and only
optimized after reaching target accuracy. The reasoning: **a system that isn't yet good
enough to adopt has no usage worth optimizing**, and cost-driven choices made early — a
smaller model, fewer retrieval passes, a dropped reranker — remove exactly the headroom you
need to find the quality bar.

The corollary: **cheap-and-wrong is the more expensive failure, because it burns adoption.**
Asymmetric QA economics (see [[Verification Loops]]) assume you already know where the
quality bar is; you cannot spend selectively until you've found it. This sequences two
optimizations that conflict when run simultaneously — it does not license permanent
extravagance.

## The Five Failure Modes

| # | Failure | Tell |
|---|---|---|
| **1** | **Skipped harness** — claiming Stage 2 while at Stage 0 | "We have evals" means one notebook run manually |
| **2** | **No Approve gate** | Plan errors propagate into fully executed wasted work |
| **3** | **No incident memory** | The same failure recurs monthly; nobody remembers the earlier fix |
| **4** | **Symmetric verification** | The same model confirms its own wrong work, confidently |
| **5** | **No binary eval** | Changes are argued about; nothing can be measured or tuned |

**Failure 1 is the meta-failure — it hides the other four.** The honest test is not *"do we
have verification?"* but:

> *"Can I point to the code that runs it, on every task, without a human remembering to?"*

## Two Records Every Mature Harness Keeps

- **Observability in two layers.** Runtime signals (logs, traces, lifecycle events) say what
  the system did; process artifacts (plans, sprint contracts, rubrics, scored verdicts) say
  why a change should be accepted. The harness collects both, not the agent —
  [[Runtime vs Process Observability]].
- **A quality document.** A per-area health record — grade, verification status, agent
  legibility, test stability, boundary compliance, key gaps — that sessions read first and
  update last, so quality is tracked rather than assumed and simplification passes have a
  baseline — [[Quality Document]].

## Builder Gotchas

Non-obvious failures for anyone *building* harness runtime (memory, tools, subagents, hooks)
rather than configuring one, drawn from an analysis of a production coding-agent runtime.
Each one fails **silently**.

**Memory and instructions**

- **Index caps truncate silently.** An always-loaded memory index is capped in lines and
  bytes at read time; long entries hit the byte cap first and recent memories "disappear".
  Keep index entries to one-line hooks and detail in topic files.
- **Most-local wins.** Org → user → project → local override; a rule set at user level is
  silently overridden by a project-root file. Test with the whole instruction stack present.
- **Don't memorize what's derivable.** Architecture, code patterns and history live in the
  repo and go stale in memory; the memory taxonomy should forbid them.
- **Two-step saves orphan in the right direction.** Write the topic file, then the index
  pointer: a crash between them orphans a file but keeps the index consistent. Add a sweep.
- **Memoized context goes stale.** Context cached at startup must be invalidated at every
  mutation point, or the model sees stale data all session.
- **Skill descriptions are truncated** (~150 characters per listing entry). Front-load the
  distinctive trigger words — see [[Skill Authoring Discipline]].

**Tools and permissions**

- **Fail closed by default.** Tools are non-concurrent and non-read-only unless marked;
  sensitive tools default to *ask*. Keep a bypass-immune list (`.git/**`, `rm -rf*`,
  `DROP TABLE*`) that no mode auto-approves.
- **Concurrency safety is per call, not per tool.** `cat` is safe to parallelize, `rm` is
  not — classify each call at runtime.
- **Permission checks have side effects** (denial tracking, mode changes). Don't cache
  verdicts across calls.

**Subagents and lifecycle**

- **Forks don't fork.** Recursive forks multiply context cost. Enforce one level, and block at
  call time rather than removing the tool, so the prompt cache still matches
  ([[Prefix Caching]]).
- **Notify, then evict.** Clear a finished work unit's disk output eagerly, but its in-memory
  record only after the parent has read the result.
- **Don't assume a "pending" state.** Work units usually register straight as running; UI
  built around *pending* shows nothing.
- **Hook trust is all-or-nothing.** An untrusted workspace skips every hook; gate trust at
  dispatch rather than judging each hook.

## Open Frontiers

Three unsolved problems, named consistently across sources:

1. **Orchestrating hundreds of parallel agents on a shared codebase** — merge conflict
   resolution and coordination at a scale current tooling doesn't reach.
2. **Agents analyzing their own traces to identify and fix harness-level failure modes** —
   automating the ratchet. LangChain's Trace Analyzer Skill is an early instance; see
   [[Verification Loops]].
3. **Just-in-time harness assembly** — dynamically composing the right tools and context per
   task instead of pre-configuring everything.

The third points somewhere interesting:

> **Harnesses stop being static config and start becoming something closer to a compiler** —
> a system that *compiles* a task specification into the tool set, context, and constraint
> layer that task needs.

## A Build Checklist

Ordered by return on effort:

- [ ] Tool schemas typed; descriptions carry `DO NOT USE FOR`
- [ ] Sandbox with a real execution boundary
- [ ] Filesystem + git for durable state and rollback
- [ ] Plan file for anything past ~5 steps
- [ ] **One binary eval** — pass/fail, runs automatically
- [ ] Verification gate that the agent cannot skip
- [ ] Structured traces on every step
- [ ] State checkpointed per step — resume from the failed node, not the start
- [ ] Blocking hooks on destructive operations
- [ ] Approve gate between plan and execution
- [ ] Separate evaluator, stronger model than the generator
- [ ] Retry caps + cost ceiling per run
- [ ] Errors fed back as context, not just re-attempted
- [ ] Model fallback across providers behind a uniform interface
- [ ] Live-traffic eval alongside the dataset eval
- [ ] Incident memory — failures become permanent fixes
- [ ] Subtraction pass scheduled on each model upgrade — and on any gate that false-positives

**Items 1–8 get you to Stage 2. Items 9–16 get you to Stage 3. Item 17 keeps it from
calcifying** — see [[Iterative Harness Simplification]].

## See Also
- [[Eval Maturity Ladder]] <!-- auto-linked -->
- [[Harness Engineering]] — part-of
- [[Iterative Harness Simplification]] — extends
- [[Production Reliability Primitives]] — complements
- [[Verification Loops]] — depends-on
- [[Harness Anatomy]] — depends-on
- [[Eval Ladder]] — depends-on
- [[Runtime vs Process Observability]] — extends
- [[Quality Document]] — extends
- [[Harness Subsystem Attribution]] — complements (diagnosing which subsystem a failure belongs to)
