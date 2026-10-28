---
title: When a Lens Earns Agenthood
tags: [llm, pattern]
summary: A reviewing lens becomes a separate agent only for Isolation (it must be denied something the caller knows) or Parallelism (N instances run at once); otherwise it is a section of a skill — "a job title is not a lens", and the failure modes are the under-loaded committee and the duplicate lens.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/agents/review.md
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
  - data/raw/claude-docs/galactus/agents/fog-advisor.md
  - data/raw/claude-docs/galactus/agents/research-scout.md
  - data/raw/claude-docs/galactus/agents/review.md
  - data/raw/claude-docs/guacamayo/agents/review.md
  - data/raw/claude-docs/galactus/docs/specs/2026-08-09-prototyping-review-subsystem.md
---

# When a Lens Earns Agenthood

Every multi-agent design eventually asks whether the next perspective should be a new
agent or a new paragraph. `decide-shared` gives a two-item test and a one-line check.

## Only two reasons

| Reason | What it buys | Example |
|---|---|---|
| **Isolation** | The agent is *denied* something the caller knows, so its agreement is evidence | `fog-advisor` never sees the author's justification — [[Rationale-Blind Worst-Case Review]] |
| **Parallelism** | N instances run at once over disjoint inputs | `research-scout`, one angle per scout; the generic `review` agent dispatched once per dimension skill |

The check: **name what this agent is denied, or what it runs N of. If neither, it is a
section.** "The security reviewer", "the product lens", "the sceptic" are job titles. A
job title with the same inputs as the caller and no fan-out adds a dispatch, a context
copy and a merge step, and returns a restatement.

## Why isolation is attention, not specialty

The prototyping review spec grounds this explicitly: dimension isolation is justified by
**attention isolation**, not by the reviewers having different expertise. A single prompt
covering seven checklists competes with itself for attention and silently prioritises
whichever came first; splitting gives each checklist a full context budget. The model is
the same haiku-tier model in every dispatch. See
[[Parallel Dimension Scanner Architecture]].

The galactus variant takes this to its conclusion: there is **one** generic `review` agent
definition (haiku, read-only, preloads `review-shared`), dispatched N times, each dispatch
loading exactly one `review-*` dimension skill. The agent carries no dimension knowledge;
the skill does. A finding whose id prefix does not match the dimension it was dispatched
for is rejected by `review/validate.py` as a **skill-load failure** — distinguishable from
an honest empty result (`[]`), which must stay legitimate.

## Two failure modes

- **The committee** — several under-loaded reviewers, each with a thin checklist and the
  same context. Costs N dispatches, finds what one would have found.
- **The duplicate lens** — two agents or skills with the same job verb over the same input
  (see [[Job Verb Taxonomy for Skills]]). They corroborate each other by construction, which
  looks like evidence and is not.

## Corollary: skills orchestrate agents, never the reverse

An agent may *preload* a shared contract skill (loading is not calling —
[[Skill Preloading via Agent Definition]]). But an agent that *dispatches* a skill has
pulled the caller's reasoning back into the isolated party, and the corroboration argument
collapses: parties can only corroborate when they could not see each other.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends (the Parallelism case, grounded)
- [[Rationale-Blind Worst-Case Review]] — instance-of (the Isolation case)
- [[Multi-Agent Role Specialization]] — contradicts (role titles as the unit of decomposition)
- [[Skill Preloading via Agent Definition]] — prerequisite-for
- [[Job Verb Taxonomy for Skills]] — extends
- [[Capability vs Phase Skills]] — extends
- [[Cross-Dimensional Review Adjudicator]] — prerequisite-for
- [[Cumulative Metric Hides the Fix]] — related (declining to invent delegation to hit an issue's workflow headcount)
