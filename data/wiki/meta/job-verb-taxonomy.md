---
title: Job Verb Taxonomy for Skills
tags: [meta, reference]
summary: Every skill declares exactly one job verb — frame / size / decide / design / derisk / report / run — chosen by what its output changes; two verbs means two skills, and the coverage table records gaps with reasons rather than claiming completeness.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/decide-shared/references/job-verbs.md
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/SKILL.md
---

# Job Verb Taxonomy for Skills

A `job:` line in SKILL.md frontmatter (ignored by the runtime, greppable by humans and
audits) names the one thing the skill does to the work in front of it.

| Verb | Output changes… | Example |
|---|---|---|
| `frame` | what the problem *is* — assumptions surfaced, unknowns mapped | `/assumption-audit`, `/fog` |
| `size` | how big it is — effort, cost, scope boundary | *(gap, recorded)* |
| `decide` | which option is chosen, with tradeoffs on the record | ADR-producing skills |
| `design` | the shape of the solution | `/proto-design` |
| `derisk` | the probability a plan survives contact | `/war-game` |
| `report` | what others know about the state | *(gap, recorded)* |
| `run` | the world — code written, commands executed | `/proto-execute` |

## Rules

- **Exactly one verb.** A skill that frames *and* decides is two skills wearing one name;
  the second verb is where its scope creeps. Split it.
- **Choose by what the output changes**, not by what the skill reads or how it feels to
  run. Two skills with the same verb and the same input are the duplicate-lens failure
  (see [[When a Lens Earns Agenthood]]).
- **Record gaps with reasons.** The coverage table in `decide-shared` lists `size` and
  `report` as uncovered and says why. *"An inventory of gaps with stated reasons is more
  useful than a claim of completeness"* — a reader who needs sizing learns at once that no
  skill does it, rather than discovering it after a `frame` skill produced an estimate it
  was never designed to defend.

## Why bother with a non-functional field

Nothing executes `job:`. Its value is at authoring and audit time: `grep -l "^job: frame"`
answers "which skills might overlap with the one I am about to write?" before the
near-duplicate exists. It is the same discipline as the type tag in this wiki's own
frontmatter — a retrieval axis that costs one line.

## See Also
- [[Capability vs Phase Skills]] — extends
- [[When a Lens Earns Agenthood]] — extends (the duplicate-lens failure the verb check catches)
- [[SKILL.md Pattern]] — extends (one more frontmatter convention)
- [[Claude Workflow System]] — instance-of
- [[Skill Admission Test: Workflow With a Gate]] — related
