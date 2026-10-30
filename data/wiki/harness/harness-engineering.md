---
title: Harness Engineering
tags: [llm, agents, infra, concept]
summary: "Agent = Model + Harness — the discipline of building everything between request and output except the weights (context, tools, constrain, verify, correct), why reliability compounding makes the harness dominate the model, and why coding agents matured first."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--01-what-a-harness-is.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--01-what-a-harness-is.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--agent-harness.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--harness-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--harness-engineering.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--agent-harness.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Harness Engineering

## Position in the Stack

The **third layer**. Prompt engineering governs the instructions; [[Context Engineering]]
governs what is assembled around them; harness engineering governs the machinery that does
the assembling, executes the tools, checks the result, and recovers when it is wrong.

The discipline nests: **prompt ⊂ context ⊂ harness ⊂ loop**. Each scope widens what the
engineer controls — the instruction, the working set, the system the model runs in, then
sustained operation across runs ([[Loop Engineering]]). *Graph engineering* is an
orchestration view across these scopes rather than a fifth one: a loop is a graph with a
back edge, and a graph node can run its own loop ([[Graph Engineering]]).

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

### The expanded equation

A book-length treatment (Li, *AI Agents in Depth*, 2026) starts from the demo-view component
formula *Agent = LLM + Context + Tools* and wraps three safeguard layers around the two
non-model terms:

> **Agent = LLM + [Context + Tools + Constrain + Verify + Correct] = Model + Harness**

The five functions on one refund request, each with its governing design principle:

| Function | In the refund example | Principle |
|---|---|---|
| Context | 7-day refund policy in the system prompt | *Information sufficiency* at every decision point |
| Tools | `query_order`, `process_refund` | *Clear interface* — intuitive names, examples, stated boundaries |
| Constrain | Refund ≤ order total, checked by the framework | *Fail-safe defaults* — every capability off until enabled |
| Verify | Confirm in the DB that the refund landed | *Input isolation* — check structured tool fields, never model prose, which injection can steer |
| Correct | Retry automatically on API timeout | *Don't expose intermediate state* until failure is confirmed unrecoverable |

Without the bracket the same model gets no policy, picks no tool, invents a success message,
and the user finds out later. The five form a **closed loop** — leave one out and there is a
reliability gap. And the centre of gravity shifts as products mature: early frameworks were
mostly context and tools, while in a mature coding agent **most harness code is
constrain/verify/correct** (process-state tracking, multi-layer compaction, permission
tiers, circuit breakers, rollback-and-retry); the tools are a small fraction.

### Where the metaphor comes from

Horse tack — directing a powerful animal's energy toward useful work without letting it
bolt. The shift the metaphor names is **from continuous prompting to upfront
orchestration**: build the harness once, then ride to different destinations with the same
ease.

That is the economic argument for the whole discipline. *Prompting cost is linear in tasks;
harness cost is paid once and amortized.*

## Observation and Action Spaces

The observation space (context) and the action space (tools) are the model's whole interface
to the world. **With the model fixed, redefining or expanding them is the main systems
lever** — a task that seems to need a smarter model often needs the right data in context or
the right operation exposed as a tool. Expansion must be **on-demand, relevant, and
controlled**: retrieval brings in what matters, tool discovery exposes only what is needed
now ([[Dynamic Tool Discovery]]), and permissions plus result verification bound the new
actions ([[Execution Boundaries and Guardrails]]).

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

Contrast the classic **agent = LLM + planning + tools + memory** decomposition. That framing
describes what the *model* does; these four parts describe what the *system around it* must
guarantee. Planning, tools and memory map onto harness components; **none of the four parts
above appears in the classic framing**, which is why agents built from it alone are
unreliable. See [[Deep Agent Pillars]] for the middle ground.

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

### Why coding agents matured first

A two-by-two of goal clarity against verification automation:

| | Verified automatically | Verified by a human |
|---|---|---|
| **Clear goal** | Sweet spot — fix a bug that has a failing test | Throughput-limited — a refactor that needs review |
| **Vague goal** | Efficiently off track — "improve code quality" scored by a linter | Hard to start — "make the UI look better" |

Coding agents matured first **not because code models are unusually strong**, but because
decades of tests, type checkers, linters, CI and git already form a harness that puts most
coding tasks in the top-left cell. **The harness's job in any other domain is to push tasks
into that cell.**

**Harness thickness depends on the model.** Offloading logic puzzles to a constraint solver
lifts a weak model dramatically and a strong reasoning model barely at all. The same harness
can support opposite conclusions depending on the model, so **state the model whenever you
report a harness result.**

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

Turned into a procedure — attribute each failure to one of five subsystems (instructions,
tools, environment, state, feedback), fix only that one on a fixed model, re-run, and change
the model last — it becomes [[Harness Subsystem Attribution]].

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

### Constraints are encoded, not documented

The ratchet has a failure mode: the cheapest response to any incident is to add a line to
`AGENTS.md`, which makes the file grow while compliance falls. The corrective is that
**a rule in documentation is probabilistic and a rule in a hook is deterministic**. The
documented rule competes for attention with everything else in the window and its
compliance rate degrades as the window fills; the hook's compliance rate is 100% regardless
of context pressure. They are different mechanisms, not different strengths of one.

So the ratchet's real instruction is *encode the constraint at the strongest available
layer* — hook > linter > test > tool schema > instruction line — and reserve the
instruction file for what genuinely cannot be mechanized. The test for any rule you rely
on: **what happens if the agent ignores it?** If nothing catches it, the rule is
documentation. See [[Agent Deployment Anti-Patterns]] (#8) and
[[Execution Boundaries and Guardrails]].

This also fixes the ~60-line ceiling, which otherwise reads as an arbitrary budget. The
instruction file works as a **table of contents rather than a manual**: it points at where
knowledge lives — skills, references, commands — instead of containing it, so the file
stays navigable while the knowledge it indexes grows without bound. Bulk material belongs
in progressively-disclosed bodies ([[SKILL.md Pattern]]), not resident text.

## The Context ↔ Harness Boundary

| Context engineering | Harness engineering |
|---|---|
| What goes in the window on *this* call | The loop that decides *whether and when* to call |
| Which documents, memory, tool results to inject | Which tools exist at all, and what they may do |
| Token budget within one assembly | Cost envelope across a whole run |
| Compaction as a technique | Compaction as middleware that fires on a trigger |

The crossing point: **the moment assembly becomes stateful and conditional** — a loop
deciding when to retrieve, compact, verify, or spawn — you have left context engineering and
entered harness engineering.

A five-component checklist for the harness side: context assembly per step, tool
orchestration (validation, parsing, error handling), verification loops, **cost envelope
management** (per-task budget ceilings against runaway spend), and observability/evaluation.
The source literature claims reliability gains of roughly 5–15% from prompt work, 15–30% from
context work, and 50–80% from harness work. Treat the numbers as directional; the ordering is
the claim.

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

This is the harness's answer to Sutton's *Bitter Lesson* (general methods that scale with
compute beat hand-encoded priors): **endorse the direction, stay pragmatic about the pace.**
Models do absorb harness layers — tool calling and long-horizon planning both began as
external orchestration — but training cycles take months and no model internalizes every
business's constraints. The harness covers what the model can't yet do reliably, drops each
layer the model absorbs, and moves to the next frontier. Learned behaviour also has more
than one home — in-context adaptation, external artifacts (docs, prompts, code), and
weights — each persisting on a different timescale.

## Topic Notes

1. [[Harness Anatomy]] — the nine components, filesystem as foundational primitive, the causal build order
2. [[Tool Design as Harness Surface]] — ACI over API, the five-section tool contract, MCP vs in-process
3. [[Execution Boundaries and Guardrails]] — sandboxes, hooks, silent-success/verbose-failure
4. [[Verification Loops]] — self-verification, reflection types, generator/evaluator separation
5. [[Long-Horizon Execution]] — state externalization, compaction vs context reset, plans as artifacts
6. [[Harness Orchestration]] — subagents as context firewall, role separation, oscillation and deadlock
7. [[Harness Maturity and Failure Modes]] — the five-stage model, production primitives, runtime vs process observability, the quality document, builder gotchas, iterative simplification

Atomic pages: [[Harness Subsystem Attribution]] · [[Dynamic Tool Discovery]] ·
[[Belief Parameters with a Ground-Truth Gate]] · [[Coding-Agent Search and Edit Schemes]] ·
[[Lethal Triad]] · [[Proposer-Reviewer and Sidecar Gating]] ·
[[Three-Layer Termination Check]] · [[Agent-Oriented Error Messages]] ·
[[Asynchronous Agent Event Loop]] · [[Runtime vs Process Observability]] ·
[[Quality Document]] · [[Deep Agent Pillars]]

## See Also
- [[Spec, Verifier, Environment Layering]] — extends (a practitioner framing of the same harness as spec + verifier + workshop)
- [[Agent Scaffolding Skill Layers]] <!-- auto-linked -->
- [[Prompt Engineering]] <!-- auto-linked -->
- [[Context Engineering]] — depends-on
- [[Harness Anatomy]] — part-of
- [[ACI (Agent-Computer Interface)]] — instance-of
- [[Loop Engineering]] — extends (the layer above: the harness supplies tools, the loop decides when to stop using them)
- [[Agentic Engineering and the New SDLC]] — complements (the same "skill issue" reframe reached from the process side, plus the TCO argument)
- [[Agent Interoperability Protocol Stack]] — complements (what governs the boundary when the other side is not under your control)
- [[Agent Deployment Anti-Patterns]] — instance-of (the eight deployment failures the reframe predicts)
- [[Skill Authoring Discipline]] — implements (authoring the skill layer of the harness)
- [[Harness Subsystem Attribution]] — extends (the skill-issue reframe as a diagnostic procedure)
- [[Deep Agent Pillars]] — complements (the architecture-level view of the same system)
