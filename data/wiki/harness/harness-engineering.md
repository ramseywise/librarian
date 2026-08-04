---
title: Harness Engineering
tags: [llm, agents, infra, concept]
summary: "Agent = Model + Harness — the discipline of building everything between request and output except the weights, and why reliability compounding makes the harness dominate the model."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--01-what-a-harness-is.md
---

# Harness Engineering

## Position in the Stack

The **third layer**. Prompt engineering governs the instructions; [[Context Engineering]]
governs what is assembled around them; harness engineering governs the machinery that does
the assembling, executes the tools, checks the result, and recovers when it is wrong.

The discipline nests: **prompt ⊂ context ⊂ harness**.

**It inherits the weaknesses of the layer below.** A harness that supplies poorly composed
context to its loops fails at scale no matter how well the scaffolding itself is built.

## The Equation

> **Agent = Model + Harness.**

A raw model is a text transformer. It becomes an *agent* only when something gives it
durable state, tool execution, feedback loops, and enforceable constraints — **every line
of code, configuration, and execution logic beyond the weights themselves**.

The formal definition: *"the discipline of designing, building, and operating the
infrastructure that constrains, informs, verifies, and corrects AI agents in production."*

Four verbs worth keeping. A harness **constrains** (boundaries), **informs** (context),
**verifies** (checks), and **corrects** (recovery).

> **Most incomplete harnesses have the first two and are missing the last two.**

### Where the metaphor comes from

Horse tack — directing a powerful animal's energy toward useful work without letting it
bolt. The shift the metaphor names is **from continuous prompting to upfront
orchestration**: build the harness once, then ride to different destinations with the same
ease.

That is the economic argument for the whole discipline. *Prompting cost is linear in tasks;
harness cost is paid once and amortized.*

## The Four Parts

The minimal decomposition. A system missing any one of these is not a harness — it is a
prompt with tools attached.

| Part | Question it answers |
|---|---|
| **Acceptance baseline** | What does "done and correct" mean, checkably? |
| **Execution boundary** | Where does the agent run, and what can it touch? |
| **Feedback signals** | How does the agent learn its last action was wrong? |
| **Rollback mechanisms** | How do we undo a bad action? |

**The most commonly missing part is rollback. The most commonly *faked* one is the
acceptance baseline** — a vibes-based "looks good" standing in for a binary check.

## Why the Harness Dominates the Model

**Reliability compounds negatively.** A step that succeeds 90% of the time, chained five
times, lands near 60%. Real agents exceed five steps as soon as you count tool calls,
output parses, and handoffs.

Model quality shifts per-step accuracy by a few points. Harness structure changes *how many
steps must succeed in a row* and *what happens when one doesn't*.

Two data points:

- **LangChain DeepAgents** — 52.8% → 66.5% on Terminal Bench 2.0 (roughly rank 30 → top
  five), **harness-only changes on a fixed model**.
- Frontier models perform far below their ceiling in a loose harness and far above it in
  one with tighter tool design and prompts.

> *A decent model with a great harness beats a great model with a bad harness.*

**The diagnostic order falls out of this.** When an agent fails, audit the **orchestration
layer first** (tool descriptions, retry budgets, handoff schemas), **then the context
layer** (data quality, coverage, recency). In a mature setup the model is rarely the
bottleneck.

## The "Skill Issue" Reframe

Most agent failures are **configuration problems, not model limitations**.

| Failure | Not this | But this |
|---|---|---|
| Ignored a convention | "The model is dumb" | The convention isn't in `AGENTS.md` |
| Ran `rm -rf` | "The model is unsafe" | There's no blocking hook |
| Lost the thread at step 40 | "Context window too small" | No planner/executor split, no plan file |
| Shipped broken code | "It can't code" | No typecheck back-pressure in the loop |
| Rated its own work 9/10 | "It's sycophantic" | Generator and evaluator are the same agent |

**Every right-hand cell is a build task. That is the whole discipline in one table.**

## The Ratchet

The operating principle that makes a harness improve monotonically:

> Anytime an agent makes a mistake, engineer a solution such that the agent **never makes
> that mistake again**.

Each failure becomes a permanent signal — a hook, a lint rule, a line in the instruction
file, a new gate. **The harness tightens every time the agent slips.**

The corollary is a strong test for instruction files:

> **Every line in a good `AGENTS.md` should be traceable back to a specific thing that
> went wrong.**

Rules for that file: keep it **under ~60 lines** — a pilot's checklist, not a style guide;
every rule traces to an actual failure or an external constraint; bias toward load-bearing
basics (package manager, test framework, formatting conventions).

Lines that cannot name their originating failure are speculative, and **speculative rules
are what turn a checklist into an ignored wall of text**. This is the same drift as
system-prompt altitude one layer down — see [[Context Anatomy]].

## Convergent Design as Evidence

Claude Code, Cursor, Codex, Aider, and Cline *"look more like each other than their
underlying models do."*

Independent teams, different models, different companies — all converging on filesystem
access, bash, sandboxes, hooks, subagents, progressive disclosure, plan files, and
verification loops.

> That convergence is the field's best evidence that these specific primitives are
> **load-bearing rather than stylistic**.

[[Harness Anatomy]] enumerates them.

## The Co-Training Loop

Harness complexity does not shrink as models improve — it **shifts**. Better models
eliminate scaffolding built to mitigate old weaknesses (context anxiety, myopic planning)
and unlock new capabilities that expose new failure modes needing different constraints.

Meanwhile the useful primitives get standardized into products, then embedded into the next
generation's training data, which makes models better at exactly those primitives. **Harness
design and model development co-train.**

Practical consequence: **a harness needs periodic subtraction, not just addition.**

## Topic Notes

1. [[Harness Anatomy]] — the nine components, filesystem as foundational primitive, the causal build order
2. [[Tool Design as Harness Surface]] — ACI over API, the five-section tool contract, MCP vs in-process
3. [[Execution Boundaries and Guardrails]] — sandboxes, hooks, silent-success/verbose-failure
4. [[Verification Loops]] — self-verification, reflection types, generator/evaluator separation
5. [[Long-Horizon Execution]] — state externalization, compaction vs context reset, plans as artifacts
6. [[Harness Orchestration]] — subagents as context firewall, role separation, oscillation and deadlock
7. [[Harness Maturity and Failure Modes]] — the five-stage model, production primitives, iterative simplification

## See Also
- [[Agent Scaffolding Skill Layers]] <!-- auto-linked -->
- [[Prompt Engineering]] <!-- auto-linked -->
- [[Context Engineering]] — depends-on
- [[Harness Anatomy]] — part-of
- [[ACI (Agent-Computer Interface)]] — instance-of
