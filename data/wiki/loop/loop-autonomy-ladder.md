---
title: Loop Autonomy Ladder
tags: [llm, agents, infra, pattern]
summary: "Four rungs of handoff — tool approval, stop condition, trigger, session — climbed one at a time, each earned with a verifier that has been observed catching a real failure."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--loop-autonomy-ladder.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--loop-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--07-autonomy-ladder.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--06-triggers-and-schedules.md
---

# Loop Autonomy Ladder

The **autonomy** axis of [[Loop Engineering]] — orthogonal to the four capability levels.
Capability asks *what the loop automates*; autonomy asks **how much of the operator's job has
been handed off**.

## The Framing

Every loop starts with a human doing four things: approving each tool call, judging when the
work is done, deciding when to start a run, and holding a session open while it runs. **The
ladder is the order in which you hand those four off.**

> **Climb one rung at a time, and earn each handoff with a verifier.**

The rungs are **cumulative** — rung 3 still needs rung 2's verifier. Skipping rungs is how you
get a doom loop: *an agent running unattended on a schedule with nothing but model judgment
deciding when to stop.*

| Rung | What you hand off | What must exist first |
|---|---|---|
| **1 — Turn-based** | Tool approval *within* a turn | Nothing — this is the entry point |
| **2 — Goal-based** | The **stop condition** | A measurable end state |
| **3 — Time-based** | The **trigger** (to a clock) | Rung 2's verifier |
| **4 — Proactive** | The trigger *and* the session | A verifier you trust unattended |

## 1 — Turn-based: hand off tool approval

You approve tool calls inside a turn, but every turn starts manually. The agent stops when
**it judges** the work is done.

Use it for interactive work you are watching. **Its value is diagnostic**: this is the rung
where you learn where your tasks actually fail, which is the raw material for the verifier you
need at rung 2.

Its weakness is exactly that stop condition — model judgment alone, which is
[[Verification Loops]]' core failure. Tolerable here only because you are present.

## 2 — Goal-based: hand off the stop condition

After each turn, a small fast model — or a deterministic check — tests whether the end
condition holds. The loop closes itself when the verifier confirms completion.

**This is the pivotal rung**, your first unattended loop. Climb it only once you can write a
*measurable* end state: tests pass, queue empty, lint clean, file exists.

> If the end state is only expressible as "looks right," you are not ready to leave rung 1.

**Everything above this rung inherits this verifier.** A weak verifier here silently becomes a
weak verifier at rungs 3 and 4, **where nobody is watching it fail.**

## 3 — Time-based: hand off the trigger to a clock

The loop re-runs on an interval. Use it to poll external state that changes on its own
schedule — deploy progress, PR review status, a queue draining.

Two properties worth noting: it is **session-scoped** (your terminal stays open), and it
**inherits your permissions** rather than needing its own credential grant. That makes it
meaningfully cheaper and safer than rung 4.

> **Time-based is the right resting place for most loops. Do not climb to proactive just
> because you can.**

## 4 — Proactive: hand off the trigger to a schedule or event

Runs with no open session — on a schedule or in response to an event. Overnight work and
event-driven automation live here.

**The prerequisite is not technical, it is evidential:** prove the loop works at rung 2 or 3
with a verifier you trust before removing the session. A proactive loop with an unproven
verifier is *an unattended, credentialed process with no stop condition* — see
[[Execution Boundaries and Guardrails]] for the credential and cost-ceiling consequences.

## Mapping to the Capability Levels

The two taxonomies are independent — a loop has a position on each:

| | Autonomy rung | Capability level |
|---|---|---|
| Asks | How much has the human handed off? | What does the loop automate? |
| 1 | Turn-based (approve tools) | Agent loop (automates work) |
| 2 | Goal-based (stop condition) | Verification loop (automates quality) |
| 3 | Time-based (trigger→clock) | Event-driven (automates invocation) |
| 4 | Proactive (trigger + session) | Hill-climbing (automates improvement) |

The rungs and levels look parallel at 3 and 4 but are **not the same claim**: capability level
3 is about *what triggers a run*; autonomy rung 3 is about *who holds the session*. A
hill-climbing loop (level 4) can perfectly well run at autonomy rung 1 — a human approving each
rewrite of the config — and that combination is the recommended starting point for the
[[Evolve Loop]].

### A Third View: the Adoption Ladder

A practical adoption order that cuts across both axes:

| Level | Name | Adds | Maps to |
|---|---|---|---|
| 1 | Goal runner | `/goal` with a stop condition | rung 2 |
| 2 | Scheduled single task | One automation on a timer (e.g. morning CI check) | rung 3–4 |
| 3 | Multi-agent loop | Maker/checker split, a worktree per finding | capability 2 |
| 4 | Self-feeding loop | Finds its own next task in external state (issues, feature list) | capability 3 |
| 5 | Fleet orchestration | Several loops in parallel sharing a memory layer | — |

Most teams sit between 2 and 3; level 1 pays off fastest.

## Triggers: How a Run Starts

Two ways a loop decides to run again: **run-until-done** (pass after pass until the scorekeeper
is green or a cap trips — needs a precise "done") and **timer** (interval or cron; never stops by
itself — each run must be **cheap when there's nothing to do**). Three ways a run starts:
**manual**, **event** (error alert, new ticket, failing CI, chat message) and **schedule**.
**Prefer events to polling**; when you must poll, put a **cheap deterministic pre-check** in
front of the agent (fetch updates since the last run, wake the agent only if there is work — the
trigger fix in [[Evolve Loop]]).

### Claude Code's built-ins mapped to rungs

| Command | Shape | Rung |
|---|---|---|
| `/goal` | Run-until-done toward a stated, verified condition | 2 |
| `/loop 5m <prompt>` | Timer, inside your session | 3 |
| `/loop <prompt>` | Self-paced: the model picks the delay | 3 |
| `/schedule` | Cloud routine on cron, no session open | 4 |

**Does this thing have an end?** Yes → `/goal`; ongoing watching → `/loop`. The common mistake
is `/loop 10m "keep implementing the payment system"`: each pass runs the same instruction from
scratch and doesn't remember where the last stopped — a timer loop that must make progress needs
a [[Loop State File]] it reads first. `/schedule` runs without you, so it needs a trusted
verifier and its own scoped credentials.

### Cost ceilings before turning a trigger on

An unattended trigger multiplies whatever one run costs: a **per-run cap** (steps, tokens,
dollars), a **per-day cap on the trigger itself** so an event storm can't start a thousand runs,
a **no-op path** that exits in seconds before calling the model, and **alerts on spend**, not
just on failure.

## Design Checklist

- [ ] Which rung is this loop on *today*?
- [ ] Can I state the stop condition as a check that returns a boolean? (Gate for rung 2.)
- [ ] **Has the verifier been observed catching a real failure — not just passing?**
- [ ] For rung 3+: what is the cost ceiling per run, and what happens when it trips?
- [ ] For rung 4: whose credentials does this run under, and who owns them?

## See Also
- [[Eval Ladder]] <!-- auto-linked -->
- [[Prompt Chaining]] <!-- auto-linked -->
- [[Harness Engineering]] <!-- auto-linked -->
- [[Graph Engineering]] <!-- auto-linked -->
- [[Loop Engineering]] — extends
- [[Loop Termination Design]] — extends
- [[Evolve Loop]] — prerequisite-for
- [[Verification Loops]] — extends
- [[Execution Boundaries and Guardrails]] — extends
- [[Loop Scorekeeper]] — extends
- [[Loop State File]] — extends
