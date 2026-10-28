---
title: Pipeline-Absorbed Skills
tags: [patterns, llm, pattern]
summary: "A well-written skill can get zero invocations because a dominant skill pipeline intercepts the user's upstream intent, and free-text requests are either absorbed by that pipeline or answered inline. When two description rewrites change nothing, the cause is structural: wire the skill into the pipeline's footers and merge any hidden prerequisite chain."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-3-design-skill-trio.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-3-design-skill-trio.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-19-skills-layer-audit.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-19-skills-layer-audit.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-22-workflow-simplification.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-22-workflow-simplification.md
---

# Pipeline-Absorbed Skills

From a guacamayo investigation into four global "design" skills (design sprint,
initiative backlog, milestones, prototype spike). All four were well scoped. They had
**zero invocations across 139 sessions**, and still zero across 222 after two rounds of
description rewrites.

## Diagnosis: the description was never the problem

The retro first called it a description-quality problem, so the descriptions were
rewritten twice with role framing and natural trigger phrases. Neither rewrite moved
the count. A structural reading did:

- **A dominant pipeline intercepts the intent.** Users ran research → plan → execute,
  a loop that is tight and well reinforced. "I want to plan a new feature" lands on the
  plan skill, which is not wrong. The initiative-backlog skill's output overlapped the
  plan's Steps list, and the milestones skill overlapped the plan's phases. Anyone who
  finished a plan felt no need for either.
- **The parallel pipeline is invisible.** The design chain (sprint → milestones →
  initiative) was a second pipeline beside the main one. Neither main-pipeline skill's
  "next step" footer mentioned it, so users never switched to it.
- **A hidden mandatory prerequisite.** The initiative skill required the milestones
  skill's output as input. That was a two-step chain users had to know about and choose
  to enter.
- **A name mismatch.** One skill's frontmatter `name:` differed from its body header
  and from every cross-reference to it, so the command users saw in footers was not the
  one that dispatched. That is a discoverability bug independent of the description.

A co-factor: a same-week skills audit listed two of the four skills as carrying
`disable-model-invocation`. That flag removes a skill's description from the model's
context entirely, so free text could not have triggered those two however their
descriptions were worded.

A five-prompt trigger test made the mechanism concrete. **These skills fired reliably
only on an explicit slash command.** Free-text versions of the same intent were taken
by the main pipeline or answered inline by the model.

## The fix order

1. Fix the name bug. It is one line, and it is a defect, not a design choice.
2. **Merge the prerequisite chain.** If skill B always needs skill A's output, they
   are one skill split across two files. Consolidate them (4 → 3 skills, the
   milestones step becoming a pre-step of the initiative skill).
3. **Wire into the dominant pipeline's footers at the right moment.** The research
   footer points to the design sprint only for blank-page problem framing. The plan
   footer points to the initiative skill only once an initiative is agreed.
4. **Set a revisit trigger.** If there are still no invocations after 15 sessions,
   move the tool-specific skills to repo-local rather than loading them in every
   session globally.

Renaming for discoverability and A/B-testing descriptions were both rejected: if the
cause is structural, they fail the same way. Retiring the skills was rejected too, since
they were correct and the problem was reachability. The ledger kept the description
rewrite as an explicitly **failed** hypothesis rather than quietly dropping it.


## Remedy instance: absorb the orphan, split by moment

A later simplification applied the remedy directly. A standalone code-PR skill with only
**2 invocations ever** was folded into the pipeline's review phase. The pipeline-native
phase name won over the standalone name. The two review skills that remained were split by
**moment** rather than by topic: `/code-review` is pre-push, and `workflow-review` is
post-PR. The same pass made the retro a *nudge*: the dream skill flags when the retro is
≥7 days overdue instead of automating it.

## See Also
- [[Skill Discovery Failure Modes]] — extends (a structural cause that no description tuning fixes)
- [[Retro Open-Hypotheses Loop]] — related (the rewrite recorded as a failed ledger hypothesis)
- [[Capability vs Phase Skills]] — related (phase pipelines absorbing capability skills)
- [[Skill Admission Test: Workflow With a Gate]] — related (whether a skill should exist at all)
