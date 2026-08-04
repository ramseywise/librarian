---
title: Loop Termination Design
tags: [llm, agents, infra, pattern]
summary: "Stop rules are layered and independent — success verifier, iteration cap, budget cap, stall detector, escalation path — and the cap is the backstop, never the primary exit."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--loop-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--README.md
---

# Loop Termination Design

The component of [[Loop Engineering]] most often written last and most often the cause of the
expensive failure. **Loops that run forever or stop arbitrarily are the second of the three
structural loop failure modes**, and unlike context rot they fail silently on the billing side.

> **Define termination before implementation, not after the first runaway.**

## Layered, Independent Exits

The governing rule: a loop needs **several exit conditions that do not depend on each other**.
Any single one can be wrong; the set is what bounds the run.

| Exit | Fires when | Fails when alone |
|---|---|---|
| **Success verifier** | The deterministic check passes | The verifier is gameable or absent |
| **Iteration cap** | `max_steps` reached | Silently truncates work that was progressing |
| **Budget cap** | Token/dollar ceiling hit | Doesn't distinguish productive from thrashing spend |
| **Stall detector** | No progress for N steps | Requires a definition of "progress" |
| **Escalation path** | Any of the above without success | Nowhere to escalate to |

**The cap is the safety backstop, not the primary exit.** A loop whose normal completion mode
is hitting `max_iterations` is a loop with no working verifier — it just has an expensive
timeout wearing a verifier's clothes.

## Stalled-Progress Detection

The exit that separates a designed loop from a capped one. Iteration and budget caps bound the
*cost* of thrashing; only a stall detector bounds the *duration* of it.

Its prerequisite is that progress be observable — a changing file, a shrinking failure count, a
newly satisfied assertion. **If nothing measurable moves between iterations, there is nothing
for the detector to read**, which is the same prerequisite as the rung-2 verifier in the
[[Loop Autonomy Ladder]]: *a measurable end state*.

Related but distinct: [[Loop Detection and the Two-Retry Rule]] catches an agent repeating an
identical action; a stall detector catches an agent making *varied* moves that go nowhere.

## Cap Reached Is Not Success

The single most important line in the canonical loop skeleton is its last one:

```
escalate to human  # cap reached, not success
```

Falling out of the bottom of a loop must be **structurally distinguishable from completing
it**. A loop that returns the same result on exhaustion as it does on success has erased the
signal that would have told you the verifier or the goal is wrong.

This connects to error handling, the fifth required component: **distinguish recoverable errors
from hard blockers, and change strategy based on error type rather than retrying the identical
failed approach** — see [[Agent Retry Taxonomy]].

## Framework Enforcement

Termination is a place where framework defaults matter, because the default is usually *no
termination*:

- **ADK `LoopAgent`** — *"the LoopAgent itself does not inherently decide when to stop
  looping. You must implement a termination mechanism."* Early exit is a sub-agent setting
  `tool_context.actions.escalate = True`, typically via an `exit_loop` tool.
  **Always provide the escalation escape hatch**; keep `max_iterations` as the backstop.
- **Vercel `ToolLoopAgent`** — `stopWhen: stepCountIs(25)`. Nominally optional; **non-optional
  in practice when the loop calls paid tools.**

Both make the same design point: the framework gives you the cap for free and leaves the
verifier to you, **which is exactly backwards from the order of importance.**

## See Also
- [[Recursive Self-Improvement]] <!-- auto-linked -->
- [[Loop Engineering]] — part-of
- [[Loop Autonomy Ladder]] — depends-on
- [[Loop Detection and the Two-Retry Rule]] — complements
- [[Agent Retry Taxonomy]] — complements
- [[Verification Loops]] — depends-on
