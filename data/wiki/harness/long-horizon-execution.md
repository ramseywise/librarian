---
title: Long-Horizon Execution
tags: [llm, agents, infra, concept]
summary: "Agents lose coherence and finish early over long tasks — the fix is externalizing progress to files so the loop is re-entrant, not stretching the context window."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--06-long-horizon-execution.md
---

# Long-Horizon Execution

Tasks that outlast a single context window need a different harness than tasks that fit
inside one.

## The Problem

Two failures compound as horizon grows:

1. **Coherence decay.** Earlier decisions fall out of the window, and the agent
   re-litigates or contradicts them.
2. **Context anxiety.** As the window fills, models **prematurely wrap up work** —
   summarizing, declaring done, closing out.

> The agent doesn't fail loudly, it **finishes early and confidently**.

The second is the more dangerous one, because it produces output that looks like
completion. It is the same adjudication problem as [[Verification Loops]], arriving through
a different door: there, the agent stops at the first plausible answer; here, it stops
because the window is running out.

## State Externalization

The governing move:

> **Progress lives in files, not in the context window.**

Once state is on disk, the loop becomes **re-entrant** — a fresh context can pick up where
the previous one stopped, because nothing load-bearing lived only in the window. The
common shape is two agents:

| Agent | Role |
|---|---|
| **Initializer** | Sets up the working state — plan file, progress log, directory layout |
| **Worker** | Reads the state, advances it by one increment, writes it back |

The worker is disposable by design. Losing its context costs one increment, not the run.

## Plans as First-Class Artifacts

An execution plan is a file, not a message.

| | **Ephemeral plan** | **Checked-in plan** |
|---|---|---|
| Lives | Scratch directory, per-run | Repo, versioned |
| Holds | Current step, immediate next actions | Progress log, decision log, rationale |
| Survives | The run | The project |

The decision log is the part that pays off later: it records *why* an approach was taken,
so a fresh context doesn't reopen a settled question.

> **A plan the agent forgets to update is a plan that doesn't exist.**

Updating it is a step in the loop, enforced by a hook where it matters — see
[[Execution Boundaries and Guardrails]].

## Compaction vs Context Reset

Two ways to handle a full window, and they are not equivalent:

| | **Compaction** | **Context reset** |
|---|---|---|
| Mechanism | Summarize the window, continue in place | Discard the window, re-read state from files |
| Preserves | A lossy trace of everything | Exactly what was written down |
| Fails when | The summary drops a load-bearing detail | The state files are incomplete |

Reported result: **context resets outperformed compaction for Sonnet 4.5**, and the gap
narrowed in newer models. That is worth reading twice — it is a live example of
**model-dependent scaffolding**. The right answer changed when the model changed, which
means this is a decision to re-test, not to settle. See
[[Harness Maturity and Failure Modes]].

The practical implication of preferring resets: **the quality of your state files becomes
the ceiling on how long the agent can run.**

## Tool-Call Offloading

Keep bulk data out of the window. Tools return `head`/`tail` slices plus a path; the agent
reads the full artifact only if it needs to.

*A 2,000-line log becomes ~40 lines plus a path.* Same information available, a fraction
of the window spent. See [[Harness Anatomy]] for why the filesystem is the foundational
primitive here.

## Structured Note-Taking

Agents write notes to disk as they work — findings, dead ends, open questions.

Partly emergent: Claude playing Pokémon **developed its own note structures** without being
told to. The harness lesson is that persistent scratch space is a capability the model will
use if you provide it, and cannot use if you don't.

## Ralph Loops

The direct structural answer to context anxiety:

> A hook **intercepts the completion attempt** and re-injects the original prompt into a
> **fresh context**.

The agent cannot finish early because finishing is not available to it — the harness
adjudicates completion, and until the acceptance baseline is met, "done" restarts the work
with a clean window and the state files intact. This is the same *request done, don't
declare done* rule from [[Verification Loops]], applied to the context boundary rather than
to quality.

## Autonomous End-to-End Execution

At the far end: harness chains that run a change from ticket to merged PR, with the agent
handling its own CI. One reported design choice is instructive — the chain **minimizes
merge resistance by rerunning flaky tests rather than blocking on them**.

That is a deliberate trade: a flaky test blocking an autonomous pipeline stalls it
permanently, and stalling is a worse failure than a rerun. It is only safe because the
acceptance baseline elsewhere is real.

## Decomposition and Specialization

Splitting a long task into sprints with role-specialized agents extends horizon — and
carries the standard caveat:

One such system's **sprint decomposition could be removed entirely when Opus 4.6 arrived**.
The scaffolding existed to compensate for a limitation the model no longer had.

> **Build it when the model needs it; re-test when the model changes.**

See [[Harness Orchestration]] for when decomposition is worth its cost, and
[[Harness Maturity and Failure Modes]] for the subtraction pass that removes it.

## See Also
- [[Loop Detection and the Two-Retry Rule]] <!-- auto-linked -->
- [[Harness Engineering]] — part-of
- [[Harness Anatomy]] — depends-on
- [[Verification Loops]] — complements
- [[Harness Orchestration]] — complements
- [[Context Engineering]] — depends-on
