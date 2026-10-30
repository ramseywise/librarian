---
title: Error Analysis (Open and Axial Coding)
tags: [eval, llm, pattern]
summary: "Find failure modes by reading ~100 traces before choosing any metric — free-text note on the first thing that went wrong (open coding), group notes into 5–15 categories (axial coding), rank by frequency × cost, and build graders only for failures you have actually seen."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--02-defining-correct.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Error Analysis (Open and Axial Coding)

Most eval problems are specification problems, and failure modes cannot be listed in
advance — they are found by reading outputs. Error analysis is the method, borrowed from
qualitative research and taught in the practitioner field guide by Husain and Shankar.

> **Don't build a grader for a failure mode you haven't seen.** Generic metrics
> ("helpfulness", "coherence") measure something, but rarely what is actually going wrong.

## The procedure

1. **Collect ~100 traces** — real if you have them, synthetic if not yet
   ([[Synthetic Dataset Generation for RAG Eval]]).
2. **Open coding.** Read each trace and write a short free-text note on the **first** thing
   that went wrong. No categories yet ("cited the 2023 pricing page", "asked for the order ID
   it already had").
3. **Axial coding.** Group the notes into categories ("stale source", "ignored context",
   "wrong tool"). Expect 5–15.
4. **Count.** Rank categories by **frequency × cost**. That ranking is the eval roadmap:
   build graders for the top few first.
5. **Repeat** until new traces stop producing new categories — theoretical saturation,
   usually 50–100 traces.

**Note the first failure only.** Later failures in a trajectory are often caused by the
first; counting them inflates the wrong category. This is the same "label the earliest
stage" rule that orders an [[Eval Failure Taxonomy]].

The output of the procedure is the failure taxonomy; the rows behind each category seed the
first golden set ([[Golden Set Mechanics]]).

## Before error analysis: write success down

Four written answers precede any data or grader:

| Question | Good answer shape |
|---|---|
| What does the user need? | A concrete deliverable, in their language, citing the source |
| What must never happen? | Named never-events (invented menu path, leaked customer data, answering a legal question instead of escalating) |
| What is the unit of success? | Per turn *and* per conversation (e.g. resolved without escalation in ≤ 6 turns) |
| What does being wrong cost? | Sets the thresholds — cheap errors can ship at 90%; expensive ones need a fallback path |

## The two-expert test

A task is well specified when **two domain experts would independently reach the same
pass/fail verdict**. Run it literally: give 20 outputs and the written criteria to two
people. Where they disagree, fix the criteria, not the people and not the grader. The
quantitative version of this check is the [[Human Agreement Ceiling Protocol]].

## One person decides

Husain recommends a single domain expert as the final word on pass/fail (the "benevolent
dictator"). Committees produce vague criteria; one accountable person produces sharp ones.
Others contribute traces and argue cases.

## Criteria drift is how the spec is discovered

Shankar et al. (*Who Validates the Validators?*, 2024) found that graders' criteria change
**while they grade** — reading outputs reveals requirements nobody wrote down. Plan for it:
version the criteria and re-grade earlier samples when they change. Unversioned criteria
drift is also a judge-drift cause ([[Eval Suite Maintenance]]).

## From criteria to dimensions

Once criteria are clear, split them into **independent dimensions** (correctness,
grounding, completeness, policy, format, efficiency), each with its own grader, and combine
only at the end, explicitly. One composite "quality" score lets a judge silently trade one
dimension for another — see [[Veto Rubric Items]] and [[Specialist Verdict Panel]].

## See Also
- [[Eval Failure Taxonomy]] — prerequisite-for (the taxonomy is the output of axial coding)
- [[Manual Review as Eval Bootstrap]] — extends (the structured version of reading outputs first)
- [[Golden Set Mechanics]] — prerequisite-for (coded failures seed the first rows)
- [[Human Agreement Ceiling Protocol]] — extends (the two-expert test, measured as κ)
- [[Decompose Low-Ceiling Dimensions into Checkable Sub-Signals]] — related (what to do when experts cannot agree)
- [[Eval-Driven Development (EDD)]] — related
