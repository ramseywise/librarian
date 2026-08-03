---
title: Design-Before-Infrastructure Sequencing
tags: [llm, decision]
summary: The decision to make design scoping a standalone skill that runs before the scaffold interview rather than a wrapper around it — because design and build are separate phases that may be months apart, and merging them makes the combined skill unusable for anyone who already designed.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/poc-system-design-interview.md
---

# Design-Before-Infrastructure Sequencing

The architectural decision behind [[Scope-POC Design Interview]] being a separate skill
rather than extra questions bolted onto the scaffold interview.

## The Gap Being Closed

The scaffold interview answers **HOW to build it** — agent framework, vector store,
TypeScript, MCP server. The research doc's core observation is that these *"can't be
answered well until you know"*:

- Who the actors are and what they do
- What the AI is actually doing for them
- What the MVP looks like (demo target)
- What constraints apply (data classification, multi-tenancy, operator model)

> *"Without that upstream conversation, copier choices become guesses."*

The dependency is concrete, not stylistic: the right agent framework depends on whether
the project is retrieval, orchestration, or automation; the right vector backend depends
on managed-cluster vs prototype; the right integration toggles depend on which external
systems exist. Each infrastructure answer has a design answer as its input.

## Sequential, Not Integrated

The rejected alternative was *"extending `/project-genesis` with design questions
prepended."* Four reasons for keeping them separate:

| Reason | What it protects |
|---|---|
| Each skill stays focused | One conversation about design, one about infrastructure |
| Design usable without building | Scoping can run for planning with no copier invocation |
| The handoff is explicit | *"run `/project-genesis` next, here's what to answer"* |
| Phases may be months apart | A DESIGN.md can predate the scaffold by months |

> *"The alternative blurs those phases and makes the skill unwieldy for users who've
> already done the design work."*

The last point is the decisive one. A merged skill is **strictly worse for the
already-designed user**, who must either skip questions or re-answer them — and there is
no version of a prepended-question skill that avoids this.

## The Temporal Argument

The strongest form of the case is that these phases have different *clocks*. For platform
projects, *"`/scope-poc` may produce a DESIGN.md months before the copier scaffold is
run — design and build are different phases."* A single skill would force them into the
same session, which is a scheduling constraint the work does not actually have.

This is the same separation-of-concerns logic that keeps
[[Deployment Topology Ladder]] selection in the design conversation while the
`deployment_target` parameter lives in the scaffold one.

## Graceful Degradation

Sequencing is a recommendation, not a hard gate. If the scaffold runs without the design
step, *"the stub ships blank with clear placeholders — better than nothing, since it forces
the conversation to happen explicitly rather than implicitly."*

The blank-with-placeholders artifact does work that no artifact would not: it makes the
skipped conversation **visible** rather than merely absent.

## See Also
- [[Scope-POC Design Interview]] — extends (the skill this sequencing decision produced)
- [[DESIGN.md Artifact]] — part-of (the artifact the design phase hands forward)
- [[Project Discovery Conversation]] — prerequisite-for
- [[Asked vs Derived Scaffold Variables]] — complements (the HOW conversation this precedes)
- [[Deployment Topology Ladder]] — related (topology chosen in design, parameterized in scaffold)
