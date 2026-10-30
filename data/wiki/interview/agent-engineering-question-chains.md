---
title: Agent Engineering Question Chains
tags: [interview, reference]
summary: "Real AIE technical rounds ask a main question about a concrete system and then push one follow-up that changes a dimension (three tools → after merge; one model → ten models; one customer → many industries and languages); the answer kernels for nine recurring themes, and the move that carries across them: name the layer, pick the cheapest check at that layer, and widen only on a trigger."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--technical-questions--real-tech-question-bank.md
  - data/raw/repos/sisyphus/interviewing--rounds--technical-questions--README.md
---

# Agent Engineering Question Chains

The breadth round's definitional half is covered in [[Technical Breadth Round Playbook]].
Real AIE loops also run a scenario half: the interviewer points at a concrete system (a
model config, an agent with three tools, a RAG product with customers) and asks a **main**
question, then a **follow-up** that changes one dimension. The source bank collects 23
such questions from real loops in nine themes, with answers drafted by research agents from
vendor docs and engineering blogs — rehearse the shape, then replace examples with your own.

## The move that carries across chains

The follow-up almost always multiplies something (models, customers, runs, data volume).
The scoring answer **names the layer the change lives in, puts the cheapest check at that
layer on every change, and runs the expensive check only on a trigger** — a schedule, a
release, or a diff that touches that layer. "Run everything everywhere" and "it depends"
both lose.

## Nine themes, main → follow-up

| Theme | Main question | Follow-up | Answer kernel |
|---|---|---|---|
| Provider-agnostic config | Redesign this config for any provider | A provider-only param breaks another provider | Canonical contract + per-provider adapters + logical-name registry; whitelist/capability flags; drop only cosmetic params, log drops — [[Provider-Agnostic Model Adapter]] |
| Reliability | Make a nondeterministic agent more reliable | Verify this three-tool system after the PR merges | Deterministic scaffolding around a probabilistic core (schemas, code for precision work, bounded retries with error-as-context, checkpoints, fallback, HITL gates). After merge: per-tool unit tests → 20–50-task regression set with multiple trials → trajectory assertions ("X never before Y") → CI gate → 24–48h live sample — see [[Trajectory Over Outcome]] |
| Testing & CI | When should unit tests run? | Ten models from five providers — full suite each? | Test at the layer of the change; fastest layer as often as possible. No full matrix per PR: mock models for harness tests, one cheap model per family on PRs, full matrix nightly or when the adapter layer changes |
| Observability | How would you collect traces? | How would you analyze them? | Trace tree (root per run, child spans per LLM/tool/retrieval call), OpenTelemetry GenAI conventions, a stable metadata contract (run/session id, prompt version, commit, model, tokens). Analysis: rule-based human sampling + calibrated LLM judge on 10–20%, full review 24–48h after any change — [[Online Eval Sampling]] |
| Prompt change management | How to introduce a prompt change? | How to evaluate it before release? / track it over time? | Prompt as a versioned artifact through PR review, pinned model snapshot, progressive rollout. Eval graders in cost order (deterministic → trajectory → judge/human) on the same fixed set; standing regression suite + drift monitoring; debug the eval system before blaming the prompt |
| Repeated-run variance | Reliable results when runs differ? | — | Non-determinism is structural (temperature 0 doesn't guarantee identity). Multiple trials; report pass@k (capability) *and* pass^k (reliability — a 75%-per-trial agent clears 3/3 only ~42% of the time); judge variance stacks on top — [[Eval Non-Determinism]] |
| Tools, skills, workflows | What makes a good tool? When add skills? | Do skills replace a small-tool agent? When skill vs tool vs workflow vs agent? | Tool = ACI contract with "do not use for" negatives and four gates (reversible, idempotent, observable, parallel-safe). Skills earn their cost through progressive disclosure once *combining* tools is the hard part; they sit above tools, never replace them. Order of reach: workflow → tool → skill → separate agent |
| Large data in context | A tool can return a huge payload | — | The tool boundary is a filter, not a pipe: paginate with a continuation marker, return summaries + drill-down ids, isolate exploration in a sub-agent, checkpoint long operations. Return what the agent needs to *decide* |
| Production RAG eval | Customers across industries and languages? "Results are bad" — what first? Build a trusted customer eval set? | Collect explicit/implicit signals → turn them into positive/negative rows | Segment evals per vertical and per language (language mismatch is its own failure mode; start new checks log-only). Triage: pull the original trace, rule out infra/grader bugs, localize retrieval vs extraction vs generation vs stale source. Trusted sets come from real failures, include restraint negatives, version rows with the corpus snapshot. Explicit feedback is 1–3% and skews extreme; implicit signals (rephrase, abandonment, escalation) cover all traffic; cluster before labeling — [[User Feedback Loops]] |

## Recurring answer habits

- **Get the trace before touching the prompt.** "Bad results" is a symptom; every diagnosis
  chain starts from the original trace, not a re-run.
- **Debug the evaluator first.** Timeouts, grader bugs and stale indexes produce regressions
  that aren't real.
- **Every confirmed failure becomes an eval row**, so it can't silently regress.
- **Negatives that test restraint** (should refuse / say "I don't know") stop a system from
  "improving" by answering more confidently.

## See Also
- [[Technical Breadth Round Playbook]] — extends (the scenario half of the same round)
- [[Evals and Observability Interview Study Guide]] — prerequisite-for (domain content behind four of the nine themes)
- [[Agents Interview Study Guide]] — prerequisite-for (tool, skill and workflow content)
- [[Provider-Agnostic Model Adapter]] — extends
- [[Trajectory Over Outcome]] — extends
- [[AI Engineering Field Question Bank]] — extends (questions-only cold-recall bank; this page adds answer kernels)
- [[System Design Interview Study Guide]] — extends
