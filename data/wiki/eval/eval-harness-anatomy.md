---
title: Eval Harness Anatomy
tags: [eval, llm, agents, reference]
summary: "Task, trial, grader, trajectory, outcome — and the separation that makes the whole thing work: the evaluation harness treats the agent harness as the system under test."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-harness.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Eval Harness Anatomy

The vocabulary of agent evaluation. Worth pinning down precisely, because the terms are
used loosely and the distinctions carry real design consequences.

> Agent evaluation should measure both **whether the agent succeeded** and **how it behaved
> while reaching the result.**

## The five nouns

| Term | Definition |
|---|---|
| **Task** | A single test with defined inputs and success criteria — what the agent must do |
| **Trial** | One attempt at a task. Multiple trials per task, because outputs vary between runs |
| **Grader** | Evaluates one aspect: correctness, tool use, policy compliance, efficiency. A task may use several |
| **Trajectory** | The complete record of a trial — outputs, tool calls, reasoning, intermediate results |
| **Outcome** | The final environment state at the end of the trial |

**Trial is the term people skip**, and skipping it is how non-determinism gets mistaken for
regression. One run of a task is not a measurement — see [[Eval Non-Determinism]].

## Trajectory and outcome answer different questions

```
Outcome:    Did the agent achieve the goal?
Trajectory: Did it achieve the goal in an acceptable way?
```

Two failure shapes make grading both non-optional:

- The agent reaches the **correct outcome through unsafe or inefficient behavior** — an
  outcome-only eval scores this green.
- The agent follows a **reasonable process but fails on an external tool or environment
  issue** — an outcome-only eval scores this as an agent failure, and you debug the wrong
  thing.

Anthropic recommends grading both the final environment state and the execution transcript;
LangChain supports trajectory evaluation against the exact sequence of messages and tool
calls. This is the same trajectory-over-outcome argument that motivates level 3 of the
[[Eval Maturity Ladder]].

## Two harnesses, and the seam between them

| | What it is |
|---|---|
| **Agent harness** | The runtime being evaluated — model, prompts, tools, routing, memory, control loop |
| **Evaluation harness** | The infrastructure that runs evals — provides tasks, runs them concurrently, records steps, grades, aggregates |

> The evaluation harness should treat the agent harness as the **system under test**.

That framing is load-bearing. **If the two share code, state, or assumptions, the eval
measures the shared part rather than the agent.** It is the same generator/evaluator
separation from [[Verification Loops]], applied one level up: not "the model shouldn't grade
its own output" but "the harness shouldn't grade its own harness."

OpenAI's formulation is compatible — an agent eval is *a prompt, a captured run containing
traces and artifacts, a set of checks, and a comparable score*.

## Core evaluation flow

```
Evaluation suite
      ↓
Select a task
      ↓
Run the agent harness
      ↓
Capture trajectory + outcome
      ↓
Apply graders
      ↓
Aggregate scores and metrics
```

LangSmith's structure maps directly: a dataset, a target application, and evaluators, with
repeated runs grouped into experiments.

## Scoring design

Per task, combine grader scores as:

- **Weighted** — combined score must clear a threshold
- **Binary** — all graders must pass
- **Hybrid** — a mix

**Binary is the right default for safety-relevant graders**, since weighted scoring lets a
strong correctness score buy off a policy violation.

## Capability vs regression evals

The most useful eval-type distinction, because the two want opposite pass rates:

| Type | Asks | Target pass rate |
|---|---|---|
| **Capability** ("quality") | *What can this agent do well?* | **Low** — a capability eval everyone passes measures nothing |
| **Regression** | *Does it still handle what it used to?* | **~100%** |

The lifecycle connects them: **a capability eval whose pass rate climbs to ~100% is
promoted to a regression eval** and run continuously to catch drift. Tasks that once
measured *"can we do this at all?"* come to measure *"can we still do this reliably?"*

> A suite where everything passes is not a healthy suite — it is a saturated one. See
> [[Eval Suite Maintenance]].

## Grader types

Three, chosen by the **simplest reliable** rule — reach for the cheapest one that can
actually judge the property:

| Grader | Use when | Property |
|---|---|---|
| **Code** | Correctness is deterministically checkable | Highest certainty, least noise — prefer whenever a clear correct answer exists |
| **LLM-as-judge** | Semantic quality or judgment required | Scales; needs calibration ([[LLM-as-Judge Evaluation]]) |
| **Human** | Ambiguous cases; calibrating the judge | Reliable but slow; establishes the benchmark |

## Evaluating by agent type

Conversational agents need graders the others don't — beyond answer quality and latency:
**interaction quality** (tone; transcript constraints like "finished in under 10 turns")
and **extended adversarial conversations** as a stress test. Coding, research, and
computer-use agents each have their own grader sets.

## See Also
- [[Evals and Observability Interview Study Guide]] <!-- auto-linked -->
- [[Harness Engineering]] <!-- auto-linked -->
- [[Anthropic Three-Tier Eval Taxonomy]] — complements (tiers of eval scope; this page is the anatomy within a tier)
- [[Eval Non-Determinism]] — extends (why one trial is not a measurement)
- [[Eval Suite Maintenance]] — extends (keeping the suite honest over time)
- [[Eval Maturity Ladder]] — complements (what infrastructure exists, stage by stage)
- [[Verification Loops]] — complements (harness-under-test as generator/evaluator separation)
- [[Eval vs Test Distinction]] — prerequisite-for (which behaviors are eval-testable at all)
- [[LLM-as-Judge Evaluation]] — instance-of (one of the three grader types)
