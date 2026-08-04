---
title: Manual Review as Eval Bootstrap
tags: [eval, planning]
summary: Human eyeballs on 10–20 real queries as the deliberate first eval rung — zero setup, doesn't scale, and valuable precisely because its failure patterns become the criteria every automated approach above it needs.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
---

# Manual Review as Eval Bootstrap

A human — domain expert, program manager, or the volunteer team — reviews outputs and
judges quality. No automation, no infrastructure. Its role is **bootstrapping**: it
produces the criteria that automated evaluation needs and cannot invent.

**Use when** you're in early prototype phase (under ~2 weeks); still figuring out what
"good" looks like; evaluation criteria aren't defined yet; or preparing a demo.

**Avoid when** past prototype phase (doesn't scale); you need repeatable measurement; or
you're making ship/no-ship calls — too subjective without criteria.

## The procedure

1. Use the system for 10–20 real queries.
2. For each response note: correct? helpful? **would you show this to the nonprofit?**
3. Identify patterns in the failures.
4. Turn those patterns into automated criteria — golden QA pairs, or judge rubric items.

Step 3 is the actual deliverable. The reviewing is a means of discovering *what to
measure*; a manual pass that ends at "seems fine" has produced nothing transferable.

## Complexity

**Weekend sprint** — literally using the system and deciding whether it's good.

No copier implications: manual review is a process, not infrastructure.

## Trade-offs

**Pro:** zero setup; catches nuance automated metrics miss; builds intuition about what
"good" means.
**Con:** doesn't scale; not repeatable; varies by reviewer; can't run in CI; blocks
deployment if required for every change.

**Upgrade path:** manual review → identify failure patterns → write golden QA pairs from
*real* failures → automate with golden-set grading. This is why the ladder starts here:
*"Bad eval with 10 real questions beats no eval with plans for 500."*

## See Also
- [[Online Eval Sampling]] <!-- auto-linked -->
- [[Eval Ladder]] — part-of (rung 1)
- [[Golden Set Mechanics]] — upgrade-path (failure patterns become golden cases)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (human grades are the calibration target)
- [[HITL Annotation Pipeline]] — related (systematized human judgment)
