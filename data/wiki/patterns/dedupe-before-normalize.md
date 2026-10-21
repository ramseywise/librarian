---
title: De-Dupe Before You Normalize
tags: [patterns, llm, pattern]
summary: "Before rolling a new convention across N copies of something, classify each copy as COPY, REPO-SPECIFIC or DIVERGED-COPY. In one audit about 120 skill instances turned out to be six clean repos, one intentional template and two drift sites, so normalizing first would have mostly polished stale duplicates."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-18-skills-refs-evals-norm.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-18-skills-refs-evals-norm.md
---

# De-Dupe Before You Normalize

From a guacamayo plan to give every repo-level Claude Code skill a standard
`references/` and `evals/` layout. The inventory changed the plan before any skill was
touched.

## The trap in the raw count

The sweep found about 120 skill instances across nine repos' `.claude/skills/`
directories. None had `evals/`. The obvious plan was to add evals to 120 skills. But
the dominant signal was **duplication**: global skills had been copied into repos,
against the standing rule that global skills are never copied into a repo. Adding evals
across all 120 would mostly have meant adding them to stale forks of global skills,
which would then drift further with their own tests attached.

## The classification

Diff every repo skill against its global namesake, then label it:

| Label | Meaning | Action |
|---|---|---|
| **COPY** | name and content match a global skill | delete; rely on global |
| **REPO-SPECIFIC** | no global equivalent, or diverged for real repo needs | keep; apply the norm |
| **DIVERGED-COPY** | started as a global copy, then edited | decide: fold the edits upstream and delete the copy, or keep it and document why it is local |

The results were much smaller than the raw count:

- **Six repos were 100% repo-specific.** They needed no de-dupe at all.
- **One intentional template** held identical copies and diverged copies of global
  skills. It is a scaffold, so it is governed by its own vendoring rule, not deleted.
  Its diverged copies are the ones to worry about, because they have already forked
  from global.
- **Two real drift sites.** One was a nested clone whose diffs from global ran to about
  90–120 lines per skill. That made it an *old* fork, not a fresh copy: a stale
  checkout and a candidate for wholesale deletion, once confirmed unwired.

So the job went from "normalize 120 skills" to "fix two drift sites and the template's
forks". That is a smaller and safer first phase.

## Companion rules from the same plan

- **Codify the norm where it loads on demand.** The new eval convention went into
  skill-creator, which is read when a skill is being written. It did not go into
  always-on rules, which would load in every session.
- **Don't turn an unproven norm into an audit check.** Promoting it to a config-audit
  rule was deferred until the classification had held up in practice. An audit rule
  enforces whatever it encodes, including mistakes.
- **Resolve each decision at the phase gate that needs it.** Open decisions were kept in
  one table, each tagged with the phase that blocks on it, rather than all being
  settled up front.

## See Also
- [[The Untested Copy Wins]] — extends (why the diverged copy is the dangerous one)
- [[Capability Parity Audit]] — related (classifying against a template's verified state)
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — prerequisite-for (the eval norm that was being rolled out)
- [[Config Reference Rot]] — related (copies drift from the source they were taken from)
