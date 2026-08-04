---
title: Bounding Agents Rather Than Trusting Them
tags: [infra, agents, concept]
summary: "A design stance — constrain what the agent can do instead of trusting it to behave, via four bounds (type/IO schemas, explicit state, escalation as an outcome, termination conditions), plus the reason guardrails alone are not reliability: nothing tells you which one fires."
updated: 2026-08-04
sources:
  - own-prose
---

# Bounding Agents Rather Than Trusting Them

Have you ever prompted an LLM with a simple task and explicit instructions it then
ignored? Now imagine a multi-step agent that also loops, or queries a knowledge graph, or
calls MCP tools. Things get messy quickly, and it becomes hard to see where it went wrong.

The stance that follows:

> Bound what the agent *can* do, rather than trusting it to behave.

This is a claim about where reliability comes from. Instruction-following is
probabilistic, and probabilistic behavior does not become deterministic by being
important — a single-step task the model ignores is a nuisance, but the same failure rate
compounded across fifteen steps with tool calls in between is a system that fails often
and opaquely. The fix is not a better prompt. It is a smaller space of possible behaviors.
Same principle as [[Harness Engineering]]'s encoded-versus-documented constraint, applied
to runtime rather than to the development loop.

## The four bounds

### 1. Type and I/O schemas

Every node has a declared input and output shape, validated at the boundary. This is the
cheapest bound and the one with the widest blast radius, because an unvalidated output is
what turns a local error into a downstream mystery — a malformed tool result propagates
three nodes before it manifests, and the traceback points at the wrong place. Schema
validation converts a silent corruption into a loud failure at its origin. See
[[Structured Output]] and [[Tool Design as Harness Surface]].

### 2. Explicit state, memory, and caching

State the agent can read and write is *declared*, not accumulated in a conversation
transcript. The distinction matters because implicit state cannot be asserted on: if
"what the agent knows right now" is a function of message history, there is no point at
which you can check it, and there is nothing to restore after a failure. Explicit state
gives you a checkpoint, a diff, and a test fixture. See [[Memory Lifecycle]] and
[[LangGraph State Reducers]].

### 3. Escalation as a first-class outcome

Handing off to a human is a *success path*, not an error branch. When escalation is
modeled as failure handling, the agent's implicit objective becomes "answer anyway,"
which is exactly the behavior that produces confident wrong answers on queries outside
its competence. Making it a legitimate terminal state means the agent can be *right* to
stop. This is Layer 5 in
[[Safeguards Architecture — Five Protection Layers]] and the fallback-versus-escalation
distinction in [[Agent Management Layer]].

### 4. Termination conditions

Explicit bounds on iterations, budget, and wall time, with a defined behavior on
exhaustion. Any loop without one is a loop that can run forever, and in practice the
question is not whether it will but what it will cost when it does. Exhaustion should be
a distinguishable outcome rather than a timeout — *hit the retry cap* and *the tool hung*
require different responses. See [[Loop Termination Design]] and
[[Loop Detection and the Two-Retry Rule]].

## Falling back to determinism

When all four bounds are in place and a node is still unreliable, the next move is to
**replace the node with a more deterministic layer**. A classifier instead of a routing
prompt; a lookup table instead of a generation step; a rule instead of a judgment. The
question to ask of any node is whether it genuinely needs a model, and often the answer
is that a model was reached for because it was convenient rather than because the task
required inference.

Essentially it is all back to basics — the bounds above are schema validation, explicit
state, defined exits, and bounded loops, none of which are agent-specific. Agents make
them urgent rather than novel.

## Guardrails are not reliability

The part that is easy to miss:

> You can't guardrail your way to reliability without measuring whether the guardrails
> fire.

Four safeguards with no instrumentation is four safeguards you cannot reason about. You
do not know which one is doing the work, which one has never fired in production, or
which one is firing constantly and silently degrading a path that would otherwise have
succeeded. Every one of those is a different problem:

| Observation | What it means | Action |
|---|---|---|
| Never fires | Dead bound, or the failure it guards doesn't occur | Remove it, or confirm the failure class is genuinely absent |
| Fires constantly | It is load-bearing — or it is masking an upstream defect | Fix upstream; the bound was catching a symptom |
| Fires on successful runs | Over-constraining; suppressing correct behavior | Loosen, and check what it cost |

Without that signal a guardrail is an article of faith, and the system's reliability is
unattributable — you know it works but not why, so you cannot tell which parts you may
safely change.

**Trajectory eval is what supplies the signal.** It records which node fired, which bound
tripped, and what the run did next, which is exactly the per-node visibility an outcome
score cannot give ([[Trajectory Over Outcome]]). That is what turns four safeguards from
a hedge into something optimizable: once you know which bound is load-bearing, you know
where tightening buys reliability and where it only buys latency.

## See Also
- [[Trajectory Over Outcome]] — prerequisite-for (the measurement that makes bounds attributable)
- [[Safeguards Architecture — Five Protection Layers]] — implements (the runtime pipeline these bounds compose into)
- [[Agent Management Layer]] — complements (escalation and fallback as operational concerns)
- [[Harness Engineering]] — extends (encoded constraints beat documented ones, applied at runtime)
- [[Loop Termination Design]] — implements (the fourth bound)
- [[Execution Boundaries and Guardrails]] — complements (bounding what the agent may touch, not just what it may do)
