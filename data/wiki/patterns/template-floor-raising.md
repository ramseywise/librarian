---
title: Template Floor Raising
tags: [infra, pattern]
summary: Prioritizing scaffold work by cross-portfolio gap frequency rather than by any single project's needs — the template's job is to make the weakness every existing repo shares impossible to inherit, so new projects start above the portfolio's floor.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/template-pillar-gaps.md
---

# Template Floor Raising

The stated goal of auditing a scaffold: *"identify what the template should add so that new
projects start above the weaknesses found across the existing portfolio."*

This is a specific and non-obvious prioritization rule. A scaffold backlog can be ordered by
what the newest consumer asked for, by what the template author finds interesting, or by
what is cheapest. Floor raising orders it by **how many existing repos already failed at
it** — the gap that is universal is the one the scaffold is uniquely positioned to close,
because a scaffold is the only artifact that touches every future project before its first
line is written.

---

## The two-sided matrix

The method requires two independent assessments, then intersects them:

1. A **portfolio assessment** — score every existing repo against the same rubric
   ([[Six-Pillar Agent Engineering Assessment]]) and extract the gaps that recur.
2. A **template assessment** — score the scaffold against that same rubric.

The intersection is the actionable list:

| Universal portfolio gap | Template scaffolds it? | Priority |
|---|---|---|
| No prompt versioning | Partial — Python has `PROMPT_VERSION`; TS does not | P1 |
| No observability spans | Partial — LangSmith tracing, no OTel spans | P1 |
| No token budget management | No | P1 |
| No prompt injection defense | Minimal — regex only | P2 |
| No continuous eval | No — point-in-time only | P2 |

The cells that matter are the ones where the portfolio gap is universal *and* the template
does not close it — those are gaps the scaffold is actively **propagating**. A universal gap
the template already closes needs no work; a template gap no project ever hit is
speculative.

The `Partial` cells are where floor raising earns its keep. Prompt versioning being present
in the Python scaffold and absent in the TypeScript one is invisible from either assessment
alone: the template author sees "we have prompt versioning," the portfolio shows repos
without it, and only the intersection reveals the asymmetry between two language paths of
the same scaffold. This is the same three-classification discipline as a
[[Capability Parity Audit]] — collapsing `partial` into `have` or `gap` loses the finding.

## Impact is measured in repos, not in features

Every backlog row carries its portfolio count as the impact justification:

| Item | Impact |
|---|---|
| Verification loop wrapper | *"4/5 repos lack this; template can set the pattern"* |
| Token budget utility | *"universal gap, template can enforce counting from day 1"* |
| OTel span scaffold | *"0/5 repos have spans; template wiring removes the activation energy"* |
| Fan-out/fan-in template | *"most common multi-agent pattern, no repo has it"* |

*"Removes the activation energy"* is the load-bearing phrase. The claim is not that the
projects couldn't add OTel spans — it is that zero out of five did, which is evidence that
the cost is not the code but the decision to start. A scaffold converts an opt-in decision
into a default, and that is the entire mechanism by which it raises a floor.

The counterpart appears at the bottom of the same ranked backlog: *"Few-shot example
directory"* is **Must**-tier and still ranked last, with impact *"Low — structural, but all
repos skip few-shot anyway."* A Must-tier requirement whose absence never hurt anyone
outranks nothing. Tier measures how fundamental a requirement is in the rubric; portfolio
frequency measures whether it binds in practice, and the backlog is sorted by the second.

## Defaults over opt-ins

Two recommendations in the audit are not "build something" but "stop making it optional":

> *"Make the LangGraph checkpointer a default scaffold (not opt-in skill) — durable state is
> foundational for any loop beyond toy."*

> *"The HITL and persistence skills are strong but opt-in; consider making persistence
> default."*

A capability that exists as an opt-in skill scores as `partial` and behaves as `gap`. Under
floor raising, the fix for a strong-but-unused capability is a **default change**, not new
code — the cheapest possible way to move a portfolio-wide number. See
[[Copier Re-Entry as Capability Path]] for the opposite direction: capabilities deliberately
left opt-in because they can be added after render.

## Logging-only counts as closing the gap

The context-budget recommendation lowers its own bar explicitly:

> *"Even a logging-only version would surface the data needed to optimize."*

Floor raising does not require the scaffold to solve the problem — it requires the scaffold
to make the problem visible in every project by default. A token counter that only logs
turns a universal blind spot into a universal dataset, which is a precondition for anyone
optimizing anything. The same logic sits behind the proposed `HARNESS_CHECKLIST.md`:
*"a 5-item checklist that new projects can audit against. Lightweight, high signal."* A
checklist scaffolds no behavior at all; it scaffolds the audit.

## See Also
- [[Six-Pillar Agent Engineering Assessment]] — prerequisite-for (the rubric both assessments run against)
- [[Capability Parity Audit]] — alternative-to (prioritize by consumer requests rather than portfolio weakness)
- [[AI Project Template Scaffold]] — instance-of (the scaffold whose backlog this method sets)
- [[Copier Re-Entry as Capability Path]] — contradicts (the case for keeping capabilities opt-in)
- [[Copier Upstream Update Workflow]] — related (how a raised floor reaches already-generated repos)
- [[Complexity Floor]] — related (a floor on project ambition rather than on scaffold quality)
- [[Eval Ladder]] — related (maturity progression the floor is meant to advance)
