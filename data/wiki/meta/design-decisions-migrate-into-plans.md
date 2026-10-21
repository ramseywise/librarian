---
title: Design Decisions Migrate Into Plans
tags: [meta, pattern]
summary: When design skills run once at initiative start, the real design decisions migrate into per-issue plans (a decision register grew 30 → 124 rows with zero design passes) because design output is the wrong granularity, shape and trigger for a one-issue-at-a-time pipeline — the fix is to turn design content into checklist rows the workflow reads, and measure "upstream-silent" questions per plan.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-22-design-phase-questions-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-09-22-design-phase-questions-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-22-design-phase-questions-audit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-design-skills-quarterly-refresh.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-design-skills-quarterly-refresh.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-design-skills-quarterly-refresh.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-design-skills-quarterly-refresh.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-design-skills-quarterly-refresh.md
---

# Design Decisions Migrate Into Plans

An audit in diskoe (2026-09-22) harvested ~560 open questions across 227 plans to find
where design decisions were actually being made. The design skills
([[Four-Stage Design Pipeline with Backflow]]) had run **once**, at initiative start. In the
following month the decision register grew from **30 to 124 rows**, and every one of the 94
new rows arrived through a plan, build or review commit — not a design pass.

> "A decision registry that only records answers to *asked* questions has a blind spot."

## Where decisions actually get made

| Stage | What it really contributes |
|---|---|
| Research | Surfaces absence and false premises, resolves neither. ~A third of build-state research concluded the *issue or spec* was wrong, not the code ("The issue's premise is false. The column exists.") |
| Plan | **Where the design decision is made.** ~55% of questions resolved in-plan "by repo precedent", not product intent |
| Refine | Separates operator-needed questions from code-settleable ones |
| Build | Adds deviations; ~39 plans punt tunables to execute time ("is a guess, not a measured value") |
| Review | Surfaces no new design questions, but ~30% of findings anchor on a design doc |

Resolution modes: decided in-plan ~55%, escalated to the operator ~20%, deferred to a named
issue ~15%, honestly left ungated ~10%. A question reaches the human only when the answer is
unknowable from the tree (legal facts, host, domain); product-shaped questions (ranking
formula, floor-or-ceiling) get decided silently under a stated default.

## Eight recurring clusters

Eval/verification (does a real corpus exist?), data contract/vocabulary (who owns the value
list?), operations (caps, cadence, host), product scope (floor vs ceiling), **trust/rights/
retention** (the most-escalated cluster — with no checklist row anywhere), UX states,
economics, and decision-ID allocation as a coordination problem between concurrent plans.

## Why design content stays inert

The design skills already *described* most of the answers. Three reasons none of it reached
the pipeline:

1. **Granularity.** One HITL-gated document per initiative, rewritten whole; the pipeline
   consumes one issue at a time and nothing maps an issue to the envelope row it must meet.
2. **Shape.** Persona prose ("the Designer is accountable for…") is not a lookup table.
   *Lanes are checklists, not personas.*
3. **Trigger.** Nothing in triage → plan → refine reads a design skill. Rewriting the skill
   description to get it invoked failed twice.

## The fix: rows, not a second skill

Don't create a parallel design-shared contract ("a rule stated in two skills is wrong in
one of them"). Extend the existing Definition-of-Ready/Done rows:

- **A `rights` lane:** any crawled-source field, outbound fetch, image URL, user-identifying
  column or retention-bearing table names its posture and retention class.
- **Every enum names its value list**, the spec that owns it, and the DB `CHECK` (or why none).
- **Every numeric tunable is labelled** `measured: <source>` or `guess: <what replaces it>`.
  A guessed cap is fine; a silent constant is not.
- **Behavioural cases from the requirement:** 10–20 Given/must/must-not cases written
  *before* the function exists (cases authored by running it are the own-oracle trap).
- **The observing corpus is named and counted today.** Zero rows is a valid answer — it turns
  "Done target: measured" into a follow-up with a named producer.
- **Empty states split:** empty-because-filtered vs empty-because-broken must not render alike.
- **Verify issue premises:** research lists the claims in the issue body that the tree
  contradicts, so a plan on a false premise fails refine instead of build.
- **Any number in an acceptance criterion names its meter.** A budget with no meter is a
  preference.

Design skills then become **phase-gate refresh skills** fed by the backflow, not blank-page
authors.

## Measure the questions, not the invocations

An earlier attempt measured "design-skill invocation count" — the wrong thing. Instead tag
every plan Open Question `origin: upstream-silent | upstream-wrong | new | tunable` and track
upstream-silent questions per plan **by lane**: lanes that got rows should fall, lanes that
didn't are the control. Baseline: ~30 upstream-silent/wrong findings across 227 plans; 3 of
227 plans carried lanes.

## Implementing the fix: refresh mode reads a backflow digest (akira, 2026-09-22)

The follow-up plan, which was executed, added the rows to the shared workflow contract.
It changed the design skills only by **citing** those rows, never restating them. It
also added a quarterly refresh mode. Specifics worth reusing:

- **The backflow digest is generated, not remembered.** A few `git` and `grep` commands
  produce it. They diff the set of decision, risk and contradiction IDs in the
  requirements doc between the last design run and now (110 new IDs). They list the
  commits that added them, which name the plans, builds and reviews involved. They count
  `upstream-silent/wrong` origin tags, and count review findings anchored on doc paths
  rather than code.
- **A dimension with three or more backflow rows is stale**, even if the problem statement
  is unchanged. In that case the pipeline has been designing that dimension one issue at
  a time.
- **Each design-envelope dimension maps to the lane row(s) it feeds**, so the design skill
  and the pipeline ask the same question at different altitudes. A dimension that cannot
  be answered at initiative altitude is dispositioned `RESEARCH FIRST`, not left to a plan.
- **Refresh allocates ID blocks** to the quarter's concurrent plans. Concurrent plans all
  claim the same next number, which is why a spec-numbers gate already existed.
- **`rights` is a lane, not a `data` sub-row.** Its triggers (an outbound fetch, an image
  URL, a human-review step) are not data-path signals. As a sub-row it would inherit the
  data lane's path triggers and miss a prompt-only or UI-only change.
- **Rewording skill descriptions changed nothing** in two earlier attempts. The plan adds
  rows and inputs, not prose.
- The origin tag ships as a grep in the retro step before it becomes a schema field. It
  is promoted only after a quarter of use.

## See Also
- [[Four-Stage Design Pipeline with Backflow]] — extends
- [[Evidence-Gated Skill Pipeline]] — extends
- [[Every Column Names Its Reader]] — extends
- [[Ungated Metric Convention]] — extends
- [[Claude Workflow System]] — instance-of
- [[Budget Without a Meter Is a Preference]] — extends
