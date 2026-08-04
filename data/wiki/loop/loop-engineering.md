---
title: Loop Engineering
tags: [llm, agents, infra, concept]
summary: "The fourth layer of the stack — designing the cycle that re-prompts, checks, and stops an agent when nobody is watching, replacing yourself as the person who prompts it."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--loop-engineering.md
---

# Loop Engineering

## Position in the Stack

The **fourth layer**: prompt → context → harness → **loop**. [[Harness Engineering]] supplies
the tools, state, and guardrails; the loop decides **how many times to use them and when to
stop**. The graph layer above composes loops into multi-agent topologies.

**It inherits the weaknesses of the harness.** A loop running inside a poorly instrumented
harness produces unreliable behavior that is hard to debug even when the loop logic is sound.

Two framings worth holding together:

> **Loop engineering is replacing yourself as the person who prompts the agent. You design
> the system that does it instead.** — Addy Osmani

> A loop is *"the trigger, the topology, the verifier, and the stop rules that decide what an
> agent does next and when it quits."* — Adnan Masood

Boris Cherny's version of the shift: agents now "prompt Claude and figure out what to do. My
job is to write loops."

### Loop vs Chain

A chain executes a predetermined sequence regardless of intermediate results. A loop is
*dynamic*: the agent may go A → B, discover B failed, revise, and only then reach C.

**That difference — feedback changing the next step — is the whole discipline.**

### Lineage

Geoffrey Huntley's "Ralph Wiggum" technique (mid-2025) was the crude ancestor: a bash loop
re-invoking the agent forever, breaking work into small context windows and persisting
progress to the filesystem so the agent could amend its own plan between runs. By May 2026 the
harnesses absorbed it — `/loop` (cadence-based) and `/goal` (condition-based) ship in Codex,
Hermes, and Claude Code, so nobody hand-rolls the wrapper. See [[Long-Horizon Execution]] for
the same pattern seen from the context-boundary side.

## The Four Capability Levels

LangChain's canonical taxonomy. Each level wraps the previous one; production systems stack
all four.

| Loop | Function | Primitive | Buys you |
|---|---|---|---|
| **1 — Agent** | Model calls tools until the task is done | `create_agent` | Work automation |
| **2 — Verification** | Grade the output, feed failures back | `RubricMiddleware`, `after_agent` hooks | Quality/consistency |
| **3 — Event-driven** | External events trigger runs in the background | Cron, webhooks, channels | Scale without invocation |
| **4 — Hill-climbing** | Analyze traces, rewrite the harness itself | Trace → analysis agent → config rewrite | Continuous self-improvement |

**Levels 1–3 automate *work*; level 4 automates *improvement*.** At level 4 *"the return arrow
doesn't just loop back to the top — it reaches inside and updates the agent loop directly."*
That is where loop engineering stops being scaffolding and starts modifying the harness
underneath it — see [[Evolve Loop]].

Level 2's tradeoff is stated plainly: *"adding verification increases latency and cost per
run. It's worth it when quality matters more than speed"* — which is most production use
cases. Mechanism in [[Verification Loops]].

**Humans sit at every level**, explicitly: approval before sensitive tool calls (L1), humans
as graders for sensitive workflows (L2), review before output reaches users (L3), harness
changes reviewed before deploy (L4). *"Automation doesn't mean removing humans from the loop."*

### Two Orthogonal Axes

Capability level asks *what the loop automates*. The [[Loop Autonomy Ladder]] asks *how much of
the operator's job has been handed off*. **A loop has a position on each** — a hill-climbing
loop (level 4) can run at autonomy rung 1, with a human approving every config rewrite. That
combination is in fact the recommended starting point for an evolve loop.

## Anatomy — The Five Required Components

A loop missing any of these will hang, thrash, or silently ship garbage.

1. **Testable goal.** Specific enough to *evaluate*. "Make all auth tests pass" is a loop
   invariant; **"improve the app" is an infinite loop.**
2. **Tool set.** Real environmental access — code execution, filesystem, terminal, test runner.
   Without it the agent cannot observe consequences and the loop degenerates into repeated
   guessing. See [[Tool Design as Harness Surface]].
3. **Context management.** Summarize and prune prior iterations into compact working memory.
4. **Termination logic.** *Layered, independent* exits — see [[Loop Termination Design]].
5. **Error handling.** Distinguish recoverable errors from hard blockers; **change strategy
   based on error type rather than retrying the identical failed approach.** Taxonomy in
   [[Agent Retry Taxonomy]].

### The Canonical Skeleton

```
initialize state with goal
for step in range(MAX_STEPS):
    reason about current state
    choose a concrete action
    execute the tool against the real environment
    update state with the outcome
    compact context to prevent overflow
    if verifier says goal met: return success
    if no progress for N steps or budget exhausted: escalate
escalate to human  # cap reached, not success
```

> *"Engineering is everything wrapped around"* the model — the model supplies the reasoning
> step; **every other line above is yours.**

### Loop Patterns — Pick by Task Shape

| Pattern | Use when |
|---|---|
| **Retry** | Atomic task, clear pass/fail |
| **Plan–Execute–Verify** | Multi-step work where order matters |
| **Explore–Narrow** | Unfamiliar territory; fan out in parallel, then converge |
| **Human-in-the-loop** | Ambiguity or high stakes require judgment |

Vercel's parallel taxonomy — planning, tool use, reflection, multi-agent collaboration —
carries sequencing advice worth following: **start with tool use, add reflection once stable,
and introduce planning/multi-agent only after eval infrastructure exists.**

## Production Building Blocks

Osmani's concrete inventory behind "design the system that prompts the agent" — five
primitives plus a spine:

- **Automations — the heartbeat.** Scheduled discovery and triage running independently;
  findings land in a triage inbox.
- **Worktrees — parallel safety.** Isolated working directories so concurrent agents don't
  collide on files.
- **Skills — intent preservation.** Standardized `SKILL.md` files codifying project knowledge
  so the agent doesn't re-derive conventions each cycle. The cost of skipping this is **intent
  debt**: agents confidently guessing your conventions.
- **Plugins & connectors — environmental integration.** MCP connectors into trackers, DBs,
  Slack. What upgrades a loop from *"here's the fix"* to *"PR opened, ticket linked, Slack
  notified."* See [[MCP Protocol]].
- **Sub-agents — separation of concerns.** Split the **maker** from the **checker** so the
  model never grades its own work. See [[Harness Orchestration]].
- **Memory — the spine.** Durable files holding state *outside* the conversation, because the
  model forgets between runs.

**Worked example (Osmani's morning loop):** automation fires the triage skill → reads CI
failures, issues, commits → writes findings to markdown → opens isolated worktrees → spawns a
sub-agent to draft each fix → a second sub-agent verifies → connectors open the PR and update
the ticket → anything unhandled lands in the triage inbox for human review.

### Patterns in the Wild

Two dominant architectures: **event-triggered** (Sentry error, new ticket, outage) and
**scheduled cron** (test stabilization, design review passes, long migrations). Reported uses
include automated incident response that investigates alerts and opens PRs, flaky-test agents
that reproduce and propose fixes, nightly test-babysitting that separates real regressions from
false negatives, and a React → React Native migration running in 30-minute cycles.

Keep the skeptical note in view — engineer Oded Messer observes that a repeatable workflow
*"becomes tactical if the AI is capable enough or it's just a high level old-school automation
I can set up like a cron or a trigger."* **Much of loop engineering is automation rediscovered;
the new part is that the thing on the cron is nondeterministic**, which is exactly why
verification and stop rules carry the weight.

## Failure Modes

**Three structural ones:**

1. **Context rot.** Working memory degrades as the transcript grows. Fix: summarization and
   pruning *inside* the loop, not after it. See [[Context Failure Modes]].
2. **Termination failures.** Loops that run forever or stop arbitrarily. Fix: layered
   independent exits *plus* no-progress detection.
3. **Weak verification.** Model self-grading is gameable. Fix: **anchor on deterministic
   checks** — tests, compilers, linters, type checkers — and use model judgment only above
   that floor.

Loop-level pitfalls: no exit condition; repeated failures without adaptation; context overflow;
vague goal specification; insufficient tool access.

**The human failure modes are the more important half**, since they don't show up in traces:

- **Verification burden.** Loops make unattended mistakes *unattended*. Verifier sub-agents
  reduce but do not remove the need for human confirmation.
- **Comprehension debt.** Unreviewed code accrues faster than understanding. **Faster loops
  widen the knowledge gap unless review is active.**
- **Cognitive surrender.** *"The comfortable posture is the dangerous one."* The same loop
  structure produces opposite outcomes depending on the operator's intention.

> *"Build the loop. But build it like someone who intends to stay the engineer, not just the
> person who presses go."* — Osmani

## Best Practices

- **Start minimal** — one simple loop with one verifier before adding levels.
- **Define termination before implementation**, not after the first runaway.
- **Prefer deterministic verification** over model judgment wherever a check exists.
- **Feed structured feedback**, not raw output dumps, into the next iteration.
- **Budget tool calls per iteration**; log everything with periodic summaries.
- **Keep durable memory outside the model.**
- **Test the failure paths deliberately** — not just the happy path.
- **Guardrails are explicit**: iteration limits, tool allowlists, confidence thresholds; roll
  out shadow → canary → wide.

The through-line: treat an autonomous run as a **thermostat, not a conversation partner**.

## Framework Bindings

### Google ADK — `LoopAgent`

Runs its `sub_agents` **sequentially, in order, each iteration**, repeating until termination.
`max_iterations` is a hard cap. **Termination is not automatic**: *"the LoopAgent itself does
not inherently decide when to stop looping. You must implement a termination mechanism."* A
sub-agent signals early exit by setting `tool_context.actions.escalate = True`, typically via
an `exit_loop` tool.

Documented refinement shape: `InitialWriterAgent` (draft) → `CriticAgent` (evaluate against
criteria) → `RefinerAgent` (apply improvements, or call `exit_loop` when the critic returns its
completion phrase). Sub-agents share state through the context dict.

> Note the shape: ADK's critic/refiner split is the same **maker/checker separation** as
> Osmani's sub-agents and LangChain's Level-2 grader. **Three vocabularies, one pattern.**

### Vercel AI SDK — `ToolLoopAgent` / `WorkflowAgent`

`ToolLoopAgent` coordinates model calls with tool execution across steps.
`stopWhen: stepCountIs(25)` is the required ceiling — **non-optional in practice when the loop
calls paid search tools**. `generate()` returns `result.text` and `result.steps` (the tool-call
history — your trace).

**Durability** via `WorkflowAgent`: each tool's `execute` carries a `'use step'` directive,
making a checkpoint boundary. Completed steps **replay from recorded output** instead of
re-executing; failed steps retry automatically. Same primitive as
[[Production Reliability Primitives]]' resume-from-failed-node, at a different layer.

**Model routing per step** rather than one frontier model for everything: frontier model for
loop reasoning and synthesis, a smaller model for aggregation and structured extraction.

**Sandboxing** untrusted model-written code, keyed by run id so retried steps reattach to the
existing sandbox:

```typescript
const sandbox = await Sandbox.getOrCreate({
  name: `analysis-${researchId}`,
  runtime: 'node24',
  timeout: 600_000,
  networkPolicy: 'deny-all',
});
```

**Runtime envelope:** Vercel Functions with fluid compute run to 800s — a real constraint on
loop length. **Anything longer must checkpoint and resume rather than hold the process.**

## Design Checklist

- [ ] What is the **trigger** — manual, cron, or event?
- [ ] What is the **testable goal**, and which deterministic check proves it?
- [ ] What are the **stop rules** — success, iteration cap, budget cap, stall detector?
- [ ] Who is the **verifier**, and is it a different agent/model from the maker?
- [ ] Where does **state** live between runs, outside the context window?
- [ ] How is context **compacted** each iteration?
- [ ] Which actions require **human approval** before execution?
- [ ] What is the **escalation path** when the cap is hit without success?
- [ ] Are parallel agents **isolated** (worktrees/sandboxes) so they can't collide?
- [ ] Are traces captured well enough to feed a **hill-climbing** pass later?

## Topic Notes

1. [[Loop Autonomy Ladder]] — the orthogonal autonomy axis: turn-based → goal-based → time-based → proactive
2. [[Loop Termination Design]] — layered independent exits, stall detection, escalation
3. [[Evolve Loop]] — the slow loop that rewrites the fast one, at practitioner scale
4. [[Recursive Self-Improvement]] — level 4 at the frontier, and the `autoresearch` worked example

## See Also
- [[Eval Harness Anatomy]] <!-- auto-linked -->
- [[Knowledge Graph as Shared Agent Memory]] <!-- auto-linked -->
- [[Single Agent With Tools]] <!-- auto-linked -->
- [[Harness Anatomy]] <!-- auto-linked -->
- [[Prompt Chaining]] <!-- auto-linked -->
- [[Iterative Harness Simplification]] <!-- auto-linked -->
- [[Harness Engineering]] — depends-on
- [[Verification Loops]] — part-of
- [[Loop Detection and the Two-Retry Rule]] — complements
- [[Long-Horizon Execution]] — complements
- [[Context Engineering]] — depends-on
- [[Graph Engineering]] — extends (the layer above: when one loop is no longer the right shape)
- [[Loop-to-Graph Escalation]] — extends (the decision procedure for crossing that boundary)
