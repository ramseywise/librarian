---
title: AI Engineering Field Question Bank
tags: [interview, reference]
summary: A questions-only bank of ~560 candidate-reported AI-engineering interview questions used for cold recall, plus the round guidance that travels with it — production thinking over theory in the technical round, decisions-not-tool-names in deep dives, how AI system design differs from classic ML design, and which take-home asks are red flags.
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--question-bank.md
  - data/raw/repos/sisyphus/interviewing--README.md
---

# AI Engineering Field Question Bank

A public, community-compiled bank of roughly 560 AI-engineering interview questions as
reported by candidates, imported into the interview-prep repo with per-question attribution
stripped. It is **questions only, no answers**, and that is the point: the use is cold recall —
pick a section, answer out loud, then check against the matching study guide or round guide.
It complements the answer-sketch guides rather than replacing them (medium confidence:
reported questions, not verified loops).

## Shape of the bank

| Section | Subsections | Rehearse against |
|---|---|---|
| Technical | LLM fundamentals, RAG, agents and tool use, fine-tuning, evaluation, ML fundamentals, Python/SWE, infra/MLOps, cost and latency, safety | the pillar guides ([[LLM Fundamentals Interview Study Guide]], [[RAG Interview Study Guide]], [[Agents Interview Study Guide]], [[Evals and Observability Interview Study Guide]], …) |
| System design | AI system design, traditional system design, troubleshooting | [[System Design Interview Study Guide]] |
| Coding | algorithm style, lab-specific practicals, ML/AI coding, data processing | [[Coding Challenge Interview Study Guide]], [[Drill Gym Tracks and Schema]] |
| Behavioral | deep dives, conflict, leadership, technical decisions, failure, AI-specific, motivation, AI-conducted follow-ups | [[Behavioral Interview Study Guide]], [[Project Deep-Dive Interview Study Guide]] |
| Take-homes | RAG/chatbot, agent, multi-agent, LLM-as-judge, document extraction, voice, full-stack, performance | [[AI-Assisted Take-Home Playbook]] |

The most-reported prompt across employers is a variant of "design a RAG system for a support
chatbot — and how do you evaluate it?"; the evaluation half is where most answers are thin.

## Round guidance that ships with the bank

**Technical/theory.** Interviewers weigh how you build, evaluate and operate systems over
transformer internals. Prepare an end-to-end RAG pipeline, the full agent architecture
(planning, tools, memory, termination — and *when not to use an agent*), and how you build a
golden dataset. Recurring misses: describing a build without its evaluation or monitoring;
knowing what a technique is but not when to use it; prototype thinking that ignores cost,
latency and failure modes.

**Project deep dive.** What is being read is seniority: did you drive decisions or execute
someone else's plan, find problems proactively, influence others? Narrate business problem →
approach → key decisions (with rejected alternatives) → what went wrong → measured outcome.
The *why* of each decision is the payload — "we chose a relational store because the
reporting layer needed joins and write volume was low" shows judgement where "we used
Postgres" does not. Frame on impact, not tool names. Misses: monologuing, tool-name lists,
no depth when probed, a project where you were not the decision-maker.

**AI system design.** Mostly a senior round; at mid-level a sound high-level architecture
suffices. The shift from classic ML design: the hard part moved from training to
orchestrating pre-trained models.

| | Classic ML design | AI/LLM system design |
|---|---|---|
| Data focus | training data, features | context engineering, chunking, retrieval quality |
| Output | structured scores/classes | open-ended text, code, images |
| Determinism | mostly deterministic | non-deterministic by default |
| Evaluation | held-out precision/recall/AUC | LLM-as-judge, human eval, task evals |
| Cost model | periodic training + serving | continuous per-token inference + retrieval |
| Failure modes | drift, training–serving skew | hallucination, injection, context overflow, cost blowup |
| Iteration | retrain | change prompt or retrieval |

Five-step answer arc: framing (5–10 min) → architecture (10–15) → deep dive on RAG/tools/
memory/eval/safety (20–30) → trade-offs, detection and degradation (10–15) → summary, risks,
next iteration. Most questions reduce to four patterns: RAG, feedback loops, hallucination
mitigation, and cost/scale (multi-layer caching, model tiering, prompt compression). Misses
include treating the LLM as a source of truth, happy-path-only designs, putting control flow
in prompts instead of the orchestrator, and choosing agents because they are exciting (what
the interviewer is scoring: [[AI System Design Interviewer Rubric]]).
Public engineering write-ups that inform these prompts include a directed graph of
specialised support agents, an internal LLM gateway with PII redaction, stateless RAG with
models in an isolated VPC, and an orchestrator/sub-agent research system spending ~15× the
tokens of chat.

**Behavioral.** Map each published company value to 2–3 STAR stories; misses are generic
answers without numbers, one story reused across rounds, and bluffing.

## Take-home red flags

Candidates report as unreasonable: a 72-hour "first round" demanding RAG + agents + UI; a
multi-year financial-report analysis agent on freemium APIs only ("an unpaid mini-consulting
project"); three complex tasks in 45 minutes. Scope like this is a signal about the employer,
not a bar to clear — see [[Timebox-Scaled Deliverable Bar]] and the fuller field data in
[[AI Engineering Take-Home Landscape]].

## See Also
- [[AI Role Interview Loop Map]] — extends (which rounds a loop runs; this bank supplies their questions)
- [[Graded Rehearsal Drill Harness]] — prerequisite-for (the recall loop these questions feed)
- [[Durable vs Performative Knowledge Split]] — extends (questions span both sides of the split)
- [[System Design Interview Study Guide]] — related
