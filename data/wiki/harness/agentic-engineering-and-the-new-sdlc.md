---
title: Agentic Engineering and the New SDLC
tags: [llm, agents, infra, concept]
summary: "The vibe-coding-to-agentic-engineering stakes spectrum, how each SDLC phase shifts when agents do the implementation, the conductor/orchestrator role split, the 80% problem, and the TCO argument for investing in the harness."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--agents-google-adk.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--agents-google-adk.md
  - data/raw/papers/2026-11-06-agarwal-2026-ai-ides-or-autonomous-agents.md
  - data/raw/papers/2026-11-06-huang-2025-professional-software-developers-don-t.md
---

# Agentic Engineering and the New SDLC

Vibe coding — natural language as the primary programming interface — and agentic
engineering are not competing methods. They are **two ends of one spectrum**, and the
choice between them is a function of stakes.

A weekend prototype can be pure vibe coding. A production API handling financial
transactions demands agentic engineering. Most real work sits in between, and the skill
being asked for is **knowing where to draw the line for each task** — not picking a side
once and applying it everywhere.

## Testing versus evaluation

The split that makes the spectrum operable:

| | Verifies | Question |
|---|---|---|
| **Tests** | The deterministic parts | Does this function, given this input, produce that output? |
| **Evals** | The non-deterministic parts | Did the agent take the right trajectory, choose the right tools, and meet the quality bar? |

Both are needed, and confusing them is a common failure — see
[[Eval vs Test Distinction]]. What is specific to the SDLC framing is that
**testing becomes the primary way to communicate intent to an agent**: a well-defined eval
suite specifies the target more precisely than a natural-language prompt can, which is the
same argument [[Specification by Example]] makes for human collaborators.

That splits evaluation in two: **output evaluation** (is the final code correct?) and
**trajectory evaluation** (were the reasoning steps sound?). A run can pass the first and
fail the second — the agent arrived at working code by skipping a verification step or
reaching for an insecure method. Only trajectory evaluation catches that.

## Six types of context

Context engineering, in this framing, is supplying an agent with structured information
about the codebase, architecture, conventions, and intent. Six primary types:

| Type | Content |
|---|---|
| **Instructions** | The agent's role, goals, operational boundaries |
| **Knowledge** | Retrieved documents, architecture diagrams, domain data |
| **Memory** | Short-term session logs; long-term persistent project state |
| **Examples** | Few-shot behavioral demonstrations, codebase reference patterns |
| **Tools** | Precise definitions of the APIs, scripts, and services available |
| **Guardrails** | Hard constraints, formatting rules, safety validations |

The load-bearing distinction is **static versus dynamic** context. Static context is
always loaded; dynamic context is loaded on demand, and managing it is what
[[SKILL.md Pattern]]-style skills exist to do. See [[Context Engineering]] for the
assembly discipline and [[Why Context Is Finite]] for why the static/dynamic split is
forced rather than stylistic.

## Phase-by-phase transformation

| Phase | What changes |
|---|---|
| **Requirements & planning** | Interactive AI conversations generate user stories, API schemas, and working prototypes simultaneously — feedback loops collapse |
| **Design & architecture** | Humans still make the trade-off calls; AI scaffolds applications and enforces conventions once the structural path is set |
| **Implementation** | Shifts from *writing* to *reviewing and guiding* — agents produce multi-file features, developers verify and debug |
| **Testing & QA** | Tests become the intent-communication channel; evaluation splits into output and trajectory |
| **Code review & deployment** | AI as first-pass reviewer for security and style; pipelines become AI-aware, monitoring health and triggering rollbacks |
| **Maintenance & evolution** | Legacy codebases become accessible — agents read impenetrable patterns, automate framework migrations and deprecated-API updates |

> What remains constant is **human judgment, taste, and the skill to verify AI output** as
> machines take on more of the implementation.

Note the direction of travel: the human work does not disappear, it moves *upstream* into
specification and *downstream* into verification, and thins out in the middle. That is the
same relocation the conductor/orchestrator split describes below.

## Conductor versus orchestrator

Two modes of working with agents, distinguished by synchrony:

**The conductor** — hands-on, real-time direction. Correct for complex logic, tricky
debugging, and unfamiliar codebases, where the developer needs to understand each change
as it is made.

**The orchestrator** — async, multi-agent delegation. Correct for well-defined tasks: bug
fixes, feature implementation against established patterns, codebase migrations, test
generation.

The orchestrator mode demands a different skill set:

- **Specification** — defining tasks precisely enough to execute without ambiguity
- **Decomposition** — breaking work into agent-sized units
- **Evaluation** — quickly judging whether output meets the bar
- **System design** — designing the constraints, tests, and feedback loops that keep agents productive

Three of those four are harness-building activities. The practical reading is that
**you cannot orchestrate without a harness** — async delegation with no acceptance
baseline and no feedback signal is just unsupervised generation. See
[[Harness Engineering]] and [[Harness Orchestration]].

## The 80% problem

Agents rapidly generate roughly **80% of the code** for a feature. The remaining 20% —
**edge cases, error handling, integration points, and subtle correctness requirements** —
demands deep contextual knowledge current models often lack.

The distribution matters more than the number. The residual is not a random 20% of the
work; it is concentrated in exactly the parts that determine whether the feature survives
production. Time saved on the 80% is real, but it does not shorten the tail, and planning
that assumes uniform speedup will underestimate the remainder badly.

## Navigating it

- **Define specs early** — treat specifications as the contract with the agent
- **Monitor the trajectory** — not just whether the code works, but how it got there
- **Design the factory, not the code** — move from implementor to factory manager, building
  the guardrails, tests, and context that produce the code
- **Beware the 80% problem** — budget for the tail
- **Use skills** — portable instructions loaded only when a task requires them, to control
  cost and avoid context rot
- **Invest in the harness** — most agent failures are configuration failures; improve tools,
  prompts, and guardrails before blaming the model

That last point is [[Harness Engineering]]'s "skill issue" reframe arrived at from the
process side rather than the debugging side.

## The economics

The argument for agentic engineering over vibe coding at high stakes is a **total cost of
ownership** argument, splitting operational burden into:

- **CapEx** — the upfront investment to build something
- **OpEx** — the ongoing cost to run, fix, and maintain it

Vibe coding minimizes CapEx. Agentic engineering spends more upfront on specs, evals,
guardrails, and harness, and buys down OpEx. Which is correct depends entirely on how long
the artifact lives and what it costs when it breaks — which is why the stakes spectrum, not
a methodology preference, is the right frame for the decision.

## Measured effects of coding agents on repositories and on developers (2025-2026 preprints, self-reported)

- **Repository study (Agarwal, He and Vasilescu, MSR 2026 short paper):** staggered difference-in-differences with propensity-matched controls on open-source GitHub repositories with at least 10 stars and 10 agentic pull requests, monthly panel, intent-to-treat. For 401 repositories whose first observable AI tool was an agent, commits rose 36.25% and lines added 76.59%; for 117 repositories that already used an AI IDE, commits rose 3.06% and lines added fell 6.34%, neither significant. The agent-first gain was front-loaded (about +111% commits at the adoption month) and stayed above baseline through month 6, while the IDE-first bump turned negative by month 6.
- **Quality side (same study):** static-analysis warnings rose 17.73% (agent-first) and 19.00% (IDE-first, not significant), and cognitive complexity rose 34.85% and 42.87%, both significant. Duplication changes were small and not significant. The authors read this as agent-induced complexity debt; that reading, and their prescriptions (complexity-aware review, routine refactoring, tests), are not tested.
- **Developer study (Huang et al., preprint):** 13 experienced developers observed for one 45-minute session each, plus a survey of 99 respondents out of 249 replies. Nine of 13 reviewed every change; the median was 1.8 plan steps executed per prompt; eight of 13 said the agent did more than asked. In survey mentions, following a well-defined plan was judged suitable 28 to 2, writing tests 19 to 2, while generating code in one shot with no edits or checks was 5 to 23. No respondent called agents suitable for fully autonomous operation. All figures are hand-coded counts, and no agent accuracy was measured.

## Limits

- Agarwal et al. concede some significant pre-treatment coefficients for warnings and complexity, intent-to-treat estimates that cannot measure usage intensity, attribution errors that probably attenuate effects, a small IDE-first sample (so the IDE-first warnings result is weak), non-random assignment between the two groups, and a single 6-month horizon. They treat "agent" as a bundle of about 12 tools. Internal inconsistency: the adoption window is May to July 2025 in the Figure 1 caption but April to June in the body.
- Huang et al.: the survey sample was recruited from AI-tool repositories (6% response, about 97 of 99 male), the observation sample is small, themes were hand-coded without inter-rater reliability, and the authors concede agents have improved since 2025. Nothing in the study demonstrates better outcomes from keeping control or reviewing.

## See Also
- [[Task Decomposition Patterns]] <!-- auto-linked -->
- [[Multi-Agent Role Specialization]] <!-- auto-linked -->
- [[Harness Engineering]] — prerequisite-for (the machinery this SDLC presumes)
- [[Context Engineering]] — prerequisite-for (the six context types, as a discipline)
- [[Eval vs Test Distinction]] — prerequisite-for (tests vs evals, stated precisely)
- [[Specification by Example]] — related (specs as the contract, for humans and agents alike)
- [[Harness Orchestration]] — extends (the orchestrator mode, mechanically)
- [[SKILL.md Pattern]] — instance-of (dynamic context loaded on demand)
- [[Git Branch Triage]] — related (branch hygiene when agents leave in-flight work behind)
- [[TypeScript any Escapes]] — related (lint rules that are correctness gates, not style)
