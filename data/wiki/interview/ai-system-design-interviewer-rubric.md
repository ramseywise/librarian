---
title: AI System Design Interviewer Rubric
tags: [interview, eval, reference]
summary: "How an applied-AI system design round is scored from the interviewer's side — eleven rubric dimensions with strong/weak evidence, five vague phrases that always draw a 'which mechanism?' probe, an eleven-phase flow with one adaptive follow-up per answer, a seniority bar, and three personas that change tone but never the rubric — usable as a mock-round script."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--interviewer-personas.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--README.md
---

# AI System Design Interviewer Rubric

[[System Design Interview Study Guide]] is the candidate's method and
[[System Design Scored Behaviors]] the in-room habits. This page is the other side of the
table: what an interviewer for an *applied AI engineering* design round listens for. The
round is neither generic backend design nor ML research. The question it tests is whether
you can take an ambiguous AI product problem and design a reliable, safe, observable,
cost-aware production system around it.

The source is a condensed third-party interviewer prompt pack, and its main use is
running **mock rounds**. An agent or a friend takes the rubric plus the flow, adds one
persona, and fills a session config: level (junior to staff), duration (30/45/60 min), a
topic, a feedback mode (end only, midpoint and end, or coaching after each section), and
optional constraints such as private documents, human approval before external actions,
a regulated domain, or multilingual users.

## The eleven dimensions

| # | Dimension | Strong evidence | Red flag |
|---|---|---|---|
| 1 | Product and task framing | user workflow, v1 scope, what stays human, high-risk actions named | "use GPT" before clarifying; nothing on refusal or escalation |
| 2 | Success metrics and launch criteria | product metrics kept apart from AI quality; offline vs online; **no-launch thresholds** | "accuracy" alone; no launch bar |
| 3 | System architecture | request flow *and* ingestion flow; where state lives; sync vs async; retries, fallback, rollback | "LLM + vector DB"; the model is the whole system |
| 4 | Model and AI approach | simplest first; **knows when not to use an LLM or agent**; deterministic code for deterministic work; output validation | biggest model always; agents for simple flows; fine-tuning where retrieval fits |
| 5 | Context and retrieval | permission-filtered retrieval; retrieval evaluated apart from generation; stale and conflicting docs handled | "put docs in a vector DB" and stop; no ACLs |
| 6 | Agent and tool design | exact tool list, typed schemas, low- vs high-risk split, policy check before execution, stop conditions | "the agent decides"; unrestricted tools |
| 7 | Evaluation and testing | regression gate before any prompt, model or index change; hallucination, refusal and injection tests; knows LLM-judge limits | "test it manually"; user ratings only |
| 8 | Production readiness | p95/p99 named; cost per task; provider failover; **versions prompt, model, retrieval config and index**; rollback | uptime-only monitoring; no versioning |
| 9 | Safety, security, privacy | authorization *before* retrieval and tool calls; model output treated as untrusted; PII-safe logging | retrieved docs bypass permissions; careless prompt logging |
| 10 | Trade-off reasoning | compares alternatives, says what is deferred, names the riskiest assumption, **revises when challenged** | one "obviously correct" answer |
| 11 | Communication and ownership | structured, assumptions stated, concrete mechanisms, clean summary | buzzwords; too model-centric *or* too infra-centric |

Dimension 8's versioning list is the one candidates most often skip: a retrieval-config or
index change can regress quality as surely as a prompt change, so all four need a version
and a rollback.

## Five phrases that always draw a probe

The interviewer is told not to accept these without a mechanism:

- **"Use RAG"**: what is indexed, how it is chunked, what the permissions are, how retrieval is evaluated.
- **"Use an agent"**: which tools, what state, what policy, what happens on failure.
- **"Monitor it"**: which metrics, which alerts.
- **"Human in the loop"**: when, why, and how.
- **Any buzzword**: give the concrete mechanism.

The practical use is to pre-empt them: every time you say one of these, attach the
mechanism in the same sentence. That is [[System Design Scored Behaviors]]'s "justify every
box" rule seen from the grader's side.

## Flow and adaptive follow-up

Eleven phases: opening (a vague prompt) → clarification (answered realistically, never
over-specified) → metrics and launch criteria → high-level architecture → AI approach →
context and data → tools and agents (if relevant) → evaluation → production → safety and
privacy → wrap-up (summary, riskiest assumption, v1, future work).

After each answer the interviewer silently classifies it (strong, missing detail, too
vague, too model-centric, too infra-centric, unsafe, over-engineered, under-scoped, not
production-ready, stuck, off-topic) and picks **one** move: ask for a mechanism, a flow,
metrics, safety, cost or latency, eval, a fallback, an alternative, a simplification, or
move on. One short question at a time; the ideal answer is never revealed mid-round.
Applied judgment counts for more than ML theory.

Topic briefs work the same way: each prompt carries three or four hidden constraints
(ACL-preserving retrieval, approval before commits, PHI audit, label delay) that are handed
over **only when the candidate asks the question that uncovers them**. Clarification is
therefore directly scored, because unasked constraints stay hidden and the design misses
them. Nine of the sixteen briefs have full walkthroughs in [[AI System Design Walkthroughs]].

## Seniority bar

| Level | Bar |
|---|---|
| Junior | basic LLM/RAG, simple architecture, basic eval, aware of hallucination, falls back to a human |
| Mid | owns a feature end to end; practical eval; latency and cost trade-offs; debugging mindset |
| Senior | strong decomposition, careful approach choice, production realism, eval design, safety, **prioritization** |
| Staff | platform thinking, reusable eval infrastructure, cross-team interfaces, governance, incident planning, data feedback loops |

## Three personas: tone changes, rubric does not

| | Supportive coach | Neutral evaluator | Adversarial challenger |
|---|---|---|---|
| Pressure | low | medium | high |
| Interrupts | rarely | for pacing | whenever you are vague or dodging |
| Hints | a five-rung ladder: restate simpler → name the dimension → offer two directions → small example → hand control back | minimal, only when blocked | rare and narrow, only after you have reasoned |
| Feedback order | strengths first | evidence-based "met the bar on… / missing area was…" | biggest gap first |

- The **coach** never completes the design or praises a weak answer. Its over-engineering probe is "what would you build in the first four weeks?"
- The **neutral evaluator** lets silence sit and redirects early depth with "hold that, high-level first".
- The **adversarial challenger** attacks premises ("why does this need an LLM at all?"), interrupts vague terms ("you said guardrails: which ones, where?"), and runs stress tests: provider down, stale index, 20× traffic, a prompt change that regresses quality, token cost doubling overnight, a tool call that partially succeeds, a user asking for another customer's data. It stays fair: it doesn't change the problem midway, nitpick, or penalize not knowing a vendor when the design is sound, and it stops pushing once the answer is reasonable. What it tests is calm, admitted uncertainty, and visibly revising the weak part.

## Feedback template

Feedback is grounded only in what was said: overall assessment, strongest and weakest
signals, missed AI-engineering considerations, 1–5 scores per dimension, a seniority signal,
pass/no-pass for the configured level, one concrete practice recommendation, and **one
answer rewritten** the way it could have been stronger. The rewritten answer is the
most useful item for the next drill.

## See Also
- [[System Design Interview Study Guide]] — extends (the grader's view of the five-step method)
- [[System Design Scored Behaviors]] — extends (the same behaviours as rubric dimensions)
- [[AI System Design Walkthroughs]] — prerequisite-for (the topic pool the rubric is run against)
- [[Graded Rehearsal Drill Harness]] — instance-of (persona plus rubric is a drill configuration)
- [[Security and Safety Interview Study Guide]] — extends (dimension 9)
- [[Evals and Observability Interview Study Guide]] — extends (dimension 7)
- [[Agents Interview Study Guide]] — related
