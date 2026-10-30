---
title: Harness Subsystem Attribution
tags: [llm, agents, infra, pattern]
summary: "Diagnose a failing agent by attributing the failure to one of five subsystems — instructions, tools, environment, state, feedback — fix only that one on a fixed model, and use ablation to learn which subsystems are load-bearing."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--01-what-a-harness-is.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--02-harness-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Harness Subsystem Attribution

The nine components in [[Harness Anatomy]] describe what *ships*. For diagnosing a failing
agent a coarser cut works better: every component serves one of **five subsystems**, and
every failure can be attributed to exactly one of them.

## The Five Subsystems

| Subsystem | Question it answers | Typical components |
|---|---|---|
| **Instructions** | What should I do, and by what rules? | System prompt / `AGENTS.md`, memory files |
| **Tools** | What can I act with? | Tools, skills, MCP servers, bash, retrieval |
| **Environment** | Where do I run, and does it start? | Filesystem, sandbox, `init.sh` |
| **State** | What has happened so far? | Plan file, progress log, feature list, git |
| **Feedback** | Did it work? | Hooks, test runners, verification gates, traces |

### The two gulfs

Two of the five map onto the two gulfs from interaction design:

- **Gulf of execution** — the agent knows what it wants but cannot act on it. A *tools* or
  *environment* gap.
- **Gulf of evaluation** — it acted but cannot tell whether that worked. A *feedback* gap.

> Agents usually fail on evaluation. **They are rarely stuck; they are confidently wrong.**

That is why [[Verification Loops]] and the [[Three-Layer Termination Check]] carry so much
of a harness's weight.

## Five Ways a Capable Model Fails Without a Harness

For a coding agent in a real repository the failures recur in five shapes, and each maps to
a harness fix rather than a model upgrade:

| Failure | Looks like | Subsystem | Harness fix |
|---|---|---|---|
| **Vague requirements** | Builds something plausible that isn't what was meant | Instructions / state | A feature list of verifiable behaviours |
| **Implicit conventions** | Breaks rules that live only in people's heads | Instructions | The repository as system of record |
| **Incomplete environment** | Fights setup all session, or "fixes" the wrong thing | Environment | `init.sh` plus a startup-readiness check |
| **No verification** | Claims done when it isn't | Feedback | [[Three-Layer Termination Check]] |
| **Cross-session loss** | Each session re-derives or undoes the last | State | Progress log plus handoff ([[Long-Horizon Execution]]) |

## Fix the Harness First

The working loop that falls out of the "skill issue" reframe in [[Harness Engineering]]:

1. **Run** the task on a **fixed model**.
2. **Attribute** the failure to one subsystem.
3. **Fix that subsystem, and only that one.**
4. **Re-run** the same task and compare.

Change the model only after several rounds of this stop helping. **Swapping models first
hides which part of the harness was missing**, so the same failure returns under the next
model.

## Ablation

The table becomes a method when run in reverse: **remove one subsystem at a time on a fixed
task and watch what breaks.** What breaks tells you which parts of *your* harness are
load-bearing — the measurement that [[Iterative Harness Simplification]] needs before it
strips anything.

## See Also
- [[Harness Anatomy]] — extends (a diagnostic cut over the nine components)
- [[Harness Engineering]] — instance-of (the skill-issue reframe turned into a procedure)
- [[Iterative Harness Simplification]] — prerequisite-for (ablation shows what is load-bearing)
- [[Verification Loops]] — extends (the gulf of evaluation is the common failure)
- [[Harness Orchestration]] — extends
