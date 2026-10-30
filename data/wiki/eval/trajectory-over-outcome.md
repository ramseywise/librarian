---
title: Trajectory Over Outcome
tags: [eval, agents, concept]
summary: "Why an agent has to be scored on the path and not just the answer — a correct output from a lucky trajectory is a latent failure, and routing and stopping point are the two decisions an outcome score cannot see."
updated: 2026-10-30
sources:
  - data/raw/articles/2026-07-19-evaluating-ai-agents-deeplearning.md
  - own-prose
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--06-evaluating-agents.md
---

# Trajectory Over Outcome

Everything in [[RAG Evaluation]] still applies to an agent — the corpus gate, the
retrieval metrics, the augmentation decision, the generation judge. What changes is that a
RAG pipeline is **deterministic and linear** and an agent is neither. The pipeline runs
the same nodes in the same order every time, so scoring the output is a valid proxy for
scoring the process: there is only one process. An agent chooses its own path, and two
runs on the same input can take different ones.

Which makes the central claim:

> A good outcome doesn't validate the path that produced it. You can get the right answer
> from a lucky trajectory and have it fail next week on a query that looks identical.

An outcome score on a nondeterministic system measures the *sample*, not the system. The
agent that answered correctly by calling the wrong tool, getting an error, retrying, and
stumbling onto the right source has produced a green test and an undiagnosed defect. It
will keep producing green tests until the day the stumble doesn't land — and because the
failing query looks like the passing ones, there is nothing in the eval history that
predicts it.

This is the *why* underneath the Tier 2 trajectory tier in
[[RAG Evaluation]]'s agent eval taxonomy. The tiers say what to measure; this says why
Tier 3 alone is not a smaller version of the same signal, but a different and weaker one.

## The two decisions an outcome cannot see

Two aspects account for most of what goes wrong, and neither is visible in the final
answer.

### Routing

Which node or tool the agent chose. A wrong route that still produces a right answer is
the canonical lucky trajectory — the agent took the general-purpose path, the general
path happened to have enough information, and the specialized tool that exists precisely
for this query never fired. Nothing in the output records that. Routing accuracy is
mechanically checkable against an expected route on a golden sample, which is why it sits
in the cheap deterministic tier rather than the expensive judge tier.

### Stopping point

When the agent decided it was done. Under-stopping burns budget and accumulates context
for no gain; over-stopping returns a partial answer that reads complete. The second is
worse, because a truncated answer with a confident tone is indistinguishable from a
correct one to an outcome judge — and often to a user. See
[[Loop Detection and the Two-Retry Rule]] and [[Loop Termination Design]].

## The retry that discarded its own evidence

A concrete instance from the Shine build. The agent's retry logic, on a low-confidence
result, re-ran retrieval — and in doing so **discarded the sources it had already found**.
Some of those were correct. The retry then returned something worse than what it threw
away.

Two properties of this failure make it the argument for trajectory eval on their own:

- **It is invisible in the outcome.** The final answer is merely mediocre. Nothing marks it
  as *having been better mid-run*. Only the trajectory shows a correct source retrieved at
  step 2 and absent from the context at step 5.
- **The retry was working as designed.** No exception, no timeout, no error. The bug was in
  the state transition — retry treated the retrieval result as replaceable rather than
  accumulable, which is a one-line decision nobody writes a test for. See
  [[Agent Retry Taxonomy]].

The related failure in the same system was the agent's inability to distinguish an
**in-scope query from an escalate-worthy one**, which is the routing decision at its most
consequential: answering a question that should have been handed off is a wrong route
whose outcome frequently looks fine. It is `wrong_escalation` in the
[[RAG Eval Gate Contract]] failure taxonomy, and it is only checkable against an
expected route.

Both point the same direction — **which is the argument for scoring nodes rather than just
the final answer.**

## Scoring nodes

Treating each node as an independently assertable unit changes what a failing eval tells
you. An end-to-end failure says the run was wrong. A node-level failure says *which
decision* was wrong, and node-level assertions are mostly deterministic:

| Node | Assertable without a judge |
|---|---|
| Router | Chosen route vs expected route |
| Retriever | Expected source present in returned set |
| Retry / loop | Did evidence from prior iterations survive? Did it terminate? |
| Escalation | Fired when the golden sample says it should |
| Synthesizer | Cited only from the context it was given |

Every row here is a cheap deterministic check that an outcome judge cannot make. The
expensive LLM judge should be reserved for the one thing genuinely not mechanically
decidable — whether the final answer is good — and it should run on trajectories that
already passed. This is the same economic argument the gate ladder makes for RAG:
**put the cheap deterministic checks upstream so the expensive judge only sees runs worth
judging.**

## The relationship to guardrails

The other reason trajectory eval matters is that it is the only way to find out whether
the safeguards are doing anything. A bounded agent has type schemas, explicit state,
escalation, and termination conditions; an outcome score confirms the system works but
says nothing about which bound is load-bearing. See
[[Bounding Agents Rather Than Trusting Them]].

## Router evals as the cheap first layer

A course sequence for agent eval (build → trace → router evals → trajectory evals →
structured evals) makes the same split operational. **Tracing comes first** — you cannot
evaluate a path you did not record. **Router evals** then score each routing decision
binary pass/fail ("was the right skill/tool chosen for this input?") and aggregate to a
routing accuracy; they are cheap and catch a large class of failures before any full-path
scoring. **Trajectory evals** score the whole action sequence, which is what catches a
right answer reached by a wrong path — e.g. an unauthorised API call on the way. Final-answer
quality is then scored per dimension rather than as one number (see
[[Specialist Verdict Panel]]).

## Tool-call match modes and the invariant rule

Trajectory checks come in strictness levels:

| Mode | Passes when | Use for |
|---|---|---|
| **Exact** | Same tools, same order, same arguments | Strict protocols (auth before action) |
| **In order** | Expected calls appear in order, extras allowed | Required sequence with some freedom |
| **Any order** | Expected calls all appear | Independent lookups |
| **Subset / superset** | Calls ⊆ (or ⊇) an allowed set | "Never call outside this set" / "must at least call these" |

Outcome should be checked by **end state** (the record in the database), not by what the agent says it did.

The reverse failure exists too: a strict trajectory check can fail a run that did *better* than the
script. Anthropic's example is a flight-booking agent that found a loophole in the fare policy and
got the user a cheaper ticket — failed against the preset path, succeeded by outcome. So **trajectory
checks should enforce invariants** ("never book before confirming"), not one golden path.

In supervisor/sub-agent systems, split **routing evals** (does the supervisor pick the right sub-agent?
seed with boundary queries) from **domain evals** (given correct routing, does the sub-agent act
correctly?). And **treat a 0% task as suspect**: a task failing every trial across versions is usually
broken (unreachable state, wrong reference, missing permission) before the agent is.

## See Also
- [[Eval Non-Determinism]] <!-- auto-linked -->
- [[Eval Harness Anatomy]] <!-- auto-linked -->
- [[Eval Suite Maintenance]] <!-- auto-linked -->
- [[VA Eval Harness]] <!-- auto-linked -->
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] <!-- auto-linked -->
- [[RAG Evaluation]] — extends (the agent eval taxonomy this supplies the rationale for)
- [[Bounding Agents Rather Than Trusting Them]] — related (guardrails need trajectory eval to be measurable)
- [[RAG Eval Gate Contract]] — related (wrong_escalation and the row-pool discipline)
- [[Agent Retry Taxonomy]] — instance-of (the retry that discarded correct sources)
- [[The Augmentation Gate]] — related (the same cheap-gates-before-expensive-judge argument, for RAG)
- [[Loop Detection and the Two-Retry Rule]] — related (the stopping-point decision, mechanically)
- [[Specialist Verdict Panel]] — related (final-answer dimensions scored independently)
- [[Simulated User Evaluation]] — extends
- [[Agent Trace Anatomy]] — prerequisite-for
