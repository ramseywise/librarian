---
title: Verification Loops
tags: [llm, agents, eval, concept]
summary: "Models stop at the first plausible solution and rate their own work generously — two distinct failures needing two distinct fixes: a forced verification pass, and an external evaluator that never generates."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--05-verification-loops.md
---

# Verification Loops

The harness's answer to the two ways agents declare success without earning it.

## The Core Failure

Agents **stop after writing code without testing it**. The output looks complete, the model
is confident, and nothing checked.

Two distinct problems underneath:

1. **Models lean toward the first plausible solution.** Without pressure to verify,
   *plausible is where they stop.*
2. **Agents rate their own work generously** — *"agents tend to respond by confidently
   praising the work — even when quality is mediocre."*

> The first needs a **forced verification pass**. The second needs an **external
> evaluator**. They are not the same fix.

## The Self-Verification Loop

Make the workflow explicit rather than implied:

```
plan → build → verify → fix → (repeat until verify passes)
```

Verification must cover **happy paths and edge cases** — *an agent asked to "test it" will
test the case it just built for.*

**Enforcement is a hook, not a hope.** A pre-completion checklist middleware intercepts the
agent's attempt to exit and forces a verification pass before completion is allowed.

> **The agent cannot declare done; it can only *request* done, and the harness adjudicates.**

This is also why sandbox tooling matters — test runners, logs, and screenshots are what
"verify" reads. See [[Execution Boundaries and Guardrails]].

## Three Kinds of Reflection

"Verify" is not one check. Splitting it into three loops that **fail independently** is this
material's most portable idea:

| Loop | Question | Catches |
|---|---|---|
| **Process reflection** | Am I on the right trajectory? | Bad sequencing, wrong tool choice, steps that don't advance the goal |
| **Data reflection** | Is the evidence sufficient? | Thin evidence, missing context, gaps in coverage |
| **Draft reflection** | Is the output complete? | Missing sections, inconsistent tables, synthesis gaps |

The reason to split them: **an agent can execute a flawless workflow and still retrieve
nothing useful** — good process, bad data. The inverse also holds. *A single "did it work?"
check collapses both into one verdict and gives the agent nothing to act on.*

**Placement matters as much as existence.** Process reflection runs *between* steps; data
reflection runs *before* synthesis, and when evidence is short it emits **specific follow-up
questions that route back to retrieval** rather than a bare "insufficient"; draft reflection
runs *after* generation.

> Each loop's output is an instruction to a named upstream stage — **that is what makes them
> loops rather than assertions.**

The reported payoff from process reflection specifically: **tool-selection accuracy improved
sharply** once the agent had a dedicated space to reason about which tool matched the
intent. That gain arrived as the tool count grew and domain boundaries began overlapping —
the same failure mode that `DO NOT USE FOR` sections address. **Reflection and tool
description are two attacks on the same problem.** See
[[Tool Design as Harness Surface]].

## Asymmetric QA

The single highest-leverage rule here:

> **The verification model must be smarter than the execution model.**

Cheap fast model for the task; expensive smart model **at the verification gate only**. This
inverts the intuition that you spend on generation, and it is economically favorable —
*verification runs once per gate over a bounded artifact, while generation runs over many
steps*.

The symmetric alternative — the same model checking its own work — is a canonical failure
mode. **It produces confident agreement, not review.**

### When a verifier is worth deleting

The counterweight, and the rarer report: a production system ran an LLM review step over
generated SQL and **removed it**. The reviewer kept flagging valid queries as erroneous —
cost and latency for a net loss in throughput, with no accuracy gain to trade against.

> **A verifier earns its place only if its false-positive rate is low enough that acting on
> its verdict beats ignoring it.**

**A gate that cries wolf gets routed around by whoever operates it, which is worse than no
gate** — it produces the appearance of verification plus the habit of overriding it.

Where a **deterministic** check can cover the same ground, prefer it: that same system kept
a hard allowlist (`SELECT` only; `DELETE`/`INSERT`/`UPDATE` blocked) and a result cap, both
exact and free. *The LLM reviewer was the layer that went, not the validation.*

> **Verify with the cheapest mechanism that is actually decisive.** Schema check before
> reference comparison before LLM judge.

**Verification layers are subject to the subtraction pass like everything else** — see
[[Harness Maturity and Failure Modes]] and [[Eval Ladder]].

## Separating Generation from Evaluation

Self-evaluation bias is structural, not a prompting problem:

> **External evaluators can be tuned to skepticism far more effectively than generators can
> be made self-critical.**

An agent asked to critique its own output is being asked to hold two conflicting objectives.
**A separate evaluator holds only one.**

A three-agent architecture for long-running app generation:

| Agent | Function | Notes |
|---|---|---|
| **Planner** | Expand a brief prompt into a full spec | High-level scope; identifies opportunities |
| **Generator** | Implement features incrementally | Self-evaluates per cycle; uses version control |
| **Evaluator** | QA the running app; verify against spec | Drives the live app; scores against explicit criteria |

**The evaluator navigates the actual running application rather than reading the diff.**
*Reading code verifies intent; driving the app verifies behavior.*

Measured result: a solo run (20 min, $9) produced broken core gameplay; the full harness
(6 hr, $200) produced a functional game with working AI integration. **~20× the cost for the
difference between broken and working** — the harness ROI question is rarely *"is it
cheaper,"* it is *"does it produce a result at all."*

## Grading Criteria Beat Vibes

Subjective judgment does not transfer to an evaluator agent. Replace it with **weighted,
named criteria** — for frontend work: design quality (coherent identity vs a collection of
parts), originality (custom vs stock), craft (typography, spacing, contrast, hierarchy),
functionality (can a user complete the task?).

> **Name the dimensions, weight them, score each separately.** A single 1–10 score collapses
> distinct failures into one number and gives the generator nothing actionable.

See [[LLM-as-Judge Evaluation]].

## Sprint Contracts

Before implementation, generator and evaluator **negotiate deliverables in writing.**

This bridges the gap between a high-level spec and testable acceptance criteria — *the gap
where scope creep and misalignment live*. The contract is written **before** work starts, by
both parties, so **the evaluator can't invent criteria afterward and the generator can't
redefine done**.

It is the **acceptance baseline** from [[Harness Engineering]], made concrete and per-task.

Related: verification contracts with **scoped claims** — the agent states precisely what it
verified, which prevents *"tests pass"* from covering an untested path.

## Eval-First

> **Establish binary pass/fail criteria before tuning anything else.**

Without a binary eval there is no signal to improve against, and every change is a vibe. The
tier ladder (cheapest first) and the Pass@k / Pass^k distinction are covered in
[[Eval Ladder]] and [[Anthropic Three-Tier Eval Taxonomy]]; ship on **Pass^k**.

The meta-rule: **if the eval system is broken, fix the eval system first.** *Never steer on a
distorted signal.*

### Two eval surfaces, different triggers

| | **Dataset eval** | **Live-traffic eval** |
|---|---|---|
| Input | Curated questions + SME reference answers | Real production queries, no reference |
| Trigger | On change to workflow, prompts, or models | Daily batch |
| Measures | Accuracy, semantic similarity to reference | Faithfulness, answer relevancy |
| Catches | Regressions | Drift, hallucination, the query distribution you didn't anticipate |

The split exists because **reference-free metrics work on live traffic and reference-based
ones don't.** Faithfulness and relevancy are computable without ground truth, so they run on
everything; accuracy needs a labeled answer, so it runs on the curated set.

> Ship with both — **the dataset eval is the regression gate; the live eval is the one that
> finds what your dataset never contained.**

### Evaluate the stages, not just the endpoint

> **Apply metrics at each workflow stage, like a testing pyramid — not only end-to-end.**

An end-to-end score tells you the answer was wrong; it does not tell you whether retrieval
missed the document, reflection accepted thin evidence, or synthesis dropped a finding that
was present in context. Per-stage metrics are what **localize a regression to the component
that caused it**.

This is the concrete reason a decomposed workflow beats a monolithic agent: **each stage can
be evaluated, debugged, and improved in isolation.**

## Trace-Driven Improvement

The ratchet needs input, and **traces are it.** A trace-analyzer skill fetches production
traces, spawns parallel error-analysis agents, and synthesizes recurring failure patterns —
reasoning errors, task misunderstanding, insufficient testing. **Each recurring pattern
becomes a harness change.**

Prerequisite: **traces exist and are structured.** Observability is not a nice-to-have — it
is the raw material for every subsequent improvement.

Worth noting how modest the production version of this is: storing traces and eval datasets
**in the same tool**, so a failing score links directly to the trace that produced it. No
parallel analysis agents — just the ability to go from *"this metric dropped"* to *"here is
the run"* without a join across systems. **That adjacency is most of the value; the
automation on top is the frontier.**

## Verification the User Performs

The last verification layer is not in the harness at all — it is **the affordance that lets
a human check the work cheaply.**

Ground every claim in retrieved context with a citation carrying **source document, page
number, and the exact supporting quote**. Display intermediate steps — queries formulated,
tools called, chunks shortlisted — as the workflow runs.

Two distinct functions:

1. **Verification cost drops far enough to be routine.** *A reviewer who must locate the
   supporting passage themselves will spot-check; one who is handed the quote and page
   checks every claim.* Same reviewer, different behavior.
2. **Visible intermediate steps make a wrong answer diagnosable** rather than merely wrong —
   the user sees *where* it went off, which is a bug report instead of a complaint.

> **In any domain where a human must sign off, traceability is a harness feature, not a UI
> nicety.**

It also disciplines the generator: **an agent required to cite can only assert what it
retrieved**, which constrains hallucination at the point of writing rather than catching it
afterward.

## See Also
- [[Eval Suite Maintenance]] <!-- auto-linked -->
- [[Harness Engineering]] — part-of
- [[Agent Retry Taxonomy]] — complements
- [[Loop Detection and the Two-Retry Rule]] — complements
- [[Eval Ladder]] — depends-on
- [[LLM-as-Judge Evaluation]] — implements
- [[TDD as Coding-Agent Harness]] — instance-of
- [[Loop Engineering]] — part-of (capability level 2 is this loop)
- [[Loop Autonomy Ladder]] — prerequisite-for (rung 2 is where the verifier stops being optional)
- [[Recursive Self-Improvement]] — extends (the write boundary enforces generator/evaluator separation structurally)
- [[Knowledge Graph as Shared Agent Memory]] — extends (isolated verifier context as the structural fix for self-agreement bias)
- [[Graph Engineering]] — complements (generate-then-verify is the highest-yield first graph)
